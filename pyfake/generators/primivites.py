"""
Handles scalar generation
* int
* float
* bool
* str
"""

import random
import string
from pyfake.core.context import Context
from typing import Optional

def generate_none():
    return None

def generate_int(*, context: Optional[Context] = None, **kwargs) -> int:
    if context:
        return context.random.randint(0, 100)
    return random.randint(0, 100)


def generate_float(*, context: Optional[Context] = None) -> float:
    if context:
        return context.random.uniform(0.0, 100.0)
    return random.uniform(0.0, 100.0)


def generate_bool(*, context: Optional[Context] = None) -> bool:
    if context:
        return context.random.choice([True, False])
    return random.choice([True, False])


def generate_str(*, context: Optional[Context] = None) -> str:
    letters = string.ascii_letters
    length = 10
    if context:
        return "".join(context.random.choice(letters) for _ in range(length))
    return "".join(random.choice(letters) for _ in range(length))
