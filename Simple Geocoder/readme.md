# Geocoder

This is a simple Flask app that turns addresses into coordinates. I wrote the actual app in 2019 but this readme was added after I cleaned up some bugs in 2024. I may or may not have also added a dark mode toggle while I was at it... I just like my eyes! No need to blind them :)

---

## Features

- **Geocode a Single Address**: Type in an address, get the latitude and longitude. Done.
- **CSV Upload**: Upload a CSV with an "Address" column, and it'll geocode all of them for you. Simple.
- **Flash Messages**: Success or failure, you’ll know what’s up.

---

## Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/akshayexists/randomprojects
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
OR
If you're like me and too lazy to deal with the entire bash terminal and stuff, just download this branch https://github.com/akshayexists/randomprojects/tree/main/Simple%20Geocoder :)


3. Run the app:

   ```bash
   python app.py
   ```

---

## How It Works

- **Single Address**: Enter an address, get latitude and longitude.
- **CSV Upload**: Upload a CSV with an "Address" column, and we’ll geocode the whole thing. Then, download the new CSV with coordinates. Easy.

---

## Flash Messages

- **Success**: "Geocoding successful!"
- **Error**: "Oops, something went wrong." (Should have an error message)

---

## Troubleshooting the CSV upload

- **No "Address" column?**: The app can’t read your file. Add a column called "Address" and try again.
- **File too big?**: Keep it under 16 MB. It’s a size thing.

---

## License

MIT License. Do whatever, just don’t blame me if you get rate limited by Geopy because I didn't bother to implement a timer for requests, should be fairly simple if you need it.
