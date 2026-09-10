#!/bin/bash
# This is called by the `app` service in `compose.yml` when the container starts.
# Runs as root so it can fix ownership of /app/data (which may be a fresh,
# root-owned bind mount on the host) before dropping to the unprivileged
# "wagtail" user for migrations and the app server itself.
set -e
chown -R wagtail:wagtail /app/data
echo "Running database migrations..."
gosu wagtail uv run python manage.py migrate --noinput
echo "Starting application server..."
exec gosu wagtail "$@"
