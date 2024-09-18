from pathlib import Path
from os import listdir


from flask import Blueprint, request, jsonify
from backend.game_logic.game_state_elements import GameStateManager
import os

game_logic_bp = Blueprint('game_logic', __name__)

backend_dir = Path(__file__).resolve().parent.parent
IMAGES_FOLDER = backend_dir.joinpath('images').joinpath('processed')


@game_logic_bp.route('/get_symbols', methods=['GET'])
def get_symbols():
    symbols_files = listdir(IMAGES_FOLDER)
    # for s in symbols_files:


@game_logic_bp.route('/get_game_state', methods=['GET'])
def get_game_state():
    game = GameStateManager(2, 7)
    return jsonify(game.game_state)
