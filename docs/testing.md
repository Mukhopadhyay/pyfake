## Tests

### Setting up the test

```bash
uv pip install -e .
uv run pytest -v
```

### Generating

```bash
uv run pytest --cov-report=html
```

### Markers

- `integer`: All integer related tests, generator + pydantic integration.
- `boolean`: All boolean related tests, generator + pydantic integration.
- `string`: All string related tests, generator + pydantic integration.
- `float`: All float related tests, generator + pydantic integration.
- `uuid`: All UUID related tests, generator + pydantic integration.
- `pyfake`: All pyfake core modules (`engine`, `generators`, `api` (Pyfake class))
- `registry`: All pyfake registry `GeneratorRegistry()` related tests.
