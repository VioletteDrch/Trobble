from flask import Flask
from flask_cors import CORS
import os
import asyncio
from threading import Thread

from numpy import False_
from lobby.lobby_controller import lobby_bp
from lobby.lobby_websockets import serve_bis, socket_serve

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

IMAGES_FOLDER = 'images'
RAW_FOLDER = os.path.join(IMAGES_FOLDER, 'raw')
PROCESSED_FOLDER = os.path.join(IMAGES_FOLDER, 'processed')
app.config['RAW_FOLDER'] = RAW_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

app.register_blueprint(lobby_bp)

# Ensure the folders exist
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def start_flask():
    print("Starting the flask server")
    app.run(debug=False, host="0.0.0.0")

async def start_servers():
    # tasks = list()
    # if not (app.debug or os.environ.get('FLASK_ENV') == 'development') or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    #     tasks.append(asyncio.create_task(socket_serve()))
    # tasks.append(asyncio.create_task(start_flask()))
    await asyncio.gather(socket_serve(), asyncio.to_thread(start_flask))

if __name__ == '__main__':
    asyncio.run(start_servers())
