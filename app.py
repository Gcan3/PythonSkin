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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
model = tf.keras.models.load_model('model.h5')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_image(file_path, model):
    img = image.load_img(file_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalize the image
    
    prediction = model.predict(img_array)
    prediction_score = prediction[0][0]  # Assuming binary classification
    
    if prediction_score > 0.5:
        result = "Malignant"
    else:
        result = "Benign"
    
    return result, float(prediction_score)  # Ensure prediction_score is a regular Python float



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze-skin')
def analyze_skin():
    return render_template('analyze-skin.html')

@app.route('/results')
def results():
    result = request.args.get('result')
    prediction_score = request.args.get('prediction_score')
    return render_template('results.html', result=result, prediction_score=prediction_score)

@app.route('/skin-type')
def skin_type():
    return render_template('skin-type.html')

@app.route('/uv-index')
def uv_index():
    return render_template('uv-index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)

        file.save(file_path)

        result, prediction_score = predict_image(file_path, model)

        os.remove(file_path)

        return jsonify({'result': result, 'prediction_score': prediction_score})
    else:
        return jsonify({'error': 'Invalid file extension'})




if __name__ == '__main__':
    app.run(debug=True)
