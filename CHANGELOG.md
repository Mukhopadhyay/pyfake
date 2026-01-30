## Changelog 🕓

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
