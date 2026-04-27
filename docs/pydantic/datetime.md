---
icon: octicons/calendar-16
tags:
  - Usage
  - Examples
  - Datetime
hide:
  - title
---

# Datetime in `pyfake`

## Simple usage
`pyfake` generates Python `datetime.date`, `datetime.datetime` and `datetime.time` objects
for fields annotated with those types. By default it inspects the model and emits
appropriate values using the package RNG.

```python
from pyfake import fake
from pydantic import BaseModel
from datetime import datetime

class Event(BaseModel):
    when: datetime

result = fake(Event)
print(result)
```
<!-- termynal -->

```console
{'when': datetime.datetime(2026, 4, 7, 12, 34, 56)}
```

Values will vary on each run; the important detail is the *type* returned is a
`datetime.datetime` object (the registry maps `datetime` → `date-time` generator).

## Date / Time variants
The registry dispatches based on the Python annotation:

- `datetime.datetime` → `pyfake.generators.datetime.generate_datetime` (returns `datetime.datetime`)
- `datetime.date` → `pyfake.generators.datetime.generate_date` (returns `datetime.date`)
- `datetime.time` → `pyfake.generators.datetime.generate_time` (returns `datetime.time`)

Example:

```python
from datetime import date, time, datetime
from pydantic import BaseModel

class Mixed(BaseModel):
    d: date
    t: time
    dt: datetime

result = fake(Mixed)
print(result)
```
<!-- termynal -->

```console
{
  'd': datetime.date(2026, 10, 4),
  't': datetime.time(14, 23, 5),
  'dt': datetime.datetime(2026, 10, 4, 14, 23, 5)
}
```

## Returning multiple values
Use `num` to generate multiple instances:

```python
results = fake(Event, num=3)
print(results)
```
<!-- termynal -->

```console
[
  {'when': datetime.datetime(2026, 4, 7, 12, 34, 56)},
  {'when': datetime.datetime(2025, 9, 1, 8, 0, 12)},
  {'when': datetime.datetime(1970, 7, 3, 3, 14, 15)}
]
```

## Receiving Pydantic model instances
By default `fake(...)` returns dictionaries. Request model instances with `as_dict=False`:

```python
results = fake(Event, num=2, as_dict=False)
print(results)
```
<!-- termynal -->

```console
[
  Event(when=datetime.datetime(2026, 4, 7, 12, 34, 56)),
  Event(when=datetime.datetime(2025, 1, 1, 0, 0, 1)),
]
```

## Nullable / Optional fields
If a field is a union that includes `None` (e.g. `Optional[datetime]` or `datetime | None`),
the registry marks the union as nullable. In the current implementation the resolver
returns `None` roughly 20% of the time for nullable variants; otherwise it generates a
datetime/date/time as usual.

```python
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Maybe(BaseModel):
    when: Optional[datetime]

results = fake(Maybe, num=5)
print(results)
```
<!-- termynal -->

```console
[
  {'when': datetime.datetime(2026, 4, 7, 12, 34, 56)},
  {'when': None},
  {'when': datetime.datetime(2022, 1, 2, 3, 4, 5)},
  {'when': datetime.datetime(2010, 6, 7, 8, 9, 10)},
  {'when': None}
]
```

## Default values
If a non-`None` default is provided on the field, the registry will return that value
instead of generating a random one.

```python
from pydantic import Field
from datetime import datetime

class Meeting(BaseModel):
    when: datetime = Field(default=datetime(2022, 1, 1, 9, 0))

result = fake(Meeting)
print(result)
```
<!-- termynal -->

```console
{'when': datetime.datetime(2022, 1, 1, 9, 0)}
```

## Bounds, formats and generator args
The datetime generators accept the usual bound arguments: `lt`, `gt`, `le`, `ge`.
The `Resolver` collects generator arguments from field metadata and annotated types
and attaches them to the resolved schema; the `GeneratorRegistry` then forwards
those arguments into the generator functions.

- Bounds (`gt`, `ge`, `lt`, `le`) are forwarded to `generate_date`, `generate_datetime`, and `generate_time`.
- You can request a specific generator format name (`date`, `date-time`, `time`) via
  field JSON schema extras (the resolver reads `Field(..., json_schema_extra={"format": "date"})`),
  or by using annotated metadata that the resolver understands (e.g. `annotated_types.Ge`).

Examples:

