from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import numpy as np
from PIL import Image
import cv2

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return "Background Removal Service is running!"


@app.route("/remove", methods=["POST"])
def remove_background():
    try:
        data = request.json
        if not data or "image" not in data:
            return jsonify({"error": "Immagine non fornita"}), 400

        # Decodifica l'immagine base64
        image_data = data["image"]
        image_data = image_data.split(",")[1] if "," in image_data else image_data
        image_bytes = base64.b64decode(image_data)

        # Carica l'immagine con OpenCV
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        # Converti in RGBA se necessario
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGRA)

        # Crea una maschera per lo sfondo bianco
        # Questa è una tecnica semplificata - può essere migliorata per casi specifici
        lower_white = np.array([200, 200, 200, 0])
        upper_white = np.array([255, 255, 255, 255])
        mask = cv2.inRange(img, lower_white, upper_white)

        # Applica una sfocatura per ammorbidire i bordi della maschera
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        # Imposta i pixel bianchi come trasparenti
        img[:, :, 3] = cv2.bitwise_not(mask)

        # Converti l'immagine in PNG con trasparenza
        _, buffer = cv2.imencode(".png", img)
        output_base64 = base64.b64encode(buffer).decode("utf-8")

        return jsonify({"image": f"data:image/png;base64,{output_base64}"})
    except Exception as e:
        print(f"Errore: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
