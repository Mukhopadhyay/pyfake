#!/bin/bash

set -e  # Exit on first error

rm -rf dist/ build/ *.egg-info

python -m build
python -m twine upload dist/*