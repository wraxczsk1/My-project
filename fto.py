"""FTO MANAGE – správa kurzů a lekcí pro povolené FTO (přihlášení přes Google)."""
import os
import secrets
import uuid
from functools import wraps

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

import manual_store as store
from manual_content import MANUAL, modul

bp = Blueprint("fto", __name__, url_prefix="/fto")
oauth = OAuth()

ICONS = {
    "stit": "Štít",
    "vysilacka": "Vysílačka",
    "kriz": "Zdravověda",
    "auto": "Policejní auto",
    "mdt": "MDT",
    "zamerovac": "Zaměřovač",
    "lupa": "Lupa",
    "pouta": "Pouta",
    "vaha": "Zákon",
    "kniha": "Kniha",
    "helikoptera": "Air unit",
}


def current_fto():
    email = session.get("fto")
    return email if email and email in store.fto_emails() else None


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(24)
    return session["csrf"]


def init_app(app):
    app.config.setdefault("GOOGLE_CLIENT_ID", os.environ.get("GOOGLE_CLIENT_ID"))
    app.config.setdefault("GOOGLE_CLIENT_SECRET", os.environ.get("GOOGLE_CLIENT_SECRET"))
    oauth.init_app(app)
    if app.config["GOOGLE_CLIENT_ID"]:
        oauth.register(
            "google",
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
            overwrite=True,
        )
    app.register_blueprint(bp)
    app.context_processor(lambda: {"fto_user": current_fto(), "csrf_token": csrf_token, "icons": ICONS})


def fto_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_fto():
            return redirect(url_for("fto.login"))
        return view(*args, **kwargs)
    return wrapper


@bp.before_request
def check_csrf():
    if request.method == "POST" and request.form.get("csrf") != session.get("csrf"):
        abort(400)


def get_course(ci):
    if not 0 <= ci < len(MANUAL):
        abort(404)
    return MANUAL[ci]


def get_lesson(ci, mi):
    c = get_course(ci)
    if not 0 <= mi < len(c["moduly"]):
        abort(404)
    return c, c["moduly"][mi]


def move(items, i, direction):
    j = i + (-1 if direction == "nahoru" else 1)
    if 0 <= i < len(items) and 0 <= j < len(items):
        items[i], items[j] = items[j], items[i]


def save_uploads(files, prefix):
    names = []
    os.makedirs(store.upload_dir(), exist_ok=True)
    for f in files:
        if not f or not f.filename:
            continue
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in store.IMAGE_EXT:
            flash(f"Soubor {f.filename} není obrázek (PNG, JPG, WEBP).", "error")
            continue
        name = secure_filename(f"{prefix}-{uuid.uuid4().hex[:8]}{ext}")
        f.save(os.path.join(store.upload_dir(), name))
        store.push(f"uploads/{name}")
        names.append(name)
    return names


@bp.route("/login")
def login():
    if current_fto():
        return redirect(url_for("fto.dashboard"))
    if not current_app.config["GOOGLE_CLIENT_ID"]:
        return render_template("fto/message.html", title="Přihlášení není nastavené",
                               text="Přihlášení přes Google zatím není zapnuté. Kontaktuj správce webu."), 503
    if request.args.get("go"):
        return oauth.google.authorize_redirect(url_for("fto.callback", _external=True))
    return render_template("fto/login.html")


@bp.route("/callback")
def callback():
    try:
        token = oauth.google.authorize_access_token()
    except Exception:
        return render_template("fto/message.html", title="Přihlášení selhalo",
                               text="Přihlášení přes Google se nepovedlo. Zkus to znovu."), 400
    info = token.get("userinfo") or {}
    email = (info.get("email") or "").lower()
    if not info.get("email_verified") or email not in store.fto_emails():
        session.pop("fto", None)
        return render_template("fto/message.html", title="Přístup odepřen",
                               text=f"Účet {email or '?'} nemá oprávnění FTO MANAGE."), 403
    session["fto"] = email
    return redirect(url_for("fto.dashboard"))


@bp.route("/logout", methods=["POST"])
def logout():
    session.pop("fto", None)
    return redirect(url_for("index"))


@bp.route("/")
@fto_required
def dashboard():
    return render_template("fto/dashboard.html", emails=store.fto_emails(), owners=store.OWNER_EMAILS)


