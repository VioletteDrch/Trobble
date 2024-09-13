from pathlib import Path

from flask import Blueprint, request, jsonify
import os

game_logic_bp = Blueprint('game_logic', __name__)


@game_logic_bp.route('/get_symbols')
def get_symbols():
    pass


@game_logic_bp.route('/get_game_state')
def get_symbols():
    pass