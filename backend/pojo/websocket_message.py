
from typing import Any, Dict

class WebsocketMessage:

    def __init__(self, method: str, player_id: int, game_id: str, payload: Any = {}) -> None:
        self.method = method
        self.player_id = player_id
        self.game_id = game_id
        self.payload = payload

def websocket_message_from_dict(s: Dict[str, Any]) -> WebsocketMessage:
    return WebsocketMessage(**s)

def websocket_message_to_dict(x: WebsocketMessage) -> Dict[str, Any]:
    return vars(x)