import json
import string
import time
import threading
import random
import uuid
from typing import Collection
from game_flow.lobby_repository import *
from game_flow.game_state_elements import GameStateManager, PlayerMove
from game_flow.game_pojos import *
from flask_sock import Sock
from utils.ping_client import ping_client
from utils.serialise_lobby import serialise_lobby

player_connections_by_game_id: Dict[str, Dict[int, Any]] = {}
games: Dict[str, GameStateManager] = {}
lobby_repository: LobbyRepository = LobbyRepository()

sock = Sock()


def create_game(websocket_message: WebsocketMessage, connection):
    host_name: str = websocket_message.payload.get("host_name")
    if not host_name:
        connection.send(json.dumps({"error": "Host name is required"}))
        return

    game_id: str = generate_game_id()
    while lobby_repository.get_lobby(game_id):
        game_id = generate_game_id()

    host_id: str = str(uuid.uuid4())

    new_lobby: Lobby = {"host_id": host_id, "players": {}, "started": False}

    lobby_repository.add_lobby(game_id, new_lobby)
    lobby_repository.add_player(game_id, host_id, host_name, connection)

    response = {
        "message": "Lobby and game created successfully",
        "game_id": game_id,
        "player_id": host_id,
        "lobby": serialise_lobby(new_lobby),
    }
    connection.send(json.dumps(response))

    print(f"Added player {host_id} to lobby {game_id}")

    threading.Thread(target=ping_client, args=(connection, host_id, game_id)).start()


def init_game(host_id, game_id):
    player_connections = player_connections_by_game_id[game_id]
    game_state_manager = GameStateManager([*player_connections], host_id)
    games[game_id] = game_state_manager
    game_state = game_state_manager.game_state

    for player, cards in game_state.players_cards.items():
        game_init_response = GameInitResponse(cards, game_state.middle_card)
        player_connections[player].send(json.dumps(game_init_response.__dict__))

    game_state.active = True


def join_game(websocket_message: WebsocketMessage, connection):
    player_name = websocket_message.payload["player_name"]
    game_id = websocket_message.game_id
    lobby = lobby_repository.get_lobby(game_id)

    if not lobby:
        error = "Lobby does not exist"
        connection.send(json.dumps({"error": error}))
        raise Exception()
    elif lobby["started"]:
        error = "Game has already started"
        connection.send(json.dumps({"error": error}))
        raise Exception()
    elif len(lobby["players"]) >= 6:
        error = "Lobby is full, limit of 6 players reached"
        connection.send(json.dumps({"error": error}))
        raise Exception()
    elif any(player["name"] == player_name for player in lobby["players"].values()):
        error = "Player name already exists in the lobby"
        connection.send(json.dumps({"error": error}))
        raise Exception()
    else:
        player_id = str(uuid.uuid4())
        lobby_repository.add_player(game_id, player_id, player_name, connection)

        response = JoinGameResponse(
            message=f"Player {player_name} entered the game",
            playerId=player_id,
            playerName=player_name,
            lobby=serialise_lobby(lobby),
        )

        for player in lobby["players"].values():
            if player["connection"] is not None:
                player["connection"].send(json.dumps(response.__dict__))

        print(f"Added player {player_id} to lobby {game_id}")

    threading.Thread(target=ping_client, args=(connection, player_id, game_id)).start()

    return player_id


def handle_score(player_connection, player_move: PlayerMove, game_id):
    game: GameStateManager = games[game_id]

    if game.game_state.active and game.resolve_game_state(player_move):
        player_connections = player_connections_by_game_id.get(game_id, {})
        response = PlayerScoredResponse(
            player_move.player_id, game.game_state.middle_card
        )
        broadcast(player_connections.values(), json.dumps(response.__dict__))
        if not game.game_state.active:
            end_game(game_id)
    else:
        player_connection.send(
            json.dumps(PlayerScoredResponse(0, [], "invalid point"))
        )  # TODO parse proper JSON error response


def end_game(game_id):
    game: GameStateManager = games[game_id]
    player_connections = player_connections_by_game_id[game_id]
    broadcast(
        player_connections.values(),
        json.dumps(GameEndResponse(game.game_state.winner).__dict__),
    )
    for connection in player_connections.values():
        connection.close()
    del player_connections_by_game_id[game_id]
    del games[game_id]


def generate_game_id(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def socket_handler(websocket):
    try:
        while True:
            message = websocket.receive()
            websocket_message: WebsocketMessage = websocket_message_from_dict(
                json.loads(message)
            )

            if websocket_message.method == "create":
                create_game(websocket_message, websocket)
            elif websocket_message.method == "join":
                join_game(websocket_message, websocket)
            elif websocket_message.method == "pong":
                websocket.pong_received = True
            elif websocket_message.method == "score":
                try:
                    player_move_req = player_move_from_dict(websocket_message.payload)
                    player_move = PlayerMove(
                        websocket_message.player_id,
                        player_move_req.symbol_id,
                        player_move_req.middle_card_id,
                    )
                    handle_score(websocket, player_move, websocket_message.game_id)
                except Exception as e:
                    websocket.send(PlayerScoredResponse(0, [], "bad request"))
    except Exception as e:
        print(f"WebSocket error: {e}")


def broadcast(websockets: Collection, message: str):
    for ws in websockets:
        ws.send(message)


@sock.route("/ws")
def serve(ws):
    socket_handler(ws)
