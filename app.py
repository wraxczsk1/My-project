import csv
import io
import os
import re
import sqlite3
from datetime import datetime

from flask import (
    Flask,
    Response,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from lspd_seed import seed_lspd

COLUMN_TYPES = {
    "TEXT": "Text",
    "INTEGER": "Celé číslo",
    "REAL": "Desetinné číslo",
    "DATE": "Datum",
    "DATETIME": "Datum a čas",
    "BOOLEAN": "Ano/Ne",
}
IDENTIFIER_RE = re.compile(r"^[^\W\d]\w{0,62}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?$")
PAGE_SIZE = 25
DISPLAY_NAMES = {
    "dustojnici": "Důstojníci", "absolvovane_vycviky": "Absolvované výcviky",
    "vycviky": "Výcviky", "sluzby": "Služby", "jmeno": "Jméno", "volacka": "Volačka",
    "oddeleni": "Oddělení", "nastup": "Nástup", "nazev": "Název", "poradi": "Pořadí",
    "povinny": "Povinný", "dustojnik": "Důstojník", "vycvik": "Výcvik",
    "splneno": "Splněno", "poznamka": "Poznámka", "zacatek": "Začátek",
}
LSPD_TABLES = ("hodnosti", "kategorie", "vycviky", "dustojnici", "absolvovane_vycviky", "sluzby")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.environ.get(
            "DATABASE_PATH", os.path.join(app.instance_path, "database.sqlite")
        ),
        SEED_LSPD=True,
        SEED_DEMO=True,
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(os.path.dirname(os.path.abspath(app.config["DATABASE"])), exist_ok=True)

    app.teardown_appcontext(close_db)
    app.add_template_filter(pretty_name, "pretty")
    if app.config["SEED_LSPD"]:
        with app.app_context():
            if "dustojnici" not in list_tables():
                seed_lspd(get_db(), demo=app.config["SEED_DEMO"])
    register_routes(app)
    return app


def pretty_name(name):
    return DISPLAY_NAMES.get(name) or name.replace("_", " ").capitalize()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def quote(identifier):
    if not IDENTIFIER_RE.match(identifier or ""):
        raise ValueError(f"Neplatný název: {identifier!r}")
    return f'"{identifier}"'


def list_tables():
    rows = get_db().execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name COLLATE NOCASE"
    ).fetchall()
    return [r["name"] for r in rows if IDENTIFIER_RE.match(r["name"])]


def table_exists(name):
    return name in list_tables()


def get_columns(table):
    db = get_db()
    refs = {
        r["from"]: r["table"]
        for r in db.execute(f"PRAGMA foreign_key_list({quote(table)})").fetchall()
    }
    columns = []
    for r in db.execute(f"PRAGMA table_info({quote(table)})").fetchall():
        if r["name"] == "id":
            continue
        col = {"name": r["name"], "type": (r["type"] or "TEXT").upper(), "ref": None}
        if r["name"] in refs:
            col.update(type="REF", ref=refs[r["name"]])
        columns.append(col)
    return columns


def referencing_tables(table):
    return [
        t for t in list_tables()
        if t != table and any(c["ref"] == table for c in get_columns(t))
    ]


def label_column(table):
    for c in get_columns(table):
        if c["type"] == "TEXT":
            return c["name"]
    return "id"


def ref_options(table):
    label = label_column(table)
    rows = get_db().execute(
        f"SELECT id, {quote(label)} AS label FROM {quote(table)} ORDER BY id"
    ).fetchall()
    return {r["id"]: (r["label"] if r["label"] is not None else f"#{r['id']}") for r in rows}


def ref_maps(columns):
    return {c["ref"]: ref_options(c["ref"]) for c in columns if c["ref"]}


def require_table(table):
    if not table_exists(table):
        abort(404)
    return get_columns(table)


def convert_value(raw, col_type):
    if col_type == "BOOLEAN":
        return 1 if raw in ("1", "on", "true", "ano", "Ano", "True") else 0
    if raw is None or str(raw).strip() == "":
        return None
    raw = str(raw).strip()
    if col_type in ("INTEGER", "REF"):
        try:
            return int(raw)
        except ValueError:
            raise ValueError(f"„{raw}“ není celé číslo")
    if col_type == "REAL":
        try:
            return float(raw.replace(",", "."))
        except ValueError:
            raise ValueError(f"„{raw}“ není číslo")
    if col_type == "DATE":
        if not DATE_RE.match(raw):
            raise ValueError(f"„{raw}“ není datum ve formátu RRRR-MM-DD")
        return raw
    if col_type == "DATETIME":
        if not DATETIME_RE.match(raw):
            raise ValueError(f"„{raw}“ není datum a čas ve formátu RRRR-MM-DD HH:MM")
        return raw.replace("T", " ")[:16]
    return raw


