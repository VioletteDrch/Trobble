from flask import Flask
from flask_cors import CORS
import os
from lobby.lobby_controller import lobby_bp
from lobby.lobby_websockets import sock  # Import the Sock instance from lobby_websockets

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

sock.init_app(app)

IMAGES_FOLDER = 'images'
RAW_FOLDER = os.path.join(IMAGES_FOLDER, 'raw')
PROCESSED_FOLDER = os.path.join(IMAGES_FOLDER, 'processed')
app.config['RAW_FOLDER'] = RAW_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

app.register_blueprint(lobby_bp)

# Ensure the folders exist
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")

