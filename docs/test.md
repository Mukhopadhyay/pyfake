```bash
pytest tests/
```

Test with coverage
```bash
coverage run -m pytest
# Generating report
coverage report
```

Generating coverage badge
```bash
coverage run -m pytest
coverage-badge -o ./docs/assets/coverage.svg -f
```
