#!/bin/bash

set -e  # Exit on first error

echo "🔍 Running tests with coverage..."
coverage run --source=pyfake -m pytest tests

echo "📊 Generating coverage report..."
coverage report
coverage html

echo "🎯 Generating coverage badge..."
coverage-badge -o ./docs/assets/coverage.svg -f

echo "🧼 Running black (code formatter)..."
black pyfake tests scripts

echo "🔎 Running flake8 (lint)..."
flake8 pyfake tests scripts

echo "📐 Running mypy (type checks)..."
mypy pyfake

echo "✅ All checks passed!"
