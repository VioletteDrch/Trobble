from typing import Dict, Optional
from game_flow.game_pojos import Lobby, Player


class LobbyRepository:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LobbyRepository, cls).__new__(cls)
            cls._instance._lobbies = {}
        return cls._instance

    def add_lobby(self, game_id: str, lobby: Lobby) -> None:
        self._lobbies[game_id] = lobby

    def get_lobby(self, game_id: str) -> Optional[Lobby]:
        return self._lobbies.get(game_id)

    def remove_lobby(self, game_id: str) -> None:
        if game_id in self._lobbies:
            del self._lobbies[game_id]

    def get_all_public_lobbies(self) -> Dict[str, Lobby]:
        return {
            code: lobby for code, lobby in self._lobbies.items() if not lobby["started"]
        }

    def add_player(self, game_id: str, player_id: str, name: str, connection) -> None:
        lobby = self._lobbies.get(game_id)
        if lobby:
            lobby["players"][player_id] = {"name": name, "connection": connection}

    def get_player(self, game_id: str, player_id: str) -> Optional[Player]:
        lobby = self._lobbies.get(game_id)
        if lobby:
            return lobby["players"].get(player_id)
        return None

    def remove_player(self, game_id: str, player_id: str) -> None:
        lobby = self._lobbies.get(game_id)
        if lobby and player_id in lobby["players"]:
            del lobby["players"][player_id]

    def get_player_connection(self, game_id: str, player_id: str):
        player = self.get_player(game_id, player_id)
        return player["connection"] if player else None
