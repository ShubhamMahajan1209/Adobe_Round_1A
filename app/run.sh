#!/usr/bin/env bash
set -euo pipefail

IN_DIR="/app/input"
OUT_DIR="/app/output"
mkdir -p "$OUT_DIR"

shopt -s nullglob
processed=0
for pdf in "$IN_DIR"/*.pdf; do
    base="$(basename "${pdf%.*}")"
    python /app/extractor.py "$pdf" "$OUT_DIR/$base.json"
    ((processed++)) || true
done

echo "✓  processed $processed PDF(s)"
