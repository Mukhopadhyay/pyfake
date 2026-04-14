---
icon: lucide/code
tags:
  - Internal
hide:
  - Developers
---

## Tests (for contributors)

This document is a short, practical guide for contributors writing and running tests for `pyfake`.

### Quick start (local)

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the package in editable mode and developer tools. The project lists dev dependencies in `pyproject.toml` (`pytest`, `pytest-cov`, `marimo`, `rich`); install them however you prefer:

```bash
pip install -e .
pip install pytest pytest-cov marimo rich
```

Notes: some contributors prefer `pip install -e .[dev]` if your tooling supports extras. The repository also exposes `uv` helper commands in docs (`uv pip install -e .`, `uv run pytest`) — you can use those if available in your environment.

### Run the test suite

- Run all tests:

```bash
pytest -v
```

- Run a specific test file:

```bash
pytest tests/core/test_pyfake_complex.py -q
```

- Run a single test case or test function:

```bash
pytest tests/core/test_pyfake_complex.py::TestPyfakeDictGeneration::test_dict_field_generates_dict_of_correct_types -q
```

- Run tests by marker (markers are defined in `pyproject.toml`):

```bash
pytest -m complex
```

- Run with coverage and an HTML report:

```bash
pytest --cov=pyfake --cov-report=html
```

### Common pytest flags

- `-k <expr>`: run tests matching the expression
- `-m <marker>`: run tests with the given marker
- `-q`, `-v`: quiet/verbose
- `-s`: show print output
- `--maxfail=1` / `-x`: stop after first failure
- `--pdb`: drop into pdb on failure

### Debugging flaky tests

- Reproduce deterministically by using the `seed` argument used throughout the tests: many tests call `Pyfake(..., seed=...)` or use `Context(seed=...)` to make generation deterministic.
- Run the failing test with `-s --pdb` to inspect state and prints.
- Add temporary `print()` statements or use `pytest --pdb` to debug interactively.

### Writing tests (guidelines)

- File layout: place tests under `tests/` following existing subfolders (e.g. `tests/core`, `tests/generators`). Name files `test_*.py`.
- Use `pytest` markers to categorise tests (see marker list below). Add a new marker in `pyproject.toml` if you create a new category.
- Prefer deterministic tests where possible. When a generator is used, pass `seed=` to `Pyfake` or `Context` to make results reproducible, e.g.:

```python
from pyfake import Pyfake

result = Pyfake(MyModel, seed=0).generate()
```

- For integration tests that exercise the registry or resolver internals, follow patterns in `tests/core/test_pyfake_complex.py` (direct `GeneratorRegistry` calls, `Resolver` checks, etc.). Example:

```python
from pyfake.core.context import Context
from pyfake.core.registry import GeneratorRegistry
from pyfake.schemas import GeneratorArgs

ctx = Context(seed=0)
registry = GeneratorRegistry(context=ctx)
schema = {
    'type': dict,
    'keys': {'type': str, 'generator_args': GeneratorArgs()},
    'values': {'type': int, 'generator_args': GeneratorArgs()},
    'generator_args': GeneratorArgs(),
}
res = registry._generate(schema)
assert isinstance(res, dict)
```

- Use fixtures for repeated setup and parametrise seeds when appropriate (the repo often uses `@pytest.mark.parametrize("seed", list(range(5)) + [None])`).

### Test conventions & style

- Keep tests small and focused: one logical assertion per test where practical.
- Name tests clearly and document the intent with short comments or docstrings.
- Avoid external network calls or OS-dependent behaviour in unit tests.

### Markers (defined in `pyproject.toml`)

- `datatypes`: Unit tests for all datatypes together.
- `integer`, `boolean`, `string`, `float`, `decimal`, `uuid`, `datetime`: datatype-specific groups.
- `pyfake`: Core generator tests.
- `api`: Tests for the `Pyfake` class and public API.
- `registry`: Tests for `GeneratorRegistry()` behaviour.
- `exceptions`: Tests for exception classes.
- `complex`: Complex-type tests (lists, sets, tuples, dicts, enums, literals, nested models).

### CI & pull-request checklist (recommended)

- Run the full test-suite locally before opening a PR: `pytest -v`.
- Run the new/changed tests only to speed up iteration: `pytest path/to/test_file.py -q`.
- Ensure new tests are deterministic (use `seed=`) or minimise flakiness.
- Add or update markers in `pyproject.toml` if you add a new category.
- Include a short note in the PR describing the tests added and the rationale.

### Coverage and metrics

The project already runs coverage (see pytest config in `pyproject.toml`). To generate an HTML report locally:

```bash
pytest --cov=pyfake --cov-report=html
open htmlcov/index.html
```

### Help & troubleshooting

- If tests fail locally but pass in CI, try clearing caches, recreating the virtualenv, and ensuring consistent Python versions.
- If you hit generator-related nondeterminism, use `seed=` when creating `Pyfake`/`Context` instances.

