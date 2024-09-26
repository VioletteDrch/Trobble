from typing import Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.game_logic.game_state_elements import get_game_state_manager
from backend.lobby.lobby_repository import LobbyRepository
from backend.lobby.lobby_service import LobbyService
from backend.lobby.lobby_types import Lobby
from face_extractor.face_extractor_controller import face_extractor_bp
from lobby.lobby_controller import lobby_bp, init_lobby_controller
from game_logic.game_logic_controller import game_logic_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Enable CORS for cross-origin requests

app.register_blueprint(lobby_bp)
app.register_blueprint(face_extractor_bp)
app.register_blueprint(game_logic_bp)

lobby_repository: LobbyRepository = LobbyRepository()
lobby_service: LobbyService = LobbyService(lobby_repository)

init_lobby_controller(lobby_service)


@app.route('/start', methods=['POST'])
def start_game():
    print('Game started')
    data = request.get_json()
    lobby_code = data.get('lobbyCode')
    lobby: Optional[Lobby] = lobby_service.get_lobby(lobby_code)
    state_manager = get_game_state_manager(nb_players=3)
    return jsonify({"message": "Game started", "game_state": state_manager.get_game_state()})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
