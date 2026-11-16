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

    `pyfake` extracts Pydantic field metadata (like `min_length`, `max_length`, and `pattern`) and uses it to drive generation. See below for the options it honours.

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

`pyfake` reads Pydantic Field metadata to decide how to generate values. For strings the generator supports `min_length`, `max_length`, `pattern`, and a `length` override. The same constraints can also come from `constr(...)` or `Annotated[str, StringConstraints(...)]`.

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
| `pattern`        | Regular expression the value must match. See [Regular expressions](#regular-expressions). |

!!! error "Unsupported / Partial Support"

    - Without a `pattern`, the built-in generator uses only ASCII letters (`string.ascii_letters`), so it will not produce digits or punctuation. Use a `pattern` if you need other characters.
    - Field names are not used yet: `first_name` and `city` both get random letters.

## Regular expressions

When a field has a `pattern`, `pyfake` generates a string that matches it:

```python
from typing import Annotated
from pydantic import BaseModel, Field, constr
from pyfake import fake

class Product(BaseModel):
    sku: Annotated[str, Field(pattern=r"^[A-Z]{3}-\d{4}$")]
    slug: constr(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=20)
    colour: Annotated[str, Field(pattern=r"^#[0-9a-f]{6}$")]

result = fake(Product)
print(result)
```

<!-- termynal -->

```console
{'sku': 'SRE-9791', 'slug': 'e1o1i', 'colour': '#b83e3c'}
```

How it works and what to expect:

- The string is written by walking the parsed pattern: literals, character classes (including `\d`, `\w`, `\s` and negated classes), alternation, groups, backreferences and repeats are all supported.
- Unbounded repeats (`*`, `+`, `{n,}`) add at most 8 extra repetitions, or up to `min_length` when that is larger.
- Anchors produce no text. Lookaheads and lookbehinds are skipped while writing, so every result is checked against the real pattern and regenerated if it doesn't match.
- Like pydantic, a match anywhere in the string counts (`re.search`).
- `min_length` and `max_length` still apply. If no matching string fits within 100 attempts, pyfake raises `InvalidConstraints`.

## Implementation notes

The default `generate_str` function (see `pyfake/generators/primitives.py`):

- Uses `string.ascii_letters` as the character set.
- Resolves the output length via `min_length`/`max_length`/`length` as described above.
- Hands fields with a `pattern` to `pyfake.generators.regex.generate_matching`, which is seeded like every other generator.

