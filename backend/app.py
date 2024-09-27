from typing import Optional, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.game.game_controller import game_bp, init_game_controller
from backend.game_logic.game_state_elements import GameStateManager
from backend.lobby.lobby_repository import LobbyRepository
from backend.lobby.lobby_service import LobbyService
from backend.lobby.lobby_types import Lobby
from images_set_creation.images_controller import images_bp
from lobby.lobby_controller import lobby_bp, init_lobby_controller

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Enable CORS for cross-origin requests

app.register_blueprint(lobby_bp)
app.register_blueprint(images_bp, url_prefix='/images')
app.register_blueprint(game_bp, url_prefix='/game')

lobby_repository: LobbyRepository = LobbyRepository()
lobby_service: LobbyService = LobbyService(lobby_repository)

game_state_managers_by_lobby_code: Dict[str, GameStateManager] = {}

init_lobby_controller(lobby_service)
init_game_controller(game_state_managers_by_lobby_code)


@app.route('/start', methods=['POST'])
def start_game():
    print('Game started')
    data = request.get_json()
    lobby_code = data.get('lobbyCode')
    lobby: Optional[Lobby] = lobby_service.get_lobby(lobby_code)

    if lobby is not None:
        game_state_managers_by_lobby_code[lobby_code] = GameStateManager(nb_players=len(lobby["players"].keys()))
        return jsonify({"message": "Game started"})

    return jsonify({"error": "Lobby not found"}), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
