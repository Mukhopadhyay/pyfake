"""
Shared execution state for Pyfake
"""

import random
from typing import Optional


class Context:
    def __init__(self, seed: Optional[int] = None):
        self.random = random.Random(seed)
