import asyncio
import json
from websockets.asyncio.connection import Connection
from websockets.asyncio.server import serve, broadcast
from lobby_repository import *
from backend.game_flow.game_state_elements import GameStateManager, PlayerMove
from flask_sock import Sock
from typing import Dict

player_connections_by_game_id: Dict[str, Dict[int, Connection]] = {}
games: Dict[str, GameStateManager] = {}

sock = Sock()


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

        if lobby_code not in player_connections_by_game_id.keys():
            player_connections_by_game_id[lobby_code] = {}

        if player_id in player_connections_by_game_id[lobby_code]:
            ws.send(json.dumps({"error": f"Player {player_id} is already in the lobby"}))
            ws.close()
            return

        player_connections_by_game_id[lobby_code][player_id] = ws
        ws.send(json.dumps({"message": f"Player {player_id} joined lobby {lobby_code}"}))
        print(f"Player {player_id} joined lobby {lobby_code}")

        while True:
            message = ws.receive()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print(f"Player {player_id} disconnected from lobby {lobby_code}")
        ws.close()


async def create_game(game_id, player_id, connection):
    if game_id in player_connections_by_game_id:
        message = 'game already exists'
    else:
        player_connections_by_game_id[game_id] = {}
        player_connections_by_game_id[game_id][player_id] = connection
        message = 'game created'
    await connection.send(json.dumps(LobbyResponse(message).__dict__))


async def init_game(host_id, game_id):
    player_connections = player_connections_by_game_id[game_id]
    game_state_manager = GameStateManager([*player_connections], host_id)
    games[game_id] = game_state_manager
    game_state = game_state_manager.game_state

    for player, cards in game_state.players_cards.items():
        game_init_response = GameInitResponse(cards, game_state.middle_card)
        await player_connections[player].send(json.dumps(game_init_response.__dict__))

    game_state.active = True


async def join_game(player_id, game_id, websocket):
    if game_id not in player_connections_by_game_id:
        message = 'game does not exist'
    else:
        connections = player_connections_by_game_id[game_id]
        if player_id in connections:
            message = 'already connected'
        else:
            broadcast(connections.values(), f"Player {player_id} entered the game")
            connections[player_id] = websocket
            player_connections_by_game_id[game_id] = connections
            print(f"Added player {player_id} to lobby {game_id}")
            message = 'ok'
    resp = LobbyResponse(message)
    await websocket.send(json.dumps(resp.__dict__))


async def handle_score(player_connection, player_move: PlayerMove, game_id):
    game: GameStateManager = games[game_id]

    if game.game_state.active and game.resolve_game_state(player_move):
        player_connections = player_connections_by_game_id.get(game_id, {})
        response = PlayerScoredResponse(player_move.player_id, game.game_state.middle_card)
        broadcast(player_connections.values(), json.dumps(response.__dict__))
        if not game.game_state.active:
            await end_game(game_id)
    else:
        await player_connection.send("Invalid point")  # TODO parse proper JSON error response


async def end_game(game_id):
    game: GameStateManager = games[game_id]
    player_connections = player_connections_by_game_id[game_id]
    broadcast(player_connections.values(), json.dumps(GameEndResponse(game.game_state.winner).__dict__))
    for connection in player_connections.values():
        await connection.close()
    del player_connections_by_game_id[game_id]
    del games[game_id]


async def socket_handler(websocket):
    while True:
        message = await websocket.recv()
        websocket_message: WebsocketMessage = websocket_message_from_dict(json.loads(message))
        if websocket_message.method == 'create':
            await create_game(websocket_message.game_id, websocket_message.player_id, websocket)
        elif websocket_message.method == 'join':
            await join_game(websocket_message.player_id, websocket_message.game_id, websocket)
        elif websocket_message.method == 'init':
            await init_game(websocket_message.player_id, websocket_message.game_id)
        elif websocket_message.method == 'score':
            player_move_req = player_move_from_dict(websocket_message.payload)
            player_move = PlayerMove(websocket_message.player_id, player_move_req.symbol_id,
                                     player_move_req.middle_card_id)
            await handle_score(websocket, player_move, websocket_message.game_id)


async def socket_serve():
    async with serve(socket_handler, "localhost", 1234):
        await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    print("Running the socket server")
    asyncio.run(socket_serve())