def values_from_form(columns, form):
    values, errors = {}, []
    for col in columns:
        try:
            values[col["name"]] = convert_value(form.get(col["name"]), col["type"])
        except ValueError as exc:
            errors.append(f"{col['name']}: {exc}")
    return values, errors


def insert_row(table, values):
    cols = list(values)
    if not cols:
        return get_db().execute(f"INSERT INTO {quote(table)} DEFAULT VALUES")
    return get_db().execute(
        f"INSERT INTO {quote(table)} ({', '.join(quote(c) for c in cols)}) "
        f"VALUES ({', '.join('?' for _ in cols)})",
        [values[c] for c in cols],
    )


def parse_column_defs(form):
    names = form.getlist("col_name")
    types = form.getlist("col_type")
    tables = list_tables()
    columns, seen = [], set()
    for name, col_type in zip(names, types):
        name = name.strip()
        if not name:
            continue
        if not IDENTIFIER_RE.match(name) or name.lower() == "id":
            raise ValueError(f"Neplatný název sloupce: „{name}“")
        if name.lower() in seen:
            raise ValueError(f"Duplicitní sloupec: „{name}“")
        if col_type.startswith("REF:"):
            target = col_type[4:]
            if target not in tables:
                raise ValueError(f"Odkazovaná tabulka „{target}“ neexistuje")
            sql_type = f"INTEGER REFERENCES {quote(target)}(id) ON DELETE SET NULL"
        elif col_type in COLUMN_TYPES:
            sql_type = col_type
        else:
            raise ValueError(f"Neplatný typ sloupce: „{col_type}“")
        seen.add(name.lower())
        columns.append((name, sql_type))
    return columns


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def lspd_ready():
    tables = set(list_tables())
    return all(t in tables for t in LSPD_TABLES)


def training_overview(db):
    categories = db.execute(
        'SELECT k.id, k."nazev", COUNT(v.id) AS total FROM "kategorie" k '
        'LEFT JOIN "vycviky" v ON v."kategorie" = k.id '
        'GROUP BY k.id ORDER BY k."poradi", k.id'
    ).fetchall()
    officers = db.execute(
        'SELECT d.id, d."jmeno", d."volacka", d."stav", h."nazev" AS hodnost '
        'FROM "dustojnici" d LEFT JOIN "hodnosti" h ON h.id = d."hodnost" '
        'ORDER BY h."poradi" DESC, d."jmeno"'
    ).fetchall()
    done = {}
    for r in db.execute(
        'SELECT a."dustojnik", v."kategorie", COUNT(DISTINCT a."vycvik") AS n '
        'FROM "absolvovane_vycviky" a JOIN "vycviky" v ON v.id = a."vycvik" '
        'WHERE a."splneno" = 1 GROUP BY a."dustojnik", v."kategorie"'
    ):
        done[(r["dustojnik"], r["kategorie"])] = r["n"]
    total = sum(c["total"] for c in categories)
    rows = []
    for o in officers:
        per_cat = [done.get((o["id"], c["id"]), 0) for c in categories]
        completed = sum(per_cat)
        rows.append({
            "officer": o,
            "per_cat": per_cat,
            "completed": completed,
            "percent": round(100 * completed / total) if total else 0,
        })
    return categories, rows, total


