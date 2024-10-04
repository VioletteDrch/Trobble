import json
from typing import Collection
from game_flow.lobby_repository import *
from game_flow.game_state_elements import GameStateManager, PlayerMove
from game_flow.game_pojos import *
from flask_sock import Sock

player_connections_by_game_id: Dict[str, Dict[int, Any]] = {}
games: Dict[str, GameStateManager] = {}

sock = Sock()

def create_game(game_id, player_id, connection):
    if game_id in player_connections_by_game_id:
        message = 'game already exists'
    else:
        player_connections_by_game_id[game_id] = {}
        player_connections_by_game_id[game_id][player_id] = connection
        message = 'ok'
    print(message)
    connection.send(json.dumps(CreateGameResponse(message).__dict__))


def init_game(host_id, game_id):
    player_connections = player_connections_by_game_id[game_id]
    game_state_manager = GameStateManager([*player_connections], host_id)
    games[game_id] = game_state_manager
    game_state = game_state_manager.game_state

    for player, cards in game_state.players_cards.items():
        game_init_response = GameInitResponse(cards, game_state.middle_card)
        player_connections[player].send(json.dumps(game_init_response.__dict__))

    game_state.active = True


def join_game(player_id, game_id, websocket):
    if game_id not in player_connections_by_game_id:
        message = 'game does not exist'
    else:
        connections = player_connections_by_game_id[game_id]
        if player_id in connections:
            message = 'already connected'
        else:
            broadcast(connections.values(), json.dumps(JoinGameResponse("Player {player_id} entered the game").__dict__))
            connections[player_id] = websocket
            player_connections_by_game_id[game_id] = connections
            print(f"Added player {player_id} to lobby {game_id}")
            message = 'ok'
    resp = JoinGameResponse(message)
    print(resp)
    websocket.send(json.dumps(resp.__dict__))


def handle_score(player_connection, player_move: PlayerMove, game_id):
    game: GameStateManager = games[game_id]

    if game.game_state.active and game.resolve_game_state(player_move):
        player_connections = player_connections_by_game_id.get(game_id, {})
        response = PlayerScoredResponse(player_move.player_id, game.game_state.middle_card)
        broadcast(player_connections.values(), json.dumps(response.__dict__))
        if not game.game_state.active:
            end_game(game_id)
    else:
        player_connection.send(json.dumps(PlayerScoredResponse(0, [], "invalid point")))  # TODO parse proper JSON error response


def end_game(game_id):
    game: GameStateManager = games[game_id]
    player_connections = player_connections_by_game_id[game_id]
    broadcast(player_connections.values(), json.dumps(GameEndResponse(game.game_state.winner).__dict__))
    for connection in player_connections.values():
        connection.close()
    del player_connections_by_game_id[game_id]
    del games[game_id]


def socket_handler(websocket):
    while True:
        message = websocket.receive()
        websocket_message: WebsocketMessage = websocket_message_from_dict(json.loads(message))
        if websocket_message.method == 'create':
            create_game(websocket_message.game_id, websocket_message.player_id, websocket)
        elif websocket_message.method == 'join':
            join_game(websocket_message.player_id, websocket_message.game_id, websocket)
        elif websocket_message.method == 'init':
            init_game(websocket_message.player_id, websocket_message.game_id)
        elif websocket_message.method == 'score':
            try:
                player_move_req = player_move_from_dict(websocket_message.payload)
            except:
                websocket.send(PlayerScoredResponse(0, [], "bad request"))
            else:
                player_move = PlayerMove(websocket_message.player_id, player_move_req.symbol_id,
                                    player_move_req.middle_card_id)
                handle_score(websocket, player_move, websocket_message.game_id)


@sock.route('/ws')
def serve(ws):
    socket_handler(ws)

def broadcast(websockets: Collection, message: str):
    for ws in websockets:
        ws.send(message)
