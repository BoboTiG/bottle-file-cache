#!/bin/bash
set -eu
python -m ruff format bottle_file_cache.py tests
python -m ruff check --fix --unsafe-fixes bottle_file_cache.py tests
python -m mypy bottle_file_cache.py tests
