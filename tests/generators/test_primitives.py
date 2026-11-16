from decimal import Decimal

import pytest

from pyfake.core.context import Context
from pyfake.exceptions import InvalidConstraints
from pyfake.generators import primitives


@pytest.mark.datatypes
class TestGenerateNone:
    def test_generate_none(self):
        assert primitives.generate_none() is None

    def test_generate_none_args_kwargs(self):
        assert primitives.generate_none(1, thing="abc") is None


@pytest.mark.datatypes
@pytest.mark.integer
class TestGenerateInteger:
    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_int_type(self, seed):
        context = Context(seed=seed)
        assert isinstance(primitives.generate_int(context=context), int)

    @pytest.mark.parametrize(
        "lt,gt,le,ge",
        [
            (20, 10, None, None),
            (None, None, 20, 10),
            (30, 15, 25, 17),
            (50, 30, 45, 31),
            (None, None, None, None),
        ],
    )
    def test_generate_int_bounds(self, lt, gt, le, ge):
        context = Context()
        result = primitives.generate_int(lt=lt, gt=gt, le=le, ge=ge, context=context)
        if ge is not None:
            assert result >= ge
        if gt is not None:
            assert result > gt
        if le is not None:
            assert result <= le
        if lt is not None:
            assert result < lt


@pytest.mark.datatypes
@pytest.mark.boolean
class TestGenerateBoolean:
    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_bool_type(self, seed):
        context = Context(seed=seed)
        assert isinstance(primitives.generate_bool(context=context), bool)


@pytest.mark.datatypes
@pytest.mark.string
class TestGenerateString:
    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_str_type(self, seed):
        context = Context(seed=seed)
        assert isinstance(primitives.generate_str(context=context), str)

    @pytest.mark.parametrize(
        "min_length,max_length,length,pattern,expected_min,expected_max",
        [
            (1, 3, None, None, 1, 3),
            (5, None, None, None, 5, 5),
            (None, 7, None, None, 7, 7),
            (None, None, 12, None, 12, 12),
            (None, None, None, None, 10, 10),
            (2, 2, None, None, 2, 2),
            (0, 0, None, None, 0, 0),
        ],
    )
    def test_generate_str_length(
        self, min_length, max_length, length, pattern, expected_min, expected_max
    ):
        context = Context(seed=42)
        result = primitives.generate_str(
            min_length=min_length,
            max_length=max_length,
            length=length,
            pattern=pattern,
            context=context,
        )
        assert isinstance(result, str)
        assert expected_min <= len(result) <= expected_max
        assert all(c.isalpha() for c in result)


@pytest.mark.datatypes
@pytest.mark.float
class TestGenerateFloat:
    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_float_type(self, seed):
        context = Context(seed=seed)
        assert isinstance(primitives.generate_float(context=context), float)

    @pytest.mark.parametrize(
        "lt,gt,le,ge",
        [
            (20.0, 10.0, None, None),
            (None, None, 20.0, 10.0),
            (30.0, 15.0, 25.0, 17.0),
            (50.0, 30.0, 45.0, 31.0),
            (None, None, None, None),
        ],
    )
    def test_generate_float_bounds(self, lt, gt, le, ge):
        context = Context(seed=42)
        for _ in range(100):
            result = primitives.generate_float(
                lt=lt, gt=gt, le=le, ge=ge, context=context
            )
            if ge is not None:
                assert result >= ge
            if gt is not None:
                assert result > gt
            if le is not None:
                assert result <= le
            if lt is not None:
                assert result < lt

    @pytest.mark.parametrize("decimal_places", [0, 1, 2, 3])
    def test_generate_float_decimal_places(self, decimal_places):
        context = Context(seed=7)
        result = primitives.generate_float(
            decimal_places=decimal_places, context=context
        )
        assert isinstance(result, float)
        # The generator formats the number to the requested decimal places before
        # converting back to float, so rounding to that many places should equal
        # the produced value.
        assert round(result, decimal_places) == result


@pytest.mark.datatypes
@pytest.mark.integer
class TestGenerateIntegerMultipleOf:
    def test_multiple_of_is_divisible(self):
        context = Context(seed=42)
        result = primitives.generate_int(multiple_of=5, context=context)
        assert isinstance(result, int)
        assert result % 5 == 0

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_multiple_of_in_range(self, seed):
        context = Context(seed=seed)
        result = primitives.generate_int(ge=10, le=50, multiple_of=10, context=context)
        assert result in {10, 20, 30, 40, 50}

    def test_multiple_of_zero_raises(self):
        context = Context(seed=1)
        with pytest.raises(InvalidConstraints):
            primitives.generate_int(multiple_of=0, context=context)

    def test_multiple_of_negative_raises(self):
        context = Context(seed=1)
        with pytest.raises(InvalidConstraints):
            primitives.generate_int(multiple_of=-3, context=context)

    def test_multiple_of_no_valid_int_raises(self):
        context = Context(seed=1)
        # Range [11, 14] contains no multiple of 5
        with pytest.raises(InvalidConstraints):
            primitives.generate_int(ge=11, le=14, multiple_of=5, context=context)


