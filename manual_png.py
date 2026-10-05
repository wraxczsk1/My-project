import io
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

import manual_store
from manual_content import MANUAL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "static", "fonts")
IMG_DIR = os.path.join(BASE_DIR, "static", "manual")

W = 1080
MARGIN = 40
PAD = 40
CW = W - 2 * (MARGIN + PAD)
HEADER_H = 230
TAPE_H = 38
FOOTER_H = 70
CARD_TOP = 30
MAX_CONTENT_H = 1450
MAX_IMG_H = 1250
NAVY = "#0b1a33"
BG = "#08111f"
TEXT = "#1f2430"
MUTED = "#5b6474"
GOLD = "#d4a017"

CODE_COLORS = {
    "status": "#eab308",
    "oznameni": "#16a34a",
    "dispatch": "#0891b2",
    "emergency": "#dc2626",
    "prikaz": "#ea580c",
}
CODE_LABELS = {
    "status": "Status",
    "oznameni": "Oznámení",
    "dispatch": "Typ dispatch callu",
    "emergency": "Emergency call",
    "prikaz": "Příkazové kódy",
}

CODE_DESC = {
    "status": "stav jednotky",
    "oznameni": "předání informace",
    "dispatch": "typ výjezdu / callu",
    "emergency": "nouze, nejvyšší priorita",
    "prikaz": "pokyn nebo žádost",
}
CODE_SHORT = {
    "status": "Status",
    "oznameni": "Oznámení",
    "dispatch": "Dispatch",
    "emergency": "Emergency",
    "prikaz": "Příkaz",
}


def parse(text):
    blocks = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            blocks.append({"type": "heading", "text": line.lstrip("#").strip().strip("_").strip()})
        elif line == "[legenda]":
            blocks.append({"type": "legend"})
        elif line.startswith("-"):
            blocks.append({"type": "bullet", "text": line[1:].strip()})
        elif line.startswith("!"):
            blocks.append({"type": "warn", "text": line[1:].strip()})
        elif line.startswith(">"):
            blocks.append({"type": "quote", "text": line[1:].strip()})
        elif "|" in line:
            parts = [p.strip() for p in line.split("|")]
            kind = parts[2] if len(parts) > 2 and parts[2] in CODE_COLORS else "info"
            row = {"code": parts[0], "text": parts[1], "kind": kind}
            if blocks and blocks[-1]["type"] == "codes":
                blocks[-1]["rows"].append(row)
            else:
                blocks.append({"type": "codes", "rows": [row]})
        else:
            blocks.append({"type": "para", "text": line})
    return blocks


def image_path(name):
    for folder in (IMG_DIR, manual_store.upload_dir()):
        path = os.path.join(folder, os.path.basename(name))
        if os.path.isfile(path):
            return path
    return None


def mix(color, other, t):
    a = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


@lru_cache(maxsize=None)
def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


@lru_cache(maxsize=None)
def head_font(size):
    return ImageFont.truetype(os.path.join(FONT_DIR, "Rajdhani-Bold.ttf"), size)


def wrap(text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        while fnt.getlength(word) > width:
            cut = len(word)
            while cut > 1 and fnt.getlength(word[:cut]) > width:
                cut -= 1
            if line:
                lines.append(line)
                line = ""
            lines.append(word[:cut])
            word = word[cut:]
        candidate = f"{line} {word}".strip()
        if line and fnt.getlength(candidate) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines or [""]


class Unit:
    def __init__(self, height, draw, keep_with_next=False, tags=()):
        self.height = height
        self.draw = draw
        self.keep_with_next = keep_with_next
        self.tags = set(tags)


def _text_lines(d, x, y, lines, fnt, fill, lh):
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=fnt, fill=fill)


def heading_unit(text, color):
    fnt = head_font(34)
    label = text.upper()

    def draw(img, d, x, y):
        cy = y + 44
        d.polygon([(x, cy), (x + 10, cy - 10), (x + 20, cy), (x + 10, cy + 10)], fill=color)
        d.text((x + 34, cy + 1), label, font=fnt, fill=NAVY, anchor="lm")
        d.line((x, y + 70, x + CW, y + 70), fill=mix(color, "#ffffff", 0.6), width=2)

    return Unit(86, draw, keep_with_next=True, tags={"heading"})


