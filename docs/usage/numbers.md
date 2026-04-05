---
icon: octicons/number-16
tags:
  - Usage
  - Examples
  - Numbers
  - Primitives
hide:
  - title
---

# Numbers in `pyfake`

## Simple Usage
pyfake supports generating fake data for integer (`<int>`), floating-point (`<float>`), and decimal (`<Decimal>`) fields in your Pydantic models. Here's a simple 

```python
from pyfake import fake
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    price: float

result = fake(Product)
print(result)
```

<!-- termynal -->

```console
{'id': 77, 'price': 82.89752225478523}
```

That’s it.

No setup, no fixtures, no config files.  
`pyfake` inspects your schema, understands each field, and generates valid data automatically.

!!! note "Constraints & Customization"

    You can also specify constraints like `gt`, `lt`, `ge`, `le` for more control over the generated numbers.  
    For example:

    ```python
    from pydantic import Field

    class Product(BaseModel):
        id: int = Field(..., gt=0)  # id must be greater than 0
        price: float = Field(..., ge=0.0)  # price must be non-negative
    ```

    `pyfake` will respect these constraints when generating values.

    Read more about this in the [Metadata & Constraints](#metadata-constraints) section below.

--- 

## Returning Multiple Values

By default, `pyfake` generates a single instance of your model. But you can easily generate multiple instances by passing the `num` parameter:

```python
from pyfake import fake
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    price: float

results = fake(Product, num=5)
print(results)
```
<!-- termynal -->

```console
[
    {'id': 77, 'price': 82.89752225478523},
    {'id': 12, 'price': 45.12345678901234},
    {'id': 34, 'price': 67.89012345678901},
    {'id': 56, 'price': 23.45678901234567},
    {'id': 89, 'price': 90.12345678901234}
]
```

## Receiving Model Instances

By default, `pyfake` returns generated data as plain dictionaries. If you want to receive actual Pydantic model instances instead, set `as_dict=False`:

```python
from pyfake import fake
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    price: float

results = fake(Product, num=3, as_dict=False)
print(results)
```
<!-- termynal -->
```console
[
    Product(id=77, price=82.89752225478523),
    Product(id=12, price=45.12345678901234),
    Product(id=34, price=67.89012345678901)
]
```

## Metadata & Constraints

pyfake also supports generating metadata about the generated values, such as which generator was used and which constraints were applied. This can be accessed via the `metadata` attribute of the generated instances:

!!! info "Pydantic Field"

    pyfake automatically extracts metadata from your Pydantic model fields, including type annotations and constraints. This metadata is used internally to determine how to generate appropriate fake data for each field.

    Read more about Field metadata in the [Pydantic documentation](https://docs.pydantic.dev/latest/usage/models/#field-metadata).

pyfake's internal architecture is designed to leverage this metadata effectively, ensuring that generated data adheres to the specified constraints and types defined in your Pydantic models.

### Using `Field` constraints

```python
from pydantic import BaseModel, Field
class Product(BaseModel):
    id: int = Field(..., gt=-4, lt=0)  # id must be greater than 0
    price: float = Field(..., ge=3.0, le=7.0)  # price must be between 3.0 and 7.0

results = fake(Product, num=1, as_dict=False)
print(results)
```

<!-- termynal -->
```console
[Product(id=-3, price=5.67890123456789)]
```

### Supported Field options
| Option           | Description                                                                                     |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| `gt`             | Greater than: the generated value will be greater than this value.
| `ge`             | Greater than or equal to: the generated value will be greater than or equal to this value.
| `lt`             | Less than: the generated value will be less than this value.
| `le`             | Less than or equal to: the generated value will be less than or equal to this value.
| `multiple_of`    | The generated value will be a multiple of this value. For floats, the generated value will be a multiple of this value within a reasonable tolerance to account for floating-point precision issues.
| `decimal_places` | For Decimal fields, this option specifies the number of decimal places to generate. The generated value will be rounded to this number of decimal places.

!!! error "Unsupported options"

    The following options are not currently supported for numeric fields:

    - `decimal_places`: This option is only currently supported for Decimal fields. For float fields, the generated value will not be rounded to a specific number of decimal places.
    - `multiple_of`: This option is currently not fully supported for integer fields. Will be implemented in a future release.


## Integer Types

Integers can be generated easily from Pydantic models, such as

```python
from pydantic import BaseModel
class User(BaseModel):
    id: int
    age: int

result = fake(User)
print(result)
```

<!-- termynal -->
```console
{'id': 77, 'age': 25}
```

### Using `Field` constraints

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(..., gt=0)  # id must be greater than 0
    age: int = Field(..., ge=18, le=99)  # age must be between 18 and 99
    score: int = Field(..., gt=-10, lt=100)  # score must be between -10 and 100

result = fake(User)
print(result)
```

<!-- termynal -->
```console
{'id': 66, 'age': 31, 'score': 88}
```

## Float Types

Floats can also be generated from Pydantic models, such as

```python
from pydantic import BaseModel

class Product(BaseModel):
    price: float
    height: float
    width: float

result = fake(Product)
print(result)
```

<!-- termynal -->
```console
{
    'price': 88.24146807024337,
    'height': 34.041684788330116,
    'width': 46.732209700107404
}
```

### Using `Field` constraints

```python
from pydantic import BaseModel, Field
from typing import Annotated

class Product(BaseModel):
    price: float = Field(..., ge=0.0)  # price must be non-negative
    height: float = Field(..., gt=0.0)  # height must be greater than 0
    width: float = Field(..., gt=0.0, le=100.0)  # width must be greater than 0 and less than or equal to 100
    expiry: Annotated[float | None, Field(..., gt=0.0, lt=100.0)]  # Optional expiry must be a positive multiple of 0.5

result = fake(Product)
print(result)
```

<!-- termynal -->
```console
{
    'price': 88.24146807024337,
    'height': 34.041684788330116,
    'width': 46.732209700107404,
    'expiry': None
}
```
