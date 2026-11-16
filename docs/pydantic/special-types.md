---
icon: lucide/shapes
tags:
  - Usage
  - Examples
  - Emails
  - URLs
  - IP addresses
hide:
  - title
---

# Other types in `pyfake`

Besides numbers, strings, dates and containers, `pyfake` generates valid values for pydantic's special types and for most of the standard library types pydantic accepts.

```python
import ipaddress
from typing import Sequence

from pydantic import BaseModel, EmailStr, HttpUrl, PostgresDsn, SecretStr
from pyfake import fake


class Account(BaseModel):
    email: EmailStr
    homepage: HttpUrl
    database: PostgresDsn
    last_ip: ipaddress.IPv4Address
    password: SecretStr
    scores: Sequence[int]


print(fake(Account, as_dict=False, seed=5))
```

<!-- termynal -->

```console
email='ixlzwxu.aoyhubf15@example.org' homepage=HttpUrl('https://mrds.example.com/xgn') database=PostgresDsn('postgresql+psycopg://toeeaag:ffjk@ymfy.example.com:10118/rvug') last_ip=IPv4Address('46.129.214.109') password=SecretStr('**********') scores=[38, 77, 75]
```

---

## Emails

| Type | Example value |
| --- | --- |
| `EmailStr` | `'ccl.xzvj33@example.net'` |
| `NameEmail` | `NameEmail(name='Tbsv Numz', email='tbsv.numz@example.net')` |

Emails use the `example.com`, `example.org` and `example.net` domains, which [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606) reserves for examples. A generated address never reaches a real mailbox.

## URLs and DSNs

Every pydantic URL type is supported: `AnyUrl`, `AnyHttpUrl`, `HttpUrl`, `FileUrl`, `FtpUrl`, `WebsocketUrl`, `AnyWebsocketUrl`, and the DSN types (`PostgresDsn`, `CockroachDsn`, `AmqpDsn`, `RedisDsn`, `MongoDsn`, `KafkaDsn`, `NatsDsn`, `MySQLDsn`, `MariaDBDsn`, `ClickHouseDsn`, `SnowflakeDsn`).

The scheme is picked from the schemes the type allows, and hosts are subdomains of the reserved `example.*` domains:

| Type | Example value |
| --- | --- |
| `HttpUrl`, `AnyUrl` | `https://ydtz.example.org/wztejdx` |
| `FileUrl` | `file:///oqibalo/mnqfr.txt` |
| `WebsocketUrl` | `ws://hafk.example.com/qqlq` |
| `RedisDsn` | `rediss://njti:wbkk@hbjacdt.example.net:3080/emmoq` |
| `PostgresDsn` | `postgresql://ptxmw:mxzsoe@ysbj.example.com:54997/dbepg` |

Database and broker schemes get DSN form, `scheme://user:password@host:port/name`.

## IP addresses

| Type | Example value |
| --- | --- |
| `ipaddress.IPv4Address` | `IPv4Address('169.179.143.32')` |
| `ipaddress.IPv6Address` | `IPv6Address('da1:9205:69eb:8cb4:8978:97da:8664:cb0')` |
| `ipaddress.IPv4Network` | `IPv4Network('207.128.0.0/9')` |
| `ipaddress.IPv6Network` | `IPv6Network('1f49:e090:3200::/39')` |
| `ipaddress.IPv4Interface` | `IPv4Interface('235.248.227.217/12')` |
| `ipaddress.IPv6Interface` | `IPv6Interface('7ccc:e344:1eb:d454:ebb6:79b4:d2d0:d097/57')` |
| `IPvAnyAddress`, `IPvAnyNetwork`, `IPvAnyInterface` | IPv4 or IPv6, picked at random |

Networks always have their host bits set to zero, as pydantic requires.

## Secrets and bytes

| Type | Generated as |
| --- | --- |
| `SecretStr` | a string, following `min_length` / `max_length` like any `str` field |
| `SecretBytes`, `bytes` | ASCII letters as bytes, following `min_length` / `max_length`. ASCII keeps the value serialisable to JSON. |
| `ByteSize` | an integer, like any `int` field |

