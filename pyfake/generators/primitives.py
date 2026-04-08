import string
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from pyfake.core.context import Context
from typing import Optional
from pyfake.exceptions import InvalidConstraints

"""
TODO:
Argument error for invalid Field args, e.g.,
- lt < gt
- le < ge
- multiple_of > (lt - gt) or multiple_of > (le - ge)
"""


def generate_none(*args, **kwargs):
    return None


def generate_int(
    *,
    lt: Optional[int] = None,
    gt: Optional[int] = None,
    le: Optional[int] = None,
    ge: Optional[int] = None,
    multiple_of: Optional[int] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> int:

    min_value = ge if ge is not None else (gt + 1 if gt is not None else 0)
    max_value = le if le is not None else (lt - 1 if lt is not None else 100)

    # Handling multiple_of within the range
    if multiple_of is not None:

        mult = int(multiple_of)
        if mult <= 0:
            raise InvalidConstraints("multiple_of must be a positive integer")

        k_start = -(-min_value // mult)
        start = k_start * mult

        if start > max_value:
            raise InvalidConstraints("No valid integer can be generated with the given constraints.")

        count = ((max_value - start) // mult) + 1
        random_multiple = context.random.randint(0, count - 1)
        return start + random_multiple * mult

    return context.random.randint(min_value, max_value)


def generate_str(
    *,
    pattern: Optional[str] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    length: Optional[int] = 10,
    context: Optional[Context] = None,
    **kwargs,
) -> str:
    # TODO: Support for pattern
    if not length:
        length = 10

    # Figuring out the length based on min & max length
    if min_length is not None and max_length is not None:
        l = context.random.randint(min_length, max_length)
    elif min_length is not None:
        l = min_length
    elif max_length is not None:
        l = max_length
    else:
        l = length

    letters = string.ascii_letters
    return "".join(context.random.choice(letters) for _ in range(l))


def generate_float(
    *,
    lt: Optional[int] = None,
    gt: Optional[int] = None,
    le: Optional[int] = None,
    ge: Optional[int] = None,
    multiple_of: Optional[float] = None,
    decimal_places: Optional[int] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> float:
    min_value = ge if ge is not None else (gt + 0.1 if gt is not None else 0.0)
    max_value = le if le is not None else (lt - 0.1 if lt is not None else 100.0)

    num = 0.0
    if multiple_of is not None:
        min_dec = Decimal(str(min_value))
        max_dec = Decimal(str(max_value))
        mult_dec = Decimal(str(multiple_of))

        if mult_dec == 0:
            raise InvalidConstraints("multiple_of cannot be zero")

        k_start = (min_dec / mult_dec).to_integral_value(rounding=ROUND_CEILING)
        start = k_start * mult_dec
        if start > max_dec:
            raise InvalidConstraints("No valid float can be generated with the given constraints.")

        k_count = ((max_dec - start) / mult_dec).to_integral_value(rounding=ROUND_FLOOR)
        count = int(k_count) + 1
        random_multiple = context.random.randint(0, count - 1)
        num = float(start + Decimal(random_multiple) * mult_dec)
    else:
        num = context.random.uniform(min_value, max_value)

    # Handling decimal places
    # https://stackoverflow.com/questions/455612/limiting-floats-to-two-decimal-points

    if decimal_places is not None:
        format_str = "{:." + str(int(decimal_places)) + "f}"
        num = float(format_str.format(num))

    return num


def generate_decimal(
    *,
    lt: Optional[int] = None,
    gt: Optional[int] = None,
    le: Optional[int] = None,
    ge: Optional[int] = None,
    multiple_of: Optional[float] = None,
    decimal_places: Optional[int] = None,
    context: Optional[Context] = None,
    **kwargs,
) -> Decimal:
    min_value = ge if ge is not None else (gt + 0.1 if gt is not None else 0.0)
    max_value = le if le is not None else (lt - 0.1 if lt is not None else 100.0)

    num = Decimal(0)
    if multiple_of is not None:
        # Use Decimal arithmetic to find the first multiple >= min_value
        # and the count of multiples <= max_value. This avoids float
        # rounding errors and incorrect floor/ceil logic.
        min_dec = Decimal(str(min_value))
        max_dec = Decimal(str(max_value))
        mult_dec = Decimal(str(multiple_of))

        if mult_dec == 0:
            raise InvalidConstraints("multiple_of cannot be zero")

        # Compute the smallest integer k such that k*mult_dec >= min_dec
        k_start = (min_dec / mult_dec).to_integral_value(rounding=ROUND_CEILING)
        start = k_start * mult_dec

        if start > max_dec:
            raise InvalidConstraints("No valid decimal can be generated with the given constraints.")

        k_count = ((max_dec - start) / mult_dec).to_integral_value(rounding=ROUND_FLOOR)
        count = int(k_count) + 1
        random_multiple = context.random.randint(0, count - 1)
        num = start + Decimal(random_multiple) * mult_dec
    else:
        num = context.random.uniform(min_value, max_value)
        num = Decimal(num)

    # Handling decimal places
    if decimal_places is not None:
        format_str = "{:." + str(int(decimal_places)) + "f}"
        num = Decimal(format_str.format(num))

    return num


def generate_bool(
    *,
    context: Optional[Context] = None,
    **kwargs,
) -> bool:
    return context.random.choice([True, False])
