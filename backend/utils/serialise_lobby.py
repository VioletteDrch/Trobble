from game_flow.game_pojos import *


# Todo: find a better way to serialise without connections
def serialise_lobby(lobby: Lobby) -> Dict:
    serialised_players = {
        player_id: {"name": player_data["name"]}
        for player_id, player_data in lobby["players"].items()
    }

    serialised_lobby = {
        "host_id": lobby["host_id"],
        "players": serialised_players,
        "started": lobby["started"],
    }

    return serialised_lobby