@bp.route("/kurz/novy", methods=["GET", "POST"])
@bp.route("/kurz/<int:ci>", methods=["GET", "POST"])
@fto_required
def course_form(ci=None):
    c = get_course(ci) if ci is not None else None
    if request.method == "POST":
        nazev = request.form.get("nazev", "").strip()
        if not nazev:
            flash("Kurz musí mít název.", "error")
        else:
            ikona = request.form.get("ikona") if request.form.get("ikona") in ICONS else "stit"
            barva = request.form.get("barva") or "#2563eb"
            if c is None:
                c = {"moduly": []}
                MANUAL.append(c)
            c.update(nazev=nazev, ikona=ikona, barva=barva, slug=store.unique_slug(nazev, MANUAL, skip=c))
            store.save()
            flash(f"Kurz „{nazev}“ uložen.", "ok")
            return redirect(url_for("fto.dashboard"))
    return render_template("fto/course_form.html", c=c, ci=ci)


@bp.route("/kurz/<int:ci>/smazat", methods=["POST"])
@fto_required
def course_delete(ci):
    c = get_course(ci)
    MANUAL.pop(ci)
    store.save()
    flash(f"Kurz „{c['nazev']}“ smazán.", "ok")
    return redirect(url_for("fto.dashboard"))


@bp.route("/kurz/<int:ci>/<direction>", methods=["POST"])
@fto_required
def course_move(ci, direction):
    move(MANUAL, ci, direction)
    store.save()
    return redirect(url_for("fto.dashboard"))


@bp.route("/kurz/<int:ci>/lekce/nova", methods=["GET", "POST"])
@bp.route("/kurz/<int:ci>/lekce/<int:mi>", methods=["GET", "POST"])
@fto_required
def lesson_form(ci, mi=None):
    c = get_course(ci)
    m = get_lesson(ci, mi)[1] if mi is not None else None
    if request.method == "POST":
        nazev = request.form.get("nazev", "").strip()
        if not nazev:
            flash("Lekce musí mít název.", "error")
        else:
            if m is None:
                m = modul(nazev, "")
                c["moduly"].append(m)
            keep = [n for n in m["obrazky"] if not request.form.get(f"smazat:{n}")]
            m.update(
                nazev=nazev,
                slug=store.unique_slug(nazev, c["moduly"], skip=m),
                text=request.form.get("text", "").replace("\r\n", "\n").strip(),
                video=request.form.get("video", "").strip() or None,
                obrazky=keep + save_uploads(request.files.getlist("obrazky"), m["slug"]),
            )
            store.save()
            flash(f"Lekce „{nazev}“ uložena.", "ok")
            return redirect(url_for("fto.dashboard") + f"#kurz-{ci}")
    return render_template("fto/lesson_form.html", c=c, ci=ci, m=m, mi=mi)


@bp.route("/kurz/<int:ci>/lekce/<int:mi>/smazat", methods=["POST"])
@fto_required
def lesson_delete(ci, mi):
    c, m = get_lesson(ci, mi)
    c["moduly"].pop(mi)
    store.save()
    flash(f"Lekce „{m['nazev']}“ smazána.", "ok")
    return redirect(url_for("fto.dashboard") + f"#kurz-{ci}")


@bp.route("/kurz/<int:ci>/lekce/<int:mi>/<direction>", methods=["POST"])
@fto_required
def lesson_move(ci, mi, direction):
    c = get_course(ci)
    move(c["moduly"], mi, direction)
    store.save()
    return redirect(url_for("fto.dashboard") + f"#kurz-{ci}")


@bp.route("/pristup", methods=["POST"])
@fto_required
def access():
    emails = [e for e in store.fto_emails() if e not in store.OWNER_EMAILS]
    add = request.form.get("pridat", "").strip().lower()
    remove = request.form.get("odebrat", "").strip().lower()
    if add:
        if "@" not in add:
            flash("Zadej platný e-mail.", "error")
        else:
            emails.append(add)
            flash(f"{add} má teď přístup do FTO MANAGE.", "ok")
    if remove in emails:
        emails.remove(remove)
        flash(f"{remove} už nemá přístup.", "ok")
    store.set_fto_emails(emails)
    return redirect(url_for("fto.dashboard") + "#pristup")
