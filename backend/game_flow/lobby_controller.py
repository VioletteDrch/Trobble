from flask import Blueprint, request, jsonify
from typing import Dict, Tuple, Optional, List
import uuid
import random
import string
from game_pojos import CreateLobbyResponse, LobbyResponse, GetLobbyResponse, Lobby, LobbyWithCode
from lobby_repository import LobbyRepository

lobby_bp = Blueprint('lobby', __name__)
lobby_repository: LobbyRepository = LobbyRepository()


def generate_lobby_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@lobby_bp.route('/lobbies', methods=['POST'])
def create_lobby() -> Tuple[CreateLobbyResponse, int]:
    data: Dict[str, Optional[str]] = request.get_json()
    host_name: Optional[str] = data.get('host_name')
    private: bool = data.get('private', False)

    if not host_name:
        return jsonify({"error": "Host name is required"}), 400

    lobby_code: str = generate_lobby_code()

    # Very unlikely to be a clash but just in case
    while lobby_repository.get_lobby(lobby_code):
        lobby_code = generate_lobby_code()

    host_id: str = str(uuid.uuid4())

    new_lobby: Lobby = {
        "host_id": host_id,
        "players": {host_id: host_name},
        "private": private,
        "started": False
    }

    lobby_repository.add_lobby(lobby_code, new_lobby)

    return jsonify({"message": "Lobby created successfully", "lobby_code": lobby_code}), 201


@lobby_bp.route('/lobbies/<lobby_code>/join', methods=['POST'])
def join_lobby(lobby_code: str) -> Tuple[LobbyResponse, int]:
    data: Dict[str, Optional[str]] = request.get_json()
    user_name: Optional[str] = data.get('username')

    if not lobby_code or not user_name:
        return jsonify({"error": "Lobby code and username are required"}), 400

    lobby: Optional[Lobby] = lobby_repository.get_lobby(lobby_code)
    if not lobby:
        return jsonify({"error": "Lobby not found"}), 404

    if lobby['started']:
        return jsonify({"error": "Game has already started"}), 400

    if len(lobby['players']) >= 6:
        return jsonify({"error": "Lobby is full, limit of 6 players reached"}), 400

    if user_name in lobby['players'].values():
        return jsonify({"error": "Username already exists in the lobby"}), 409

    user_id: str = str(uuid.uuid4())
    lobby['players'][user_id] = user_name

    return jsonify({"message": "Joined lobby successfully"}), 200


@lobby_bp.route('/lobbies/<lobby_code>', methods=['GET'])
def get_lobby(lobby_code: str) -> Tuple[GetLobbyResponse, int]:
    if not lobby_code:
        return jsonify({"error": "Lobby code is required"}), 400

    lobby: Optional[Lobby] = lobby_repository.get_lobby(lobby_code)
    if not lobby:
        return jsonify({"error": "Lobby not found"}), 404

    return jsonify(lobby), 200


@lobby_bp.route('/lobbies', methods=['GET'])
def get_all_public_lobbies() -> Tuple[List[LobbyWithCode], int]:
    public_lobbies = lobby_repository.get_all_public_lobbies()

    mapped_lobbies: LobbyWithCode = [
        {**lobby, 'lobby_code': code}
        for code, lobby in public_lobbies.items()
    ]

    return jsonify(mapped_lobbies), 200
