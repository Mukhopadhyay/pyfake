---
icon: octicons/unwrap-16
tags:
  - Usage
  - Examples
  - Strings
  - Primitives
hide:
  - title
---

# Strings in `pyfake`

## Simple Usage
`pyfake` can generate values for `str` fields in your Pydantic models. By default it produces ASCII-letter strings with a sensible default length.

```python
from pyfake import fake
from pydantic import BaseModel

class User(BaseModel):
    username: str
    bio: str | None

result = fake(User)
print(result)
```

<!-- termynal -->

```console
{'username': 'aBcDeFgHiJ', 'bio': None}
```

No setup required — `pyfake` inspects the schema and generates valid values automatically.

!!! note "Constraints & Customization"

    `pyfake` extracts Pydantic field metadata (like `min_length`, `max_length`, and `regex`) and uses it to drive generation when supported. See below for which options are currently honored.

---

## Returning Multiple Values

Generate more than one instance by passing `num`:

```python
from pyfake import fake
from pydantic import BaseModel

class User(BaseModel):
    username: str

results = fake(User, num=3)
print(results)
```

<!-- termynal -->

```console
[
    {'username': 'xYzAbCdEfG'},
    {'username': 'GhIjKlMnOp'},
    {'username': 'QrStUvWxYz'}
]
```

## Receiving Model Instances

By default `pyfake` returns dictionaries. To receive Pydantic model instances set `as_dict=False`:

```python
from pyfake import fake
from pydantic import BaseModel

class User(BaseModel):
    username: str

results = fake(User, num=2, as_dict=False)
print(results)
```

<!-- termynal -->

```console
[
    User(username='aBcDeFgHiJ'),
    User(username='XyZaBcDeFg')
]
```

## Metadata & Constraints

`pyfake` reads Pydantic Field metadata to decide how to generate values. For strings the generator currently supports `min_length`, `max_length`, and a `length` override. There is also a `pattern` argument on the generator, but note that pattern/regex matching is not yet applied by the default string generator.

### How length is chosen

- If both `min_length` and `max_length` are provided, `pyfake` picks a random length uniformly between them.
- If only `min_length` is provided, the generated string length equals `min_length`.
- If only `max_length` is provided, the generated string length equals `max_length`.
- If neither is provided, the generator uses a default `length` of `10` (or the explicit `length` if set).

This behavior matches the implementation in `pyfake.generators.primitives.generate_str` which picks an integer length and then samples ASCII letters to build the string.

### Using `Field` constraints

```python
from pyfake import fake
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=12)
    code: str = Field(..., min_length=8, max_length=8)

result = fake(User)
print(result)
```

<!-- termynal -->

```console
{'username': 'AbcDef', 'code': 'GhIjKlMn'}
```

### Supported Field options
| Option | Description |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| `min_length`     | Minimum length for the generated string. If provided alone, generated length == `min_length`. |
| `max_length`     | Maximum length for the generated string. If provided alone, generated length == `max_length`. |
| `length`         | Explicit length used when no min/max constraints are provided. Default is `10`. |
| `pattern`        | Regular expression the value should match. NOTE: currently accepted but not enforced by the built-in generator. |

!!! error "Unsupported / Partial Support"

    - `pattern`/`regex`: the generator accepts this metadata but does not yet generate strings that match arbitrary regular expressions. Pattern support is planned but not implemented in the default `generate_str` function.
    - The built-in generator uses only ASCII letters (`string.ascii_letters`) — it will not produce digits or punctuation. If you need other character classes, implement a custom generator or post-process generated values.

## Implementation notes

The default `generate_str` function (see `pyfake/generators/primitives.py`) currently:

- Uses `string.ascii_letters` as the character set.
- Resolves the output length via `min_length`/`max_length`/`length` as described above.
- Contains a `pattern` parameter placeholder (TODO in code) but does not apply it yet.

If you rely on regex-based outputs, consider writing a small custom generator that uses `rstr` or similar libraries, or open an enhancement request.

