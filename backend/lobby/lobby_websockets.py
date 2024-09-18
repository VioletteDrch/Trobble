import asyncio
import json
from typing_extensions import Any
from websockets.asyncio.connection import Connection
from websockets.asyncio.server import serve, broadcast
from websockets.typing import Origin
from lobby_repository import *

# TODO will need to handle concurrent access in case multiple players join at the same time
lobby_connections : Dict[str, Dict[str, Connection]] = dict()

async def handle_player_connected(websocket, player_id):
    async for message in websocket:
        print(message)

        resp = "Hey there, received your message"
        await websocket.send(resp)
        print("Response sent")

async def add_player_to_lobby(player_id, lobby_code, websocket):
    # todo check that lobby is "joinable", e.g. the player is allowed to join AND game has not started
    connections = lobby_connections.get(lobby_code, dict())

    broadcast(connections.values(), f"Player {player_id} entered the game")
    # todo send message to connected players that a new player is joining
    connections[player_id] = websocket
    lobby_connections[lobby_code] = connections

    print(f"Added player {player_id} to lobby {lobby_code}")

    try:
        await handle_player_connected(websocket, player_id)
    finally:
        print(f"Removing player {player_id} from the lobby {lobby_code}")
        del lobby_connections[lobby_code]

async def socket_handler(websocket):
    # we assume lobby has been created by another http request
    print("new websocket connection established")

    # wait for init message to come in. TODO add a timeout if first message never comes ?
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    lobby_code = event["lobby_code"]
    # todo maybe we want better authentication than that, like using cookies ?
    player_id = event["player_id"]

    # TODO error case should return objects and not simple strings, to carry the "an error occurred" info
    if not lobby_code:
        await websocket.send("Lobby code is required")
        await websocket.close()
        return

    # Comment the following lines for testing
    # if lobby_code not in lobbies:
    #     await websocket.send("Unknown lobby")
    #     await websocket.close()
    #     return

    await add_player_to_lobby(player_id, lobby_code, websocket)

async def socket_serve():
    async with serve(socket_handler, "localhost", 1234):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    print("Running the socket server")
    asyncio.run(socket_serve())
