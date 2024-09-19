from typing import Dict, List, Optional, TypedDict

class Player(TypedDict):
    user_id: str
    username: str

class Lobby(TypedDict):
    host_id: str
    players: Dict[str, str]
    private: bool
    started: bool

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
