---
icon: octicons/file-binary-16
tags:
  - Usage
  - Examples
  - Booleans
  - Primitives
hide:
  - title
---

# Booleans in `pyfake`

## Simple usage
`pyfake` can generate values for `bool` fields in your Pydantic models. By default it samples `True` or `False` uniformly.

```python
from pyfake import fake
from pydantic import BaseModel

class Feature(BaseModel):
  enabled: bool

result = fake(Feature)
print(result)
```

```console
{'enabled': True}
```

No setup required — `pyfake` inspects the model schema and generates valid boolean values automatically.

## Returning multiple values
Generate more than one instance by passing `num`:

```python
from pyfake import fake
from pydantic import BaseModel

class Feature(BaseModel):
  enabled: bool

results = fake(Feature, num=3)
print(results)
```

```console
[
  {'enabled': True},
  {'enabled': False},
  {'enabled': True}
]
```

## Receiving model instances
By default `pyfake` returns dictionaries. To receive Pydantic model instances set `as_dict=False`:

```python
from pyfake import fake
from pydantic import BaseModel

class Feature(BaseModel):
  enabled: bool

results = fake(Feature, num=2, as_dict=False)
print(results)
```

```console
[
  Feature(enabled=True),
  Feature(enabled=False)
]
```

## Nullable / Optional fields
If a field is declared as `Optional[bool]` or using the `| None` shorthand (e.g. `bool | None`), `pyfake` treats the field as a union that may be `None`.

The registry currently returns `None` roughly 20% of the time for nullable unions; otherwise it generates `True` or `False` as usual.

```python
from typing import Optional
from pyfake import fake
from pydantic import BaseModel

class Feature(BaseModel):
  enabled: Optional[bool]

results = fake(Feature, num=5)
print(results)
```

```console
[
  {'enabled': True},
  {'enabled': None},
  {'enabled': False},
  {'enabled': True},
  {'enabled': False}
]
```

## Default values
If you provide an explicit (non-`None`) default for a field, `pyfake` will return that default instead of generating a random value. For example:

```python
from pydantic import BaseModel, Field
from pyfake import fake

class User(BaseModel):
  active: bool = Field(default=True)

result = fake(User)
print(result)
```

```console
{'active': True}
```

## Implementation notes
- The boolean generator is `pyfake.generators.primitives.generate_bool` and simply samples from `[True, False]` using the `Context` RNG.
- Nullability is handled by the resolver/registry: union/optional fields are eligible to be `None` (about 20% probability in current implementation).
- If a non-`None` `default` is present in the field metadata, the registry returns that value before attempting generation.

## Unsupported / Partial support
- There is no built-in way to bias the generator (e.g., 70% True / 30% False). Use a custom generator if you need weighted booleans.
- There are no field-level boolean constraints (min/max, pattern, etc.) — booleans are binary values.

## Custom generators
If you need more control (for example, a weighted probability), write a small custom generator that accepts a `prob_true` argument and registers it with the registry.

If you'd like, I can add an example custom generator or implement weighted/biased boolean support. Which would you prefer?
