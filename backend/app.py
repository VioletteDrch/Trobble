from flask import Flask
from flask_cors import CORS
from images_set_creation.images_controller import images_bp
from game_flow.lobby_controller import lobby_bp
from game_flow.game_flow_websocket import sock

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

app.register_blueprint(lobby_bp)
app.register_blueprint(images_bp, url_prefix='/images')
sock.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
