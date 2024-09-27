from pathlib import Path
from os import listdir
import numpy as np

from flask import Blueprint, request, jsonify, send_from_directory
from game_state_elements import GameStateManager
import os

game_logic_bp = Blueprint('game-logic', __name__)

backend_dir = Path(__file__).resolve().parent.parent
IMAGES_FOLDER = backend_dir.joinpath('images').joinpath('processed')


@game_logic_bp.route('/images', methods=['GET'])
def get_images():
    image_files = listdir(IMAGES_FOLDER)
    np.random.shuffle(image_files)  # return in random order
    return jsonify(image_files)


@game_logic_bp.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)