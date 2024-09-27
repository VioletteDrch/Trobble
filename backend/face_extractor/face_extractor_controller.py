from pathlib import Path

from flask import Blueprint, request, jsonify
import os

from backend.face_extractor.face_extractor import extract_face

face_extractor_bp = Blueprint('extractor', __name__)

# Define path to images inputs and outputs
backend_dir = Path(__file__).resolve().parent.parent
IMAGES_FOLDER = backend_dir.joinpath('images')
RAW_FOLDER = IMAGES_FOLDER.joinpath('raw')
PROCESSED_FOLDER = IMAGES_FOLDER.joinpath('processed')

# Ensure the folders exist
os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@face_extractor_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Store file in raw directory
        file_path = os.path.join(RAW_FOLDER, file.filename)
        file.save(file_path)

        # Extract face and store in processed directory
        output_path = os.path.join(PROCESSED_FOLDER, file.filename)
        extract_face(file_path, output_path)

        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200