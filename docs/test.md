```bash
pytest tests/
```

Test with coverage
```bash
coverage run -m pytest

# Generating report
coverage report

# Generating html report
coverage html
```

Generating coverage badge
```bash
coverage run -m pytest
coverage-badge -o ./docs/assets/coverage.svg -f
```