def bullet_unit(text, color):
    fnt, lh = font(29), 41
    lines = wrap(text, fnt, CW - 36)

    def draw(img, d, x, y):
        d.ellipse((x + 4, y + 13, x + 18, y + 27), fill=color)
        _text_lines(d, x + 36, y, lines, fnt, TEXT, lh)

    return Unit(len(lines) * lh + 8, draw, tags={"bullet"})


def para_unit(text):
    fnt, lh = font(28), 40
    lines = wrap(text, fnt, CW)

    def draw(img, d, x, y):
        _text_lines(d, x, y, lines, fnt, MUTED, lh)

    return Unit(len(lines) * lh + 14, draw)


def box_unit(text, fnt, bar, fill, ink, lh=38, tag=None):
    lines = wrap(text, fnt, CW - 52)
    box_h = len(lines) * lh + 28

    def draw(img, d, x, y):
        d.rounded_rectangle((x, y + 6, x + CW, y + 6 + box_h), radius=12, fill=fill)
        d.rounded_rectangle((x, y + 6, x + 9, y + 6 + box_h), radius=4, fill=bar)
        _text_lines(d, x + 30, y + 20, lines, fnt, ink, lh)

    return Unit(box_h + 16, draw, tags={tag} if tag else ())


def legend_unit():
    fnt = font(22, True)
    chips = [(CODE_LABELS[k], c) for k, c in CODE_COLORS.items()]
    rows, row, width = [], [], 0
    for label, color in chips:
        w = fnt.getlength(label) + 32
        if row and width + w > CW:
            rows.append(row)
            row, width = [], 0
        row.append((label, color, w))
        width += w + 12
    rows.append(row)

    def draw(img, d, x, y):
        for r, items in enumerate(rows):
            cx = x
            for label, color, w in items:
                top = y + 6 + r * 52
                d.rounded_rectangle((cx, top, cx + w, top + 40), radius=20, fill=color)
                ink = TEXT if color == CODE_COLORS["status"] else "#ffffff"
                d.text((cx + w / 2, top + 20), label, font=fnt, fill=ink, anchor="mm")
                cx += w + 12

    return Unit(len(rows) * 52 + 12, draw)


def code_units(rows, color):
    cols, gap = 3, 14
    code_font, label_font, text_font, lh = font(30, True), font(16, True), font(24), 30
    head_h = 52
    col_w = (CW - gap * (cols - 1)) / cols
    units = []
    for i in range(0, len(rows), cols):
        group = [(r, wrap(r["text"], text_font, col_w - 28)) for r in rows[i:i + cols]]
        tile_h = head_h + max(len(t) for _, t in group) * lh + 24

        def draw(img, d, x, y, group=group, tile_h=tile_h):
            for col, (r, text_lines) in enumerate(group):
                cx = x + col * (col_w + gap)
                chip = CODE_COLORS.get(r["kind"], color)
                ink = TEXT if r["kind"] == "status" else "#ffffff"
                d.rounded_rectangle((cx, y, cx + col_w, y + tile_h), radius=10, fill="#ffffff", outline=mix(chip, "#ffffff", 0.55), width=2)
                d.rounded_rectangle((cx, y, cx + col_w, y + head_h), radius=10, fill=chip)
                d.rectangle((cx, y + head_h - 10, cx + col_w, y + head_h), fill=chip)
                d.text((cx + 16, y + head_h / 2), r["code"], font=code_font, fill=ink, anchor="lm")
                label = CODE_SHORT.get(r["kind"])
                if label and code_font.getlength(r["code"]) + label_font.getlength(label) + 44 < col_w:
                    d.text((cx + col_w - 14, y + head_h / 2), label.upper(), font=label_font, fill=ink, anchor="rm")
                for n, ln in enumerate(text_lines):
                    d.text((cx + 14, y + head_h + 12 + n * lh + lh / 2), ln, font=text_font, fill=TEXT, anchor="lm")

        units.append(Unit(tile_h + 12, draw, tags={"code:" + r["kind"] for r, _ in group}))
    return units


def image_unit(path):
    with Image.open(path) as src:
        pic = src.convert("RGB")
    scale = min(CW / pic.width, MAX_IMG_H / pic.height)
    pic = pic.resize((round(pic.width * scale), round(pic.height * scale)), Image.LANCZOS)

    def draw(img, d, x, y):
        left = x + (CW - pic.width) // 2
        img.paste(pic, (left, y + 14))
        d.rectangle((left - 1, y + 13, left + pic.width, y + 14 + pic.height), outline="#d6dbe5")

    return Unit(pic.height + 28, draw, tags={"image"})


