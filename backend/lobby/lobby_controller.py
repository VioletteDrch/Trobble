from flask import Blueprint, request, jsonify
from typing import Dict, Tuple, Optional
import uuid
import random
import string
from .lobby_types import *

lobby_bp = Blueprint('lobby', __name__)

# We can replace this with something better when we need it
lobbies: Dict[str, Lobby] = {}


def generate_lobby_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@lobby_bp.route('/lobbies', methods=['POST'])
def create_lobby() -> Tuple[CreateLobbyResponse, int]:
    data = request.get_json()
    host_name: Optional[str] = data.get('host_name')
    private: bool = data.get('private', False)

    if not host_name:
        return jsonify({"error": "Host name is required"}), 400

    lobby_code = generate_lobby_code()

    # Very unlikely to be a clash but just in case
    while lobby_code in lobbies:
        lobby_code = generate_lobby_code()

    host_id = str(uuid.uuid4())

    lobbies[lobby_code] = {
        "host_id": host_id,
        "players": {host_id: host_name},
        "private": private
    }

    return jsonify({"message": "Lobby created successfully", "lobby_code": lobby_code}), 201


@lobby_bp.route('/lobbies/<lobby_code>/join', methods=['POST'])
def join_lobby(lobby_code: str) -> Tuple[JoinLobbyResponse, int]:
    data = request.get_json()
    user_name: Optional[str] = data.get('username')

    if not lobby_code or not user_name:
        return jsonify({"error": "Lobby code and username are required"}), 400

    if lobby_code not in lobbies:
        return jsonify({"error": "Lobby not found"}), 404

    lobby = lobbies[lobby_code]
    if user_name in lobby['players'].values():
        return jsonify({"error": "Username already exists in the lobby"}), 400

    user_id = str(uuid.uuid4())

    lobby['players'][user_id] = user_name

    return jsonify({"message": "Joined lobby successfully"}), 200


@lobby_bp.route('/lobbies/<lobby_code>', methods=['GET'])
def get_lobby(lobby_code: str) -> Tuple[GetLobbyResponse, int]:
    if not lobby_code:
        return jsonify({"error": "Lobby code is required"}), 400

    if lobby_code not in lobbies:
        return jsonify({"error": "Lobby not found"}), 404

    return jsonify(lobbies[lobby_code]), 200


@lobby_bp.route('/lobbies', methods=['GET'])
def get_all_public_lobbies() -> Tuple[List[Lobby], int]:
    public_lobbies = [
        {code: lobby}
        for code, lobby in lobbies.items()
        if not lobby['private']
    ]

    return jsonify(public_lobbies), 200


# Technically anyone can change anyones username unless we add authentication
@lobby_bp.route('/lobbies/<lobby_code>/users/<user_id>', methods=['PUT'])
def change_username(lobby_code: str, user_id: str) -> Tuple[ChangeNameResponse, int]:
    data = request.get_json()
    new_username: Optional[str] = data.get('new_username')

    if not lobby_code or not new_username:
        return jsonify({"error": "Lobby code and new username are required"}), 400

    if lobby_code not in lobbies:
        return jsonify({"error": "Lobby not found"}), 404

    lobby = lobbies[lobby_code]
    if user_id not in lobby['players']:
        return jsonify({"error": "User not found in the lobby"}), 404

    if new_username in lobby['players'].values():
        return jsonify({"error": "Username already exists in the lobby"}), 400

    lobby['players'][user_id] = new_username

    return jsonify({"message": "Username changed successfully"}), 200
