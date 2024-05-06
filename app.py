import requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import locale
import tensorflow as tf
import geocoder
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
from geopy.geocoders import Nominatim
from os import system, name


locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Allow image files to be submitted
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# Import the model
model = tf.keras.models.load_model('model.h5')

# API key for OpenUV
OPENUV_API_KEY = 'openuv-11bvz3rlvm6g1gn-io'  # Replace this with your actual API key

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_image(file_path, model):
    # Resize image file
    img = image.load_img(file_path, target_size=(224, 224))
    # Convert the file into an array of values
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # And normalize the image
    
    prediction = model.predict(img_array) # Predict the array-converted image using the deployed model
    prediction_score = prediction[0][0]  # Get prediction score in a form of binary classification
    
    # Malignant and benign classifications
    if prediction_score > 0.5:
        result = "Malignant"
    else:
        result = "Benign" # Results ranges from 0.49 to less than 0.01
    
    return result, float(prediction_score)  # Ensure prediction_score is a float type



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze-skin')
def analyze_skin():
    return render_template('analyze-skin.html')

@app.route('/skin-type')
def skin_type():
    return render_template('skin-type.html')

@app.route('/upload', methods=['POST'])

# File function
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    # Get file from the website
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Use the 'uploads' folder to store the uploaded image
        file_path = os.path.join('uploads', filename)

        file.save(file_path)

        # Predict the image using that function
        result, scaled_value = predict_image(file_path, model)

        # Remove the image after analysis
        os.remove(file_path)
        
        # Display the response of the model
        return jsonify({'result': result, 'scaled_value': scaled_value})
    else:
        return jsonify({'error': 'Invalid file extension'})



################UV INDEX SECTION##############################################
geolocator = Nominatim(user_agent="coordinateconverter")
def get_user_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            lat, lon = g.latlng
            print(f"Latitude: {lat}, Longitude: {lon}")  # Add this line for debugging
            return lat, lon
    except Exception as e:
        print(f"Error getting user location: {e}")
    return None


@app.route('/uv-index')
def uv_index():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    # Initialize location to None
    location = None

    # Check if latitude and longitude are provided
    if lat is None or lon is None:
        # Try to get user's location using their IP address
        user_location = get_user_location()
        if user_location:
            lat, lon = user_location

    # If still no coordinates, return error response
    if lat is None or lon is None:
        return jsonify({'error': 'Latitude and longitude could not be determined'})

    # Print latitude and longitude for debugging
    print(f"Latitude: {lat}, Longitude: {lon}")

    # Use provided location string if available
    provided_location = request.args.get('location')
    if provided_location:
        location = provided_location
        print("Location from request:", location)  # Add this line for debugging

    # If location is still None, try to get it from coordinates
    if location is None:
        location = get_place_from_geopy(lat, lon)

    if location is None:
        print("Location is None, using default value")  # Add this line for debugging
        location = "Unknown Location"

    uv_index_data = get_uv_index(lat, lon)

    if 'error' in uv_index_data:
        print("Error fetching UV index data:", uv_index_data['error'])  # Log the error
        return jsonify({'error': 'Failed to fetch UV index data'})

    print("UV Index Data:", uv_index_data)  # Add this line for debugging

    # Render the 'uv-index.html' template and pass UV index data and location to it
    return render_template('uv-index.html', uv_index_data=uv_index_data, location=location)

def get_uv_index(lat, lon):
    headers = {'x-access-token': OPENUV_API_KEY}
    url = f"https://api.openuv.io/api/v1/uv?lat={lat}&lng={lon}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()

        current_uv_index = int(data.get('result', {}).get('uv') or 0)  # Convert to integer
        uv_max = int(data.get('result', {}).get('uv_max') or 0)  # Convert to integer
        location = data.get('result', {}).get('location', {}).get('name')  # Get location name

        return {
            'current_uv_index': current_uv_index,
            'uv_max': uv_max,
            'location': location  # Add location to the response
        }
    except Exception as e:
        print(f"Error fetching UV index data: {e}")
        return {'error': 'Failed to fetch UV index data'}

def get_place_from_geopy(lat, lon):
    try:
        geolocator = Nominatim(user_agent="coordinateconverter")
        location = geolocator.reverse((lat, lon), language='en')
        print("Location:", location)  # Add this line for debugging
        print("Raw data:", location.raw)  # Add this line for debugging
        if location:
            city = location.raw['address'].get('city')
            country = location.raw['address'].get('country')
            if city and country:
                return f"{city}, {country}"
            else:
                print("City or country not found in address")
                return None
        else:
            print("No results found from Geopy")
            return None
    except Exception as e:
        print(f"Error getting place from Geopy: {e}")
        return None



if __name__ == '__main__':
    app.run(debug=True)