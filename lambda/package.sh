#!/usr/bin/env bash
set -euo pipefail

WORKDIR="$(pwd)/lambda_build"
ZIPNAME="remediation.zip"
SRC_DIR="$(pwd)/lambda"

rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"

python -m venv "$WORKDIR/venv"
source "$WORKDIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$SRC_DIR/requirements.txt" -t "$WORKDIR/package"

cp "$SRC_DIR/remediation_lambda.py" "$WORKDIR/package/"

cd "$WORKDIR/package"
zip -r "../$ZIPNAME" .
cd ..
mv "$ZIPNAME" "$SRC_DIR/$ZIPNAME"

# cleanup
deactivate
rm -rf "$WORKDIR"
echo "Packaged $SRC_DIR/$ZIPNAME"
