import random
import string


def generate_game_id(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
