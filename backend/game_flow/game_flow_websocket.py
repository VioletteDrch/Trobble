import json
from backend.game_flow.lobby_repository import *
from backend.game_flow.game_state_elements import GameStateManager, PlayerMove
from flask_sock import Sock, WebSocket
from typing import Dict

player_connections_by_game_id: Dict[str, Dict[int, WebSocket]] = {}
games: Dict[str, GameStateManager] = {}

sock = Sock()


async def create_game(game_id, player_id, ws):
    print('Creating game')
    if game_id in player_connections_by_game_id:
        message = 'game already exists'
    else:
        player_connections_by_game_id[game_id] = {}
        player_connections_by_game_id[game_id][player_id] = ws
        message = 'game created'
    await ws.send(json.dumps(LobbyResponse(message).__dict__))


async def init_game(game_id, host_id):
    print('Initiating game')
    player_connections = player_connections_by_game_id[game_id]
    game_state_manager = GameStateManager([*player_connections], host_id)
    games[game_id] = game_state_manager
    game_state = game_state_manager.game_state

    for player, cards in game_state.players_cards.items():
        game_init_response = GameInitResponse(cards, game_state.middle_card)
        await player_connections[player].send(json.dumps(game_init_response.__dict__))

    game_state.active = True


async def join_game(game_id, player_id, ws):
    print('Player joining game')
    if game_id not in player_connections_by_game_id:
        message = 'game does not exist'
    else:
        connections = player_connections_by_game_id[game_id]
        if player_id in connections:
            message = 'already connected'
        else:
            await broadcast(game_id, f"Player {player_id} entered the game")
            connections[player_id] = ws
            player_connections_by_game_id[game_id] = connections
            print(f"Added player {player_id} to lobby {game_id}")
            message = 'ok'
    resp = LobbyResponse(message)
    await ws.send(json.dumps(resp.__dict__))


async def handle_score(ws, player_move: PlayerMove, game_id):
    print('Handling score')
    game: GameStateManager = games[game_id]

    if game.game_state.active and game.resolve_game_state(player_move):
        player_connections = player_connections_by_game_id.get(game_id, {})
        response = PlayerScoredResponse(player_move.player_id, game.game_state.middle_card)
        await broadcast(game_id, json.dumps(response.__dict__))
        if not game.game_state.active:
            await end_game(game_id)
    else:
        await ws.send("Invalid point")  # TODO parse proper JSON error response


async def end_game(game_id):
    print('Ending game')
    game: GameStateManager = games[game_id]
    player_connections = player_connections_by_game_id[game_id]
    await broadcast(game_id, json.dumps(GameEndResponse(game.game_state.winner).__dict__))
    for connection in player_connections.values():
        await connection.close()
    del player_connections_by_game_id[game_id]
    del games[game_id]


async def broadcast(game_id, message):
    connections = player_connections_by_game_id[game_id]
    for connection in connections.values():
        await connection.send(message)


@sock.route('/ws')
async def websocket_handler(ws):
    while True:
        message = await ws.receive()
        event = json.loads(message)
        event_type = event['type']
        game_id = event.get['game_id']
        player_id = event.get['player_id']

        if event_type == 'create':
            await create_game(game_id, player_id, ws)

        elif event_type == 'join':
            await join_game(game_id, player_id, ws)

        elif event_type == 'init':
            await init_game(game_id, player_id)

        elif event_type == 'score':
            player_move_req = event['payload']
            player_move = PlayerMove(player_id, player_move_req['symbol_id'],
                                     player_move_req['middle_card_id'])
            await handle_score(ws, player_move, game_id)