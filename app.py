import csv
import io
import os
import re
import sqlite3

from flask import (
    Flask,
    Response,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

COLUMN_TYPES = {
    "TEXT": "Text",
    "INTEGER": "Celé číslo",
    "REAL": "Desetinné číslo",
    "DATE": "Datum",
    "BOOLEAN": "Ano/Ne",
}
IDENTIFIER_RE = re.compile(r"^[^\W\d]\w{0,62}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PAGE_SIZE = 25


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.environ.get(
            "DATABASE_PATH", os.path.join(app.instance_path, "database.sqlite")
        ),
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(os.path.dirname(os.path.abspath(app.config["DATABASE"])), exist_ok=True)

    app.teardown_appcontext(close_db)
    register_routes(app)
    return app


def get_db():
    if "db" not in g:
        from flask import current_app

        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
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
    rows = get_db().execute(f"PRAGMA table_info({quote(table)})").fetchall()
    return [
        {"name": r["name"], "type": (r["type"] or "TEXT").upper()}
        for r in rows
        if r["name"] != "id"
    ]


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
    if col_type == "INTEGER":
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
    columns, seen = [], set()
    for name, col_type in zip(names, types):
        name = name.strip()
        if not name:
            continue
        if not IDENTIFIER_RE.match(name) or name.lower() == "id":
            raise ValueError(f"Neplatný název sloupce: „{name}“")
        if name.lower() in seen:
            raise ValueError(f"Duplicitní sloupec: „{name}“")
        if col_type not in COLUMN_TYPES:
            raise ValueError(f"Neplatný typ sloupce: „{col_type}“")
        seen.add(name.lower())
        columns.append((name, col_type))
    return columns


def register_routes(app):
    @app.context_processor
    def inject_globals():
        return {"all_tables": list_tables(), "column_types": COLUMN_TYPES}

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
        return render_template("index.html", tables=tables)

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
        if q and col_names:
            where = "WHERE " + " OR ".join(
                f"CAST({quote(c)} AS TEXT) LIKE ?" for c in ["id", *col_names]
            )
            params = [f"%{q}%"] * (len(col_names) + 1)

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
            rows=rows,
            q=q,
            sort=sort,
            direction=direction.lower(),
            page=page,
            pages=pages,
            total=total,
        )

    @app.route("/t/<table>/add", methods=["GET", "POST"])
    def add_row(table):
        columns = require_table(table)
        if request.method == "POST":
            values, errors = values_from_form(columns, request.form)
            if errors:
                for e in errors:
                    flash(e, "error")
                return render_template(
                    "row_form.html", table=table, columns=columns, row=request.form
                ), 400
            insert_row(table, values)
            get_db().commit()
            flash("Záznam přidán", "success")
            return redirect(url_for("view_table", table=table))
        return render_template("row_form.html", table=table, columns=columns, row={})

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
            if errors:
                for e in errors:
                    flash(e, "error")
                return render_template(
                    "row_form.html",
                    table=table,
                    columns=columns,
                    row=request.form,
                    row_id=row_id,
                ), 400
            if values:
                db.execute(
                    f"UPDATE {quote(table)} SET "
                    + ", ".join(f"{quote(c)} = ?" for c in values)
                    + " WHERE id = ?",
                    [*values.values(), row_id],
                )
                db.commit()
            flash("Záznam uložen", "success")
            return redirect(url_for("view_table", table=table))
        return render_template(
            "row_form.html", table=table, columns=columns, row=row, row_id=row_id
        )

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
        for name, col_type in new:
            db.execute(f"ALTER TABLE {quote(table)} ADD COLUMN {quote(name)} {col_type}")
        db.commit()
        if new:
            flash("Sloupec přidán", "success")
        return redirect(url_for("view_table", table=table))

    @app.post("/t/<table>/delete")
    def drop_table(table):
        require_table(table)
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
            except ValueError as exc:
                errors.append(f"Řádek {line}: {exc}")
                continue
            insert_row(table, values)
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
