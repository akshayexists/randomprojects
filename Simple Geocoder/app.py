from flask import Flask, render_template, request, redirect, url_for, flash
from geopy.geocoders import Nominatim
import pandas as pd
import datetime
import os
import traceback

app = Flask(__name__)

# Setup for file upload and geocoding
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size (16 MB)
UPLOAD_FOLDER = 'static/uploads/'  # Save to static/uploads
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

# Route to handle single address geocoding
@app.route("/geocode_single_address", methods=["POST"])
def geocode_single_address():
    address = request.form.get("address")

    if address:
        geocoder = Nominatim(user_agent="GeocoderApp")
        try:
            location = geocoder.geocode(address)
            if location:
                lat, lon = location.latitude, location.longitude
                return render_template("index.html", text=f"Address found: {lat}, {lon}", 
                                       lat=lat, lon=lon, address=address)
            else:
                flash('Address not found.', 'error')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error geocoding address: {str(e)}", 'error')
            return redirect(url_for('index'))
    else:
        flash("Please enter an address.", 'error')
        return redirect(url_for('index'))

# Route to handle CSV file upload and geocoding
@app.route('/success-table', methods=['POST'])
def success_table():
    if request.method == "POST":
        file = request.files.get('file')

        if not file or not file.filename.endswith('.csv'):
            flash("Invalid file. Only CSV files are allowed.", 'error')
            return redirect(url_for('index'))

        try:
            # Save the file in static/uploads/
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            df = pd.read_csv(file_path)

            if 'Address' not in df.columns:
                flash("CSV does not contain 'Address' column.", 'error')
                return redirect(url_for('index'))

            gc = Nominatim(user_agent="geocoder_service")

            # Filter out empty addresses
            df = df[df['Address'].notna()]

            # Geocode addresses
            def geocode_address(address):
                try:
                    location = gc.geocode(address)
                    if location:
                        return location.latitude, location.longitude
                    else:
                        return None, None
                except Exception:
                    return None, None

            df['Latitude'], df['Longitude'] = zip(*df['Address'].apply(geocode_address))

            # Save the geocoded CSV file
            geocoded_filename = "geocoded_" + file.filename  # You can modify this as per your requirement
            geocoded_filepath = os.path.join(app.config['UPLOAD_FOLDER'], geocoded_filename)
            df.to_csv(geocoded_filepath, index=False)

            # Pass df and geocoded filename to the template
            return render_template("index.html", text="Geocoding successful.", 
                                   df=df.to_html(classes='table table-bordered', index=False),
                                   filename=geocoded_filename)

        except Exception as e:
            error_message = traceback.format_exc()
            flash(f"Error processing file: {error_message}", 'error')
            return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
