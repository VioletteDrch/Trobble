import time
import json
from game_flow.lobby_repository import LobbyRepository

lobby_repository = LobbyRepository()


def ping_client(websocket, player_id, game_id):
    while True:
        time.sleep(2)
        try:
            websocket.pong_received = False
            ping_message = json.dumps({"method": "ping"})
            websocket.send(ping_message)

            time.sleep(2)
            if not websocket.pong_received:
                raise Exception("Ping timeout")

        except Exception as e:
            print(f"Player {player_id} did not respond to ping, removing from lobby")
            remove_player_from_lobby(game_id, player_id)
            break


# todo: handle host leaving
def remove_player_from_lobby(game_id, player_id):
    print(f"Removing player {player_id} from game {game_id}")

    lobby = lobby_repository.get_lobby(game_id)
    player = lobby_repository.get_player(game_id, player_id)

    if player:
        lobby_repository.remove_player(game_id, player_id)
        for p in lobby["players"].values():
            if p["connection"] is not None:
                p["connection"].send(
                    json.dumps(
                        {
                            "method": "disconnect",
                            "playerId": player_id,
                            "message": f"Player {player_id} has left the game.",
                        }
                    )
                )

        lobby = lobby_repository.get_lobby(game_id)
        if not lobby["players"]:
            lobby_repository.remove_lobby(game_id)
