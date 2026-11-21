"""
Shared execution state for Pyfake
"""

import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


class Context:
    def __init__(self, seed: int | None = None, now: datetime | None = None):
        self.seed = seed
        self.random = random.Random(seed)

        # Reference point for values relative to "now" (PastDate, FutureDatetime, time based UUIDs).
        # Defaults to the start of the current UTC day, so seeded output is the same all day.
        if now is None:
            now = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        self.now = now


@dataclass(frozen=True)
class GeneratorContext:
    """
    What a custom generator receives as its first argument (see `pyfake.register`)
    """

    # The seeded random stream. Draw every random value from it so seeded output is reproducible.
    random: random.Random
    # Reference point for values relative to "now"
    now: datetime
    # Path of the field being generated, e.g. "User.avatar" or "User.tags[]"
    path: str
    # The annotation type the generator was registered for
    type: Any
