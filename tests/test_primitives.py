import itertools
import pytest
from pyfake.core.context import Context
from pyfake.generators import primitives


class TestGenerateNone:

    def test_generate_none(self):
        assert primitives.generate_none() is None

    def test_generate_none_args_kwargs(self):
        assert primitives.generate_none(1, thing="abc") is None


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
