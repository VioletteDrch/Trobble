from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import random
import string
from face_extractor.face_extractor import extract_face
from lobby.lobby_controller import lobby_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

IMAGES_FOLDER = 'images'
RAW_FOLDER = os.path.join(IMAGES_FOLDER, 'raw')
PROCESSED_FOLDER = os.path.join(IMAGES_FOLDER, 'processed')
app.config['RAW_FOLDER'] = RAW_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

app.register_blueprint(lobby_bp)

# Ensure the folders exist
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Store file in raw directory
        file_path = os.path.join(app.config['RAW_FOLDER'], file.filename)
        file.save(file_path)

        # Extract face and store in processed directory
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], file.filename)
        extract_face(file_path, output_path)

        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
