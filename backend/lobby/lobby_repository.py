from typing import Any, Dict, Optional
from .lobby_types import *

class LobbyRepository:
    def __init__(self):
        self._lobbies: Dict[str, Lobby] = {}

    def add_lobby(self, lobby_code: str, lobby: Lobby) -> None:
        self._lobbies[lobby_code] = lobby

    def get_lobby(self, lobby_code: str) -> Optional[Lobby]:
        return self._lobbies.get(lobby_code)

    def remove_lobby(self, lobby_code: str) -> None:
        if lobby_code in self._lobbies:
            del self._lobbies[lobby_code]

    def get_all_public_lobbies(self) -> List[Dict[str, Any]]:
        return [
            {**lobby, 'lobby_code': code}
            for code, lobby in self._lobbies.items()
            if not lobby['started'] and not lobby['private']
        ]

