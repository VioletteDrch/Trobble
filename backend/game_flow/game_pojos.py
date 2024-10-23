from typing import Dict, List, Any, TypedDict
from dataclasses import dataclass, asdict
from game_flow.game_state_elements import Card


class Player(TypedDict):
    name: str
    connection: any


class Lobby(TypedDict):
    host_id: str
    players: Dict[str, Player]
    started: bool


class WebsocketMessage:

    def __init__(
            self, method: str, player_id: int, game_id: str, payload: Any = {}
    ) -> None:
        self.method = method
        self.player_id = player_id
        self.game_id = game_id
        self.payload = payload


def websocket_message_from_dict(s: Dict[str, Any]) -> WebsocketMessage:
    return WebsocketMessage(**s)


@dataclass
class CreateGameResponse:
    message: str
    gameId: str
    playerId: str
    lobby: any
    method: str = "create"


@dataclass
class JoinGameResponse:
    message: str
    playerId: str
    playerName: str
    lobby: any
    method: str = "join"


@dataclass
class PlayerScoredResponse:
    player_id: int
    new_middle_card: list
    error: str = ""
    method: str = "score"


@dataclass
class GameInitResponse:
    player_cards: List[Dict[str, List]]
    middle_card: Dict[str, List]
    method: str = "init"

    def __init__(self, players_cards, middle_card: Card):
        self.player_cards = [
            asdict(card) for card in players_cards
        ]
        self.middle_card = asdict(middle_card)
        self.method = "init"


@dataclass
class GameEndResponse:
    winner: int  # change to proper player object once we have it, with the name, color, etc.
    method: str = "end"


@dataclass
class PlayerMoveRequest:
    symbol_id: int
    middle_card_id: int


def player_move_from_dict(s: Dict[str, Any]) -> PlayerMoveRequest:
    print("dict receive = ", s)
    return PlayerMoveRequest(**s)
