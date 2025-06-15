import random


def integer() -> int:
    return random.randint(0, 100)


def number() -> float:
    return random.uniform(0.0, 100.0)
