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

Note: Pydantic's serialization (`model_dump()`) may convert `Set` to a `list` when `pyfake` returns dicts, so tests accept either representation.

!!! note "Set semantics"

    Sets are unordered and deduplicate values — the final number of elements may be smaller than the requested/generated length.

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
  {'items': [1, 2]},
  {'items': [3]},
  {'items': [4, 5, 6]}
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

`pyfake` honors `min_length` and `max_length` for container sizes. For sets these parameters control how many items are generated before deduplication.

### How length is chosen

- **Default:** when no bounds are provided, the generator chooses a length uniformly at random between `1` and `5` (inclusive).
- **Both `min_length` and `max_length`:** the length is chosen uniformly between the two bounds.
- **Only `min_length` provided:** the length is chosen between `min_length` and the default upper bound `5`.
- **Only `max_length` provided:** the length is chosen between the default lower bound `1` and `max_length`.

These rules match the registry implementation: `rng.randint(args.min_length or 1, args.max_length or 5)`.

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
 # generator asked for 2..4 items before deduplication
{'nums': {3, 7}}
```

### Supported Field options
| Option | Description |
| ---------------- | -------------------------------------------------------------- |
| `min_length`     | Minimum number of items to generate (before deduplication).     |
| `max_length`     | Maximum number of items to generate (before deduplication).     |

!!! error "Unsupported / Partial Support"

  - There is no explicit `length` override for sets; use `min_length`/`max_length` instead.
  - The default string generator does not guarantee arbitrary regex matches for string elements. Use a custom generator for strict regex-based elements.

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

Inner-type `Annotated` metadata is propagated to element generation, just like lists. For example `Set[Annotated[UUID, UuidVersion(1)]]` will request UUID v1 strings for elements when resolved.

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
{'ids': {'a1b2c3d4-0000-1000-8000-000000000001'}}
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

- Sets use the same length selection mechanism as lists: `rng.randint(args.min_length or 1, args.max_length or 5)`.
- Items are generated first into a list, then converted to `set(items)`, which removes duplicates and may reduce the final size.
- Elements must be hashable for `set(...)` to succeed — generating sets of unhashable inner types (e.g. `list`) can raise `TypeError`.
- Format-based dispatch and inner-type metadata (UUID versions, numeric bounds, patterns) are handled by the resolver and applied to the element schema.

## Unsupported / Partial support

- The built-in string generator does not guarantee arbitrary regex matches for set elements. Use a custom generator if you need guaranteed pattern matches.
- Deduplication means you cannot rely on a fixed final size when using `set[...]` — generate more items or post-process if you need to guarantee size.


