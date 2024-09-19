from pathlib import Path
from os import listdir

from flask import Blueprint, request, jsonify, send_from_directory
from backend.game_logic.game_state_elements import GameStateManager
import os

game_logic_bp = Blueprint('game-logic', __name__)

backend_dir = Path(__file__).resolve().parent.parent
IMAGES_FOLDER = backend_dir.joinpath('images').joinpath('processed')


@game_logic_bp.route('/images-list', methods=['GET'])
def get_images_urls():
    return jsonify(listdir(IMAGES_FOLDER))


@game_logic_bp.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)


# @game_logic_bp.route('/game-state', methods=['GET'])  # temp until the websocket server is up and running
# def get_game_state():
#     current_state = {
#         'middleCard': game_state_manager.get_middle_card_compo(),
#         'players': game_state_manager.game_state.players_cards_ids,
#     }
#     return jsonify(current_state)
