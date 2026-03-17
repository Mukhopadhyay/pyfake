---
icon: lucide/rocket
tags:
  - Get started
  - Setup
hide:
  - title
---

<!-- # Getting Started -->

<p align="center">
  <a href="https://github.com/Mukhopadhyay/pyfake"><img src="https://raw.githubusercontent.com/Mukhopadhyay/pyfake/refs/heads/master/docs/assets/logo.png" alt="Pyfake" ></a>
</p>

<p align="center">
<i>A Flexible and Extensible fake data generator based on <strong>Pydantic</strong> models.</i>
</p>

<p align="center">
<a href="https://pypi.org/project/pyfake/" target="_blank">
<img src="https://img.shields.io/pypi/v/pyfake?pypiBaseUrl=https%3A%2F%2Fpypi.org&style=for-the-badge"/></a> <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/> <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json&style=for-the-badge"/>
</p>

---

**Documentation**: [https://pyfake.readthedocs.io/en/latest](https://pyfake.readthedocs.io/en/latest)<br/>
**Source**: [https://github.com/Mukhopadhyay/pyfake](https://github.com/Mukhopadhyay/pyfake)

---

### 📦 Installation

`pyfake` can be installed **uv (recommended)**, **pip**, or directly from **source**.

#### ⚡ Using uv (Recommended)

[`uv`](https://github.com/astral-sh/uv) is a fast Python package manager and resolver written in Rust.

**Install using uv**

```bash
uv add pyfake
```

#### 🐍 Using pip

```bash
python -m venv .venv
source .venv/bin/activate
```

**Install pyfake**

```bash
pip install pyfake
```

---

### 💡 Examples

```python

import uuid
import pydantic
from typing import Annotated
from pydantic import BaseModel, Field

# Import pyfake
from pyfake import Pyfake


class Model(BaseModel):
  id: uuid.UUID = Field(default_factory=uuid.uuid4)
  name: str = Annotated[str, Field(min_length=3, max_length=20)]
  address: str = Annotated[str, Field(max_length=255)]
  age: Annotated[int, Field(ge=18)]
  is_deleted: bool

# Generating data using Pyfake
Pyfake.from_schema(Model, num=10, as_dict=False)
```
