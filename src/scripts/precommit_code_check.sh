#!/usr/bin/env bash

cd `git rev-parse --show-toplevel`

staged=$(git diff --cached --name-only)
for filen in $staged; do
    if [ ${filen: -3} == ".py" ]
    then
        echo "Checking code with Black..."
        black --py36 --diff $filen

        echo "Checking code with flake8..."
        flake8 $filen

        echo "Checking code with mypy..."
        mypy --strict $filen
    fi
done