---
icon: lucide/parentheses
tags:
  - Usage
  - Examples
  - Tuples
  - Complex
hide:
  - title
---

# Tuples in `pyfake`

## Simple usage
`pyfake` supports both fixed-length and variable-length tuples declared with `typing.Tuple[...]` or the native `tuple[...]` generics.

```python
from typing import Tuple
from pyfake import fake
from pydantic import BaseModel

class TModel(BaseModel):
  variable: Tuple[int, ...]
  fixed: Tuple[int, str]

result = fake(TModel)
print(result)
```

<!-- termynal -->

```console
# pydantic may serialise tuples as lists
{'variable': [1, 2], 'fixed': [7, 'AbcDef']}
```

!!! note "Tuple serialization"

    The registry generates `tuple` objects for tuple schemas, but Pydantic's `model_dump()` (used when `pyfake` returns dicts) may represent tuples as lists. When you request model instances (`as_dict=False`) you will generally see Python `tuple` values on the model.

---

## Receiving model instances

To get Pydantic model instances (with tuple types preserved), set `as_dict=False`:

```python
from pyfake import fake
from pydantic import BaseModel
from typing import Tuple

class M(BaseModel):
  pair: Tuple[int, str]

instances = fake(M, as_dict=False, num=2)
print(instances)
```

<!-- termynal -->

```console
[M(pair=(3, 'Ab')), M(pair=(9, 'Xy'))]
```

## Metadata & Constraints

The resolver populates `GeneratorArgs` from `Field` / `Annotated` metadata. For *variable-length* tuples (`Tuple[T, ...]`) the registry uses `min_length` / `max_length` to choose the generated length (same rules as for lists and sets).

### How length is chosen (variable tuples)

- **Default:** when no bounds are provided the length is chosen randomly between `1` and `5` (inclusive).
- **Both `min_length` and `max_length`:** a random length is chosen uniformly between the bounds.
- **Only `min_length` provided:** the random length is chosen between `min_length` and the default upper bound `5`.
- **Only `max_length` provided:** the random length is chosen between the default lower bound `1` and `max_length`.

These rules match the implementation in `pyfake.core.registry.GeneratorRegistry._generate`, which uses `rng.randint(args.min_length or 1, args.max_length or 5)` for variable-length containers.

### Using `Field` / `Annotated` constraints

Attach constraints with `Annotated[T, Field(...)]` or with `Field(...)` directly on the attribute to influence tuple generation.

```python
from typing import Annotated, Tuple
from pydantic import BaseModel, Field
from pyfake import fake

class Bounded(BaseModel):
  many: Annotated[Tuple[int, ...], Field(min_length=2, max_length=4)]

print(fake(Bounded, seed=42))
```

<!-- termynal -->

```console
{'many': [4, 1, 7]}  # length will be between 2 and 4
```

### Supported Field options
| Option | Description |
| ---------------- | --------------------------------------------------------------- |
| `min_length`     | Minimum number of elements for *variable* tuples (`Tuple[T, ...`). |
| `max_length`     | Maximum number of elements for *variable* tuples.                 |

!!! error "Unsupported / Partial Support"

    - `min_length`/`max_length` do **not** affect fixed-length tuples (`Tuple[T1, T2, ...]`).
    - The default string generator does not guarantee arbitrary regex matches for string elements; `pattern` metadata is accepted by the resolver but not enforced by the built-in string generator.

---

## Fixed-length tuples (heterogeneous elements)

For fixed tuples like `Tuple[int, str]`, `pyfake` generates each element using the corresponding element type schema. There is no length selection step — the tuple length and per-position types are taken from the annotation.

```python
from typing import Tuple
from pydantic import BaseModel
from pyfake import fake

class Fixed(BaseModel):
  pair: Tuple[int, str]

print(fake(Fixed, seed=0))
```

<!-- termynal -->

```console
{'pair': [5, 'AbcDef']}  # order and types are preserved; Pydantic may display as list
```

## Tuples containing unions and optional elements

Each element in a tuple may be a union type (e.g. `Tuple[int | str, ...]`) and will be resolved per-item — variants are chosen for each generated element independently. If a union includes `None` (e.g. `Optional[...]`), the resolver marks the union as nullable and the registry may emit `None` values for that element (the registry's nullable branch fires roughly 20% of the time when present).

```python
from typing import Optional, Tuple
from pydantic import BaseModel
from pyfake import fake

class Mixed(BaseModel):
  values: Tuple[Optional[int], Optional[str]]

print(fake(Mixed, num=3, seed=1))
```

<!-- termynal -->

```console
[
  {'values': [None, 'Xy']},
  {'values': [3, None]},
  {'values': [5, 'Ab']}
]
```

## Variable-tuples generated directly by the registry

When calling the registry directly with a `tuple` schema in `mode: 'variable'`, it returns Python `tuple` objects:

```python
from pyfake.core.context import Context
from pyfake.core.registry import GeneratorRegistry

context = Context(seed=0)
registry = GeneratorRegistry(context=context)
schema = {
  'type': tuple,
  'mode': 'variable',
  'items': {'type': int, 'generator_args': None},
  'generator_args': None,
}

result = registry._generate(schema)
assert isinstance(result, tuple)
```

This mirrors the behaviour covered by tests in `tests/core/test_pyfake_complex.py`.

## Implementation notes

- **Fixed vs variable**: `mode == 'fixed'` → generator creates one element per annotated position; `mode == 'variable'` → generator chooses a length and repeats the single `items` schema.
- **Length selection** (variable tuples) uses `rng.randint(args.min_length or 1, args.max_length or 5)` (default range `1..5`).
- **Defaults**: if a field has a non-`None` default, the resolver will set `GeneratorArgs.default` and the registry will return that default instead of generating a value.
- **Pydantic serialization**: `model_dump()` may convert tuples to lists — tests accept either list or tuple when validating outputs.

## Unsupported / Partial support

- Regex-based generation for string elements is not guaranteed by the built-in string generator. Use a custom generator for strict regex requirements.
- Fixed-length tuples cannot have their length adjusted via `min_length`/`max_length` — use variable tuples if you need length bounds.



