from os import listdir
from pathlib import Path

import numpy as np
from flask import Blueprint, jsonify, send_from_directory

from backend.game_logic.game_state_elements import GameStateManager

game_bp = Blueprint('game', __name__)


@game_bp.route('/cards', methods=['GET'])
def get_cards():
    manager = GameStateManager(3, 7)
    return jsonify(manager.cards)


@game_bp.route('/game_state', methods=['GET'])
def get_game_state():
    manager = GameStateManager(3, 7)
    return jsonify(manager.get_game_state())