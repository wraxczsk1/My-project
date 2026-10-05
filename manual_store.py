"""Ukládání upraveného obsahu manuálu a seznamu FTO (JSON v datové složce)."""
import json
import os
import tempfile

from manual_content import MANUAL, slugify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OWNER_EMAILS = [e.strip().lower() for e in os.environ.get("FTO_EMAILS", "kudelka.zdenek0@gmail.com").split(",") if e.strip()]
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}

data_dir = os.environ.get("LSPD_DATA_DIR") or os.path.join(BASE_DIR, "instance")
_listeners = []


def configure(path):
    global data_dir
    data_dir = path


def path(*parts):
    return os.path.join(data_dir, *parts)


def upload_dir():
    return path("uploads")


def on_change(fn):
    _listeners.append(fn)
    return fn


def _read(name, default):
    try:
        with open(path(name), encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return default


def _write(name, data):
    os.makedirs(data_dir, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=data_dir, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path(name))


def load():
    saved = _read("manual.json", None)
    if saved is not None:
        MANUAL[:] = saved
    for fn in _listeners:
        fn()


def save():
    _write("manual.json", MANUAL)
    for fn in _listeners:
        fn()


def fto_emails():
    return sorted(set(OWNER_EMAILS) | set(_read("fto.json", [])))


def set_fto_emails(emails):
    _write("fto.json", sorted({e.strip().lower() for e in emails if e.strip()} - set(OWNER_EMAILS)))


def unique_slug(name, items, skip=None):
    base = slugify(name)
    taken = {it["slug"] for it in items if it is not skip}
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}-{n}", n + 1
    return slug
