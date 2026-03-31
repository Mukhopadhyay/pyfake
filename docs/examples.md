---
icon: lucide/book-open
tags:
  - Usage
  - Examples
hide:
  - title
---

# Usage & Examples

Everything `pyfake` can do, shown in working code — from a three-line hello-world to a fully-constrained real-world schema.

<!-- termynal -->
```shell
$ pip install pyfake
---> 100%
Successfully installed pyfake
```

## Your First Fake

Define a Pydantic model and hand it to `Pyfake.from_schema`. That's really all there is to it:

```python
from pydantic import BaseModel
from pyfake import Pyfake


class User(BaseModel):
    id: int
    username: str
    is_active: bool


result = Pyfake.from_schema(User)
print(result)
# {'id': 47, 'username': 'xKLmPqRstU', 'is_active': True}
```

<!-- termynal -->

```console
$ python
>>> from pydantic import BaseModel
>>> from pyfake import Pyfake
>>> class User(BaseModel):
...     id: int
...     username: str
...     is_active: bool
...
>>> Pyfake.from_schema(User)
{'id': 47, 'username': 'xKLmPqRstU', 'is_active': True}
```

No setup, no fixtures, no config files. `pyfake` reads `User.model_fields`, figures out what type each field wants, and generates valid values.

---

## Two Ways to Use `pyfake`

### The quick way — `from_schema`

```python
result = Pyfake.from_schema(User)
```

`from_schema` is a class-method shortcut. It creates a `Pyfake` instance, calls `generate`, and returns the result in one line. Perfect for one-offs.

### The instance way

```python
fake = Pyfake(User)

first_batch  = fake.generate(num=5)
second_batch = fake.generate(num=5)  # fresh values, same stream
```

The instance keeps the internal random stream alive between calls. Creating a `Pyfake` once and calling `generate` repeatedly gives you a consistent, continuous sequence — useful when you need to produce data in batches without reinitialising.

---

## Generating Multiple Records

Pass `num` to get a list instead of a single dict:

```python
results = Pyfake.from_schema(User, num=3)
# [
#   {'id': 83, 'username': 'fGhJkLmNpQ', 'is_active': False},
#   {'id': 12, 'username': 'WxYzAbCdEf', 'is_active': True},
#   {'id': 65, 'username': 'RsTuVwXyZa', 'is_active': True},
# ]
```

`num=1` (the default) returns a single dict. Anything larger returns a list. `num=None` is treated as `num=1`.

---

## Getting Model Instances Back

By default `pyfake` returns plain `dict`s via `.model_dump()`. Set `as_dict=False` to get the actual Pydantic model instances:

```python
user = Pyfake.from_schema(User, as_dict=False)

print(type(user))        # <class '__main__.User'>
print(user.is_active)    # True
print(user.model_dump()) # {'id': 47, 'username': 'xKLmPqRstU', 'is_active': True}
```

Every generated value still passes Pydantic's own validation — if it didn't, you'd get a `ValidationError` before it ever reached you.

---

## Reproducible Data with Seeds

Need the same data every run? Pass a `seed`:

```python
a = Pyfake.from_schema(User, seed=42)
b = Pyfake.from_schema(User, seed=42)

assert a == b  # always True, always
```

<!-- termynal -->

```
$ python
>>> from pyfake import Pyfake
>>> a = Pyfake.from_schema(User, seed=42)
>>> b = Pyfake.from_schema(User, seed=42)
>>> a == b
True
>>> a == Pyfake.from_schema(User, seed=99)
False
```

Seeds are invaluable for tests — pin a seed once and your test data never drifts between runs or environments.

!!! tip
    All randomness in `pyfake` flows through a single `random.Random` instance stored in a `Context`. Seeding it makes every generator call downstream deterministic, including nested models, collections, and unions.

---

## Numeric Constraints

