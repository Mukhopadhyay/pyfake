---
icon: lucide/braces
tags:
  - Usage
  - Examples
  - Sets
  - Complex
hide:
  - title
---

# Sets in `pyfake`

## Simple usage
`pyfake` can generate values for set fields declared with `typing.Set[...]` or the built-in `set[...]` generic.

```python
from typing import Set
from pyfake import fake
from pydantic import BaseModel

class Collection(BaseModel):
  tags: Set[str]

result = fake(Collection)
print(result)
```

<!-- termynal -->

```console
{'tags': {'aBcDeFgHiJ', 'XyZaBcDeFg'}}
```

`model_dump()` keeps sets as Python `set`s, so the dicts `pyfake` returns contain sets. `fake.json(...)` serialises them as lists.

!!! note "Set semantics"

    Sets are unordered and hold distinct values. `pyfake` keeps generating items until it has enough distinct ones, so a set always reaches its `min_length`.

---

## Returning Multiple Values

Generate several examples with `num` as usual:

```python
from pyfake import fake
from pydantic import BaseModel
from typing import Set

class S(BaseModel):
  items: Set[int]

print(fake(S, num=3))
```

<!-- termynal -->

```console
[
  {'items': {72, 97}},
  {'items': {32}},
  {'items': {4, 5, 6}}
]
```

## Receiving model instances

To receive Pydantic model instances (where `set` objects are preserved), set `as_dict=False`:

```python
from pyfake import fake
from pydantic import BaseModel
from typing import Set

class M(BaseModel):
  s: Set[str]

instances = fake(M, as_dict=False, num=2)
print(instances)
```

<!-- termynal -->

```console
[M(s={'a', 'b'}), M(s={'c'})]
```

## Metadata & Constraints

`pyfake` honors `min_length` and `max_length` for container sizes. For sets they bound the number of distinct items.

### How length is chosen

- **Default:** when no bounds are provided, the length is chosen randomly between `1` and `5` (inclusive).
- **Both `min_length` and `max_length`:** a random length is chosen uniformly between the two bounds (inclusive).
- **Only `min_length` provided:** the length is chosen between `min_length` and `5`. When `min_length` is above `5`, it is chosen between `min_length` and `min_length + 4`.
- **Only `max_length` provided:** the length is chosen between `1` and `max_length`.
- **`min_length=0`** allows an empty collection, and `max_length=0` always gives one.

When the item type has only a few possible values (`bool`, a `Literal`, an `Enum`, or a union of them), the length is capped at that number. If even `min_length` is more than the number of possible values (e.g. `Set[bool]` with `min_length=3`), `pyfake` raises `InvalidConstraints`. It also raises `InvalidConstraints` when it can't find enough distinct values after a number of attempts, e.g. `Set[Annotated[int, Field(ge=1, le=2)]]` with `min_length=3`.

### Using `Field` / `Annotated` constraints

Attach constraints via `Annotated[..., Field(...)]` or `Field(...)` directly on the attribute.

```python
from typing import Annotated, Set
from pydantic import BaseModel, Field
from pyfake import fake

class BoundedSet(BaseModel):
  nums: Annotated[Set[int], Field(min_length=2, max_length=4)]

print(fake(BoundedSet, seed=42))
```

<!-- termynal -->

```console
 # between 2 and 4 distinct items
{'nums': {3, 7, 81}}
```

### Supported Field options
| Option | Description |
| ---------------- | -------------------------------------------------------------- |
| `min_length`     | Minimum number of distinct items.                               |
| `max_length`     | Maximum number of distinct items.                               |

!!! error "Unsupported / Partial Support"

    - There is no explicit `length` override for sets; use `min_length`/`max_length` instead.

---

## Several element types & unions

Sets can contain union types like `Set[int | str]`. Each generated candidate element is produced by selecting a variant. Because sets require hashable elements, prefer primitives (`int`, `str`, `tuple`, etc.).

```python
from typing import Set
from pydantic import BaseModel
from pyfake import fake

class Mixed(BaseModel):
  items: Set[int | str]

print(fake(Mixed, seed=0))
```

<!-- termynal -->

```console
{'items': {123, 'AbcDef'}}
```

## Nullable sets

If the field is optional (`Optional[Set[T]]` or `Set[T] | None`) the resolver marks the field as a nullable union. The registry will return `None` for nullable unions when its RNG condition triggers (the current implementation uses a ~20% chance). Otherwise it generates a set as usual.

```python
from typing import Optional, Set
from pydantic import BaseModel
from pyfake import fake

class MaybeSet(BaseModel):
  vals: Optional[Set[int]]

print(fake(MaybeSet, num=5, seed=1))
```

<!-- termynal -->

```console
[
  {'vals': {1, 2}},
  {'vals': None},
  {'vals': {3}},
  {'vals': None},
  {'vals': {4}}
]
```

## Annotated inner types (UUID example)

Inner-type `Annotated` metadata is propagated to element generation, just like lists. For example `Set[Annotated[UUID, UuidVersion(1)]]` generates version 1 UUIDs.

```python
from typing import Annotated, Set
from uuid import UUID
from pydantic.types import UuidVersion
from pydantic import BaseModel
from pyfake import fake

class USet(BaseModel):
  ids: Set[Annotated[UUID, UuidVersion(1)]]

print(fake(USet, seed=0))
```

<!-- termynal -->

```console
{'ids': {UUID('6bca4a77-d371-11f1-9092-83e2f728b4fa')}}
```

## Registry direct generation

The `GeneratorRegistry` can be invoked directly with a `set` schema (see tests). Example:

```python
from pyfake.core.context import Context
from pyfake.core.registry import GeneratorRegistry
from pyfake.schemas import GeneratorArgs

context = Context(seed=0)
registry = GeneratorRegistry(context=context)
schema = {
  'type': set,
  'items': {'type': int, 'generator_args': GeneratorArgs()},
  'generator_args': GeneratorArgs(),
}

result = registry._generate(schema)
assert isinstance(result, set)
```

This mirrors the behaviour asserted in `tests/core/test_pyfake_complex.py`.

## Implementation notes

- Sets use the same length rules as lists.
- Items are generated until there are enough distinct values, with a limited number of attempts.
- `FrozenSet[T]`, `AbstractSet[T]` and `MutableSet[T]` are generated the same way.
- Elements must be hashable — generating sets of unhashable inner types (e.g. `list`) raises `TypeError`.
- Format-based dispatch and inner-type metadata (UUID versions, numeric bounds, patterns) are handled by the resolver and applied to the element schema.

## Unsupported / Partial support

- Sets of pydantic models need a frozen model (`model_config = ConfigDict(frozen=True)`), because other models aren't hashable.


