"""Ukládání upraveného obsahu manuálu a seznamu FTO (JSON v datové složce)."""
import base64
import json
import os
import tempfile

import requests

from manual_content import MANUAL, slugify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OWNER_EMAILS = [e.strip().lower() for e in os.environ.get("FTO_EMAILS", "kudelka.zdenek0@gmail.com").split(",") if e.strip()]
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}

data_dir = os.environ.get("LSPD_DATA_DIR") or ("/data" if os.path.isdir("/data") else os.path.join(BASE_DIR, "instance"))
_listeners = []

GITHUB_API = "https://api.github.com"


def _gh():
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPO")
    if not (token and repo):
        return None
    return {
        "repo": repo,
        "branch": os.environ.get("GITHUB_BRANCH", "fto-data"),
        "headers": {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    }


def _gh_url(gh, rel):
    return f"{GITHUB_API}/repos/{gh['repo']}/contents/data/{rel}"


def _gh_ensure_branch(gh):
    base = f"{GITHUB_API}/repos/{gh['repo']}"
    if requests.get(f"{base}/branches/{gh['branch']}", headers=gh["headers"], timeout=20).status_code == 200:
        return
    default = requests.get(base, headers=gh["headers"], timeout=20).json()["default_branch"]
    sha = requests.get(f"{base}/git/ref/heads/{default}", headers=gh["headers"], timeout=20).json()["object"]["sha"]
    requests.post(f"{base}/git/refs", headers=gh["headers"], timeout=20,
                  json={"ref": f"refs/heads/{gh['branch']}", "sha": sha}).raise_for_status()


def _gh_download(gh, rel):
    r = requests.get(_gh_url(gh, rel), headers={**gh["headers"], "Accept": "application/vnd.github.raw+json"},
                     params={"ref": gh["branch"]}, timeout=30)
    if r.status_code == 404:
        return False
    r.raise_for_status()
    dest = path(rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(r.content)
    return True


def pull():
    """Stáhne uložená data z GitHub repa do lokální datové složky."""
    gh = _gh()
    if not gh:
        return
    _gh_ensure_branch(gh)
    for name in ("manual.json", "fto.json"):
        _gh_download(gh, name)
    r = requests.get(_gh_url(gh, "uploads"), headers=gh["headers"], params={"ref": gh["branch"]}, timeout=30)
    if r.status_code == 200:
        for item in r.json():
            if item["type"] == "file" and not os.path.isfile(path("uploads", item["name"])):
                _gh_download(gh, f"uploads/{item['name']}")


def push(rel, message=None):
    """Nahraje soubor z datové složky do GitHub repa (trvalé uložení)."""
    gh = _gh()
    if not gh:
        return
    url = _gh_url(gh, rel)
    current = requests.get(url, headers=gh["headers"], params={"ref": gh["branch"]}, timeout=30)
    with open(path(rel), "rb") as fh:
        body = {"message": message or f"FTO MANAGE: {rel}", "branch": gh["branch"],
                "content": base64.b64encode(fh.read()).decode()}
    if current.status_code == 200:
        body["sha"] = current.json()["sha"]
    requests.put(url, headers=gh["headers"], json=body, timeout=60).raise_for_status()


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
    push(name)


def load():
    pull()
    saved = _read("manual.json", None)
    if saved is not None:
        MANUAL[:] = saved
    for fn in _listeners:
        fn()


def save():
    _write("manual.json", MANUAL)
    for fn in _listeners:
        fn()


def tests():
    return _read("tests.json", [])


def save_tests(items):
    _write("tests.json", items)


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
