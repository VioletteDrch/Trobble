from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.game_logic.game_state_elements import get_game_state_manager
from face_extractor.face_extractor_controller import face_extractor_bp
from lobby.lobby_controller import lobby_bp
from game_logic.game_logic_controller import game_logic_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Enable CORS for cross-origin requests

app.register_blueprint(lobby_bp)
app.register_blueprint(face_extractor_bp)
app.register_blueprint(game_logic_bp)


@app.route('/start', methods=['POST'])
def start_game():
    print('Game started')
    data = request.get_json()
    # nb_players = data.get('nbPlayers')
    state_manager = get_game_state_manager(nb_players=3)
    return jsonify({"message": "Game started", "game_state": state_manager.get_game_state()})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")