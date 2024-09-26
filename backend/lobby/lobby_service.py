class LobbyService:
    def __init__(self, lobby_repository):
        self._lobby_repository = lobby_repository

    def get_lobby(self, lobby_code):
        return self._lobby_repository.get_lobby(lobby_code)

    def add_lobby(self, lobby_code, new_lobby):
        self._lobby_repository.add_lobby(lobby_code, new_lobby)

    def remove_lobby(self):
        self._lobby_repository.remove_lobby()

    def get_all_public_lobbies(self):
        return self._lobby_repository.get_all_public_lobbies()