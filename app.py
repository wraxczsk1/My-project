import io
import os
import secrets
import zipfile
from collections import Counter
from functools import lru_cache

from flask import Flask, Response, abort, render_template, request, send_file
from werkzeug.middleware.proxy_fix import ProxyFix

import fto
import manual_store as store
from manual_content import MANUAL
from manual_png import CODE_COLORS, CODE_LABELS, image_path, module_pages, overview_png, parse


def find_category(cat):
    for ci, c in enumerate(MANUAL):
        if c["slug"] == cat:
            return ci, c
    abort(404)


def find_module(cat, mod):
    ci, c = find_category(cat)
    for mi, m in enumerate(c["moduly"]):
        if m["slug"] == mod:
            return ci, c, mi, m
    abort(404)


def png_filename(ci, mi, page, pages):
    c = MANUAL[ci]
    m = c["moduly"][mi]
    suffix = f"-{page}" if pages > 1 else ""
    return f"{ci + 1:02d}-{c['slug']}/{mi + 1:02d}-{m['slug']}{suffix}.png"


def png_response(data, filename):
    disposition = "attachment" if request.args.get("download") else "inline"
    return Response(
        data,
        mimetype="image/png",
        headers={"Content-Disposition": f'{disposition}; filename="{filename}"'},
    )


@lru_cache(maxsize=1)
def manual_zip_bytes():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("00-obsah.png", overview_png())
        for ci, c in enumerate(MANUAL):
            for mi in range(len(c["moduly"])):
                pages = module_pages(ci, mi)
                for p, data in enumerate(pages, start=1):
                    archive.writestr(png_filename(ci, mi, p, len(pages)), data)
    return buf.getvalue()


def module_preview(ci, mi, m):
    blocks = parse(m["text"])
    codes = [r for b in blocks if b["type"] == "codes" for r in b["rows"]]
    return {
        "sections": [b["text"] for b in blocks if b["type"] == "heading"][:3],
        "lines": [b["text"] for b in blocks if b["type"] in ("bullet", "para", "quote", "warn")][:3],
        "codes": codes[:6],
        "code_count": len(codes),
        "images": len(m["obrazky"]),
        "video": bool(m["video"]),
        "pages": len(module_pages(ci, mi)),
    }


@store.on_change
def clear_caches():
    module_pages.cache_clear()
    overview_png.cache_clear()
    manual_zip_bytes.cache_clear()


def secret_key():
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    path = store.path("secret_key")
    if not os.path.isfile(path):
        os.makedirs(store.data_dir, exist_ok=True)
        with open(path, "w") as fh:
            fh.write(secrets.token_hex(32))
    with open(path) as fh:
        return fh.read().strip()


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=20 * 1024 * 1024, SESSION_COOKIE_SAMESITE="Lax", **(config or {}))
    if app.config.get("DATA_DIR"):
        store.configure(app.config["DATA_DIR"])
    app.secret_key = secret_key()
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    store.load()
    fto.init_app(app)

    @app.context_processor
    def inject_manual():
        return {"categories": MANUAL, "code_colors": CODE_COLORS, "code_labels": CODE_LABELS}

    @app.route("/")
    def index():
        previews = [[module_preview(ci, mi, m) for mi, m in enumerate(c["moduly"])]
                    for ci, c in enumerate(MANUAL)]
        flat = [p for cat in previews for p in cat]
        stats = {
            "modules": len(flat),
            "pages": sum(p["pages"] for p in flat),
            "images": sum(p["images"] for p in flat),
        }
        return render_template("index.html", previews=previews, stats=stats)

    @app.route("/k/<cat>")
    def category(cat):
        ci, c = find_category(cat)
        previews = [module_preview(ci, mi, m) for mi, m in enumerate(c["moduly"])]
        return render_template("category.html", c=c, ci=ci, previews=previews, active_cat=c["slug"])

    @app.route("/k/<cat>/<mod>")
    def module(cat, mod):
        ci, c, mi, m = find_module(cat, mod)
        images = [name for name in m["obrazky"] if image_path(name)]
        blocks = parse(m["text"])
        code_counts = Counter(r["kind"] for b in blocks if b["type"] == "codes" for r in b["rows"])
        prev_m = c["moduly"][mi - 1] if mi > 0 else None
        next_m = c["moduly"][mi + 1] if mi + 1 < len(c["moduly"]) else None
        return render_template(
            "module.html", c=c, ci=ci, m=m, mi=mi, blocks=blocks, images=images, code_counts=code_counts,
            pages=len(module_pages(ci, mi)), prev_m=prev_m, next_m=next_m, active_cat=c["slug"],
        )

    @app.route("/obrazky/<name>")
    def image(name):
        path = image_path(name)
        if not path:
            abort(404)
        return send_file(path, max_age=3600)

    @app.route("/png/obsah.png")
    def overview_image():
        return png_response(overview_png(), "00-obsah.png")

    @app.route("/png/<cat>/<mod>/<int:page>.png")
    def module_image(cat, mod, page):
        ci, c, mi, m = find_module(cat, mod)
        pages = module_pages(ci, mi)
        if not 1 <= page <= len(pages):
            abort(404)
        name = png_filename(ci, mi, page, len(pages)).replace("/", "-")
        return png_response(pages[page - 1], name)

    @app.route("/lspd-manual.zip")
    def manual_zip():
        return Response(
            manual_zip_bytes(),
            mimetype="application/zip",
            headers={"Content-Disposition": 'attachment; filename="lspd-manual.zip"'},
        )

    return app


app = create_app()
