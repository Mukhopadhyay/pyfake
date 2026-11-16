"""
Integration tests for pydantic's special types (emails, URLs, IP addresses, secrets,
bytes, relative dates, ...) and abstract container types.
"""

import ipaddress
from collections import Counter, OrderedDict, defaultdict, deque
from collections.abc import Iterable, Mapping, MutableMapping, MutableSequence, Sequence
from datetime import date, datetime, timedelta, timezone
from typing import (
    AbstractSet,
    Annotated,
    Any,
    Literal,
)

import pydantic
import pytest
from pydantic import BaseModel, ByteSize, Field

from pyfake import Pyfake, fake

SEEDS = list(range(20)) + [None]


class NetworkModel(BaseModel):
    email: pydantic.EmailStr
    contact: pydantic.NameEmail
    any_url: pydantic.AnyUrl
    http_url: pydantic.HttpUrl
    file_url: pydantic.FileUrl
    ws_url: pydantic.WebsocketUrl
    postgres: pydantic.PostgresDsn
    redis: pydantic.RedisDsn
    mongo: pydantic.MongoDsn
    nats: pydantic.NatsDsn
    mysql: pydantic.MySQLDsn
    ipv4: ipaddress.IPv4Address
    ipv6: ipaddress.IPv6Address
    ip_any: pydantic.IPvAnyAddress
    net4: ipaddress.IPv4Network
    net_any: pydantic.IPvAnyNetwork
    iface6: ipaddress.IPv6Interface
    iface_any: pydantic.IPvAnyInterface
    emails: list[pydantic.EmailStr]
    maybe_url: pydantic.HttpUrl | None


class SecretsAndBytesModel(BaseModel):
    password: pydantic.SecretStr
    short_password: Annotated[pydantic.SecretStr, Field(min_length=4, max_length=6)]
    token: pydantic.SecretBytes
    blob: bytes
    small_blob: Annotated[bytes, Field(max_length=3)]
    size: ByteSize


class TimeModel(BaseModel):
    born: pydantic.PastDate
    expires: pydantic.FutureDate
    last_login: pydantic.PastDatetime
    next_run: pydantic.FutureDatetime
    aware: pydantic.AwareDatetime
    naive: pydantic.NaiveDatetime
    since_2020: Annotated[pydantic.PastDate, Field(ge=date(2020, 1, 1))]
    duration: timedelta
    short_duration: Annotated[
        timedelta, Field(ge=timedelta(minutes=1), lt=timedelta(minutes=5))
    ]


class ContainerModel(BaseModel):
    seq: Sequence[int]
    mutable_seq: MutableSequence[str]
    iterable: Iterable[int]
    queue: deque
    mapping: Mapping[str, int]
    mutable_mapping: MutableMapping[str, int]
    ordered: OrderedDict[str, int]
    default_dict: defaultdict[str, int]
    counter: Counter[str]
    abstract_set: AbstractSet[int]
    frozen: frozenset[Literal["a", "b", "c"]]
    anything: Any
    obj: object
    bare_list: list
    bare_dict: dict
    bare_tuple: tuple
    any_dict: dict[Any, Any]
    nothing: None


@pytest.mark.datatypes
@pytest.mark.pyfake
@pytest.mark.network
class TestNetworkTypes:
    @pytest.mark.parametrize("seed", SEEDS)
    def test_network_model_is_valid(self, seed):
        model = fake(NetworkModel, seed=seed, as_dict=False)
        assert isinstance(model, NetworkModel)
        # Must also serialise
        model.model_dump_json()

    def test_url_schemes_follow_the_type(self):
        model = fake(NetworkModel, seed=1, as_dict=False)
        assert model.http_url.scheme in {"http", "https"}
        assert model.file_url.scheme == "file"
        assert model.ws_url.scheme in {"ws", "wss"}
        assert str(model.postgres).startswith("postgres")
        assert model.redis.scheme in {"redis", "rediss"}

    def test_ip_versions_follow_the_type(self):
        model = fake(NetworkModel, seed=1, as_dict=False)
        assert isinstance(model.ipv4, ipaddress.IPv4Address)
        assert isinstance(model.ipv6, ipaddress.IPv6Address)
        assert isinstance(model.net4, ipaddress.IPv4Network)
        assert isinstance(model.iface6, ipaddress.IPv6Interface)

    def test_format_key_on_a_str_field(self):
        class M(BaseModel):
            email: str = Field(json_schema_extra={"format": "email"})
            url: str = Field(json_schema_extra={"format": "uri"})

        result = fake(M, seed=1)
        assert "@example." in result["email"]
        assert result["url"].startswith("http")


@pytest.mark.datatypes
@pytest.mark.pyfake
class TestSecretsAndBytes:
    @pytest.mark.parametrize("seed", SEEDS)
    def test_model_is_valid(self, seed):
        model = fake(SecretsAndBytesModel, seed=seed, as_dict=False)
        assert 4 <= len(model.short_password.get_secret_value()) <= 6
        assert len(model.small_blob) == 3
        assert isinstance(model.size, int)
        model.model_dump_json()


@pytest.mark.datatypes
@pytest.mark.datetime
@pytest.mark.pyfake
class TestRelativeAndAwareDatetimes:
    @pytest.mark.parametrize("seed", SEEDS)
    def test_model_is_valid(self, seed):
        model = fake(TimeModel, seed=seed, as_dict=False)
        now = datetime.now(timezone.utc)
        assert model.born < date.today()
        assert model.expires > date.today()
        assert model.last_login < now
        assert model.next_run > now
        assert model.aware.tzinfo is not None
        assert model.naive.tzinfo is None
        assert date(2020, 1, 1) <= model.since_2020 < date.today()
        assert timedelta(minutes=1) <= model.short_duration < timedelta(minutes=5)

    def test_aware_datetime_with_timezone(self):
        from zoneinfo import ZoneInfo

        tz = ZoneInfo("Asia/Tokyo")

        class M(BaseModel):
            ts: Annotated[
                pydantic.AwareDatetime, Field(json_schema_extra={"timezone": tz})
            ]

        assert fake(M, seed=1)["ts"].tzinfo is tz

    def test_seeded_output_is_reproducible(self):
        assert fake(TimeModel, seed=5) == fake(TimeModel, seed=5)


@pytest.mark.pyfake
@pytest.mark.complex
class TestAbstractContainers:
    @pytest.mark.parametrize("seed", SEEDS)
    def test_model_is_valid(self, seed):
        model = fake(ContainerModel, seed=seed, as_dict=False)
        assert isinstance(model.frozen, frozenset)
        assert isinstance(model.queue, deque)
        assert isinstance(model.counter, Counter)
        assert model.nothing is None
        model.model_dump_json()

    def test_frozenset_of_literals_stays_within_values(self):
        for seed in range(20):
            assert fake(ContainerModel, seed=seed, as_dict=False).frozen <= {
                "a",
                "b",
                "c",
            }

    def test_fixed_tuple_of_special_types(self):
        class M(BaseModel):
            pair: tuple[pydantic.EmailStr, ipaddress.IPv4Address]

        result = Pyfake(M, seed=2).generate(as_dict=False)
        assert isinstance(result.pair[1], ipaddress.IPv4Address)
