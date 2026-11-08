"""
Helpers for turning optional lower/upper constraints into a concrete range
"""

from pyfake.exceptions import InvalidConstraints


def resolve_bounds(
    lower, upper, default_lower, default_upper, floor=None, ceiling=None
):
    """
    Fill in missing bounds with their defaults.

    When the default would leave the range empty (e.g. only ge=500 against a default
    upper bound of 100), the range keeps the default width and moves next to the bound
    that was given instead, clamped to floor/ceiling.
    """
    span = default_upper - default_lower

    if lower is None:
        if upper is None or default_lower <= upper:
            lower = default_lower
        else:
            try:
                lower = upper - span
            except OverflowError:
                lower = floor
            if floor is not None:
                lower = max(lower, floor)

    if upper is None:
        if default_upper >= lower:
            upper = default_upper
        else:
            try:
                upper = lower + span
            except OverflowError:
                upper = ceiling
            if ceiling is not None:
                upper = min(upper, ceiling)

    return lower, upper


def check_range(lower, upper, kind: str):
    if lower > upper:
        raise InvalidConstraints(
            f"No valid {kind} can be generated with the given constraints ({lower} > {upper})."
        )
