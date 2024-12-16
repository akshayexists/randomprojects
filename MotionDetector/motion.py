import cv2
import os
import time
import smtplib
import numpy as np
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from imutils.video import VideoStream
from threading import Thread
import logging
import signal
import sys
import random

logging.basicConfig(filename="motion_detector.log", level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

USER_EMAIL = "user@example.com"
USER_IMAGE_PATH = "user_image.jpg"
ALERT_EMAIL = "alert@example.com"
MOTION_THRESHOLD = 5000
LOCK_SCREEN_IMAGE_PATH = "lock_screen_image.jpg"
MOTION_DURATION = 5
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_PASSWORD = "password"

def check_file_exists(file_path, file_description):
    if not os.path.exists(file_path):
        logging.error(f"{file_description} not found: {file_path}")
        sys.exit(f"Error: {file_description} not found at {file_path}")

check_file_exists(USER_IMAGE_PATH, "User image")
check_file_exists(LOCK_SCREEN_IMAGE_PATH, "Lock screen image")

vs = None
def init_webcam():
    global vs
    attempts = 5
    while attempts > 0:
        vs = VideoStream(src=0).start()
        frame = vs.read()
        if frame is not None:
            logging.info("Webcam successfully initialized.")
            return
        time.sleep(1)
        attempts -= 1
        logging.warning(f"Failed to initialize webcam. Retrying... {attempts} attempts left.")
    logging.error("Failed to initialize webcam after multiple attempts.")
    sys.exit("Error: Webcam initialization failed.")

init_webcam()

# Use LBPH for face recognition
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
lbph = cv2.face_LBPHFaceRecognizer.create()

def load_user_image():
    user_image = cv2.imread(USER_IMAGE_PATH)
    if user_image is None:
        logging.error("User image invalid.")
        sys.exit("Error: User image is invalid.")
    gray = cv2.cvtColor(user_image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        sys.exit("Error: No face detected in the user image.")
    (x, y, w, h) = faces[0]
    user_face = gray[y:y + h, x:x + w]
    lbph.train([user_face], np.array([0]))
    return lbph

user_lbph = load_user_image()

def send_email_alert(image_path):
    try:
        msg = MIMEMultipart()
        msg['From'] = ALERT_EMAIL
        msg['To'] = USER_EMAIL
        msg['Subject'] = "Motion Detected at Your Desk!"
        msg.attach(MIMEText("Motion detected. A photo has been captured.", 'html'))

        with open(image_path, "rb") as img_file:
            img_data = MIMEImage(img_file.read())
            img_data.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
            msg.attach(img_data)

        retry_send_email(msg)
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        raise

def retry_send_email(msg, retries=3):
    for attempt in range(retries):
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(ALERT_EMAIL, SMTP_PASSWORD)
                server.sendmail(ALERT_EMAIL, USER_EMAIL, msg.as_string())
            logging.info("Alert email sent successfully.")
            return
        except Exception as e:
            logging.error(f"Error sending email, attempt {attempt + 1}/{retries}: {e}")
            time.sleep(random.uniform(2, 4))
    logging.error("Email sending failed after multiple attempts.")
    raise Exception("Email sending failed.")

def detect_motion(frame, prev_frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (21, 21), 0)
    if prev_frame is None:
        return None, gray_blurred

    frame_delta = cv2.absdiff(prev_frame, gray_blurred)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_area = 0
    for contour in contours:
        if cv2.contourArea(contour) > MOTION_THRESHOLD:
            motion_area += cv2.contourArea(contour)
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return motion_area, gray_blurred

def is_known_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    for (x, y, w, h) in faces:
        face_roi = gray[y:y + h, x:x + w]
        label, confidence = lbph.predict(face_roi)
        if confidence < 100:  # Low confidence indicates a match
            return True
    return False

def display_lock_screen(frame):
    lock_screen = cv2.imread(LOCK_SCREEN_IMAGE_PATH)
    lock_screen_resized = cv2.resize(lock_screen, (frame.shape[1], frame.shape[0]))
    cv2.putText(lock_screen_resized, "Your Desk is Unattended", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
    cv2.imshow("Locked Screen", lock_screen_resized)  # Show the lock screen while no motion is detected
    cv2.waitKey(1)  # This ensures the lock screen is updated continuously

def motion_detection_loop():
    prev_frame = None
    motion_detected_time = None
    frame_count = 0
    face_check_interval = 10

    while True:
        frame = vs.read()
        if frame is None:
            logging.warning("Failed to grab frame from webcam. Reinitializing...")
            init_webcam()
            continue

        motion_area, prev_frame = detect_motion(frame, prev_frame)
        
        # If significant motion is detected, handle accordingly
        if motion_area is not None and motion_area > MOTION_THRESHOLD:
            motion_detected_time = time.time()
            logging.info("Significant motion detected.")

            if frame_count % face_check_interval == 0:
                if not is_known_face(frame):
                    logging.info("Stranger detected. Capturing photo and sending alert.")
                    photo_path = f"stranger_{int(time.time())}.jpg"
                    cv2.imwrite(photo_path, frame)
                    send_email_alert(photo_path)

        # If no motion detected for a while, show the lock screen
        if motion_detected_time is not None and time.time() - motion_detected_time > MOTION_DURATION:
            logging.info("No motion detected for a while. Displaying lock screen.")
            display_lock_screen(frame)

        # Keep the lock screen displayed continuously, even when motion is detected
        if motion_detected_time is None or time.time() - motion_detected_time > MOTION_DURATION:
            display_lock_screen(frame)  # Ensure the lock screen is visible when idle

        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vs.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        motion_thread = Thread(target=motion_detection_loop, daemon=True)
        motion_thread.start()

        signal.signal(signal.SIGINT, lambda signum, frame: sys.exit("Program exited gracefully."))

        motion_thread.join()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit("Fatal error, exiting.")
