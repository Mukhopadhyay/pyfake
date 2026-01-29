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
