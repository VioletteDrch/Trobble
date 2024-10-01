from flask import Flask
from flask_cors import CORS

from backend.game_flow.game_flow_websocket import sock
from backend.images_set_creation.images_controller import images_bp
from backend.game_flow.lobby_controller import lobby_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

sock.init_app(app)

app.register_blueprint(lobby_bp)
app.register_blueprint(images_bp, url_prefix='/images')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")