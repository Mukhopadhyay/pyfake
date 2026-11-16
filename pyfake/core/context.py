"""
Shared execution state for Pyfake
"""

import random
from datetime import datetime, timezone


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
