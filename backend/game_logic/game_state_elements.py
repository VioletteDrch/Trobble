from typing import Dict

import numpy as np
from backend.game_logic.cards_creator import get_cards


# Game state describes two things:
#   - which card is in the middle
#   - which cards are in each user pile
#
# A card has an id (rank in the deck) and a composition (which symbols are disposed on the card)
# To update the game state and interact with players, cards are manipulated with their ids only for ease
#
# The composition of the cards is used:
#   - at the beginning of the game, when sent to the client so that it can build the cards with a set of symbols
#   - when a player clicks on a symbol, and then we check if that symbol is present on their card and on the middle card
#     (in which case, it is a winning move and the player's card goes in the middle)


class GameState:
    # Contains game status info in cards ids, aka their position in the deck.
    def __init__(self, middle_card: int, players_cards: Dict[int, list]):
        self.middle_card_id = middle_card
        self.players_cards_ids = players_cards

    def set_middle_card(self, card_id: int):
        self.middle_card_id = card_id


class PlayerMove:
    def __init__(self, player_id: int, clicked_symbol: int):
        self.player_id = player_id
        self.symbol_id = clicked_symbol


class GameStateManager:
    def __init__(self, nb_players: int, prime_number: int = 7):
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
                          f"* {len(self.game_state.players_cards_ids.keys())} players\n"
                          f"* Middle card: "
                          f"id = {self.game_state.middle_card_id}, "
                          f"composition = {self.cards[self.game_state.middle_card_id]}")

        for player_id in self.game_state.players_cards_ids.keys():
            player_cards_ids = self.game_state.players_cards_ids[player_id]
            game_state_str += (f"\n"
                               f"* Player {player_id} has {len(self.game_state.players_cards_ids[player_id])} cards left. "
                               f"First card: "
                               f"id = {player_cards_ids[0]}, "
                               f"composition = {self.cards[player_cards_ids[0]]}")
        return game_state_str

    def get_card_composition(self, card_id: int):
        return self.cards[card_id]

    def get_middle_card_compo(self):
        return self.get_card_composition(self.game_state.middle_card_id)

    def get_top_card_compo_for_player(self, player_id):
        return self.get_card_composition(self.game_state.players_cards_ids[player_id][0])

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
            new_middle_card = self.game_state.players_cards_ids[move.player_id].pop(0)  # remove top card from player's pile
            self.game_state.set_middle_card(new_middle_card)  # set it as the new middle card


if __name__ == '__main__':
    n = 3
    p = 7
    game_on = GameStateManager(n, p)
    print(game_on.__str__())
    game_on.resolve_game_state(PlayerMove(
        0, 0
    ))