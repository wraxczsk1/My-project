#!/usr/bin/env bash
# Sestaví složku pro hosting (FastAPI + Poetry, aplikace v app/main.py).
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$HOME/lspd-backend}"
rm -rf "$OUT" && mkdir -p "$OUT/app"
cp "$SRC"/{fto,manual_content,manual_png,manual_store}.py "$OUT/app/"
cp "$SRC/app.py" "$OUT/app/webapp.py"
cp -r "$SRC/static" "$SRC/templates" "$OUT/app/"
[ -f "$SRC/.env" ] && cp "$SRC/.env" "$OUT/app/.env"
cat > "$OUT/app/__init__.py" <<'PY'
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PY
cat > "$OUT/app/main.py" <<'PY'
from a2wsgi import WSGIMiddleware
from fastapi import FastAPI

from webapp import app as flask_app

app = FastAPI()
app.mount("/", WSGIMiddleware(flask_app))
PY
cat > "$OUT/pyproject.toml" <<'TOML'
[tool.poetry]
name = "app"
version = "0.1.0"
description = "LSPD MANUAL"
authors = ["LSPD Academy <lspd@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
fastapi = {extras = ["standard"], version = ">=0.110,<1"}
uvicorn = ">=0.29,<1"
a2wsgi = ">=1.10,<2"
Flask = ">=3.0,<4"
Pillow = ">=10.4,<12"
Authlib = ">=1.3,<2"
requests = ">=2.31,<3"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
TOML
(cd "$OUT" && ${POETRY:-poetry} lock -q)
echo "$OUT"