Subclasses of supported types (for example `class Name(str)`) are generated like their base type.

## Durations and relative dates

| Type | Generated as |
| --- | --- |
| `timedelta` | a whole number of seconds, between 0 and 30 days by default. `ge` / `gt` / `le` / `lt` bounds take `timedelta` values. |
| `PastDate`, `FutureDate` | a date before / after today |
| `PastDatetime`, `FutureDatetime` | a timezone-aware (UTC) datetime before / after now |
| `AwareDatetime`, `NaiveDatetime` | a datetime with / without a timezone |

See [Datetime](datetime.md#relative-and-timezone-types) for details.

## `Any` and `object`

A field typed `Any` or `object` gets a random JSON-safe scalar: an `int`, `float`, `str` or `bool`. The same goes for the items of bare containers such as `list`, `dict` or `tuple`, and for `Dict[Any, Any]`. A field typed `None` is always `None`.

## Abstract and specialised containers

Abstract container types are generated as the concrete type pydantic accepts for them, using the same length rules as [lists](lists.md#how-length-is-chosen):

| Annotation | Generated as |
| --- | --- |
| `Sequence[T]`, `MutableSequence[T]`, `Iterable[T]`, `deque[T]` | a list |
| `AbstractSet[T]`, `MutableSet[T]` | a set |
| `FrozenSet[T]` | a frozenset |
| `Mapping[K, V]`, `MutableMapping[K, V]`, `OrderedDict[K, V]`, `DefaultDict[K, V]` | a dict |
| `Counter[K]` | a dict from `K` to `int` |
| bare `list`, `set`, `frozenset`, `tuple`, `dict` | the same container, with `Any` items |

## Constrained types

`conint`, `confloat`, `condecimal`, `constr`, `conlist`, `conset`, `StringConstraints`, `annotated_types.Interval` and bare `annotated_types` constraints work the same as the equivalent `Field(...)` arguments, including inside containers:

```python
from typing import Annotated, List

from annotated_types import Gt, Interval
from pydantic import BaseModel, StringConstraints, conint, constr
from pyfake import fake


class Order(BaseModel):
    quantity: conint(gt=0, lt=10)
    code: constr(pattern=r"^[A-Z]{3}-\d{4}$")
    country: Annotated[str, StringConstraints(min_length=2, max_length=2, to_upper=True)]
    priority: Annotated[int, Interval(ge=1, le=3)]
    discount: Annotated[float, Gt(0)]
    sizes: List[conint(ge=36, le=46)]


print(fake(Order, seed=1))
```

## Picking a generator with `format`

`Field(json_schema_extra={"format": ...})` picks a generator by its JSON Schema format name. This is how you get an email or a URL in a plain `str` field:

```python
from pydantic import BaseModel, Field
from pyfake import fake


class Contact(BaseModel):
    email: str = Field(json_schema_extra={"format": "email"})
    website: str = Field(json_schema_extra={"format": "uri"})
```

The available names are listed in the [format table](../dev/internals.md#type-and-format-map).

## Unsupported types

If `pyfake` has no generator for a field's type, it raises `GeneratorNotFound` and names the field, instead of returning a value that fails validation:

```python
import pathlib

from pydantic import BaseModel
from pyfake import fake


class Upload(BaseModel):
    location: pathlib.Path


fake(Upload)
# pyfake.exceptions.GeneratorNotFound: No generator registered for type <class 'pathlib.Path'>
# (field 'Upload.location'). Use a supported type or give the field a default value.
```

Giving the field a default works around it, because fields with a non-`None` default are never generated.

Not supported yet: `Path` and its pydantic variants (`FilePath`, `DirectoryPath`, ...), `TypedDict`, dataclasses and `NamedTuple` used as field types (these raise `GeneratorNotFound`), and `Json[T]` and the types from `pydantic-extra-types` (these may fail pydantic validation).
