#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:3000/api}"
API_KEY="${API_KEY:-change-me}"

curl -fsS "$API_BASE_URL/health" >/dev/null

TODAY="$(date -u +%F)"
YEAR="$(date -u +%Y)"

curl -fsS -X POST "$API_BASE_URL/compute/scores" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{\"year\": $YEAR, \"period\": \"$TODAY\"}" >/dev/null

curl -fsS "$API_BASE_URL/counties" >/dev/null
curl -fsS "$API_BASE_URL/scores/latest" >/dev/null
curl -fsS "$API_BASE_URL/alerts/active" >/dev/null
curl -fsS "$API_BASE_URL/waterpoints?limit=1000" >/dev/null
curl -fsS "$API_BASE_URL/tiles/waterpoints/6/38/32.pbf" >/dev/null

curl -fsS -X POST "$API_BASE_URL/lookup/waterpoint" \
  -H "Content-Type: application/json" \
  -d '{"lat": 0.2, "lng": 37.9}' >/dev/null

echo "OK"
