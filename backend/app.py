from flask import Flask
from flask_cors import CORS
from face_extractor.face_extractor_controller import face_extractor_bp
from lobby.lobby_controller import lobby_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

app.register_blueprint(lobby_bp)
app.register_blueprint(face_extractor_bp)


if __name__ == '__main__':
    app.run(debug=True)
