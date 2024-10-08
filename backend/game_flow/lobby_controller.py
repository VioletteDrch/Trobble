from flask import Blueprint, request, jsonify
from typing import Dict, Tuple, Optional, List
import uuid
import random
import string
from game_flow.game_pojos import Lobby
from game_flow.lobby_repository import LobbyRepository

lobby_bp = Blueprint('lobby', __name__)
lobby_repository: LobbyRepository = LobbyRepository()

@lobby_bp.route('', methods=['GET'])
def get_all_public_lobbies() -> Tuple[List[str], int]:
    public_lobbies: List[Lobby] = lobby_repository.get_all_public_lobbies()

    return jsonify(list(public_lobbies.keys())), 200