```python
from datetime import datetime, date
from pydantic import Field
from annotated_types import Ge, Le
from typing import Annotated

class Bounded(BaseModel):
    # annotated bounds (resolver recognizes annotated_types.Ge/Le)
    when: Annotated[datetime, Ge(datetime(2020, 1, 1)), Le(datetime(2030, 1, 1))]

class DateOnly(BaseModel):
    # request the date generator explicitly via json_schema_extra
    day: date = Field(json_schema_extra={"format": "date"})

print(fake(Bounded))
print(fake(DateOnly))
```
<!-- termynal -->

```console
{'when': datetime.datetime(2024, 5, 20, 8, 13, 45)}
{'day': datetime.date(2026, 10, 4)}
```

Implementation detail: when the resolved `GeneratorArgs` includes a `format` that matches
a generator key (for example `date`, `date-time`, `time`) the registry will choose that
generator and pass the other generator args (`gt`, `lt`, `ge`, `le`, etc.) into it.

## JSON output
If you need JSON strings rather than Python objects use `fake.json(...)`. That helper
serializes the generated output with `json.dumps(..., default=str)`, so dates and
datetimes are turned into their `str()` representations (e.g. `"2026-04-07 12:34:56"`).

## Timezone-aware datetimes

Pass any [`datetime.tzinfo`](https://docs.python.org/3/library/datetime.html#datetime.tzinfo)
subclass — including `datetime.timezone` constants and `zoneinfo.ZoneInfo` instances —
through `json_schema_extra={"timezone": ...}` on a `datetime` field.

```python
from pyfake import fake
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated
from zoneinfo import ZoneInfo

class Event(BaseModel):
    # stdlib UTC constant
    utc_ts: Annotated[datetime, Field(..., json_schema_extra={"timezone": timezone.utc})]
    # IANA timezone via zoneinfo
    ny_ts: Annotated[datetime, Field(..., json_schema_extra={"timezone": ZoneInfo("America/New_York")})]

result = fake(Event)
print(result)
```
<!-- termynal -->

```console
{
  'utc_ts': datetime.datetime(2024, 3, 15, 9, 42, 17, tzinfo=datetime.timezone.utc),
  'ny_ts': datetime.datetime(2019, 11, 7, 22, 5, 33, tzinfo=zoneinfo.ZoneInfo(key='America/New_York'))
}
```

The timezone is stamped onto the generated datetime via `replace(tzinfo=timezone)` *after*
the random value is produced, so bounds (`ge`, `gt`, `le`, `lt`) are still expressed as
naive datetimes:

```python
from datetime import datetime
from pydantic import Field
from typing import Annotated
from zoneinfo import ZoneInfo

class Bounded(BaseModel):
    ts: Annotated[
        datetime,
        Field(
            ge=datetime(2020, 1, 1),
            le=datetime(2020, 12, 31, 23, 59, 59),
            json_schema_extra={"timezone": ZoneInfo("UTC")},
        ),
    ]

result = fake(Bounded)
print(result)
```
<!-- termynal -->

```console
{'ts': datetime.datetime(2020, 8, 22, 14, 37, 55, tzinfo=zoneinfo.ZoneInfo(key='UTC'))}
```

Omitting `timezone` (or annotating a field without `json_schema_extra`) always returns
a naive `datetime`, preserving backward-compatible behaviour.

!!! note "date and time fields"
    Timezone is only meaningful for `datetime` fields.  If you accidentally pass
    `timezone` on a `date` or `time` field the generator silently absorbs the argument
    via `**kwargs` and continues to return a naive value — no error is raised.

## JSON output
If you need JSON strings rather than Python objects use `fake.json(...)`. That helper
serializes the generated output with `json.dumps(..., default=str)`, so dates and
datetimes (including timezone-aware ones) are turned into their `str()` representations
(e.g. `"2026-04-07 12:34:56+00:00"`).

## Implementation notes
- Generator functions: `pyfake.generators.datetime.generate_date`,
  `generate_datetime`, `generate_time`.
- Registry type mapping: `datetime.datetime` → `date-time`; `datetime.date` → `date`; `datetime.time` → `time`.
- Nullable unions are handled by the resolver/registry: `None` is selected roughly 20% of the time for
  nullable variants.
- Generators return native Python objects (not ISO strings) — use `fake.json()` to get
  a string-serialized form.
- `generate_datetime` accepts a `timezone` keyword argument (any `datetime.tzinfo` subclass).
  The resolver extracts it from `Field(json_schema_extra={"timezone": ...})` and the
  registry forwards it through `GeneratorArgs.timezone`.

## Unsupported / Partial support
- Locale-aware generation: there is no built-in locale or format-string based datetime generation.

