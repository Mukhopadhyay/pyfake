<p align="center">
  <a href="https://github.com/Mukhopadhyay/pyfake">
    <img src="https://raw.githubusercontent.com/Mukhopadhyay/pyfake/refs/heads/master/docs/assets/logo.png" alt="Pyfake" width="180">
  </a>
</p>

<h1 align="center">Pyfake</h1>

<p align="center">
  <i>A flexible, schema-driven fake data generator built on top of <b>Pydantic v2</b>.</i>
</p>

<p align="center">
  <a href="https://pypi.org/project/pyfake/">
    <img src="https://img.shields.io/pypi/v/pyfake?style=for-the-badge">
  </a>
  <img src="https://img.shields.io/badge/python-3.9+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/>
  <img src="https://img.shields.io/badge/pydantic-v2-4B8BBE?style=for-the-badge"/>
  <img src="https://img.shields.io/github/stars/Mukhopadhyay/pyfake?style=for-the-badge"/>
</p>

---

<p align="center">
  <b>Docs</b>: <a href="https://mukhopadhyay.github.io/pyfake/">mukhopadhyay.github.io/pyfake</a> &nbsp;•&nbsp;
  <b>Source</b>: <a href="https://github.com/Mukhopadhyay/pyfake">github.com/Mukhopadhyay/pyfake</a>
</p>

---

## ✨ Why Pyfake?

Most fake data generators are either:
- ❌ Random but not structured  
- ❌ Structured but not realistic  
- ❌ Hard to extend  

**Pyfake fixes that.**

It leverages **Pydantic models** as the single source of truth to generate:
- ✅ Validated data  
- ✅ Schema-aware fake data  
- ✅ Easily extensible generators  
- ✅ Strong typing + IDE autocomplete  

---

## ⚡ Quick Example

```python
import uuid
from typing import Annotated
from pydantic import BaseModel, Field
from pyfake import Pyfake


class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: Annotated[str, Field(min_length=3, max_length=20)]
    address: Annotated[str, Field(max_length=255)]
    age: Annotated[int, Field(ge=18)]
    is_deleted: bool


users = Pyfake.from_schema(User, num=5)

print(users)
```


### 🧠 How It Works

Pyfake reads your Pydantic schema and:

* Inspects field types and constraints
* Applies intelligent generators
* Produces validated fake data


```mermaid
flowchart LR
    A[Pydantic Model] --> B[Schema Parser]
    B --> C[Generator Engine]
    C --> D[Validated Fake Data]
```

### Installation

**Using `uv` (Recommended)**

```bash
uv add pyfake
```

**Using `pip`**

```bash
python -m venv .venv
source .venv/bin/activate
pip install pyfake
```