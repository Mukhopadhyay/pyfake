---
icon: lucide/boxes
tags:
  - Internal
hide:
  - title
---

# Supported Types

A summary of the types `pyfake` can generate and the constraints each one honours. The usage pages have the details and examples.

## Integer

- `lt`, `gt`, `ge`, `le` (default range `0` to `100`)
- `multiple_of`

## Floating Point

- `lt`, `gt`, `ge`, `le` (default range `0.0` to `100.0`)
- `multiple_of`
- `decimal_places`

## Decimal

- `lt`, `gt`, `ge`, `le` (default range `0` to `100`)
- `multiple_of`
- `decimal_places` (default `2`)
- `max_digits`

## String

- `min_length: int | None`
- `max_length: int | None`
- `length: int | None` (Default: `10`, used when neither bound is set)
- `pattern: str | None`

`SecretStr` is generated like `str`; `bytes` and `SecretBytes` use the same length rules.

## Boolean

## UUID

**Supported formats**<br/>
**`format`** = `uuid1` | `uuid3` | `uuid4` | `uuid5` | `uuid6` | `uuid7` | `uuid8`

## Date, time and duration

- `date`, `datetime`, `time`, `timedelta`: `lt`, `gt`, `ge`, `le`
- `datetime`: `timezone` (via `json_schema_extra`)
- `PastDate`, `FutureDate`, `PastDatetime`, `FutureDatetime`, `AwareDatetime`, `NaiveDatetime`

## Network

- `EmailStr`, `NameEmail`
- `AnyUrl`, `HttpUrl` and the other URL types, and every DSN type
- `IPv4Address`, `IPv6Address`, `IPvAnyAddress` and the matching network and interface types

## Containers

- `list`, `set`, `frozenset`, `dict` and variable-length `tuple`: `min_length`, `max_length`
- fixed-length `tuple`
- `Sequence`, `MutableSequence`, `Iterable`, `deque`, `Mapping`, `MutableMapping`, `OrderedDict`, `DefaultDict`, `Counter`, `AbstractSet`, `MutableSet`

## Other

- `Literal`, `Enum`
- `Optional` and `Union`
- nested and self-referencing `BaseModel`s
- `Any`, `object`, `None`
- constrained types: `conint`, `confloat`, `condecimal`, `constr`, `conlist`, `conset`, `StringConstraints`, `annotated_types` constraints
