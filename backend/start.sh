#!/bin/sh
# Container entrypoint: migrate, load reference data and the real opportunities, ensure admin, serve.
set -e
flask db upgrade
flask seed-reference
flask purge-demo
flask seed-opportunities
flask ensure-admin
flask run-jobs || true
exec gunicorn --workers "${WEB_CONCURRENCY:-2}" --threads 4 --timeout 90 --bind "0.0.0.0:${PORT:-10000}" wsgi:app
