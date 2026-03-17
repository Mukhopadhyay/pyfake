---
icon: lucide/cog
tags:
  - Internal
hide:
  - title
---

```
Pydantic model
  |
Field metadata (types, constraints)
  |
Registry resolves the generators
  |
Engine orchestrates the recursion
  |
Final fake object
```

## Possible usage

```python
from pyfake import Pyfake
from pydantic import BaseModel

class Model(BaseModel):
    something: int
    something_optional: int | None
    some_string: str = 'default'

## OO usage (More expensive, the Pyfake object is bound to the pydantic model)
Pyfake(Model).generate()

# or,

# v0 Functional usage
Pyfake.generate(Model, num=5)
```

```python
{
    "properties": {
        "integer_basic": {"title": "Integer Basic", "type": "integer"},
        "integer_optional": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "title": "Integer Optional",
        },
        "integer_with_bounds": {
            "maximum": 100,
            "minimum": 1,
            "title": "Integer With Bounds",
            "type": "integer",
        },
        "integer_with_multiple_annotations": {
            "anyOf": [
                {"maximum": 100, "minimum": 1, "type": "integer"},
                {"maximum": 300, "minimum": 200, "type": "integer"},
            ],
            "title": "Integer With Multiple Annotations",
        },
        "integer_optional_default": {
            "anyOf": [{"type": "integer"}, {"type": "null"}],
            "default": 42,
            "title": "Integer Optional Default",
        },
    },
    "required": [
        "integer_basic",
        "integer_optional",
        "integer_with_bounds",
        "integer_with_multiple_annotations",
    ],
    "title": "StressTestModel",
    "type": "object",
}

```

### Fields schema

```python
class Model(BaseModel):
    title: str = Field(title="Model Title")
    frozen: str = Field(frozen=True)
    description: str = Field(description="This is a description of the model.")
    alias: str = Field(alias="model_alias")
    examples: list[str] = Field(examples=["example1", "example2"])
    gt: int = Field(gt=10)
    lt: int = Field(lt=100)
    ge: int = Field(ge=5)
    le: int = Field(le=200)
    default: int = Field(default=42)
    pattern: str = Field(pattern=r"^[a-zA-Z0-9_]+$")
    allow_inf_nan: float = Field(allow_inf_nan=False)
    multiple_of: int = Field(multiple_of=3)
    decimal_places: float = Field(decimal_places=2)
    min_length: str = Field(min_length=3)
    max_length: str = Field(max_length=50)
```

```python
{
    "properties": {
        "title": {"title": "Model Title", "type": "string"},
        "frozen": {"title": "Frozen", "type": "string"},
        "description": {
            "description": "This is a description of the model.",
            "title": "Description",
            "type": "string",
        },
        "model_alias": {"title": "Model Alias", "type": "string"},
        "examples": {
            "examples": ["example1", "example2"],
            "items": {"type": "string"},
            "title": "Examples",
            "type": "array",
        },
        "gt": {"exclusiveMinimum": 10, "title": "Gt", "type": "integer"},
        "lt": {"exclusiveMaximum": 100, "title": "Lt", "type": "integer"},
        "ge": {"minimum": 5, "title": "Ge", "type": "integer"},
        "le": {"maximum": 200, "title": "Le", "type": "integer"},
        "default": {"type": "integer", "default": 42, "title": "Default"},
        "pattern": {"pattern": "^[a-zA-Z0-9_]+$", "title": "Pattern", "type": "string"},
        "allow_inf_nan": {"title": "Allow Inf Nan", "type": "number"},
        "multiple_of": {"multipleOf": 3, "title": "Multiple Of", "type": "integer"},
        "decimal_places": {
            "decimal_places": 2,
            "title": "Decimal Places",
            "type": "number",
        },
        "min_length": {"minLength": 3, "title": "Min Length", "type": "string"},
        "max_length": {"maxLength": 50, "title": "Max Length", "type": "string"},
    },
    "required": [
        "title",
        "frozen",
        "description",
        "model_alias",
        "examples",
        "gt",
        "lt",
        "ge",
        "le",
        "pattern",
        "allow_inf_nan",
        "multiple_of",
        "decimal_places",
        "min_length",
        "max_length",
    ],
    "title": "Model",
    "type": "object",
}

```
