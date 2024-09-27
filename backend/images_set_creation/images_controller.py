from pathlib import Path

import numpy as np
from flask import Blueprint, request, jsonify, send_from_directory
import os

from backend.images_set_creation.face_extractor import extract_face

images_bp = Blueprint('images', __name__)

# Define path to images inputs and outputs
backend_dir = Path(__file__).resolve().parent.parent
IMAGES_FOLDER = backend_dir.joinpath('images')
RAW_FOLDER = IMAGES_FOLDER.joinpath('raw')
PROCESSED_FOLDER = IMAGES_FOLDER.joinpath('processed')

# Ensure the folders exist
os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@images_bp.route('/upload', methods=['POST'])
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


@images_bp.route('', methods=['GET'])
def get_images():
    image_files = os.listdir(PROCESSED_FOLDER)
    np.random.shuffle(image_files)  # return in random order
    return jsonify(image_files)


@images_bp.route('/<filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)