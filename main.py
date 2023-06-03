import tensorflow as tf
import numpy as np
import io
import os
from flask import Flask, request, jsonify
from PIL import Image

model = tf.saved_model.load('./')
class_labels = ['petai', 'peterseli', 'rebung', 'serai', 'bawang-bombay', 'bawang-merah', 'bawang-putih', 'bayam', 'bayam-merah', 'brokoli', 'buncis', 'cabai', 'cauliflower', 'daun-bawang', 'jengkol', 'kacang-panjang', 'kailan', 'kale', 'kangkung', 'kates', 'kecambah', 'kecipir', 'kemangi', 'kubis', 'lobak', 'paprika', 'pare', 'peas', 'potato', 'sawi', 'selada', 'seledri', 'singkong', 'spinach', 'terong', 'timun', 'tomat', 'wortel']

def transform_image(image):
    image = image.resize((224, 224))
    image_np = np.array(image)
    image_np = image_np / 255.0
    image_np = image_np.astype(np.float32)
    return image_np

def predict(x):
    input_tensor = tf.convert_to_tensor(x)
    input_tensor = input_tensor[tf.newaxis, ...]
    
    prediction = model(input_tensor)
    predicted_class = np.argmax(prediction)
    predicted_label = class_labels[predicted_class]
    return predicted_label

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get('file')
        if file is None or file.name == "":
            return jsonify({"status": "failed", "message": "No file"})
        
        try:
            image_bytes = file.read()
            pillow_img = Image.open(io.BytesIO(image_bytes))
            tensor = transform_image(pillow_img)
            prediction = predict(tensor)
            data = {"status": "success", "message": "Finished predict the image", "prediction": prediction}
            return jsonify(data)
        except Exception as e:
            return jsonify({"status": "failed", "message": str(e)})
        
    return "OK"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))