def register_routes(app):
    @app.context_processor
    def inject_globals():
        return {
            "all_tables": list_tables(),
            "column_types": COLUMN_TYPES,
            "lspd": lspd_ready(),
        }

    @app.route("/")
    def index():
        db = get_db()
        tables = [
            {
                "name": t,
                "rows": db.execute(f"SELECT COUNT(*) FROM {quote(t)}").fetchone()[0],
                "columns": len(get_columns(t)),
            }
            for t in list_tables()
        ]
        stats, on_duty, recent, officers = None, [], [], {}
        if lspd_ready():
            one = lambda sql: db.execute(sql).fetchone()[0]  # noqa: E731
            stats = {
                "officers": one('SELECT COUNT(*) FROM "dustojnici"'),
                "cadets": one(
                    'SELECT COUNT(*) FROM "dustojnici" d JOIN "hodnosti" h '
                    'ON h.id = d."hodnost" WHERE h."zkratka" = \'CDT\''
                ),
                "on_duty": one('SELECT COUNT(*) FROM "sluzby" WHERE "konec" IS NULL'),
                "trainings": one(
                    'SELECT COUNT(*) FROM "absolvovane_vycviky" WHERE "splneno" = 1'
                ),
            }
            on_duty = db.execute(
                'SELECT s.id, s."zacatek", s."unit", d."jmeno", d."volacka", '
                'p."jmeno" AS partner FROM "sluzby" s '
                'LEFT JOIN "dustojnici" d ON d.id = s."dustojnik" '
                'LEFT JOIN "dustojnici" p ON p.id = s."partner" '
                'WHERE s."konec" IS NULL ORDER BY s."zacatek"'
            ).fetchall()
            recent = db.execute(
                'SELECT a."datum", a."body", a."splneno", d."jmeno", v."nazev" AS vycvik, '
                'i."jmeno" AS instruktor FROM "absolvovane_vycviky" a '
                'LEFT JOIN "dustojnici" d ON d.id = a."dustojnik" '
                'LEFT JOIN "vycviky" v ON v.id = a."vycvik" '
                'LEFT JOIN "dustojnici" i ON i.id = a."instruktor" '
                'ORDER BY a."datum" DESC, a.id DESC LIMIT 8'
            ).fetchall()
            officers = ref_options("dustojnici")
        return render_template(
            "index.html", tables=tables, stats=stats, on_duty=on_duty,
            recent=recent, officers=officers,
        )

    @app.post("/sluzba/start")
    def duty_start():
        if not lspd_ready():
            abort(404)
        try:
            officer = convert_value(request.form.get("dustojnik"), "REF")
            partner = convert_value(request.form.get("partner"), "REF")
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("index"))
        if officer is None:
            flash("Vyber důstojníka", "error")
            return redirect(url_for("index"))
        db = get_db()
        if db.execute(
            'SELECT 1 FROM "sluzby" WHERE "dustojnik" = ? AND "konec" IS NULL', [officer]
        ).fetchone():
            flash("Důstojník už je ve službě", "error")
            return redirect(url_for("index"))
        try:
            insert_row("sluzby", {
                "dustojnik": officer,
                "zacatek": now_str(),
                "unit": request.form.get("unit", "").strip() or None,
                "partner": partner,
            })
            db.commit()
        except sqlite3.IntegrityError:
            flash("Neexistující důstojník", "error")
            return redirect(url_for("index"))
        flash("Služba zahájena", "success")
        return redirect(url_for("index"))

    @app.post("/sluzba/<int:shift_id>/end")
    def duty_end(shift_id):
        if not lspd_ready():
            abort(404)
        db = get_db()
        db.execute(
            'UPDATE "sluzby" SET "konec" = ? WHERE id = ? AND "konec" IS NULL',
            [now_str(), shift_id],
        )
        db.commit()
        flash("Služba ukončena", "success")
        return redirect(url_for("index"))

    @app.route("/vycvik")
    def training():
        if not lspd_ready():
            abort(404)
        categories, rows, total = training_overview(get_db())
        return render_template("training.html", categories=categories, rows=rows, total=total)

    @app.route("/vycvik/<int:officer_id>")
    def officer_training(officer_id):
        if not lspd_ready():
            abort(404)
        db = get_db()
        officer = db.execute(
            'SELECT d.*, h."nazev" AS hodnost_nazev FROM "dustojnici" d '
            'LEFT JOIN "hodnosti" h ON h.id = d."hodnost" WHERE d.id = ?',
            [officer_id],
        ).fetchone()
        if officer is None:
            abort(404)
        modules = db.execute(
            'SELECT v.id, v."nazev", v."povinny", k."nazev" AS kategorie, '
            'a."datum", a."body", a."splneno", i."jmeno" AS instruktor '
            'FROM "vycviky" v LEFT JOIN "kategorie" k ON k.id = v."kategorie" '
            'LEFT JOIN "absolvovane_vycviky" a ON a.id = ('
            '  SELECT a2.id FROM "absolvovane_vycviky" a2 '
            '  WHERE a2."vycvik" = v.id AND a2."dustojnik" = ? '
            '  ORDER BY a2."splneno" DESC, a2."datum" DESC, a2.id DESC LIMIT 1) '
            'LEFT JOIN "dustojnici" i ON i.id = a."instruktor" '
            'ORDER BY k."poradi", k.id, v.id',
            [officer_id],
        ).fetchall()
        groups = {}
        for m in modules:
            groups.setdefault(m["kategorie"] or "Bez kategorie", []).append(m)
        completed = sum(1 for m in modules if m["splneno"])
        return render_template(
            "officer.html", officer=officer, groups=groups,
            completed=completed, total=len(modules),
        )

    @app.route("/tables/new", methods=["GET", "POST"])
    def create_table():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            try:
                quote(name)
                if table_exists(name) or name.lower().startswith("sqlite_"):
                    raise ValueError(f"Tabulka „{name}“ již existuje nebo je rezervovaná")
                columns = parse_column_defs(request.form)
                if not columns:
                    raise ValueError("Přidej alespoň jeden sloupec")
            except ValueError as exc:
                flash(str(exc), "error")
                return render_template("create_table.html", form=request.form), 400
            col_sql = ", ".join(f"{quote(n)} {t}" for n, t in columns)
            db = get_db()
            db.execute(
                f"CREATE TABLE {quote(name)} "
                f"(id INTEGER PRIMARY KEY AUTOINCREMENT, {col_sql})"
            )
            db.commit()
            flash(f"Tabulka „{name}“ vytvořena", "success")
            return redirect(url_for("view_table", table=name))
        return render_template("create_table.html", form={})

    @app.route("/t/<table>")
    def view_table(table):
        columns = require_table(table)
        col_names = [c["name"] for c in columns]
        q = request.args.get("q", "").strip()
        sort = request.args.get("sort", "id")
        direction = "DESC" if request.args.get("dir") == "desc" else "ASC"
        if sort not in col_names and sort != "id":
            sort = "id"
        page = max(request.args.get("page", 1, type=int), 1)

        where, params = "", []
        if q:
            conds = ['CAST("id" AS TEXT) LIKE ?']
            for c in columns:
                if c["ref"]:
                    conds.append(
                        f"{quote(c['name'])} IN (SELECT id FROM {quote(c['ref'])} "
                        f"WHERE CAST({quote(label_column(c['ref']))} AS TEXT) LIKE ?)"
                    )
                else:
                    conds.append(f"CAST({quote(c['name'])} AS TEXT) LIKE ?")
            where = "WHERE " + " OR ".join(conds)
            params = [f"%{q}%"] * len(conds)

        db = get_db()
        total = db.execute(
            f"SELECT COUNT(*) FROM {quote(table)} {where}", params
        ).fetchone()[0]
        pages = max((total + PAGE_SIZE - 1) // PAGE_SIZE, 1)
        page = min(page, pages)
        rows = db.execute(
            f"SELECT * FROM {quote(table)} {where} "
            f"ORDER BY {quote(sort)} {direction} LIMIT ? OFFSET ?",
            [*params, PAGE_SIZE, (page - 1) * PAGE_SIZE],
        ).fetchall()
        return render_template(
            "table.html",
            table=table,
            columns=columns,
            refs=ref_maps(columns),
            rows=rows,
            q=q,
            sort=sort,
            direction=direction.lower(),
            page=page,
            pages=pages,
            total=total,
        )

    def render_row_form(table, columns, row, row_id=None, status=200):
        return render_template(
            "row_form.html", table=table, columns=columns, row=row,
            row_id=row_id, refs=ref_maps(columns),
        ), status

    @app.route("/t/<table>/add", methods=["GET", "POST"])
    def add_row(table):
        columns = require_table(table)
        if request.method == "POST":
            values, errors = values_from_form(columns, request.form)
            if not errors:
                try:
                    insert_row(table, values)
                    get_db().commit()
                except sqlite3.IntegrityError as exc:
                    errors.append(f"Neplatný odkaz: {exc}")
            if errors:
                for e in errors:
                    flash(e, "error")
                return render_row_form(table, columns, request.form, status=400)
            flash("Záznam přidán", "success")
            return redirect(request.args.get("next") or url_for("view_table", table=table))
        return render_row_form(table, columns, request.args)

    @app.route("/t/<table>/<int:row_id>/edit", methods=["GET", "POST"])
    def edit_row(table, row_id):
        columns = require_table(table)
        db = get_db()
        row = db.execute(
            f"SELECT * FROM {quote(table)} WHERE id = ?", [row_id]
        ).fetchone()
        if row is None:
            abort(404)
        if request.method == "POST":
            values, errors = values_from_form(columns, request.form)
            if not errors and values:
                try:
                    db.execute(
                        f"UPDATE {quote(table)} SET "
                        + ", ".join(f"{quote(c)} = ?" for c in values)
                        + " WHERE id = ?",
                        [*values.values(), row_id],
                    )
                    db.commit()
                except sqlite3.IntegrityError as exc:
                    errors.append(f"Neplatný odkaz: {exc}")
            if errors:
                for e in errors:
                    flash(e, "error")
                return render_row_form(table, columns, request.form, row_id, 400)
            flash("Záznam uložen", "success")
            return redirect(url_for("view_table", table=table))
        return render_row_form(table, columns, row, row_id)

    @app.post("/t/<table>/<int:row_id>/delete")
    def delete_row(table, row_id):
        require_table(table)
        db = get_db()
        db.execute(f"DELETE FROM {quote(table)} WHERE id = ?", [row_id])
        db.commit()
        flash("Záznam smazán", "success")
        return redirect(url_for("view_table", table=table))

    @app.post("/t/<table>/columns")
    def add_column(table):
        columns = require_table(table)
        try:
            new = parse_column_defs(request.form)
            existing = {c["name"].lower() for c in columns} | {"id"}
            for name, _ in new:
                if name.lower() in existing:
                    raise ValueError(f"Sloupec „{name}“ již existuje")
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("view_table", table=table))
        db = get_db()
        for name, sql_type in new:
            db.execute(f"ALTER TABLE {quote(table)} ADD COLUMN {quote(name)} {sql_type}")
        db.commit()
        if new:
            flash("Sloupec přidán", "success")
        return redirect(url_for("view_table", table=table))

    @app.post("/t/<table>/delete")
    def drop_table(table):
        require_table(table)
        users = referencing_tables(table)
        if users:
            flash(
                f"Tabulku „{table}“ nelze smazat, odkazují na ni: {', '.join(users)}",
                "error",
            )
            return redirect(url_for("view_table", table=table))
        db = get_db()
        db.execute(f"DROP TABLE {quote(table)}")
        db.commit()
        flash(f"Tabulka „{table}“ smazána", "success")
        return redirect(url_for("index"))

    @app.route("/t/<table>/export.csv")
    def export_csv(table):
        columns = require_table(table)
        names = ["id", *(c["name"] for c in columns)]
        rows = get_db().execute(f"SELECT * FROM {quote(table)} ORDER BY id").fetchall()
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(names)
        for r in rows:
            writer.writerow([r[n] for n in names])
        return Response(
            "\ufeff" + buf.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={table}.csv"},
        )

    @app.post("/t/<table>/import")
    def import_csv(table):
        columns = require_table(table)
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Vyber CSV soubor", "error")
            return redirect(url_for("view_table", table=table))
        text = file.read().decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        known = {c["name"]: c for c in columns}
        usable = [h for h in (reader.fieldnames or []) if h in known]
        if not usable:
            flash("CSV neobsahuje žádný sloupec této tabulky", "error")
            return redirect(url_for("view_table", table=table))
        db = get_db()
        count, errors = 0, []
        for line, rec in enumerate(reader, start=2):
            try:
                values = {h: convert_value(rec.get(h), known[h]["type"]) for h in usable}
                insert_row(table, values)
            except (ValueError, sqlite3.IntegrityError) as exc:
                errors.append(f"Řádek {line}: {exc}")
                continue
            count += 1
        db.commit()
        flash(f"Importováno {count} záznamů", "success")
        for e in errors[:10]:
            flash(e, "error")
        return redirect(url_for("view_table", table=table))

    @app.route("/sql", methods=["GET", "POST"])
    def sql_console():
        query = request.form.get("query", "").strip()
        result, error = None, None
        if request.method == "POST" and query:
            uri = f"file:{os.path.abspath(app.config['DATABASE'])}?mode=ro"
            conn = sqlite3.connect(uri, uri=True)
            try:
                cur = conn.execute(query)
                headers = [d[0] for d in cur.description or []]
                result = {"headers": headers, "rows": cur.fetchmany(1000)}
            except sqlite3.Error as exc:
                error = str(exc)
            finally:
                conn.close()
        return render_template("sql.html", query=query, result=result, error=error)


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
