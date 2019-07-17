#!/usr/bin/env bash

echo "Checking code with Black..."
black --py36 --diff $1

echo "Checking code with flake8..."
flake8 $1

echo "Checking code with mypy..."
mypy --strict $1
