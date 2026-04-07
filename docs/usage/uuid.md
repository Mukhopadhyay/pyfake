---
icon: octicons/id-badge-16
tags:
  - Usage
  - Examples
  - UUID
hide:
  - title
---

# UUIDs in `pyfake`

## Simple usage
`pyfake` can generate values for `uuid.UUID` fields. By default it produces UUID v4 values as string representations.

```python
from uuid import UUID
from pyfake import fake
from pydantic import BaseModel

class Item(BaseModel):
  id: UUID

result = fake(Item)
print(result)
```

```console
{'id': '3b241101-e2bb-4255-8caf-4136c566a962'}
```

Note: the generators return strings (tests assert `str`). When you request model instances (`as_dict=False`), Pydantic will coerce those strings into `uuid.UUID` objects when constructing the model.

## Returning multiple values
Generate more than one instance by passing `num`:

```python
results = fake(Item, num=3)
print(results)
```

```console
[
  {'id': '3b241101-e2bb-4255-8caf-4136c566a962'},
  {'id': '27a4d3e0-4c9a-4e13-9b45-83d22f6e8f2d'},
  {'id': 'b3e8c2d4-6d53-45bd-9adb-28e5c1a9a5d0'}
]
```

## Receiving model instances
By default `pyfake` returns dictionaries. To receive Pydantic model instances set `as_dict=False`:

```python
results = fake(Item, num=2, as_dict=False)
print(results)
```

```console
[
  Item(id=UUID('3b241101-e2bb-4255-8caf-4136c566a962')),
  Item(id=UUID('27a4d3e0-4c9a-4e13-9b45-83d22f6e8f2d'))
]
```

## Nullable / Optional fields
If a field is declared as `Optional[UUID]` or using the `| None` shorthand, `pyfake` treats the field as a union that may be `None`.

The resolver/registry currently returns `None` roughly 20% of the time for nullable unions; otherwise it generates a UUID as usual.

```python
from typing import Optional
from uuid import UUID
from pyfake import fake
from pydantic import BaseModel

class Item(BaseModel):
  id: Optional[UUID]

results = fake(Item, num=5)
print(results)
```

```console
[
  {'id': '3b241101-e2bb-4255-8caf-4136c566a962'},
  {'id': None},
  {'id': '27a4d3e0-4c9a-4e13-9b45-83d22f6e8f2d'},
  {'id': 'b3e8c2d4-6d53-45bd-9adb-28e5c1a9a5d0'},
  {'id': None}
]
```

## Default values
If you provide an explicit (non-`None`) default for a field, `pyfake` will return that default instead of generating a random UUID. For example:

```python
from uuid import UUID
from pydantic import BaseModel, Field
from pyfake import fake

class User(BaseModel):
  id: UUID = Field(default=UUID('11111111-1111-1111-1111-111111111111'))

result = fake(User)
print(result)
```

```console
{'id': '11111111-1111-1111-1111-111111111111'}
```

## Choosing UUID version / format
The registry supports several UUID formats and maps them to generator functions:

- `uuid` (registry default → v4)
- `uuid1`, `uuid3`, `uuid4`, `uuid5`, `uuid6`, `uuid7`, `uuid8`

You can request a specific version by setting the field's format via annotated metadata or JSON-schema extra. Two supported ways:

- `Annotated[uuid.UUID, UuidVersion(n)]` (Pydantic's `UuidVersion`) — the resolver will set `format` accordingly.
- `Field(..., json_schema_extra={"format": "uuid7"})` — the resolver will read `json_schema_extra['format']`.

Example (Annotated):

```python
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel
from pydantic.types import UuidVersion
from pyfake import fake

class Item(BaseModel):
  id: Annotated[UUID, UuidVersion(1)]  # request UUIDv1

print(fake(Item))
```

Example (`json_schema_extra`):

```python
from uuid import UUID
from pydantic import BaseModel, Field
from pyfake import fake

class Item(BaseModel):
  id: UUID = Field(..., json_schema_extra={"format": "uuid7"})

print(fake(Item))
```

Notes:
- The `format` value is looked up in the registry's generator map (see `pyfake.core.registry`).
- All built-in uuid generators return string representations; Pydantic will coerce strings to `uuid.UUID` when constructing model instances.

## Implementation notes
- The UUID generators live in `pyfake.generators.uuid` and return string UUIDs.
- The default mapping for `uuid` (and for `uuid.UUID` annotated fields) is `generate_uuid4` — see `pyfake/core/registry.py` for the dispatch table.
- Format-based dispatch uses `GeneratorArgs.format` (populated from `Annotated` metadata or `json_schema_extra`).
- Nullability is handled by the resolver/registry: union/optional fields are eligible to be `None` (about 20% probability in current implementation).

## Unsupported / Partial support
- `uuid3`/`uuid5` currently use `uuid.NAMESPACE_DNS` with a random name under the hood; there is no exposed `namespace` generator-arg in the current `GeneratorArgs`, so custom namespaces or deterministic name inputs are not supported via field metadata today.
- If you need a specific namespace, deterministic name-based UUIDs, or different return types, register a small custom generator with the registry.

<!-- ## Custom generators
If you need more control (for example, deterministic name-based UUIDs or custom namespace handling), write a small custom generator that accepts the required arguments and register it with the registry.

If you'd like, I can add an example custom generator or demonstrate how to register one. Which would you prefer? -->
