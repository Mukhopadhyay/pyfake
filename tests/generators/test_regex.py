import re
import sys

import pytest

from pyfake.core.context import Context
from pyfake.exceptions import InvalidConstraints
from pyfake.generators.regex import generate_matching

PATTERNS = [
    r"^[A-Z]{3}-\d{4}$",
    r"^\d{5}(-\d{4})?$",
    r"^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$",
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+)?$",
    r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    r"^\+?[1-9]\d{1,14}$",
    r"^#[0-9a-fA-F]{6}$",
    r"^(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])-(?P<day>0[1-9]|[12]\d|3[01])$",
    r"^[^\s@]+@[^\s@]+\.[a-z]{2,}$",
    r"^SKU-[A-Z0-9]{8}$",
    r"^(\w)\w*\1$",
    r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,16}$",
    r"^[^aeiou]{3}$",
    r"^(a|b)(?(1)c|d)$",
    r"^\S+\s\S+$",
    r"^\W\D$",
    r"^a*?b+?$",
    r"^.{3}$",
    r"^[一-鿿]{2,4}$",
    r"\d+",
    r"^(?i:ab)c$",
    r"^(a)?(?(1)b)c$",
    r"^[\u0000-\uffff]{3}$",
    r"^[^a]b$",
]


@pytest.mark.datatypes
@pytest.mark.string
class TestGenerateMatching:
    @pytest.mark.parametrize("pattern", PATTERNS)
    def test_output_matches_pattern(self, pattern):
        for seed in range(50):
            assert re.search(
                pattern, generate_matching(pattern, context=Context(seed=seed))
            )

    @pytest.mark.parametrize("pattern", PATTERNS)
    def test_deterministic_with_seed(self, pattern):
        assert generate_matching(pattern, context=Context(seed=9)) == generate_matching(
            pattern, context=Context(seed=9)
        )

    @pytest.mark.skipif(
        sys.version_info < (3, 11),
        reason="atomic groups and possessive repeats need Python 3.11+",
    )
    @pytest.mark.parametrize("pattern", [r"^(?>ab|a)c$", r"^a++b$"])
    def test_atomic_and_possessive(self, pattern):
        for seed in range(20):
            assert re.search(
                pattern, generate_matching(pattern, context=Context(seed=seed))
            )

    def test_length_bounds(self):
        for seed in range(30):
            result = generate_matching(
                r"^[a-z]+$", min_length=10, max_length=12, context=Context(seed=seed)
            )
            assert 10 <= len(result) <= 12

    def test_no_context_creates_one(self):
        assert re.fullmatch(r"\d{3}", generate_matching(r"^\d{3}$"))

    def test_impossible_length_raises(self):
        with pytest.raises(InvalidConstraints):
            generate_matching(r"^[A-Z]{3}$", min_length=5, context=Context(seed=1))

    def test_invalid_pattern_raises(self):
        with pytest.raises(InvalidConstraints):
            generate_matching(r"^[a-z", context=Context(seed=1))

    def test_empty_character_class_raises(self):
        # Negating every printable character leaves nothing to choose from
        with pytest.raises(InvalidConstraints):
            generate_matching(r"^[^\x20-\x7e]$", context=Context(seed=1))
