"""
Generates strings that match a regular expression,
by walking its parsed form, not the best implementation
can fail after certain attempts
"""

import re
import string
import sys
from functools import lru_cache
from typing import Optional

from pyfake.core.context import Context
from pyfake.exceptions import InvalidConstraints

if sys.version_info >= (3, 11):
    from re import _constants as sre_constants
    from re import _parser as sre_parse
else:
    import sre_constants
    import sre_parse


# Unbounded repeats (*,+,{n,}) add at most this many repetitions
REPEAT_LIMIT = 8
# The number of attempts to try generating a matching string before giving up
ATTEMPTS = 100

_PRINTABLE = string.ascii_letters + string.digits + string.punctuation + " "
_CATEGORIES = {
    sre_constants.CATEGORY_DIGIT: string.digits,
    sre_constants.CATEGORY_NOT_DIGIT: string.ascii_letters + string.punctuation + " ",
    sre_constants.CATEGORY_SPACE: " ",
    sre_constants.CATEGORY_NOT_SPACE: string.ascii_letters
    + string.digits
    + string.punctuation,
    sre_constants.CATEGORY_WORD: string.ascii_letters + string.digits + "_",
    sre_constants.CATEGORY_NOT_WORD: string.punctuation.replace("_", "") + " ",
}
# POSSESSIVE_REPEAT and ATOMIC_GROUP only exist on Python 3.11+
# https://github.com/python/cpython/issues/153044
_REPEATS = tuple(
    getattr(sre_constants, name)
    for name in ("MAX_REPEAT", "MIN_REPEAT", "POSSESSIVE_REPEAT")
    if hasattr(sre_constants, name)
)
# Anchors and lookarounds dont produce text
_ZERO_WIDTH = (sre_constants.AT, sre_constants.ASSERT, sre_constants.ASSERT_NOT)
_ATOMIC_GROUP = getattr(sre_constants, "ATOMIC_GROUP", None)


def generate_matching(
    pattern: str,
    *,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    context: Optional[Context] = None,
) -> str:
    """
    Generate a string that matches pattern and the length bounds.

    Lookarounds are skipped while writing the string, so the result is checked against the
    real pattern and regenerated if needed. Like pydantic, a match anywhere in the string
    counts (re.search).
    """
    if context is None:
        context = Context()

    parsed, compiled = _compile(pattern)
    repeat_limit = max(REPEAT_LIMIT, min_length or 0)

    for _ in range(ATTEMPTS):
        text = _PatternWriter(context.random, repeat_limit).write(parsed)
        if min_length is not None and len(text) < min_length:
            continue
        if max_length is not None and len(text) > max_length:
            continue
        if compiled.search(text):
            return text

    raise InvalidConstraints(
        f"Could not generate a string matching {pattern!r} with min_length={min_length} and max_length={max_length}."
    )


@lru_cache(maxsize=256)
def _compile(pattern: str):
    try:
        return sre_parse.parse(pattern), re.compile(pattern)
    except re.error as e:
        raise InvalidConstraints(f"Invalid regex pattern {pattern!r}: {e}") from e


class _PatternWriter:
    def __init__(self, rng, repeat_limit: int):
        self.rng = rng
        self.repeat_limit = repeat_limit
        self.groups = {}

    def write(self, parsed) -> str:
        return "".join(self._write_node(op, av) for op, av in parsed)

    def _write_node(self, op, av) -> str:
        if op is sre_constants.LITERAL:
            return chr(av)
        if op is sre_constants.NOT_LITERAL:
            return self.rng.choice(_PRINTABLE.replace(chr(av), ""))
        if op is sre_constants.ANY:
            return self.rng.choice(_PRINTABLE)
        if op is sre_constants.IN:
            return self.rng.choice(self._charset(av))
        if op is sre_constants.BRANCH:
            return self.write(self.rng.choice(av[1]))
        if op is sre_constants.SUBPATTERN:
            group, _, _, sub = av
            text = self.write(sub)
            if group is not None:
                self.groups[group] = text
            return text
        if op in _REPEATS:
            low, high, sub = av
            if high == sre_constants.MAXREPEAT:
                high = low + self.repeat_limit
            return "".join(self.write(sub) for _ in range(self.rng.randint(low, high)))
        if op is sre_constants.GROUPREF:
            return self.groups.get(av, "")
        if op is sre_constants.GROUPREF_EXISTS:
            group, yes, no = av
            branch = yes if group in self.groups else no
            return self.write(branch) if branch is not None else ""
        if op is _ATOMIC_GROUP:
            return self.write(av)
        if op in _ZERO_WIDTH:
            return ""
        raise InvalidConstraints(f"Unsupported regex construct: {op}")

    def _charset(self, items) -> str:
        chars = []
        negate = False

        for op, av in items:
            if op is sre_constants.NEGATE:
                negate = True
            elif op is sre_constants.LITERAL:
                chars.append(chr(av))
            elif op is sre_constants.RANGE:
                low, high = av
                if high - low > 255:
                    # Wide ranges (e.g. unicode blocks): stick to the printable ASCII inside them
                    chars.extend(ch for ch in _PRINTABLE if low <= ord(ch) <= high)
                    if not chars:
                        chars.extend(chr(code) for code in range(low, low + 256))
                else:
                    chars.extend(chr(code) for code in range(low, high + 1))
            elif op is sre_constants.CATEGORY:
                chars.extend(_CATEGORIES.get(av, ""))

        if negate:
            excluded = set(chars)
            chars = [ch for ch in _PRINTABLE if ch not in excluded]

        if not chars:
            raise InvalidConstraints(
                "A character class in the regex pattern matches no printable characters."
            )
        return "".join(chars)
