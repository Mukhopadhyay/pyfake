import random


def integer() -> int:
    return random.randint(0, 100)


def float() -> float:
    return random.uniform(0.0, 100.0)