`pyfake` respects `ge`, `le`, `gt`, and `lt` from Pydantic's [`Field()`](https://docs.pydantic.dev/latest/api/fields/):

```python
from typing import Annotated
from pydantic import BaseModel, Field
from pyfake import Pyfake


class Product(BaseModel):
    price:        Annotated[float, Field(ge=0.01, le=999.99)]
    stock:        Annotated[int,   Field(ge=0,    le=1000)]
    discount_pct: Annotated[float, Field(gt=0.0,  lt=50.0)]


result = Pyfake.from_schema(Product)
# {'price': 312.74, 'stock': 487, 'discount_pct': 23.61}
```

| Constraint | Meaning          |
| ---------- | ---------------- |
| `ge`       | greater or equal |
| `le`       | less or equal    |
| `gt`       | strictly greater |
| `lt`       | strictly less    |

---

## String Constraints

Control generated string length with `min_length` and `max_length`:

```python
from typing import Annotated
from pydantic import BaseModel, Field
from pyfake import Pyfake


class Profile(BaseModel):
    handle: Annotated[str, Field(min_length=3,  max_length=20)]
    bio:    Annotated[str, Field(max_length=160)]
    pin:    Annotated[str, Field(min_length=4,  max_length=4)]


result = Pyfake.from_schema(Profile)
# {'handle': 'kBvMxR', 'bio': 'gHjKlMnPqRsTuVwXyZ', 'pin': 'QrSt'}
```

Without any length constraints, strings default to 10 random ASCII letters.

---

## Optional / Nullable Fields

`Optional[T]` — which is just `Union[T, None]` — works exactly as you'd expect:

```python
from typing import Optional
from pydantic import BaseModel
from pyfake import Pyfake


class Event(BaseModel):
    title:        str
    description:  Optional[str]
    cancelled_at: Optional[str]


results = Pyfake.from_schema(Event, num=3)
# [
#   {'title': 'xKLmPqRstU', 'description': 'fGhJkLmNpQ', 'cancelled_at': None},
#   {'title': 'WxYzAbCdEf', 'description': None,          'cancelled_at': None},
#   {'title': 'RsTuVwXyZa', 'description': 'bCdEfGhJkL', 'cancelled_at': 'mNoPqRsTuV'},
# ]
```

Nullable fields have roughly a **20% chance** of being `None` per generation — run enough samples and you'll see a healthy mix of real values and nulls.

---

## Union Types

`Union[A, B]` picks a variant at random on each generation:

```python
from typing import Union, Annotated
from pydantic import BaseModel, Field
from pyfake import Pyfake


class Measurement(BaseModel):
    value: Union[
        Annotated[int,   Field(ge=0,   le=100)],
        Annotated[float, Field(ge=0.0, le=1.0)],
    ]


# One run might give {'value': 73},    next run {'value': 0.42}
```

Each variant is equally likely. Constraints defined per-variant are respected independently — the `int` variant won't accidentally produce a float, and vice versa.

---

## Literal Fields

When only a fixed set of values is valid, `Literal` has you covered:

```python
from typing import Literal
from pydantic import BaseModel
from pyfake import Pyfake


class Order(BaseModel):
    status:   Literal["pending", "processing", "shipped", "delivered", "cancelled"]
    priority: Literal[1, 2, 3]


result = Pyfake.from_schema(Order)
# {'status': 'shipped', 'priority': 2}
```

`pyfake` picks one of the declared values at random — you'll never get a value that isn't in the list.

---

## Enums

Python `Enum` classes work the same way — a random member is chosen:

```python
from enum import Enum
from pydantic import BaseModel
from pyfake import Pyfake


class Role(str, Enum):
    ADMIN  = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Member(BaseModel):
    name: str
    role: Role


member = Pyfake.from_schema(Member, as_dict=False)
print(member.role)        # Role.EDITOR
print(member.role.value)  # 'editor'
```

---

## Collections

### Lists and Sets

