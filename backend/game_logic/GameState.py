from typing import Dict, List

import numpy as np
from .cards_creator import get_cards


# Game state describes two things:
#   - which card is in the middle
#   - which cards are in each user pile
#   - if game is active
#   - current point
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
    def __init__(self, middle_card: list, players_cards: Dict[int, List[list]], game_id: str, host_id: int):
        self.middle_card = middle_card
        self.players_cards = players_cards
        self.active = False
        self.game_id = game_id
        self.host_id = host_id
        self.winner: int = 0

class PlayerMove:
    def __init__(self, player_id: int, clicked_symbol: int, middle_card_id: int):
        self.player_id = player_id
        self.symbol_id = clicked_symbol
        self.middle_card_id = middle_card_id


class GameStateManager:
    def __init__(self, player_ids: list, host_id : int, prime_number: int = 7, game_id: str = ''):
        # Create cards deck
        cards = get_cards(prime_number)
        np.random.shuffle(cards)
        self.cards = cards

        # Select first card as middle card
        middle_card = cards.pop(0)
        
        nb_players = len(player_ids)
        # Deal the rest of the cards evenly to the players
        nb_cards_per_player = len(cards) // nb_players
        players_cards = {}

        first_card_id = 1  # first card of the deck has been used as middle card
        for player_id in player_ids:
            last_card_id = first_card_id + nb_cards_per_player
            players_cards[player_id] = cards[first_card_id:last_card_id]
            first_card_id += nb_cards_per_player


        # Initialize game state
        self.game_state = GameState(middle_card, players_cards, game_id, host_id)

    def __str__(self):
        game_state_str = (f"Current game state\n------------------\n"
                          f"* {len(self.game_state.players_cards.keys())} players\n"
                          f"* Middle card: {self.game_state.middle_card}")

        for player_id in self.game_state.players_cards.keys():
            player_cards = self.game_state.players_cards[player_id]
            game_state_str += (f"\n"
                               f"* Player {player_id} has {len(self.game_state.players_cards[player_id])} cards left. "
                               f"First card: {player_cards[0]}")
        return game_state_str

    def get_top_card_compo_for_player(self, player_id):
        return self.game_state.players_cards[player_id][0]

    def valid_player_match(self, move: PlayerMove) -> bool:
        # check the symbol exists both in the player's card and the middle card
        player_top_card_compo = self.get_top_card_compo_for_player(move.player_id)
        print(player_top_card_compo)
        print(self.game_state.middle_card)

        if move.symbol_id not in player_top_card_compo:
            # symbol should have not been clickable FIXME
            print('symbol not present')
            return False

        if move.symbol_id not in self.game_state.middle_card:
            # not a match FIXME penalty?
            print("Invalid move")
            return False

        print("Valid move")
        return True

    def resolve_game_state(self, move: PlayerMove) -> bool:
        # If the player's move is valid, update game state
        if self.valid_player_match(move):
            #resolve if game is still going or it should end, set active = False and set self.winner
            new_middle_card = self.game_state.players_cards[move.player_id].pop(0)  # remove top card from player's pile
            self.game_state.middle_card = new_middle_card  # set it as the new middle card
            return True
        else:
            return False


if __name__ == '__main__':
    p = 7
    id = 'game'
    game_on = GameStateManager([1,2,3], p, 1, id)
    print(game_on.__str__())
    game_on.resolve_game_state(PlayerMove(
        0, 0, 0
    ))
