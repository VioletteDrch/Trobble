from typing import Dict, List, Any, TypedDict
from dataclasses import dataclass


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


class WebsocketMessage:

    def __init__(self, method: str, player_id: int, game_id: str, payload: Any = {}) -> None:
        self.method = method
        self.player_id = player_id
        self.game_id = game_id
        self.payload = payload


def websocket_message_from_dict(s: Dict[str, Any]) -> WebsocketMessage:
    return WebsocketMessage(**s)


@dataclass
class CreateGameResponse:
    message: str
    method: str = "create"

@dataclass
class JoinGameResponse:
    message: str
    method: str = "join"

@dataclass
class PlayerScoredResponse:
    player_id: int
    new_middle_card: list
    error: str = ""
    method: str = "score"


@dataclass
class GameInitResponse:
    cards: list
    middle_card: list
    method: str = "init"


@dataclass
class GameEndResponse:
    winner: int  # change to proper player object once we have it, with the name, color, etc.
    method: str = "end"


@dataclass
class PlayerMoveRequest:
    symbol_id: int
    middle_card_id: int


def player_move_from_dict(s: Dict[str, Any]) -> PlayerMoveRequest:
    return PlayerMoveRequest(**s)
