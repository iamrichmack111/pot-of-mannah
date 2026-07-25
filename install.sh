#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
printf '\nInstalled Pot of Mannah. Launch with:\n  source .venv/bin/activate\n  pot-of-mannah\n'
