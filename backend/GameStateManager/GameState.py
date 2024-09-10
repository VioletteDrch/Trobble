import numpy as np
from cards_creator import get_cards


class GameState:
    # Only stores cards as ids, aka their position in the deck.
    def __init__(self, middle_card, players_cards):
        self.middle_card = middle_card
        self.players_cards = players_cards

    def set_middle_card(self, card_id):
        self.middle_card = card_id


class PlayerMove:
    def __init__(self, player_id, clicked_symbol):
        self.player_id = player_id
        self.symbol_id = clicked_symbol


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
        players_cards = {}

        first_card_id = 1  # first card of the deck has been used as middle card
        for player_id in range(nb_players):
            first_card_id += nb_cards_per_player * player_id
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

    def get_card_composition(self, card_id):
        return self.cards[card_id]

    def get_middle_card_compo(self):
        return self.get_card_composition(self.game_state.middle_card)

    def get_top_card_compo_for_player(self, player_id):
        return self.get_card_composition(self.game_state.players_cards[player_id][0])

    def valid_player_match(self, move: PlayerMove) -> bool:
        # check the symbol exists both in the player's card and the middle card
        player_top_card_compo = self.get_top_card_compo_for_player(move.player_id)
        middle_card_compo = self.get_middle_card_compo()

        if move.symbol_id not in player_top_card_compo:
            # symbol should have not been clickable FIXME
            print("Invalid move")
            return False

        if move.symbol_id not in middle_card_compo:
            # not a match FIXME penalty?
            print("Invalid move")
            return False

        print("Valid move")
        return True

    def resolve_game_state(self, move: PlayerMove):
        # If the player's move is valid, update game state
        if self.valid_player_match(move):
            new_middle_card = self.game_state.players_cards[move.player_id].pop(0)  # remove top card from player's pile
            self.game_state.set_middle_card(new_middle_card)  # set it as the new middle card


if __name__ == '__main__':
    nb_players = 3
    prime_number = 7
    game_on = GameStateManager(nb_players, prime_number)
    print(game_on.__str__())
    game_on.resolve_game_state(PlayerMove(
        0, 0
    ))
