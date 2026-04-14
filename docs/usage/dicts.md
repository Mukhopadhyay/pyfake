---
icon: lucide/braces
tags:
  - Usage
  - Examples
  - Dicts
  - Dictionary
  - Complex
hide:
  - title
---

# Dicts in `pyfake`

## Simple usage
`pyfake` generates values for mapping fields declared with `typing.Dict[...]` or the builtin `dict[...]` generic. Keys and values are generated independently from their annotated types.

```python
from typing import Dict
from pyfake import fake
from pydantic import BaseModel

class Maps(BaseModel):
  by_name: Dict[str, int]
  by_id: dict[int, float]

print(fake(Maps))
```

<!-- termynal -->

```console
{'by_name': {'alice': 10, 'bob': 7}, 'by_id': {1: 3.14}}
```

No setup required — `pyfake` inspects the schema and generates keys and values automatically.

!!! note "Typing forms"

    Both `typing.Dict[K, V]` and `dict[K, V]` are resolved. Prefer explicit key/value types for predictable results.

---

## Receiving Model Instances

By default `pyfake` returns dictionaries (serialized). To obtain Pydantic model instances (preserving types where Pydantic coerce applies), set `as_dict=False`.

```python
from pyfake import fake
from pydantic import BaseModel

class Item(BaseModel):
  label: str

class Container(BaseModel):
  mapping: dict[int, Item]

print(fake(Container, as_dict=False))
```

<!-- termynal -->

```console
[Container(mapping={1: Item(label='Abc'), 2: Item(label='Xy')})]
```

## Returning Multiple Values

Use `num` to generate multiple examples as with other types.

```python
print(fake(Maps, num=3))
```

<!-- termynal -->
```console
[
    {'by_name': {'gllDxwbMVV': 27, 'grIUPcdNDM': 99}, 'by_id': {41: 38.31790652661318, 67: 16.56897318208862, 8: 79.2069059099716}},
    {'by_name': {'CZDQHnlJrt': 86, 'mSoZkjgxWj': 53, 'IUIJAQwzXx': 52, 'sNfLpYthTK': 26}, 'by_id': {23: 74.71911608258735}},
    {'by_name': {'AVelENxysQ': 22, 'dOeRvKfxTs': 31}, 'by_id': {47: 28.34939934408407, 43: 4.9681132448364025}}
]
```

---
:lucide-key:
## Keys, Values, and Constraints

`pyfake` resolves and generates keys and values independently. Container size uses `min_length`/`max_length` on the mapping itself (controls how many key/value pairs are generated). Key and value types may themselves be annotated with `Field`/`Annotated` metadata which the resolver propagates into the inner `GeneratorArgs`.

### How mapping size is chosen

- Default: when no `min_length`/`max_length` are provided the registry picks a length between `1` and `5` (inclusive).
- With `min_length`/`max_length`: a random length is chosen between those bounds (inclusive).

This mirrors `pyfake.core.registry.GeneratorRegistry._generate` that uses `rng.randint(args.min_length or 1, args.max_length or 5)` for container lengths.

### Key/value constraints (Annotated / Field)

You can apply `Annotated[...]` / `Field(...)` constraints to either the key type or the value type. Those constraints are used when generating each key or value.

```python
from typing import Annotated, Dict
from pydantic import BaseModel, Field
from pyfake import fake

class Constrained(BaseModel):
  # keys between 1 and 10, values are short strings
  mapping: Dict[Annotated[int, Field(ge=1, le=10)], Annotated[str, Field(min_length=3, max_length=6)]]

print(fake(Constrained, seed=42))
```

<!-- termynal -->

```console
{'mapping': {3: 'Abc', 7: 'XyZ'}}
```

### Examples: different key/value shapes

- `Dict[int, str]`

```python
class M1(BaseModel):
  m: Dict[int, str]

print(fake(M1))
```

<!-- termynal -->

```console
{'m': {0: 'ZCJDoXiPWO', 19: 'MYySQSGYOv', 9: 'qpomBeNoaK'}}
```

- `Dict[int, list[int]]` — values are collections generated according to list rules (inner min/max lengths apply):

```python
from typing import List

class M2(BaseModel):
  m: Dict[int, List[int]]

print(fake(M2, seed=1))
```