def image_pair_unit(paths):
    gap = 16
    cell_w = (CW - gap) / 2
    pics = []
    for path in paths:
        with Image.open(path) as src:
            pic = src.convert("RGB")
        scale = min(cell_w / pic.width, MAX_IMG_H / pic.height)
        pics.append(pic.resize((round(pic.width * scale), round(pic.height * scale)), Image.LANCZOS))
    row_h = max(p.height for p in pics)

    def draw(img, d, x, y):
        for i, pic in enumerate(pics):
            left = round(x + i * (cell_w + gap) + (cell_w - pic.width) / 2)
            top = y + 14 + (row_h - pic.height) // 2
            img.paste(pic, (left, top))
            d.rectangle((left - 1, top - 1, left + pic.width, top + pic.height), outline="#d6dbe5")

    return Unit(row_h + 28, draw, tags={"image"})


def video_unit(url):
    title_font, url_font = font(27, True), font(19)
    lines = wrap(url, url_font, CW - 52)
    box_h = 56 + len(lines) * 26 + 16

    def draw(img, d, x, y):
        d.rounded_rectangle((x, y + 6, x + CW, y + 6 + box_h), radius=12, fill="#eef0ff")
        d.rounded_rectangle((x, y + 6, x + 9, y + 6 + box_h), radius=4, fill="#4f46e5")
        d.text((x + 30, y + 22), "▶  Video ukázka (odkaz)", font=title_font, fill="#3730a3")
        _text_lines(d, x + 30, y + 62, lines, url_font, MUTED, 26)

    return Unit(box_h + 16, draw, tags={"video"})