```python
from typing import Annotated, List, Set
from pydantic import BaseModel, Field
from pyfake import Pyfake


class Playlist(BaseModel):
    track_ids:      List[int]
    tags:           Annotated[List[str], Field(min_length=2, max_length=5)]
    unique_ratings: Set[int]


result = Pyfake.from_schema(Playlist)
# {
#   'track_ids':      [34, 91, 7, 55, 12],
#   'tags':           ['aXbYc', 'mNoPq', 'rStUv'],
#   'unique_ratings': {3, 88, 12},
# }
```

Without length constraints, `pyfake` picks a length between **1 and 5** for any collection.

### Dictionaries

```python
from typing import Annotated, Dict
from pydantic import BaseModel, Field
from pyfake import Pyfake


class Config(BaseModel):
    settings: Annotated[Dict[str, int], Field(min_length=2, max_length=4)]


result = Pyfake.from_schema(Config)
# {'settings': {'kBvMxR': 42, 'gHjKlM': 7, 'nPqRsT': 91}}
```

### Tuples

Fixed-length tuples generate exactly one value per position, respecting each type independently:

```python
from typing import Tuple
from pydantic import BaseModel
from pyfake import Pyfake


class Point(BaseModel):
    coords: Tuple[float, float, float]
    label:  Tuple[str, int]


result = Pyfake.from_schema(Point)
# {'coords': (34.7, 81.2, 6.5), 'label': ('xKLmPq', 47)}
```

Variable-length tuples (`Tuple[T, ...]`) behave like lists — a random length between 1 and 5.

---

## Nested Models

`pyfake` recurses into nested Pydantic models automatically:

```python
from pydantic import BaseModel
from pyfake import Pyfake


class Address(BaseModel):
    street:   str
    city:     str
    zip_code: str


class Customer(BaseModel):
    name:    str
    age:     int
    address: Address


result = Pyfake.from_schema(Customer)
# {
#   'name': 'xKLmPqRstU',
#   'age':  47,
#   'address': {
#     'street':   'gHjKlMnPqR',
#     'city':     'sTuVwXyZaB',
#     'zip_code': 'cDeFgHjKlM',
#   }
# }
```

Nesting can go as deep as you like — `pyfake` just keeps recursing.

---

## UUID Fields

`uuid.UUID` fields generate a UUID4 by default:

```python
import uuid
from pydantic import BaseModel
from pyfake import Pyfake


class Resource(BaseModel):
    id: uuid.UUID


result = Pyfake.from_schema(Resource)
# {'id': '3f2504e0-4f89-11d3-9a0c-0305e82c3301'}
```

Need a specific UUID version? Use `json_schema_extra` on the field:

```python
import uuid
from pydantic import BaseModel, Field
from pyfake import Pyfake


class Resource(BaseModel):
    id_v1: uuid.UUID = Field(json_schema_extra={"format": "uuid1"})
    id_v4: uuid.UUID = Field(json_schema_extra={"format": "uuid4"})
    id_v7: uuid.UUID = Field(json_schema_extra={"format": "uuid7"})
```

Supported UUID formats: `uuid1`, `uuid3`, `uuid4`, `uuid5`, `uuid6`, `uuid7`, `uuid8`.

---

## Date & Time

```python
from datetime import date, datetime, time
from pydantic import BaseModel
from pyfake import Pyfake


class Schedule(BaseModel):
    created_on: date
    starts_at:  datetime
    opens_at:   time


result = Pyfake.from_schema(Schedule)
# {
#   'created_on': datetime.date(2041, 7, 14),
#   'starts_at':  datetime.datetime(2067, 3, 22, 14, 37, 9),
#   'opens_at':   datetime.time(9, 15, 42),
# }
```

Dates span `1970-01-01` to `2100-12-31` by default. Tighten the window with `ge` / `le` bounds:

