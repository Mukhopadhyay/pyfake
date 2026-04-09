---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: Mukhopadhyay

---

## 🐛 Bug Report

### 1. Describe the bug

A clear and concise description of the issue.

Example:

For the following Pydantic model, I'm getting `a` as None, resulting in a Validation Error at pyfake.

```python
from pydantic import BaseModel

class Something(BaseModel):
    a: int
```
---

### 2. Minimal reproducible example

Please provide the **smallest possible code snippet** to reproduce the issue.

```python
from pyfake import fake
from pydantic import BaseModel

class Something(BaseModel):
    a: int

x = fake(Something, num=5)
assert isinstance(x.a, int)
```

---

### 3. Expected behavior

What did you expect to happen?

**Example:**
_Should always return an integer._

---

### 4. Actual behavior

What actually happened?

Output:

```
""
```

Error (if any):

```
Traceback (most recent call last):
...
```

---

### 5. Seed (if applicable) 🎲

If you are using a seed, please provide it.

```
from pyfake import fake

fake(Model, seed=42, num=5)
```

Or mention if the issue is:

* Reproducible only with a specific seed
* Not reproducible consistently

---

### 6. Context/configuration

Provide relevant details:

* pyfake version:
* Python version:
* OS:

---

### 7. Are you using models?

If the issue involves Pydantic or structured data, share your model.

```
from pydantic import BaseModel

class User(BaseModel):
    name: str
```

---

### 8. Additional context

* Does this happen always or intermittently?
* Any edge cases?
* Related to randomness, batching, or performance?
