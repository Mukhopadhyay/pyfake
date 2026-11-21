---
icon: lucide/puzzle
tags:
  - Usage
  - Examples
  - Custom generators
  - Extending
hide:
  - title
---

# Custom generators

When `pyfake` has no generator for a type, or you want different values for a type it already supports, register your own generator.

```python
import pathlib

from pydantic import BaseModel
from pyfake import fake


class Upload(BaseModel):
    location: pathlib.Path


def path_generator(ctx, **constraints):
    return pathlib.Path(f"/tmp/upload-{ctx.random.randint(0, 999)}")


fake.register(pathlib.Path, path_generator)

print(fake(Upload))
```

```console
{'location': PosixPath('/tmp/upload-394')}
```

The generator is used wherever the type appears, including inside `Optional[...]`, unions, `list[...]`, dicts, tuples and nested models. The generated model is still validated by pydantic, so a generator that returns an invalid value raises a `ValidationError`.

## The generator signature

A generator is called as `fn(ctx, **constraints)`.

`ctx` is a `pyfake.GeneratorContext` with:

| Attribute | Description |
| --- | --- |
| `ctx.random` | The seeded `random.Random` stream. Draw every random value from it so seeded output stays reproducible. |
| `ctx.now` | The reference point for values relative to "now". |
| `ctx.path` | The path of the field being generated, e.g. `"Upload.location"` or `"Upload.backups[]"` for list items. |
| `ctx.type` | The type the generator was registered for. |

`constraints` holds only the constraints that are set on the field. The possible keys are `gt`, `ge`, `lt`, `le`, `multiple_of`, `decimal_places`, `max_digits`, `min_length`, `max_length`, `pattern` and `timezone`. An unconstrained field gets no constraints, so accept `**constraints` if the type might ever be used with constraints:

```python
from typing import Annotated

from pydantic import BaseModel, Field
from pyfake import Fake, GeneratorContext


def even_int(ctx: GeneratorContext, **constraints) -> int:
    low = constraints.get("ge", 0)
    high = constraints.get("le", 100)
    return ctx.random.randrange(low + low % 2, high + 1, 2)


class Order(BaseModel):
    quantity: Annotated[int, Field(ge=10, le=20)]


f = Fake()
f.register(int, even_int)
print(f(Order))  # even_int receives ge=10, le=20
```

```console
{'quantity': 14}
```

## Instance vs module-level registration

There are two ways to register a generator:

- `Fake().register(type, fn)` (and `fake.register(type, fn)` on the default instance) registers it for that instance only. Other `Fake` instances are not affected, so tests that each create their own `Fake` don't leak registrations into each other.
- `pyfake.register(type, fn)` registers it for every `Fake` instance, and for `Pyfake`.

```python
import pathlib

import pyfake
from pyfake import Fake

pyfake.register(pathlib.Path, path_generator)  # every instance

f = Fake()
# this instance only, wins over the global one
f.register(pathlib.Path, lambda ctx, **constraints: pathlib.Path("/srv/data"))
```

`fake.seed(n)` returns a new `Fake` that starts with a copy of the instance's registered generators. Generators registered on either one afterwards don't affect the other.

## Overriding built-in generators

Registering a type that `pyfake` already supports replaces the built-in generator for it. Registering the same type again replaces the previous generator, so the most recent registration wins. When a type is registered in more than one place, the order of precedence is:

1. the `Fake` instance's registration,
2. the module-level registration (`pyfake.register`),
3. the built-in generator.

```python
from pydantic import BaseModel
from pyfake import Fake


class Feature(BaseModel):
    enabled: bool


def mostly_true(ctx, **constraints):
    return ctx.random.random() < 0.7


f = Fake()
f.register(bool, mostly_true)
print(f(Feature, num=3))
```

```console
[{'enabled': True}, {'enabled': True}, {'enabled': False}]
```

A few rules decide which fields a registration applies to:

- **Exact type only.** A registration matches the field's type exactly, not its subclasses. Registering `int` doesn't change `bool` fields (`bool` is a subclass of `int`), or pydantic's `ByteSize`.
- **Leaf types only.** Registrations apply to value types such as `str`, `int`, `UUID` or your own classes. Containers (`list`, `dict`, ...), nested models, enums and `Literal`s are generated as usual, and their items use any registered generators.
- **Annotated types match their base type.** `UUID4` is `Annotated[UUID, ...]`, so registering `uuid.UUID` also covers `UUID4` fields, and a registered `str` generator also covers `str` fields that use `json_schema_extra={"format": ...}`. Registering an `Annotated` alias itself has no effect.
- **Defaults still win.** A field with a non-`None` default always gets its default.

## Seeding

Generators that draw from `ctx.random` follow the same seeding rules as the built-in ones:

```python
from pyfake import Fake

a, b = Fake(seed=1), Fake(seed=1)
a.register(pathlib.Path, path_generator)
b.register(pathlib.Path, path_generator)

assert a(Upload, num=5) == b(Upload, num=5)
```

Using the global `random` module, or any other source of randomness, makes seeded output change between runs.

## Errors

`register` raises `TypeError` if the generator isn't callable or the type isn't hashable.