@pytest.mark.datatypes
@pytest.mark.float
class TestGenerateFloatMultipleOf:
    def test_multiple_of_basic(self):
        context = Context(seed=42)
        result = primitives.generate_float(multiple_of=0.5, context=context)
        assert isinstance(result, float)
        assert Decimal(str(result)) % Decimal("0.5") == 0

    @pytest.mark.parametrize("seed", list(range(5)) + [None])
    def test_multiple_of_in_range(self, seed):
        context = Context(seed=seed)
        result = primitives.generate_float(
            ge=0.0, le=10.0, multiple_of=2.5, context=context
        )
        assert Decimal(str(result)) % Decimal("2.5") == 0
        assert 0.0 <= result <= 10.0

    def test_multiple_of_zero_raises(self):
        context = Context(seed=1)
        with pytest.raises(InvalidConstraints):
            primitives.generate_float(multiple_of=0, context=context)

    def test_multiple_of_no_valid_float_raises(self):
        context = Context(seed=1)
        # Range [1.0, 1.1] contains no multiple of 10.0
        with pytest.raises(InvalidConstraints):
            primitives.generate_float(ge=1.0, le=1.1, multiple_of=10.0, context=context)


@pytest.mark.datatypes
@pytest.mark.decimal
class TestGenerateDecimal:
    def test_generate_decimal_type(self):
        context = Context(seed=42)
        result = primitives.generate_decimal(context=context)
        assert isinstance(result, Decimal)

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_generate_decimal_default_range(self, seed):
        context = Context(seed=seed)
        result = primitives.generate_decimal(context=context)
        assert isinstance(result, Decimal)
        assert Decimal(0) <= result <= Decimal(100)

    @pytest.mark.parametrize(
        "lt,gt,le,ge",
        [
            (None, None, 50, 10),
            (30.0, 5.0, None, None),
            (20.0, 5.0, 18.0, 7.0),
            (None, None, None, None),
        ],
    )
    def test_generate_decimal_bounds(self, lt, gt, le, ge):
        context = Context(seed=7)
        result = primitives.generate_decimal(
            lt=lt, gt=gt, le=le, ge=ge, context=context
        )
        if ge is not None:
            assert result >= ge
        if gt is not None:
            assert result > gt
        if le is not None:
            assert result <= le
        if lt is not None:
            assert result < lt

    def test_generate_decimal_multiple_of(self):
        context = Context(seed=42)
        result = primitives.generate_decimal(
            multiple_of=Decimal("0.5"), context=context
        )
        assert isinstance(result, Decimal)
        assert result % Decimal("0.5") == 0

    @pytest.mark.parametrize("decimal_places", [0, 1, 2, 3])
    def test_generate_decimal_decimal_places(self, decimal_places):
        context = Context(seed=7)
        result = primitives.generate_decimal(
            decimal_places=decimal_places, context=context
        )
        assert isinstance(result, Decimal)
        quantizer = Decimal(10) ** -decimal_places
        assert result == result.quantize(quantizer)

    def test_generate_decimal_multiple_of_zero_raises(self):
        context = Context(seed=1)
        with pytest.raises(InvalidConstraints):
            primitives.generate_decimal(multiple_of=0, context=context)

    def test_generate_decimal_multiple_of_no_valid_raises(self):
        context = Context(seed=1)
        with pytest.raises(InvalidConstraints):
            primitives.generate_decimal(ge=1, le=1.1, multiple_of=10, context=context)


@pytest.mark.datatypes
class TestOneSidedBounds:
    """A single bound outside the default range moves the range next to it instead of crashing."""

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_int_lower_bound_above_default_range(self, seed):
        result = primitives.generate_int(ge=500, context=Context(seed=seed))
        assert 500 <= result <= 600

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_int_upper_bound_below_default_range(self, seed):
        result = primitives.generate_int(le=-5, context=Context(seed=seed))
        assert -105 <= result <= -5

    def test_int_bound_inside_default_range_keeps_default(self):
        for seed in range(20):
            assert (
                50 <= primitives.generate_int(ge=50, context=Context(seed=seed)) <= 100
            )

    def test_int_multiple_of_with_one_sided_bound(self):
        result = primitives.generate_int(
            gt=1000, multiple_of=7, context=Context(seed=3)
        )
        assert result > 1000
        assert result % 7 == 0

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_float_one_sided_bounds(self, seed):
        assert primitives.generate_float(gt=500.0, context=Context(seed=seed)) > 500.0
        assert primitives.generate_float(lt=-5.0, context=Context(seed=seed)) < -5.0

    def test_float_exclusive_bounds_close_together(self):
        for seed in range(50):
            result = primitives.generate_float(
                gt=0.0, lt=0.05, context=Context(seed=seed)
            )
            assert 0.0 < result < 0.05

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_decimal_one_sided_bounds(self, seed):
        assert (
            primitives.generate_decimal(ge=Decimal(500), context=Context(seed=seed))
            >= 500
        )
        assert primitives.generate_decimal(le=-5, context=Context(seed=seed)) <= -5

    @pytest.mark.parametrize(
        "generator,kwargs",
        [
            (primitives.generate_int, {"ge": 10, "le": 5}),
            (primitives.generate_float, {"gt": 1.0, "lt": 0.5}),
            (primitives.generate_decimal, {"ge": 10, "le": 5}),
        ],
    )
    def test_conflicting_bounds_raise(self, generator, kwargs):
        with pytest.raises(InvalidConstraints):
            generator(context=Context(seed=1), **kwargs)

    def test_invalid_constraints_is_a_value_error(self):
        with pytest.raises(ValueError):
            primitives.generate_int(ge=10, le=5, context=Context(seed=1))


