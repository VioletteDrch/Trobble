# From source https://math.stackexchange.com/questions/36798/what-is-the-math-behind-the-game-spot-it
from itertools import combinations

def get_cards(p):
    cards = [[] for _ in range(p ** 2 + p + 1)]
    cards[0].append(0)
    for i in range(p + 1):
        for j in range(p):
            cards[1 + i * p + j].append(i)
            cards[i].append(1 + i * p + j)
    for i in range(p):
        for j in range(p):
            for k in range(p):
                cards[1 + p + i * p + k].append(1 + p + j * p + (i * j - k) % p)
    return cards

if __name__ == "__main__":
    prime_number = 7
    cards = get_cards(prime_number)
    for card0, card1 in combinations(cards, 2):
        assert len(set(card0) & set(card1)) == 1

    for card in cards:
        print(card)

__all__ = ['get_cards']
