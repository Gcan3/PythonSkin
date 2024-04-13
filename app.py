from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import locale
import tensorflow as tf
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app = Flask(__name__)
# Enable automatic reloading of templates
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Load the pre-trained model
model = tf.keras.models.load_model('model.keras')

# Define the allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Function to check if a file has a permitted file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to make predictions
def predict_image(file_path, model):
    img = image.load_img(file_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalize the image
    
    prediction = model.predict(img_array)
    prediction_score = prediction[0][0]  # Assuming binary classification
    
    if prediction_score > 0.5:
        return "Malignant", prediction_score
    else:
        return "Benign", prediction_score

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', message='No file part')

    file = request.files['file']

    if file and allowed_file(file.filename):
        # Save the file without encoding
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)

        # Save the file
        file.save(file_path)

        # Make prediction
        result, prediction_score = predict_image(file_path, model)

        # Delete the uploaded file
        os.remove(file_path)

        return render_template('index.html', message='Prediction: {}, Prediction Score: {:.2f}'.format(result, prediction_score))
    else:
        return render_template('index.html', message='Invalid file extension')

if __name__ == '__main__':
    app.run(debug=True)
