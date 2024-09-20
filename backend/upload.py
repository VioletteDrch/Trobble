from flask import current_app as app, request, jsonify
from face_extractor.face_extractor import extract_face
import uuid
import random
import os

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
