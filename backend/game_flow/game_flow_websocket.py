import asyncio
import json
from typing_extensions import Any, Dict
from websockets.asyncio.connection import Connection
from websockets.asyncio.server import serve, broadcast
from websockets.typing import Origin
from lobby_repository import *
import sys
sys.path.append('../')
from game_logic.game_state_elements import GameStateManager, PlayerMove

game_connections : Dict[str, Dict[int, Connection]] = dict()
games : Dict[str, GameStateManager] = dict()

async def create_game(game_id, player_id, connection):
    if (game_id in game_connections):
        message = 'game already exists'
    else:
        game_connections[game_id] = dict()
        game_connections[game_id][player_id] = connection
        message = 'game created'
    await connection.send(json.dumps(LobbyResponse(message).__dict__))


async def init_game(player_id, game_id):
    player_connections = game_connections[game_id]
    game_state_manager = GameStateManager([*player_connections], player_id)
    games[game_id] = game_state_manager
    connections = game_connections.get(game_id, dict())
    game_state = game_state_manager.game_state
    for player, cards in game_state.players_cards.items():
        game_init_response = GameInitResponse(cards, game_state.middle_card)
        await connections[player].send(json.dumps(game_init_response.__dict__))
    game_state.active = True

async def join_game(player_id, game_id, websocket):
    if (game_id not in game_connections):
        message = 'game does not exist'
    connections = game_connections[game_id]
    if player_id in connections:
        message = 'already connected'
    else:
        broadcast(connections.values(), f"Player {player_id} entered the game")
        connections[player_id] = websocket
        game_connections[game_id] = connections
        print(f"Added player {player_id} to lobby {game_id}")
        message = 'ok'
    resp = LobbyResponse(message)
    await websocket.send(json.dumps(resp.__dict__))

async def handle_score(player_connection, player_move: PlayerMove, game_id):
    game: GameStateManager = games[game_id]
    if (game.game_state.active and game.resolve_game_state(player_move)):
        connections = game_connections.get(game_id, dict())
        response = PlayerScoredResponse(player_move.player_id, game.game_state.middle_card)
        broadcast(connections.values(), json.dumps(response.__dict__))
        if (not game.game_state.active):
            await end_game(game_id)
    else:
        await player_connection.send("Invalid point") #TODO parse proper JSON error response

async def end_game(game_id):
    game: GameStateManager = games[game_id]
    connections = game_connections[game_id]
    broadcast(connections.values(), json.dumps(GameEndResponse(game.game_state.winner).__dict__))
    for connection in connections.values():
        await connection.close()
    del game_connections[game_id]
    del games[game_id]

async def socket_handler(websocket):
    while True:
        message = await websocket.recv()
        websocket_message: WebsocketMessage = websocket_message_from_dict(json.loads(message))
        if (websocket_message.method == 'create'):
            await create_game(websocket_message.game_id, websocket_message.player_id, websocket)
        elif (websocket_message.method == 'join'):
            await join_game(websocket_message.player_id, websocket_message.game_id, websocket)
        elif (websocket_message.method == 'init'):
            await init_game(websocket_message.player_id, websocket_message.game_id)
        elif (websocket_message.method == 'score'):
            player_move_req = player_move_from_dict(websocket_message.payload)
            player_move = PlayerMove(websocket_message.player_id, player_move_req.symbol_id, player_move_req.middle_card_id)
            await handle_score(websocket, player_move, websocket_message.game_id)

async def socket_serve():
    async with serve(socket_handler, "localhost", 1234):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    print("Running the socket server")
    asyncio.run(socket_serve())
