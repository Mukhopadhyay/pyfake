import pytest
from decimal import Decimal
from pyfake.core.context import Context
from pyfake.generators import primitives
from pyfake.exceptions import InvalidConstraints


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
    def test_generate_str_length(self, min_length, max_length, length, pattern, expected_min, expected_max):
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
            result = primitives.generate_float(lt=lt, gt=gt, le=le, ge=ge, context=context)
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
        result = primitives.generate_float(decimal_places=decimal_places, context=context)
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
        result = primitives.generate_float(ge=0.0, le=10.0, multiple_of=2.5, context=context)
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
        assert Decimal("0") <= result <= Decimal("100")

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
        result = primitives.generate_decimal(lt=lt, gt=gt, le=le, ge=ge, context=context)
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
        result = primitives.generate_decimal(multiple_of=Decimal("0.5"), context=context)
        assert isinstance(result, Decimal)
        assert result % Decimal("0.5") == 0

    @pytest.mark.parametrize("decimal_places", [0, 1, 2, 3])
    def test_generate_decimal_decimal_places(self, decimal_places):
        context = Context(seed=7)
        result = primitives.generate_decimal(decimal_places=decimal_places, context=context)
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
