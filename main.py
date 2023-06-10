#main.py
from flask import Flask, jsonify, request
from db import get_detail_vegetable
import tensorflow as tf
from tensorflow import keras
import numpy as np
import io
import os
import requests
from PIL import Image


model = keras.models.load_model("model.h5")
class_names = ['bawang-bombay', 'bawang-merah', 'bawang-putih', 'bayam', 'bayam-merah', 'brokoli', 'buncis', 'cabai', 'daun-bawang', 'jengkol', 'kacang-panjang', 'kacang-polong', 'kailan', 'kale', 'kangkung', 'kates', 'kecambah', 'kecipir', 'kemangi', 'kembang-kol', 'kentang', 'kubis', 'labu-kuning', 'labu-siam', 'lobak', 'melinjo', 'paprika', 'pare', 'petai', 'peterseli', 'rebung', 'sawi', 'selada', 'seledri', 'serai', 'singkong', 'talas', 'terong', 'timun', 'tomat', 'wortel']


def transform_image(image):
    image = image.convert("RGB")
    image = image.resize((224, 224))
    image_np = np.array(image)
    image_np = image_np / 255.0
    return image_np

def predict(x):
    input_image = np.expand_dims(x, axis=0)
    prediction = model.predict(input_image)
    class_probabilities = prediction[0]
    highest_prob_index = np.argmax(class_probabilities)
    highest_prob = class_probabilities[highest_prob_index]
    threshold = 0.5
    class_label = class_names[highest_prob_index]
    if highest_prob < threshold:
        return ["error", class_label, highest_prob]
    return ["success", class_label, highest_prob]

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def songs():
    return "OK"    

@app.route("/predict", methods=["POST"])
def index():
    if request.method == "POST":
        file = request.files.get('image')
        user_id = request.form['user_id']

        if file is None or file.name == "":
            return jsonify({"status": "failed", "message": "File not found"})
        
        try:
            image_bytes = file.read()
            pillow_img = Image.open(io.BytesIO(image_bytes))
            image_input = transform_image(pillow_img)
            prediction = predict(image_input)
        
            vegetable = get_detail_vegetable(class_name=prediction[1])

            save_history = False
            try:
                if user_id != 0:
                    save_history = requests.get(f"http://35.202.36.69/api/v1/save-history/{vegetable['id']}/{user_id}").json()
                
            except Exception as e:
                save_history = False

            data = {"status": "success", "message": "finished predict the image", "vegetable": vegetable, "probabilities": str(prediction[2] * 100), 'is_auth': save_history}

            return jsonify(data)
        except Exception as e:
            return jsonify({"status": "failed", "message": str(e)})
        


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
