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
pyfake supports generating fake data for both integer (`<int>`) and floating-point (`<float>`) fields in your Pydantic models. Here's a simple 

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
