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
