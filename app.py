from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import locale
import tensorflow as tf

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Allow image files to be submitted
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# Import the model
model = tf.keras.models.load_model('model.h5')

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

@app.route('/risk-profile')
def risk_profile():
    return render_template('risk-profile.html')

@app.route('/skin-type')
def skin_type():
    return render_template('skin-type.html')

@app.route('/uv-index')
def uv_index():
    return render_template('uv-index.html')

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


if __name__ == '__main__':
    app.run(debug=True)