#!/usr/bin/env bash

GIT_DIR=$(git rev-parse --git-dir)

TOP_DIR=$(git rev-parse --show-toplevel)

PRECOMMIT_SCRIPT="$TOP_DIR/src/scripts/pre-commit.sh"

rm $GIT_DIR/hooks/pre-commit

echo "Installing hooks..."
# this command creates symlink to our pre-commit script
ln -s $PRECOMMIT_SCRIPT $GIT_DIR/hooks/pre-commit
echo "Done!"

chmod +x $PRECOMMIT_SCRIPT