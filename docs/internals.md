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