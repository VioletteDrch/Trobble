from typing import Dict, List, Optional, TypedDict
from dataclasses import dataclass

class Player(TypedDict):
    user_id: str
    username: str

class Lobby(TypedDict):
    host_id: str
    players: Dict[str, str]
    private: bool
    started: bool

class LobbyWithCode(Lobby):
    lobby_code: str

class GetLobbyResponse(TypedDict):
    lobby_code: str
    host: str
    players: List[Player]

class ErrorResponse(TypedDict):
    error: str

class CreateLobbyResponse(TypedDict):
    message: str
    lobby_code: str

class JoinLobbyResponse(TypedDict):
    message: str

class ChangeNameResponse(TypedDict):
    message: str

@dataclass
class PlayerScoredResponse:
    player_id: str
    middle_card: list #TODO update once the card object is not only array but the dict with id + url Dict[int, str]

@dataclass
class GameInitResponse:
    cards: list #TODO change to List[Dict[]] once that has been implemented
    middle_card: list #TODO change to Dict[] once that has been implemented