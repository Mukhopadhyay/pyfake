---
icon: lucide/workflow
tags:
  - Internal
hide:
  - title
---

# How It Works

`pyfake` inspects a Pydantic model's field metadata at runtime and produces realistic fake values that satisfy every declared constraint — bounds, length, format, defaults, and more.

## The Pipeline

```
Pyfake.from_schema(MyModel)
         │
         ▼
   Engine.generate(MyModel)
         │  iterates model.model_fields
         │
         ▼  (for each field)
   Resolver.resolve(FieldInfo)
         │  annotation → schema dict
         │
         ▼
   GeneratorRegistry._generate(schema)
         │  dispatches by type / format
         │
         ▼
   Generator function
   (generate_int, generate_str, generate_uuid4 …)
         │
         ▼
      generated value
```

---

## Components

### `Pyfake` — Public API

The `Pyfake` class is the user-facing entry point. It holds a [`Context`](#context) and an [`Engine`](#engine), both bound to the model you pass in.

```python
from pyfake import Pyfake

# Class method shortcut — no need to instantiate manually
result = Pyfake.from_schema(MyModel, num=5, seed=42)

# Or instantiate first for repeated generation
fake = Pyfake(MyModel, seed=42)
fake.generate(num=3)
```

The optional `seed` parameter is forwarded to the `Context`, making generation fully deterministic and reproducible.

When `as_dict=True` (the default), instances are returned as plain `dict`s via `.model_dump()`. Set `as_dict=False` to get back the actual Pydantic model instances.

---

### `Engine` — Orchestration

`Engine` knows nothing about types or constraints. Its only job is to walk `model.model_fields` and ask the `GeneratorRegistry` for a value for each field.

```python
# Internally, Engine does roughly this:
data = {}
for field_name, field_info in MyModel.model_fields.items():
    data[field_name] = registry.generate(field_info)
return data
```

The resulting `data` dict is passed directly to the model's constructor, so Pydantic validates the output before it is returned to you.

---

### `Resolver` — Type Resolution

`Resolver` takes a `FieldInfo` object and converts its annotation into a **schema dict** — a plain Python dict that encodes everything the generators need to know.

It resolves annotations recursively, handling:

| Annotation form                            | Resolved as                                      |
| ------------------------------------------ | ------------------------------------------------ |
| `int`, `str`, `float`, `bool`, `uuid.UUID` | primitive schema node                            |
| `Optional[T]` / `T | None`                | `union` node with `nullable=True`                |
| `Union[A, B]`                              | `union` node with multiple variants              |
| `List[T]`, `Set[T]`                        | container node with an `items` sub-schema        |
| `Tuple[A, B]` / `Tuple[T, ...]`            | fixed or variable-length tuple                   |
| `Dict[K, V]`                               | dict node with `keys` and `values` sub-schemas   |
| `Literal["a", "b"]`                        | literal node with a `values` list                |
| `Enum` subclasses                          | enum node                                        |
| Nested `BaseModel`                         | model node, recursively resolved                 |
| `Annotated[T, Field(...)]`                 | delegates to the inner type, merging constraints |

Constraints extracted from `Field(...)` — like `ge`, `lt`, `min_length`, `max_length`, `multiple_of`, `decimal_places`, `pattern`, `format` — are collected into a `GeneratorArgs` instance and attached to the schema node.

#### Schema node shape

Each resolved node is a dict with at minimum a `type` key and a `generator_args` key. Complex types add their own keys:

```python
# primitive
{"type": str, "generator_args": GeneratorArgs(min_length=3, max_length=20)}

# union / Optional
{"type": "union", "nullable": True, "variants": [...]}

# list
{"type": list, "items": {...}, "generator_args": GeneratorArgs()}

# nested model
{"type": "model", "model": Address, "fields": {"street": {...}, "city": {...}}}
```

---

### `GeneratorRegistry` — Dispatch

The registry receives a schema node and routes it to the correct generator function. The dispatch order is:

1. **Default shortcut** — if `generator_args.default` is set, return it immediately.
2. **Union** — pick a random variant; occasionally return `None` for nullable unions.
3. **Literal / Enum** — pick a random value from the declared set.
4. **Container types** (`list`, `set`, `dict`, `tuple`) — generate the appropriate number of items by recursing into sub-schemas.
5. **Nested model** — recurse into its `fields` dict and construct the model.
6. **Format-based dispatch** — if `generator_args.format` is set (e.g. `"uuid4"`, `"date-time"`), look up the matching generator by that string key.
7. **Primitive type dispatch** — map the Python type to a generator via the `_type_map` table.

Below are the built-in type and format mappings:

| Key               | Generator                           |
| ----------------- | ----------------------------------- |
| `integer`         | `generate_int`                      |
| `number`          | `generate_float`                    |
| `string`          | `generate_str`                      |
| `bool`            | `generate_bool`                     |
| `uuid` / `uuid4`  | `generate_uuid4`                    |
| `uuid1` … `uuid8` | `generate_uuid1` … `generate_uuid8` |
| `date`            | `generate_date`                     |
| `date-time`       | `generate_datetime`                 |
| `time`            | `generate_time`                     |

If no match is found after all steps, `None` is returned.

---

### `Context` — Shared Random State

Every generator receives a shared `Context` instance. It carries a single `random.Random` object, which all generators use instead of the global `random` module.

```python
# Unseeded — different output each run
fake = Pyfake(MyModel)

# Seeded — identical output every run
fake = Pyfake(MyModel, seed=123)
```

Passing a seed through the `Pyfake` constructor guarantees that all fields, across all generated instances, use the same seeded random stream — making test fixtures fully reproducible.
