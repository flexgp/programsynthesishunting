#!/usr/bin/env bash

echo "Running pre-commit hook"
bash $(git rev-parse --show-toplevel)/src/scripts/precommit_code_check.sh