def explain_unit(tags, color):
    items = []
    if "heading" in tags:
        items.append(("heading", color, "Nadpis – téma lekce"))
    if "bullet" in tags:
        items.append(("dot", color, "Bod k zapamatování"))
    if "warn" in tags:
        items.append(("bar", "#dc2626", "Pozor – důležité pravidlo"))
    if "quote" in tags:
        items.append(("bar", color, "Vzor hlášení / příklad"))
    for kind, kc in CODE_COLORS.items():
        if "code:" + kind in tags:
            items.append(("tile", kc, f"{CODE_SHORT[kind]} – {CODE_DESC[kind]}"))
    if "code:info" in tags:
        items.append(("tile", color, "Kód / pojem a jeho význam"))
    if "image" in tags:
        items.append(("image", "#64748b", "Obrázek k lekci"))
    if "video" in tags:
        items.append(("video", "#4f46e5", "Odkaz na video ukázku"))
    if not items:
        return None
    fnt, row_h = font(20), 40
    col_w = (CW - 48) / 2
    rows = (len(items) + 1) // 2
    box_h = 62 + rows * row_h + 10

    def draw(img, d, x, y):
        top = y + 22
        d.rounded_rectangle((x, top, x + CW, top + box_h), radius=12, fill="#f3f5f9", outline="#e1e6ef")
        d.rectangle((x, top + 10, x + 6, top + box_h - 10), fill=GOLD)
        d.text((x + 24, top + 30), "VYSVĚTLIVKY", font=head_font(26), fill=NAVY, anchor="lm")
        for i, (shape, c, label) in enumerate(items):
            ix = x + 24 + (i % 2) * col_w
            iy = top + 62 + (i // 2) * row_h + row_h / 2 - 6
            if shape == "heading":
                d.polygon([(ix + 2, iy), (ix + 11, iy - 9), (ix + 20, iy), (ix + 11, iy + 9)], fill=c)
            elif shape == "dot":
                d.ellipse((ix + 4, iy - 7, ix + 18, iy + 7), fill=c)
            elif shape == "bar":
                d.rounded_rectangle((ix, iy - 12, ix + 22, iy + 12), radius=4, fill=mix(c, "#ffffff", 0.82))
                d.rectangle((ix, iy - 12, ix + 5, iy + 12), fill=c)
            elif shape == "tile":
                d.rounded_rectangle((ix, iy - 12, ix + 22, iy + 12), radius=4, fill=c)
            elif shape == "image":
                d.rectangle((ix, iy - 10, ix + 22, iy + 10), outline=c, width=2)
                d.polygon([(ix + 3, iy + 8), (ix + 9, iy), (ix + 14, iy + 5), (ix + 17, iy + 2), (ix + 20, iy + 8)], fill=c)
            elif shape == "video":
                d.rounded_rectangle((ix, iy - 12, ix + 22, iy + 12), radius=4, fill=c)
                d.polygon([(ix + 8, iy - 6), (ix + 8, iy + 6), (ix + 16, iy)], fill="#ffffff")
            d.text((ix + 34, iy), label, font=fnt, fill=TEXT, anchor="lm")

    return Unit(box_h + 30, draw)


def module_units(module, color):
    units = []
    for b in parse(module["text"]):
        kind = b["type"]
        if kind == "heading":
            units.append(heading_unit(b["text"], color))
        elif kind == "bullet":
            units.append(bullet_unit(b["text"], color))
        elif kind == "warn":
            units.append(box_unit("⚠  " + b["text"], font(27, True), "#dc2626", "#fdecec", "#9b1c1c", tag="warn"))
        elif kind == "quote":
            units.append(box_unit(b["text"], font(27), color, mix(color, "#ffffff", 0.88), TEXT, tag="quote"))
        elif kind == "legend":
            continue
        elif kind == "codes":
            units.extend(code_units(b["rows"], color))
        else:
            units.append(para_unit(b["text"]))
    paths = [p for p in map(image_path, module.get("obrazky", [])) if p]
    for i in range(0, len(paths), 2):
        pair = paths[i:i + 2]
        units.append(image_pair_unit(pair) if len(pair) == 2 else image_unit(pair[0]))
    if module.get("video"):
        units.append(video_unit(module["video"]))
    return units


def paginate(units):
    pages, height = [[]], 0
    for unit in units:
        if pages[-1] and height + unit.height > MAX_CONTENT_H:
            carry = []
            while pages[-1] and pages[-1][-1].keep_with_next:
                carry.insert(0, pages[-1].pop())
            if not pages[-1]:
                pages[-1], carry = carry, []
            pages.append(carry)
            height = sum(u.height for u in carry)
        pages[-1].append(unit)
        height += unit.height
    return [p for p in pages if p]


def draw_shield(d, cx, cy, text):
    pts = [(cx - 54, cy - 46), (cx, cy - 64), (cx + 54, cy - 46), (cx + 54, cy + 6), (cx, cy + 62), (cx - 54, cy + 6)]
    d.polygon(pts, fill="#13254a")
    d.line(pts + [pts[0], pts[1]], fill=GOLD, width=5, joint="curve")
    fnt = head_font(46 if len(text) <= 3 else 38)
    d.text((cx, cy - 2), text, font=fnt, fill=GOLD, anchor="mm")


def draw_tape(d, y):
    d.rectangle((0, y, W, y + TAPE_H), fill="#facc15")
    d.line((0, y + 3, W, y + 3), fill="#111111", width=2)
    d.line((0, y + TAPE_H - 4, W, y + TAPE_H - 4), fill="#111111", width=2)
    fnt = font(17, True)
    chunk = "LSPD ACADEMY   ★   VÝCVIK KADETŮ   ★   "
    step = fnt.getlength(chunk)
    x = -20
    while x < W:
        d.text((x, y + TAPE_H / 2), chunk, font=fnt, fill="#111111", anchor="lm")
        x += step


def draw_header(d, color, kicker, title, subtitle, badge=None):
    d.rectangle((0, 0, W, HEADER_H), fill=NAVY)
    for gx in range(0, W, 36):
        d.line((gx, 10, gx, HEADER_H), fill="#0f2140")
    d.rectangle((0, 0, W // 2, 10), fill="#dc2626")
    d.rectangle((W // 2, 0, W, 10), fill="#2563eb")
    d.rectangle((0, 10, 10, HEADER_H), fill=color)
    d.rectangle((0, HEADER_H - 5, W, HEADER_H), fill=GOLD)
    x = MARGIN + 16
    star = "★ LSPD ACADEMY"
    d.text((x, 44), star, font=font(22, True), fill=GOLD)
    if kicker:
        sx = x + font(22, True).getlength(star)
        d.text((sx, 44), "  ·  " + kicker.upper(), font=font(22, True), fill=mix(color, "#ffffff", 0.45))
    title_font = head_font(76)
    max_w = W - 2 * x - (140 if badge else 0)
    while title_font.size > 44 and title_font.getlength(title.upper()) > max_w:
        title_font = head_font(title_font.size - 4)
    d.text((x, 122), title.upper(), font=title_font, fill="#ffffff", anchor="lm")
    d.text((x, 182), subtitle, font=font(23), fill="#c7d2e6", anchor="lm")
    if badge:
        draw_shield(d, W - MARGIN - 70, 116, badge)
    draw_tape(d, HEADER_H)


def draw_footer(d, height, text, more=False):
    y = height - FOOTER_H / 2
    d.text((MARGIN + 16, y), text, font=font(20), fill="#9fb0cc", anchor="lm")
    if more:
        d.text((W - MARGIN - 16, y), "Pokračování na další straně →", font=font(20, True), fill=GOLD, anchor="rm")


def to_png(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


@lru_cache(maxsize=None)
def module_pages(ci, mi):
    category = MANUAL[ci]
    module = category["moduly"][mi]
    color = category["barva"]
    pages = paginate(module_units(module, color))
    out = []
    for p, units in enumerate(pages, start=1):
        explain = explain_unit(set().union(*(u.tags for u in units)), color)
        if explain:
            units = units + [explain]
        content_h = sum(u.height for u in units)
        height = HEADER_H + TAPE_H + CARD_TOP + 2 * PAD + content_h + FOOTER_H
        img = Image.new("RGB", (W, height), BG)
        d = ImageDraw.Draw(img)
        subtitle = f"Kurz {ci + 1:02d}  ·  Lekce {ci + 1}.{mi + 1} z {len(category['moduly'])}"
        if len(pages) > 1:
            subtitle += f"   ·   strana {p}/{len(pages)}"
        draw_header(d, color, category["nazev"], module["nazev"], subtitle, badge=f"{ci + 1}.{mi + 1}")
        top = HEADER_H + TAPE_H + CARD_TOP
        d.rounded_rectangle((MARGIN, top, W - MARGIN, top + 2 * PAD + content_h), radius=18,
                            fill="#ffffff", outline="#dde2ec")
        y = top + PAD
        for unit in units:
            unit.draw(img, d, MARGIN + PAD, y)
            y += unit.height
        draw_footer(d, height, f"LSPD MANUAL · {category['nazev']} · {module['nazev']}", more=p < len(pages))
        out.append(to_png(img))
    return tuple(out)


@lru_cache(maxsize=None)
def overview_png():
    row_h, head_h, gap = 46, 66, 22
    col_w = (W - 2 * MARGIN - 2 * 28 - 16) / 2
    blocks = []
    for c in MANUAL:
        rows = (len(c["moduly"]) + 1) // 2
        blocks.append((c, head_h + 18 + rows * row_h + 14))
    height = HEADER_H + TAPE_H + CARD_TOP + sum(h + gap for _, h in blocks) + FOOTER_H
    img = Image.new("RGB", (W, height), BG)
    d = ImageDraw.Draw(img)
    total = sum(len(c["moduly"]) for c in MANUAL)
    draw_header(d, GOLD, None, "Obsah výcviku", f"{len(MANUAL)} kurzů · {total} lekcí · výcvikový materiál pro kadety")
    y = HEADER_H + TAPE_H + CARD_TOP
    for ci, (c, h) in enumerate(blocks, start=1):
        color = c["barva"]
        d.rounded_rectangle((MARGIN, y, W - MARGIN, y + h), radius=16, fill="#ffffff", outline="#dde2ec")
        d.rounded_rectangle((MARGIN, y, W - MARGIN, y + head_h), radius=16, fill=color)
        d.rectangle((MARGIN, y + head_h - 16, W - MARGIN, y + head_h), fill=color)
        d.text((MARGIN + 28, y + head_h / 2), f"KURZ {ci:02d} · {c['nazev'].upper()}", font=head_font(36), fill="#ffffff", anchor="lm")
        d.text((W - MARGIN - 28, y + head_h / 2), f"{len(c['moduly'])} {'lekce' if len(c['moduly']) < 5 else 'lekcí'}", font=font(22, True),
               fill=mix(color, "#ffffff", 0.75), anchor="rm")
        for i, m in enumerate(c["moduly"]):
            cx = MARGIN + 28 + (i % 2) * (col_w + 16)
            cy = y + head_h + 18 + (i // 2) * row_h
            d.ellipse((cx, cy + 2, cx + 34, cy + 36), fill=mix(color, "#ffffff", 0.82))
            d.text((cx + 17, cy + 19), f"{ci}.{i + 1}", font=font(15, True), fill=color, anchor="mm")
            d.text((cx + 48, cy + 19), m["nazev"], font=font(26), fill=TEXT, anchor="lm")
        y += h + gap
    draw_footer(d, height, "LSPD MANUAL · Los Santos Police Department")
    return to_png(img)
