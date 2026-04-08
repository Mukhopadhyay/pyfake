---
icon: lucide/calendar-days
tags:
  - Get started
  - Setup
hide:
  - title
---

# Changelog 🕓

### `0.0.9` - 2026-04-09

**New Features**
-  Support for `multiple_of` constraint for numeric fields, allowing users to specify that generated numbers must be multiples of a given value. This is implemented in the generator registry and integrated into the schema resolution process.
- Improved support for the `decimal_places` option for both `float` and `Decimal` fields, with documentation clarifying floating-point precision nuances.

**Docs**
- Added comprehensive new documentation pages for datetime and uuid usage, including examples, option explanations, and implementation notes.
- Updated the README with a clearer quick example, a new feature matrix comparing pyfake to other generators, and a more concise project introduction.

### `0.0.8` - 2026-04-06

**Major changes**

- Introduced the Fake class as a new, user-friendly API for generating fake data (`from pyfake import fake`), accessible via the fake singleton in `pyfake/__init__.py`. This class provides methods for generating data as dicts, models, or JSON, and supports seeding for reproducibility. (`pyfake/core/api.py`, `pyfake/__init__.py`)
  
**New Features**

- Added support for the `Decimal` type, including generator registration and type mapping in the registry.
- Improved metadata parsing for field constraints (e.g., `pattern`, `decimal_places`) and fixed a bug in how these are extracted from Pydantic field metadata.

**Docs**
- Added comprehensive usage guides for [booleans](https://mukhopadhyay.github.io/pyfake/usage/boolean/), [numbers](https://mukhopadhyay.github.io/pyfake/usage/numbers/) (including constraints and Decimal), and [strings](https://mukhopadhyay.github.io/pyfake/usage/strings/), with examples and notes on supported/unsupported features.
- Updated the main [README.md](https://github.com/Mukhopadhyay/pyfake/blob/master/README.md) with new documentation links and fixed minor formatting issues.

### `0.0.7` - 2026-04-02

**Major changes**

- Recursive generator support for nested Pydantic models
- Recursive resolver for resolving nested Pydantic models in the input Schema


**New Features**

- Support for `datetime`, `date` & `time` formats
  - Ability to set bounds using pydantic [`Field()`](https://docs.pydantic.dev/latest/concepts/fields/) function
- Flag based return for either accepting a **dictionary** or the **input Pydantic model** (`as_dict = True`)
- Updated ReadTheDocs documentation
- Support for `list`, `set` and `tuple` types with length constraints using pydantic [`Field()`](https://docs.pydantic.dev/latest/concepts/fields/) function
- Moving documentations to [`zensical`](https://zensical.org/) for better experience and future support.

---

### `0.0.6` - 2026-01-30

**Major changes**

- Migrated the entire project to [`uv`](https://docs.astral.sh/uv/) for faster, deterministic dependency management and installs.
- Introduced a new modular and expandable architecture, separating concerns into:
  - `engine` – execution and orchestration layer
  - `registry` – type to generator resolution
  - `context` – shared runtime state and randomness control

**New Features**

- Added full support for UUID generation across all formats:
  - `UUID1`, `UUID3`, `UUID4`, `UUID5`, `UUID6`, `UUID7`, `UUID8`
- Added support for legacy primitive types:
  - `int`
  - `float`
  - `str`
- Introduced a reproducible generation context, allowing users to set a seed for deterministic fake data generation.

**Testing**

- Added **comprehensive test coverage** across all generators and core components.
- Tests now validate:
  - Correct type resolution
  - Deterministic output with seeded contexts
  - UUID format correctness
  - Edge cases across primitive and complex generators

---

### `0.0.5` - 2025-06-16

- Initial release
