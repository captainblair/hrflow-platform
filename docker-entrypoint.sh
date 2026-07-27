#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import time

import psycopg

raw = os.environ.get("DATABASE_URL", "")
# psycopg wants postgresql://, not the SQLAlchemy driver prefix.
dsn = raw.replace("postgresql+psycopg://", "postgresql://", 1)

for attempt in range(40):
    try:
        with psycopg.connect(dsn) as conn:
            conn.execute("SELECT 1")
        print("PostgreSQL is ready.")
        break
    except Exception as exc:
        if attempt == 39:
            raise SystemExit(f"Database not ready: {exc}") from exc
        time.sleep(1)
PY

echo "Applying migrations..."
flask db upgrade

echo "Loading seed data (skipped automatically if data already exists)..."
flask seed

echo "Starting HRFlow..."
exec python run.py
