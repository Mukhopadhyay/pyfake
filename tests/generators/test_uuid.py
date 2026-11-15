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


@pytest.mark.datatypes
@pytest.mark.uuid
class TestUUIDReproducibility:
    GENERATORS = [
        pyfake_uuid.generate_uuid1,
        pyfake_uuid.generate_uuid3,
        pyfake_uuid.generate_uuid4,
        pyfake_uuid.generate_uuid5,
        pyfake_uuid.generate_uuid6,
        pyfake_uuid.generate_uuid7,
        pyfake_uuid.generate_uuid8,
    ]

    @pytest.mark.parametrize("generator", GENERATORS)
    def test_same_seed_same_uuid(self, generator):
        assert generator(context=Context(seed=1)) == generator(context=Context(seed=1))

    @pytest.mark.parametrize("generator", GENERATORS)
    def test_different_seeds_different_uuids(self, generator):
        assert generator(context=Context(seed=1)) != generator(context=Context(seed=2))

    @pytest.mark.parametrize("generator", GENERATORS)
    def test_stream_gives_distinct_uuids(self, generator):
        context = Context(seed=1)
        values = {generator(context=context) for _ in range(100)}
        assert len(values) == 100

    @pytest.mark.parametrize("generator", GENERATORS)
    def test_variant_is_rfc_4122(self, generator):
        assert uuid.UUID(generator(context=Context(seed=3))).variant == uuid.RFC_4122

    def test_time_based_uuids_use_context_now(self):
        from datetime import datetime, timedelta, timezone

        now = datetime(2024, 5, 1, tzinfo=timezone.utc)
        u7 = uuid.UUID(pyfake_uuid.generate_uuid7(context=Context(seed=1, now=now)))
        ts = datetime.fromtimestamp((u7.int >> 80) / 1000, tz=timezone.utc)
        assert now - timedelta(days=1) <= ts <= now

        u1 = uuid.UUID(pyfake_uuid.generate_uuid1(context=Context(seed=1, now=now)))
        ts1 = datetime(1582, 10, 15, tzinfo=timezone.utc) + timedelta(microseconds=u1.time // 10)
        assert now - timedelta(days=1) <= ts1 <= now

    @pytest.mark.parametrize("generator", GENERATORS)
    def test_no_context_creates_one(self, generator):
        assert uuid.UUID(generator())
