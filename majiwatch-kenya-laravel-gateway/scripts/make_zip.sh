#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-maji-sentinel.zip}"

rm -f "$OUT"

zip -r "$OUT" . \
  -x "web/node_modules/*" \
  -x "web/dist/*" \
  -x ".git/*" \
  -x ".venv/*" \
  -x "gateway/vendor/*" \
  -x "gateway/node_modules/*" \
  -x "gateway/public/build/*" \
  -x "gateway/.env" \
  -x "gateway/database/database.sqlite" \
  -x "**/__pycache__/*" \
  -x "**/*.pyc" \
  -x "*.zip" \
  -x ".env" \
  -x "db_data/*" \
  -x "data/*"

echo "$OUT"
