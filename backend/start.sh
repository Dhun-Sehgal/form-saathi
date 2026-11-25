#!/bin/sh
# Container entrypoint: migrate, load reference data, optionally demo data, ensure admin, serve.
set -e
flask db upgrade
flask seed-reference
if [ "${SEED_DEMO:-true}" = "true" ]; then flask seed-demo; fi
flask ensure-admin
flask run-jobs || true
exec gunicorn --workers "${WEB_CONCURRENCY:-2}" --threads 4 --timeout 90 --bind "0.0.0.0:${PORT:-10000}" wsgi:app
