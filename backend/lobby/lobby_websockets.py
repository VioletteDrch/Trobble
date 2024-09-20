import json
from flask_sock import Sock
from typing import Dict

sock = Sock()

lobby_connections: Dict[str, Dict[str, object]] = dict()

@sock.route('/ws')
def websocket_handler(ws):
    print("New WebSocket connection established")

    try:
        message = ws.receive()
        event = json.loads(message)
        if event['type'] != "init":
            ws.send(json.dumps({"error": "Invalid init message"}))
            ws.close()
            return

        lobby_code = event.get('lobby_code')
        player_id = event.get('player_id')

        if not lobby_code or not player_id:
            ws.send(json.dumps({"error": "Lobby code and player ID are required"}))
            ws.close()
            return

        if lobby_code not in lobby_connections:
            lobby_connections[lobby_code] = {}

        if player_id in lobby_connections[lobby_code]:
            ws.send(json.dumps({"error": f"Player {player_id} is already in the lobby"}))
            ws.close()
            return

        lobby_connections[lobby_code][player_id] = ws
        ws.send(json.dumps({"message": f"Player {player_id} joined lobby {lobby_code}"}))
        print(f"Player {player_id} joined lobby {lobby_code}")

        while True:
            message = ws.receive()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print(f"Player {player_id} disconnected from lobby {lobby_code}")
        ws.close()

