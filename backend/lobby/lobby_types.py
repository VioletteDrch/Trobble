from typing import Dict, List, Optional, TypedDict

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
    players: Dict[str, str]

class ErrorResponse(TypedDict):
    error: str

class CreateLobbyResponse(TypedDict):
    message: str
    lobby_code: str

class JoinLobbyResponse(TypedDict):
    message: str

class ChangeNameResponse(TypedDict):
    message: str
