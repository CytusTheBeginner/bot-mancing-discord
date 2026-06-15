import random
from database import get_fishes

def fish_roll(rod_level: int):
    fishes = get_fishes()
    pool = []

    rod_modifier = 1 + (rod_level - 1) * 0.05

    for fish in fishes:
        chance = fish["chance"] * rod_modifier
        pool.extend([fish] * int(chance))

    pool.extend([None] * 100)  # zonk

    return random.choice(pool)
