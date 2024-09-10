import numpy as np
from cards_creator import get_cards


class GameState:
    # Only stores cards as ids, aka their position in the deck.
    def __init__(self, middle_card, players_cards):
        self.middle_card = middle_card
        self.players_cards = players_cards


class PlayerMove:
    def __init__(self, player_id, clicked_symbol):
        self.player_id = player_id
        self.symbol_id = clicked_symbol


class Card:
    def __init__(self, card_id, composition):
        self.card_id = card_id
        self.composition = composition


class GameStateManager:
    def __init__(self, nb_players, prime_number=7):
        # Create cards deck
        cards = get_cards(prime_number)
        np.random.shuffle(cards)
        self.cards = cards

        # Select first card as middle card
        middle_card = 0
        cards.pop(middle_card)

        # Deal the rest of the cards evenly to the players
        nb_cards_per_player = len(cards) // nb_players
        players_cards = {
            player_id: []
            for player_id in range(nb_players)
        }
        for player_id in range(nb_players):
            first_card_id = 1 + nb_cards_per_player * player_id  # first card of the deck has been used as middle card
            last_card_id = first_card_id + nb_cards_per_player

            players_cards[player_id] = [
                i for i in range(first_card_id, last_card_id)
            ]

        # Initialize game state
        self.game_state = GameState(middle_card, players_cards)

    def __str__(self):
        game_state_str = (f"Current game state\n------------------\n"
                          f"* {len(self.game_state.players_cards.keys())} players\n"
                          f"* Middle card: "
                          f"id = {self.game_state.middle_card}, "
                          f"composition = {self.cards[self.game_state.middle_card]}")

        for player_id in self.game_state.players_cards.keys():
            player_cards_ids = self.game_state.players_cards[player_id]
            game_state_str += (f"\n"
                               f"* Player {player_id} has {len(self.game_state.players_cards[player_id])} cards left. "
                               f"First card: "
                               f"id = {player_cards_ids[0]}, "
                               f"composition = {self.cards[player_cards_ids[0]]}")
        return game_state_str

    def get_top_card_for_player(self, player_id) -> Card:
        card_id = self.game_state.players_cards[player_id][0]
        return Card(
            card_id,
            self.cards[card_id]
        )

    def get_middle_card(self) -> Card:
        card_id = self.game_state.middle_card
        return Card(
            card_id,
            self.cards[card_id]
        )

    def valid_player_match(self, move: PlayerMove) -> bool:
        # check the symbol exists both in the player's card and the middle card
        player_top_card = self.get_top_card_for_player(move.player_id)
        middle_card = self.get_middle_card()

        if move.symbol_id not in player_top_card.composition:
            # symbol should have not been clickable FIXME
            return False

        if move.symbol_id not in middle_card.composition:
            # not a match FIXME penalty
            return False

    def resolve_game_state(self, move: PlayerMove):
        # If the player's move is valid, update game state
        if self.valid_player_match(move):
            # FIXME update
            return self.game_state


if __name__ == '__main__':
    nb_players = 3
    prime_number = 7
    game_on = GameStateManager(nb_players, prime_number)
    print(game_on.__str__())

    for p in range(nb_players):
        print(game_on.get_top_card_for_player(p).id, game_on.get_top_card_for_player(p).composition)

    print(game_on.get_middle_card().id, game_on.get_middle_card().composition)
