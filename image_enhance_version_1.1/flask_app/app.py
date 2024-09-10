import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  

import time
import cv2
from PIL import Image
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from flask import Flask, render_template, request, send_file

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SAVED_MODEL_PATH = "https://tfhub.dev/captain-pool/esrgan-tf2/1"
model = hub.load(SAVED_MODEL_PATH)

def preprocess_image(image_path):
    hr_image = tf.image.decode_image(tf.io.read_file(image_path))
    if hr_image.shape[-1] == 4:
        hr_image = hr_image[...,:-1]
    hr_size = (tf.convert_to_tensor(hr_image.shape[:-1]) // 4) * 4
    hr_image = tf.image.crop_to_bounding_box(hr_image, 0, 0, hr_size[0], hr_size[1])
    hr_image = tf.cast(hr_image, tf.float32)
    return tf.expand_dims(hr_image, 0)

def save_image(image, filename):
    if not isinstance(image, Image.Image):
        image = tf.clip_by_value(image, 0, 255)
        image = Image.fromarray(tf.cast(image, tf.uint8).numpy())
    image.save(filename)
    print(f"Saved as {filename}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            
            hr_image = preprocess_image(filename)
            fake_image = model(hr_image)
            fake_image = tf.squeeze(fake_image)
            
            enhanced_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'enhanced_' + file.filename)
            save_image(fake_image, enhanced_filename)
            
            return send_file(enhanced_filename, mimetype='image/jpeg')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)