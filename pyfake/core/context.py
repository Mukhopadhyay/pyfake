"""
Shared execution state for Pyfake
"""

import random


class Context:
    def __init__(self, seed: int | None = None):
        self.random = random.seed(seed)
