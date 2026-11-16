---
icon: lucide/rocket
tags:
  - Get started
  - Setup
hide:
  - toc
---
# Getting Started

<p align="center">
  <a href="https://github.com/Mukhopadhyay/pyfake">
    <img src="https://raw.githubusercontent.com/Mukhopadhyay/pyfake/refs/heads/master/docs/assets/logo.png" alt="Pyfake" width="180">
  </a>
</p>


<p align="center">
  <i>A flexible, schema-driven fake data generator built on top of <b>Pydantic v2</b>.</i>
</p>

<p align="center">
  <a href="https://pypi.org/project/pyfake/">
    <img src="https://img.shields.io/pypi/v/pyfake?style=for-the-badge">
  </a>
  <img src="https://img.shields.io/badge/python-3.10+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/>
  <img src="https://img.shields.io/badge/pydantic-v2-4B8BBE?style=for-the-badge"/>
  <img src="https://img.shields.io/github/stars/Mukhopadhyay/pyfake?style=for-the-badge"/>
</p>


<p align="center">
  <a href="https://mukhopadhyay.is-a.dev/pyfake/"><strong>Documentation</strong></a> &middot; <a href="https://github.com/Mukhopadhyay/pyfake"><strong>Github</strong></a> &middot; <a href="https://pypi.org/project/pyfake/"><strong>PyPI</strong></a>
</p>

<p align="center">
Generate valid fake data for your Pydantic models with ease. Perfect for testing, prototyping, and anywhere you need valid mock data.
</p>
---

<!-- <p align="center">
  <b>Docs</b>: pyfake.readthedocs.io/en/latest &nbsp;•&nbsp;
  <b>Source</b>: github.com/Mukhopadhyay/pyfake
</p> -->


## ⚡ Quick Example

```python
from typing import Annotated, List, Set, Literal
from pydantic import BaseModel, Field
from pyfake import fake
from rich import print


class Playlist(BaseModel):
    track_ids: List[int]
    genre: Literal["rock", "pop", "jazz"]
    tags: Annotated[List[str], Field(min_length=2, max_length=5)]
    unique_ratings: Set[int]


result = fake(Playlist, as_dict=True)
print(result)
```
<!-- termynal -->
```console
$ python example.py

{
    "track_ids": [28, 25, 95, 40], 
    "genre": "pop", 
    "tags": ["CJKHILHXTN", "qkhhjDJYiV"], 
    "unique_ratings": {17, 49}
}
```

## ✨ Why Pyfake?

|Problem| Most fake data generators | Pyfake|
|-|-|-|
|Random but not structured| ❌ Generates random data without understanding the schema | ✅ Reads your Pydantic models to produce structured, schema-aware data |
|Structured but not valid| ❌ Generates strings for emails, URLs or IP addresses that fail validation | ✅ Format-aware generators for `EmailStr`, `HttpUrl`, DSNs, IP addresses, UUIDs and regex `pattern`s |
|Support for constraints| ❌ Ignores field constraints like `min_length`, `gt`, `multiple_of` | ✅ Respects Pydantic constraints: bounds, lengths, `multiple_of`, `max_digits`/`decimal_places`, `pattern`, and `conint`/`constr`-style types |
|Support for python types| ❌ Limited support for complex types like `Decimal`, `UUID`, `datetime` | ✅ Supports `Decimal`, `UUID`, `datetime`, `timedelta`, `bytes`, enums, literals, nested and self-referencing models, and more |
|Clear failures| ❌ Silently returns invalid data | ✅ Raises an error that names the field when a type or constraint can't be satisfied |
|Reproducibility| ❌ No built-in way to generate the same fake data across runs | ✅ Supports seeding for reproducible fake data generation |



## Installation

`pyfake` is a lightweight and flexible fake data generation library built for developers, data scientists, and testers. You can install it using your preferred Python package manager.


=== "uv (Recommended)"

    [`uv`](https://github.com/astral-sh/uv) is a fast Python package manager and installer. It is the recommended way to install `pyfake` for better performance and dependency resolution.

    ```bash
    # Add pyfake to your project
    uv add pyfake
    ```

    !!! note "Non-project environment"
        If you're working in a non-project environment, you can use `uv` to install `pyfake` directly:

        ```bash
        uv pip install pyfake
        ```

        > 💡 `uv` is significantly faster than pip and handles virtual environments automatically.
    


=== "pip"

    You can install `pyfake` using the standard Python package manager:

    ```bash
    pip install pyfake
    ```

    To install a specific version:

    ```bash
    pip install pyfake==0.0.x
    ```

    If you're working in a virtual environment (recommended):

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install pyfake
    ```


=== "GitHub"

    If you want the latest development version or plan to contribute, you can install directly from GitHub:

    ```bash
    pip install git+https://github.com/Mukhopadhyay/pyfake.git
    ```

    !!! note "For a local development"
        If you want to clone the repository and install in editable mode for development:

        ```bash
        git clone https://github.com/Mukhopadhyay/pyfake.git
        cd pyfake
        pip install -e .
        ```

        This installs `pyfake` in editable mode, so changes to the source code are reflected immediately.


### Requirements

- Python **3.10+**
- Pydantic **2.12+** (installed with the `email` and `timezone` extras)
- NumPy **2.2+**

## How It Works

Pyfake reads your Pydantic schema and:

* Inspects field types and constraints
* Picks a generator for each field (realistic names and addresses are on the roadmap)
* Validates the result with your model, so every value it returns is valid

```mermaid
flowchart LR
    A[Pydantic Model] --> B[Schema Parser]
    B --> C[Generator Engine]
    C --> D[Validated Fake Data]
```

Read more about the design and implementation in the [how it works](dev/how-it-works.md) section.