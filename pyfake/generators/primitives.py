import math
import string
from collections.abc import Callable
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from typing import Any

from pyfake.core.context import Context
from pyfake.exceptions import InvalidConstraints
from pyfake.generators import regex
from pyfake.generators.bounds import check_range, resolve_bounds


def generate_none(*args: Any, **kwargs: Any) -> None:
    return None


def generate_int(
    *,
    lt: int | None = None,
    gt: int | None = None,
    le: int | None = None,
    ge: int | None = None,
    multiple_of: int | None = None,
    context: Context | None = None,
    **kwargs: Any,
) -> int:
    if context is None:
        context = Context()

    low = (
        math.ceil(ge)
        if ge is not None
        else (math.floor(gt) + 1 if gt is not None else None)
    )
    high = (
        math.floor(le)
        if le is not None
        else (math.ceil(lt) - 1 if lt is not None else None)
    )
    min_value, max_value = resolve_bounds(low, high, 0, 100)

    # Handling multiple_of within the range
    if multiple_of is not None:
        mult = int(multiple_of)
        if mult <= 0:
            raise InvalidConstraints("multiple_of must be a positive integer")

        k_start = -(-min_value // mult)
        start = k_start * mult

        if start > max_value:
            raise InvalidConstraints(
                "No valid integer can be generated with the given constraints."
            )

        count = ((max_value - start) // mult) + 1
        random_multiple = context.random.randint(0, count - 1)
        return start + random_multiple * mult

    check_range(min_value, max_value, "integer")
    return context.random.randint(min_value, max_value)


def generate_str(
    *,
    pattern: str | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = 10,
    context: Context | None = None,
    **kwargs: Any,
) -> str:
    if context is None:
        context = Context()

    if pattern is not None:
        return regex.generate_matching(
            pattern, min_length=min_length, max_length=max_length, context=context
        )

    if not length:
        length = 10

    # Figuring out the length based on min & max length
    if min_length is not None and max_length is not None:
        size = context.random.randint(min_length, max_length)
    elif min_length is not None:
        size = min_length
    elif max_length is not None:
        size = max_length
    else:
        size = length

    letters = string.ascii_letters
    return "".join(context.random.choice(letters) for _ in range(size))


def generate_bytes(
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    context: Context | None = None,
    **kwargs: Any,
) -> bytes:
    # ASCII letters, so the value can still be serialised to JSON
    return generate_str(
        min_length=min_length, max_length=max_length, context=context
    ).encode()


def generate_float(
    *,
    lt: float | None = None,
    gt: float | None = None,
    le: float | None = None,
    ge: float | None = None,
    multiple_of: float | None = None,
    decimal_places: int | None = None,
    context: Context | None = None,
    **kwargs: Any,
) -> float:
    if context is None:
        context = Context()

    num = 0.0
    if multiple_of is not None:
        num = float(
            _pick_multiple(
                lt=lt,
                gt=gt,
                le=le,
                ge=ge,
                multiple_of=multiple_of,
                kind="float",
                context=context,
            )
        )
    else:
        # The closest floats inside exclusive bounds
        low = (
            ge
            if ge is not None
            else (math.nextafter(gt, math.inf) if gt is not None else None)
        )
        high = (
            le
            if le is not None
            else (math.nextafter(lt, -math.inf) if lt is not None else None)
        )
        min_value, max_value = resolve_bounds(low, high, 0.0, 100.0)
        check_range(min_value, max_value, "float")
        num = context.random.uniform(min_value, max_value)

    # Handling decimal places
    # https://stackoverflow.com/questions/455612/limiting-floats-to-two-decimal-points

    if decimal_places is not None:
        format_str = "{:." + str(int(decimal_places)) + "f}"
        num = float(format_str.format(num))

    return num


def generate_decimal(
    *,
    lt: Decimal | None = None,
    gt: Decimal | None = None,
    le: Decimal | None = None,
    ge: Decimal | None = None,
    multiple_of: Decimal | None = None,
    decimal_places: int | None = None,
    max_digits: int | None = None,
    context: Context | None = None,
    **kwargs: Any,
) -> Decimal:
    if context is None:
        context = Context()

    if multiple_of is not None:
        num = _pick_multiple(
            lt=lt,
            gt=gt,
            le=le,
            ge=ge,
            multiple_of=multiple_of,
            kind="decimal",
            context=context,
        )

        # Handling decimal places
        if decimal_places is not None:
            format_str = "{:." + str(int(decimal_places)) + "f}"
            num = Decimal(format_str.format(num))

        return num

    # Prefer 2 decimal places. Fall back to fewer when max_digits leaves no room for the
    # integer part, or to more when the bounds are closer together than 0.01.
    candidates = (
        range(decimal_places, -1, -1)
        if decimal_places is not None
        else (2, 1, 0, 3, 4, 5, 6)
    )
    for places in candidates:
        if max_digits is not None and places > max_digits:
            continue
        scaled = _scaled_decimal(
            lt=lt,
            gt=gt,
            le=le,
            ge=ge,
            places=places,
            max_digits=max_digits,
            context=context,
        )
        if scaled is not None:
            return scaled

    raise InvalidConstraints(
        "No valid decimal can be generated with the given constraints."
    )


def _scaled_decimal(
    *,
    lt: Decimal | None,
    gt: Decimal | None,
    le: Decimal | None,
    ge: Decimal | None,
    places: int,
    max_digits: int | None,
    context: Context,
) -> Decimal | None:
    """
    A random Decimal with exactly ``places`` decimal places, generated as a scaled integer
    so it never carries float noise. Returns None when no such value fits the constraints.
    """
    scale = Decimal(10) ** places

    low: int | None = None
    high: int | None = None
    if ge is not None:
        low = _scale(ge, scale, ROUND_CEILING)
    elif gt is not None:
        low = _scale(gt, scale, ROUND_FLOOR) + 1
    if le is not None:
        high = _scale(le, scale, ROUND_FLOOR)
    elif lt is not None:
        high = _scale(lt, scale, ROUND_CEILING) - 1
    lower, upper = resolve_bounds(low, high, 0, 100 * 10**places)

    # A scaled integer with at most max_digits digits gives a Decimal with at most max_digits digits
    if max_digits is not None:
        largest = 10**max_digits - 1
        lower, upper = max(lower, -largest), min(upper, largest)

    if lower > upper:
        return None
    return Decimal(context.random.randint(lower, upper)).scaleb(-places)


def _scale(value: Decimal, scale: Decimal, rounding: str) -> int:
    return int((Decimal(str(value)) * scale).to_integral_value(rounding=rounding))


def _pick_multiple(
    *,
    lt: float | Decimal | None,
    gt: float | Decimal | None,
    le: float | Decimal | None,
    ge: float | Decimal | None,
    multiple_of: float | Decimal,
    kind: str,
    context: Context,
) -> Decimal:
    """
    Pick a random multiple of ``multiple_of`` within the bounds. Decimal arithmetic avoids
    float rounding errors and incorrect floor/ceil logic.
    """
    mult = Decimal(str(multiple_of))
    if mult <= 0:
        raise InvalidConstraints("multiple_of must be a positive number")

    low, high = resolve_bounds(
        ge if ge is not None else gt, le if le is not None else lt, 0, 100
    )
    lower, upper = Decimal(str(low)), Decimal(str(high))

    # The smallest and largest k such that k * mult is within the bounds
    k_start = (lower / mult).to_integral_value(rounding=ROUND_CEILING)
    if ge is None and gt is not None and k_start * mult == lower:
        k_start += 1
    k_end = (upper / mult).to_integral_value(rounding=ROUND_FLOOR)
    if le is None and lt is not None and k_end * mult == upper:
        k_end -= 1

    if k_start > k_end:
        raise InvalidConstraints(
            f"No valid {kind} can be generated with the given constraints."
        )

    return context.random.randint(int(k_start), int(k_end)) * mult


def generate_bool(
    *,
    context: Context | None = None,
    **kwargs: Any,
) -> bool:
    if context is None:
        context = Context()

    return context.random.choice([True, False])


def generate_any(
    *,
    context: Context | None = None,
    **kwargs: Any,
) -> int | float | str | bool:
    """A random JSON-safe scalar, for `Any` and `object` fields"""
    if context is None:
        context = Context()

    generators: list[Callable[..., int | float | str | bool]] = [
        generate_int,
        generate_float,
        generate_str,
        generate_bool,
    ]
    return context.random.choice(generators)(context=context)
