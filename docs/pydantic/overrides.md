---
icon: lucide/pencil
tags:
  - Usage
  - Examples
  - Overrides
  - Extending
hide:
  - title
---

# Field overrides

Overrides set the value of specific fields for a single call, while every other field is generated as usual.

```python
from pydantic import BaseModel, Field
from pyfake import fake


class User(BaseModel):
    email: str
    age: int = Field(ge=0, le=120)


print(fake(User, overrides={"email": "a@b.com", "age": 30}))
```

```console
{'email': 'a@b.com', 'age': 30}
```

## Keyword shorthand

Fields can also be passed as keyword arguments. Both forms can be combined in one call:

```python
fake(User, email="a@b.com")
fake(User, overrides={"email": "a@b.com"}, age=30)
```

Overrides work the same way with `fake.dict`, `fake.model` and `fake.json`. `Pyfake(User).generate(overrides={...})` takes the `overrides=` mapping only.

The parameters of the call (`schema`, `num`, `as_dict`, `seed` and `overrides`) always keep their meaning. A field with one of those names can only be overridden through `overrides={...}`:

```python
class Settings(BaseModel):
    seed: str


# num is the row count, seed is the field
fake(Settings, num=2, overrides={"seed": "abc"})
```

Giving the same field both in `overrides=` and as a keyword raises `TypeError`.

## Plain values and callables

A plain value is used as-is, and is the same in every row. A callable is called with a `pyfake.GeneratorContext` once for every row, so each row gets its own value:

```python
rows = fake(
    User,
    num=3,
    seed=1,
    email="a@b.com",
    age=lambda ctx: ctx.random.randint(18, 65),
)
print(rows)
```

```console
[{'email': 'a@b.com', 'age': 26}, {'email': 'a@b.com', 'age': 54}, {'email': 'a@b.com', 'age': 22}]
```

`ctx` is the same context that [custom generators](custom-generators.md) receive:

| Attribute | Description |
| --- | --- |
| `ctx.random` | The seeded `random.Random` stream. Draw every random value from it so seeded output stays reproducible. |
| `ctx.now` | The reference point for values relative to "now". |
| `ctx.path` | The path of the field being generated, e.g. `"User.age"` or `"Account.previous[].city"`. |
| `ctx.type` | The field's annotation. |

To set a field to a callable object itself, wrap it in a callable that returns it: `fake(Job, handler=lambda ctx: my_handler)`.

## Nested fields

Use a dotted path to override a field of a nested model:

```python
class Address(BaseModel):
    street: str
    city: str


class Customer(BaseModel):
    name: str
    address: Address


print(fake(Customer, seed=1, overrides={"address.city": "Pune"}))
```

```console
{'name': 'iKZWeqhFWC', 'address': {'street': 'EPyYngFbyB', 'city': 'Pune'}}
```

A path can go as deep as the models do (`"order.customer.address.city"`), and it also reaches models inside `Optional[...]`, unions, lists, sets, tuples and dict values. For a `list[Address]` field, `"addresses.city"` applies to every item. When an `Optional` field comes out `None`, its nested overrides are simply not used.

When a field is a union of several models, a nested key has to exist on at least one of them, and it's applied to the ones that have it.

## Errors

Overrides are checked before any row is generated. A key that doesn't match the model raises `pyfake.exceptions.InvalidOverride` (also a `ValueError`):

```python
fake(User, emial="a@b.com")
# InvalidOverride: Unknown field 'emial' in overrides: 'User' has no field 'emial'. Fields: email, age

fake(Customer, overrides={"name.first": "Ada"})
# InvalidOverride: 'Customer.name' has no nested model, so 'name.first' can't be overridden

fake(Customer, overrides={"address": {...}, "address.city": "Pune"})
# InvalidOverride: Overrides for 'address' and 'address.city' conflict. Override either the whole field or its nested fields.
```

Keys are field names, not aliases. A field declared as `user_name: str = Field(alias="userName")` is overridden with `user_name`.

## Constraints and defaults

- **Constraints are not applied to overrides.** The generated model is still validated by pydantic, so a value that breaks a constraint raises a `ValidationError`: `fake(User, age=500)` fails because of `le=120`.
- **Overrides win over defaults.** A field with a default gets the override instead.
- **Overridden fields are never generated.** Overriding a field whose type `pyfake` doesn't support (such as `pathlib.Path`) avoids `GeneratorNotFound`.
