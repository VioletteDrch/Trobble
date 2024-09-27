from flask import Blueprint, jsonify

game_bp = Blueprint('game', __name__)


game_managers_by_game_id = {}


def init_game_controller(game_managers_dict):
    global game_managers_by_game_id
    game_managers_by_game_id = game_managers_dict


@game_bp.route('/<game_id>/cards', methods=['GET'])
def get_cards(game_id):
    manager = game_managers_by_game_id[game_id]
    return jsonify(manager.cards)


@game_bp.route('/<game_id>/game_state', methods=['GET'])
def get_game_state(game_id):
    manager = game_managers_by_game_id[game_id]
    return jsonify(manager.get_game_state())