#!/usr/bin/env sh
set -eu

STATE_DIR="${GATEWAY_STATE_DIR:-/state}"
APP_KEY_FILE="$STATE_DIR/app_key"

mkdir -p "$STATE_DIR"

if [ -z "${APP_KEY:-}" ]; then
  if [ -f "$APP_KEY_FILE" ]; then
    export APP_KEY="$(cat "$APP_KEY_FILE")"
  else
    export APP_KEY="base64:$(php -r 'echo base64_encode(random_bytes(32));')"
    printf "%s" "$APP_KEY" > "$APP_KEY_FILE"
  fi
fi

php artisan config:clear || true
php artisan migrate --force
php artisan db:seed --force

exec php-fpm

