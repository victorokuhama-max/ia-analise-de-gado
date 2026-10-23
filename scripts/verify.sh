#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="src"
python3 scripts/run_coverage.py
