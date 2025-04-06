from flask import Flask, request, jsonify
from rembg import remove
import base64
import re
from flask_cors import CORS

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
        image_data = re.sub("^data:image/.+;base64,", "", image_data)
        image_bytes = base64.b64decode(image_data)

        # Rimuovi lo sfondo
        output_bytes = remove(image_bytes)

        # Codifica il risultato in base64
        output_base64 = base64.b64encode(output_bytes).decode("utf-8")
        result_image = f"data:image/png;base64,{output_base64}"

        return jsonify({"image": result_image})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
