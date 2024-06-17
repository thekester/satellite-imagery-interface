from flask import Flask, request, jsonify, render_template
import ee
import os
import logging
from datetime import datetime
import json

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

# Get current working directory and list files
cwd = os.getcwd()
files = os.listdir(cwd)
logging.debug("Files in %r: %s", cwd, files)

# Replace with your service account email and the path to your private key
with open('privatekey.json', 'r') as file:
    data = json.load(file)

service_account = data.get("service_account")
key_path = 'privatekey.json'

# Authenticate and initialize Earth Engine
try:
    credentials = ee.ServiceAccountCredentials(service_account, key_path)
    ee.Initialize(credentials)
    logging.info("Earth Engine initialized successfully.")
except Exception as e:
    logging.error("Error initializing Earth Engine: %s", e)

# Verify initialization
try:
    info = ee.Image('COPERNICUS/S2_SR/20190606T104031_20190606T104545_T31TFJ').getInfo()
    logging.debug("Earth Engine Image info: %s", info)
except Exception as e:
    logging.error("Error fetching image info: %s", e)

@app.route('/')
def home():
    return render_template('template.html')

def maskS2clouds(image):
    qa = image.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    return image.updateMask(mask).divide(10000)

def find_images(lon, lat, start_date, end_date):
    point = ee.Geometry.Point(lon, lat)
    image_collection = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
                        .filterBounds(point) \
                        .filterDate(start_date, end_date) \
                        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                        .map(maskS2clouds) \
                        .sort('CLOUDY_PIXEL_PERCENTAGE')
    return image_collection

@app.route('/v5000/earth/imagery/', methods=['GET'])
def get_imagery():
    try:
        lon = float(request.args.get('lon'))
        lat = float(request.args.get('lat'))
        year = request.args.get('date')
        dim = float(request.args.get('dim', 0.1))
        
        logging.debug("Received parameters - Longitude: %f, Latitude: %f, Year: %s, Dimension: %f", lon, lat, year, dim)

        # Validate the year format
        try:
            year_int = int(year)
            start_date = f"{year_int}-01-01"
            end_date = f"{year_int}-12-31"
            logging.debug("Year is valid: %d", year_int)
        except ValueError as ve:
            logging.error("Invalid year format: %s", year)
            return jsonify({"error": "Invalid year format. Please use YYYY."}), 400

        # Find images within the year range
        image_collection = find_images(lon, lat, start_date, end_date)
        collection_size = image_collection.size().getInfo()
        logging.debug("Image collection size for year range: %d", collection_size)

        if collection_size == 0:
            logging.warning("No images found for year range. Exiting.")
            return jsonify({"error": "No images found for the given year and location. Please try different years or locations."}), 404

        image = image_collection.first().select(['B4', 'B3', 'B2'])
        logging.debug("Selected image bands.")

        region = ee.Geometry.Point(lon, lat).buffer(dim * 1000).bounds().getInfo()['coordinates']
        logging.debug("Region for thumbnail: %s", region)

        # Define visualization parameters
        vis_params = {
            'min': 0,
            'max': 0.3,
            'bands': ['B4', 'B3', 'B2'],
            'gamma': 1.4
        }

        thumbnail = image.getThumbURL({
            'region': region,
            'dimensions': '2048x2048',  # Increased resolution
            'format': 'png',
            **vis_params
        })
        logging.info("Thumbnail URL generated successfully: %s", thumbnail)

        return jsonify({"url": thumbnail})
    except Exception as e:
        logging.error("Error in get_imagery: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
