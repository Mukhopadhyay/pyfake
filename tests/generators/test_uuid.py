import pytest
from pyfake.core.context import Context
import uuid
from pyfake.generators import uuid as pyfake_uuid


@pytest.mark.datatypes
@pytest.mark.uuid
class TestGenerateUUIDs:
    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_uuid1(self, seed):
        context = Context(seed)
        result = pyfake_uuid.generate_uuid1(context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 1

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_uuid3(self, seed):
        context = Context(seed)
        result = pyfake_uuid.generate_uuid3(context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 3

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_uuid4(self, seed):
        context = Context(seed)
        result = pyfake_uuid.generate_uuid4(context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 4

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_uuid5(self, seed):
        context = Context(seed)
        result = pyfake_uuid.generate_uuid5(context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 5

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_uuid6(self, seed):
        context = Context(seed)
        result = pyfake_uuid.generate_uuid6(context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 6

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_uuid7(self, seed):
        context = Context(seed)
        result = pyfake_uuid.generate_uuid7(context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 7

    @pytest.mark.parametrize(
        "seed",
        list(range(10))
        + [
            None,
        ],
    )
    def test_generate_uuid8(self, seed):
        context = Context(seed)
        result = pyfake_uuid.generate_uuid8(context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 8

    def test_generate_uuid3_namespace_none_uses_default(self):
        context = Context(seed=0)
        result = pyfake_uuid.generate_uuid3(namespace=None, context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 3

    def test_generate_uuid5_namespace_none_uses_default(self):
        context = Context(seed=0)
        result = pyfake_uuid.generate_uuid5(namespace=None, context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 5

    def test_generate_uuid8_namespace_none_uses_default(self):
        context = Context(seed=0)
        result = pyfake_uuid.generate_uuid8(namespace=None, context=context)
        assert isinstance(result, str)
        assert uuid.UUID(result).version == 8
