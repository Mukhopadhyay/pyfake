"""
Helpers for turning optional lower/upper constraints into a concrete range
"""

from typing import Any, TypeVar

from pyfake.exceptions import InvalidConstraints

T = TypeVar("T")


def resolve_bounds(
    lower: T | None,
    upper: T | None,
    default_lower: T,
    default_upper: T,
    floor: T | None = None,
    ceiling: T | None = None,
) -> tuple[T, T]:
    """
    Fill in missing bounds with their defaults.

    When the default would leave the range empty (e.g. only ge=500 against a default
    upper bound of 100), the range keeps the default width and moves next to the bound
    that was given instead, clamped to floor/ceiling.
    """
    # Bounds can be numbers, dates, datetimes or timedeltas, so the arithmetic below is untyped
    low: Any = lower
    high: Any = upper
    dl: Any = default_lower
    du: Any = default_upper
    span = du - dl

    if low is None:
        if high is None or dl <= high:
            low = dl
        else:
            try:
                low = high - span
            except OverflowError:
                low = floor
            if floor is not None:
                low = max(low, floor)

    if high is None:
        if du >= low:
            high = du
        else:
            try:
                high = low + span
            except OverflowError:
                high = ceiling
            if ceiling is not None:
                high = min(high, ceiling)

    return low, high


def check_range(lower: Any, upper: Any, kind: str) -> None:
    if lower > upper:
        raise InvalidConstraints(
            f"No valid {kind} can be generated with the given constraints ({lower} > {upper})."
        )
