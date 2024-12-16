# Motion Detector Desk Lock - **Your Laptop's Personal Bodyguard**

## What is it?

This Python script is your desk's bouncer—keeping unwanted guests at bay while you're away:

- **Motion Detection**: It keeps a vigilant

 eye on your desk and detects movement.
- **Face Recognition**: It recognizes you and won't alert you when you're back (we know you don't need a notification every time).
- **Intruder Alerts**: If someone sneaks in, it takes their photo and emails it straight to you.
- **Lock Screen**: When you're gone, your desk locks up with a "Do Not Disturb" image.
  
## Features:

- **Face Recognition**: It recognizes you and prevents false alerts.
- **Robust Motion Detection**: Detects movement and notifies you if there's an intruder.
- **Automatic Webcam Reconnect**: If the webcam disconnects or fails, it will automatically attempt to reconnect.
- **Automatic Lock Screen**: It locks your screen when you're away from your desk for a while.
- **Email Alerts with Retries**: If email sending fails, the script retries, so you never miss an alert.

## Setup:

1. **USER_EMAIL**: Enter your email address where you want the alerts to go (Line 7).
2. **USER_IMAGE_PATH**: Put your face photo in the specified path (Line 8).
3. **ALERT_EMAIL**: The email address that will send you the alerts (Line 10).
4. **Lock Screen Image**: Ensure you have a custom lock screen image (Line 14).
5. **Email Credentials**: Set up the SMTP server and email credentials for sending alerts (Lines 15-17).

## License

Licensed under the **"Stay-Away-From-My-Damn-Desk"**. (MIT License lol, play with it as you wish, just credit me)

## Enjoy your **peace of mind**!

---

I wrote this in 2021, my aim was to learn error logging (opencv is annoyingly error-prone to write code for) and make some kind of a motion detector after I watched a show about them :)