@pytest.mark.datatypes
@pytest.mark.decimal
class TestGenerateDecimalDigits:
    @staticmethod
    def _digits(value: Decimal):
        # Same counting rule as pydantic: (total digits, decimal places)
        _, digits, exponent = value.normalize().as_tuple()
        decimals = max(-exponent, 0)
        return max(len(digits) + max(exponent, 0), decimals), decimals

    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_unbounded_decimal_has_two_places(self, seed):
        result = primitives.generate_decimal(context=Context(seed=seed))
        assert result == result.quantize(Decimal("0.01"))
        assert len(result.as_tuple().digits) <= 4

    @pytest.mark.parametrize(
        "max_digits,decimal_places,ge",
        [
            (4, None, None),
            (5, 2, None),
            (3, None, 100),
            (2, 2, None),
            (1, None, None),
            (6, 4, 10),
        ],
    )
    def test_max_digits_respected(self, max_digits, decimal_places, ge):
        for seed in range(50):
            result = primitives.generate_decimal(
                max_digits=max_digits,
                decimal_places=decimal_places,
                ge=ge,
                context=Context(seed=seed),
            )
            digits, decimals = self._digits(result)
            assert digits <= max_digits
            if decimal_places is not None:
                assert decimals <= decimal_places
            if ge is not None:
                assert result >= ge

    def test_bounds_closer_than_a_cent(self):
        result = primitives.generate_decimal(
            gt=0, lt=Decimal("0.01"), context=Context(seed=1)
        )
        assert 0 < result < Decimal("0.01")

    def test_multiple_of_with_decimal_places(self):
        result = primitives.generate_decimal(
            multiple_of=Decimal("0.25"), decimal_places=2, context=Context(seed=1)
        )
        assert result % Decimal("0.25") == 0
        assert result == result.quantize(Decimal("0.01"))

    @pytest.mark.parametrize("seed", list(range(20)))
    def test_multiple_of_with_exclusive_bounds_on_a_multiple(self, seed):
        result = primitives.generate_decimal(
            gt=0, lt=1, multiple_of=Decimal("0.5"), context=Context(seed=seed)
        )
        assert result == Decimal("0.5")

    def test_impossible_max_digits_raises(self):
        with pytest.raises(InvalidConstraints):
            primitives.generate_decimal(max_digits=2, ge=1000, context=Context(seed=1))

    def test_exclusive_bounds(self):
        for seed in range(50):
            result = primitives.generate_decimal(
                gt=1, lt=2, decimal_places=1, context=Context(seed=seed)
            )
            assert Decimal(1) < result < Decimal(2)


@pytest.mark.datatypes
@pytest.mark.string
class TestGenerateStringPattern:
    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_pattern_is_matched(self, seed):
        import re

        result = primitives.generate_str(
            pattern=r"^[A-Z]{3}-\d{4}$", context=Context(seed=seed)
        )
        assert re.fullmatch(r"[A-Z]{3}-\d{4}", result)

    def test_pattern_with_length_bounds(self):
        for seed in range(20):
            result = primitives.generate_str(
                pattern=r"^[a-z]+$",
                min_length=4,
                max_length=6,
                context=Context(seed=seed),
            )
            assert 4 <= len(result) <= 6
            assert result.isalpha() and result.islower()


@pytest.mark.datatypes
class TestGenerateBytesAndAny:
    @pytest.mark.parametrize("seed", list(range(10)) + [None])
    def test_generate_bytes(self, seed):
        result = primitives.generate_bytes(
            min_length=2, max_length=4, context=Context(seed=seed)
        )
        assert isinstance(result, bytes)
        assert 2 <= len(result) <= 4
        # ASCII, so it can be serialised to JSON
        result.decode("ascii")

    @pytest.mark.parametrize("seed", list(range(20)) + [None])
    def test_generate_any_is_a_json_scalar(self, seed):
        assert isinstance(
            primitives.generate_any(context=Context(seed=seed)), (int, float, str, bool)
        )