<!-- termynal -->

```console
{'m': {2: [1, 5], 7: [3]}}
```

- `Dict[int, Dict[str, str]]` — nested mappings; inner keys/values are generated using their schemas. You can annotate inner key/value types as well:

```python
class M3(BaseModel):
  nested: Dict[int, Dict[str, str]]

print(fake(M3, seed=2))
```

<!-- termynal -->

```console
{'nested': {1: {'a': 'Abc'}, 3: {'b': 'XyZ'}}}
```

### Annotated keys & values with Field

You can annotate the key or the inner value with `Field` to influence generation. The resolver merges these constraints into the inner `GeneratorArgs` (see `tests/core/test_pyfake_complex.py` for examples of inherited/propagated constraints).

```python
from typing import Annotated

class AnnotatedKV(BaseModel):
  data: Dict[Annotated[int, Field(ge=10, le=20)], Annotated[List[int], Field(min_length=2, max_length=3)]]

print(fake(AnnotatedKV, seed=3))
```

<!-- termynal -->

```console
{'data': {12: [1, 2], 19: [3]}}
```

## Nullable mappings

If a mapping is declared `Optional[Dict[K, V]]` or `Dict[K, V] | None`, the resolver marks the field as a nullable union. The registry will return `None` when the nullable branch triggers (currently about 20% probability); otherwise it generates a mapping normally.

```python
from typing import Optional

class MaybeMap(BaseModel):
  maybe: Optional[Dict[int, str]]

print(fake(MaybeMap, num=6, seed=1))
```

<!-- termynal -->

```console
[
  {'maybe': {1: 'Abc'}},
  {'maybe': None},
  {'maybe': {3: 'Xy'}},
  {'maybe': {7: 'Z'}},
  {'maybe': None},
  {'maybe': {2: 'Qw'}}
]
```

## Dict[Any, Any] and dynamic types

`Dict[Any, Any]` is permissive but not recommended: the resolver will produce a schema node with `type` equal to the annotation and the registry needs concrete types to map to generators. If the registry does not recognise the concrete type (or `Any`), generation will fall back to `None` for that node. For predictable results prefer explicit key and value types.

## Keys must be hashable

Because Python dict keys must be hashable, ensure your key type produces hashable values (e.g. `int`, `str`, `tuple`). If a generator produces an unhashable key (e.g. `list`) a `TypeError` will be raised when the mapping is constructed.

## Registry direct generation

You can call the `GeneratorRegistry` directly with an explicit schema (tests exercise this path):

```python
from pyfake.core.context import Context
from pyfake.core.registry import GeneratorRegistry
from pyfake.schemas import GeneratorArgs

context = Context(seed=0)
registry = GeneratorRegistry(context=context)
schema = {
  'type': dict,
  'keys': {'type': str, 'generator_args': GeneratorArgs()},
  'values': {'type': int, 'generator_args': GeneratorArgs()},
  'generator_args': GeneratorArgs(),
}

result = registry._generate(schema)
assert isinstance(result, dict)
```

This mirrors the behaviour tested in `tests/core/test_pyfake_complex.py`.

## Implementation notes

- Container size selection: `rng.randint(args.min_length or 1, args.max_length or 5)` — default range `1..5`.
- Keys and values are generated by recursively resolving their schemas; any `Annotated`/`Field` metadata on key/value types is propagated and honoured where the underlying generator supports those constraints (e.g. `ge`/`le` for integers, `min_length`/`max_length` for strings/lists).
- Duplicate keys: the registry generates candidate key/value pairs and inserts them into a dict — later duplicate keys replace earlier entries, so the final number of items may be smaller than the requested/generated length.
- Unsupported inner types: if the registry does not have a generator for a key or value type (e.g. `bytes`, `Any`), that node will produce `None` (see `TestRegistryFallback` in tests). Prefer explicit, supported types for keys and values.

## Unsupported / Partial support

- Regex-based generation (`pattern`) for string values is parsed by the resolver but not enforced by the default string generator. Use a custom generator for strict regex requirements.
- `Dict[Any, Any]` and other highly dynamic annotations may not produce useful values — use concrete types.