```python
from datetime import date
from typing import Annotated
from pydantic import BaseModel, Field
from pyfake import Pyfake


class Campaign(BaseModel):
    start_date: Annotated[date, Field(ge=date(2025, 1, 1), le=date(2025, 12, 31))]
    end_date:   Annotated[date, Field(ge=date(2026, 1, 1), le=date(2026, 12, 31))]


result = Pyfake.from_schema(Campaign)
# {'start_date': datetime.date(2025, 6, 17), 'end_date': datetime.date(2026, 4, 3)}
```

---

## Pinning Fields with Defaults

A field with a non-`None` default is never generated — `pyfake` returns the default directly and skips the generator entirely:

```python
from pydantic import BaseModel, Field
from pyfake import Pyfake


class AppConfig(BaseModel):
    version: str = "1.0.0"
    timeout: int = Field(default=30)
    debug:   bool = Field(default=False)
    name:    str                          # this one gets generated


result = Pyfake.from_schema(AppConfig)
# {'version': '1.0.0', 'timeout': 30, 'debug': False, 'name': 'xKLmPqRstU'}
```

This makes it easy to pin configuration fields you care about while letting `pyfake` handle everything else.

!!! note
    This relies on `Field(default=...)` being captured as part of the field's `FieldInfo`. A bare `= value` assignment on a model field works the same way in Pydantic — both set `FieldInfo.default`.

---

## A Real-World Example

Let's bring everything together. Here's a `UserProfile` model that uses most of what we've covered:

```python
import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field
from pyfake import Pyfake


class AccountStatus(str, Enum):
    ACTIVE    = "active"
    SUSPENDED = "suspended"
    PENDING   = "pending"


class Address(BaseModel):
    street:       Annotated[str, Field(min_length=5, max_length=80)]
    city:         Annotated[str, Field(min_length=2, max_length=50)]
    country_code: Annotated[str, Field(min_length=2, max_length=2)]


class UserProfile(BaseModel):
    id:        uuid.UUID
    username:  Annotated[str,   Field(min_length=3, max_length=30)]
    age:       Annotated[int,   Field(ge=18, le=120)]
    score:     Annotated[float, Field(ge=0.0, le=100.0)]
    status:    AccountStatus
    tags:      Annotated[List[str], Field(min_length=1, max_length=5)]
    address:   Address
    joined_at: datetime
    last_seen: Optional[datetime]


profiles = Pyfake.from_schema(UserProfile, num=2, seed=99)
```

<!-- termynal -->

```
$ python profiles.py
{'id': UUID('3f2504e0-4f89-11d3-9a0c-0305e82c3301'), 'username': 'PqRsT', 'age': 34, 'score': 67.31, 'status': <AccountStatus.ACTIVE: 'active'>, 'tags': ['aBcDe', 'fGhIj'], 'address': {'street': 'KlMnOpQrSt', 'city': 'UvWxYz', 'country_code': 'AB'}, 'joined_at': datetime.datetime(2051, 4, 12, 9, 44, 0), 'last_seen': None}
{'id': UUID('9a8b7c6d-5e4f-3a2b-1c0d-e8f7a6b5c4d3'), 'username': 'kLmNo', 'age': 72, 'score': 91.45, 'status': <AccountStatus.PENDING: 'pending'>, 'tags': ['xYzAb'], 'address': {'street': 'CdEfGhIjKl', 'city': 'MnOpQr', 'country_code': 'ST'}, 'joined_at': datetime.datetime(2078, 11, 3, 15, 2, 0), 'last_seen': datetime.datetime(2089, 6, 21, 7, 30, 0)}
```

Two fully-valid `UserProfile` dicts, every constraint respected, the nested `Address` populated, `last_seen` occasionally `None`. Swap `num` for however many you need, drop the `seed` for fresh data each run.

!!! tip
    Use `as_dict=False` here if you want typed `UserProfile` instances that support method calls, serialisation, and IDE autocomplete — the generation logic is identical, just the return type changes.
