"""Renders LSPD MANUAL categories as PNG study sheets (e.g. for Discord)."""
import io
import os

from PIL import Image, ImageDraw, ImageFont

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "fonts")
WIDTH = 1080
PAD = 48
NAVY = "#0b1a33"
GOLD = "#d4a017"
BG = "#eef1f7"
TEXT = "#1f2430"
MUTED = "#6b7280"
BORDER = "#e3e5ec"


def _font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def _wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and draw.textlength(candidate, font=font) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def _bullets(text):
    return [b.strip() for b in (text or "").split("\n") if b.strip()]


def _header(draw, title, subtitle, color, height):
    draw.rectangle([0, 0, WIDTH, height], fill=NAVY)
    draw.rectangle([0, height - 10, WIDTH, height], fill=color)
    draw.text((PAD, 38), "★ LSPD MANUAL", font=_font(26, True), fill=GOLD)
    draw.text((PAD, 78), title, font=_font(46, True), fill="white")
    draw.text((PAD, 142), subtitle, font=_font(22), fill="#cbd2e0")


def _footer(draw, height):
    draw.text(
        (WIDTH / 2, height - 34), "LSPD MANUAL · Los Santos Police Department",
        font=_font(18), fill=MUTED, anchor="mm",
    )


def _save(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def render_category(category):
    """category: dict with nazev, barva and modules = [{nazev, popis}]."""
    color = category["barva"]
    modules = category["modules"]
    f_title, f_body, f_num = _font(30, True), _font(22), _font(20, True)
    card_pad, line_h, header_h = 28, 32, 200
    text_x = PAD + 12 + card_pad + 28
    text_w = WIDTH - PAD - card_pad - text_x
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    blocks = []
    for module in modules:
        bullets = [_wrap(measure, b, f_body, text_w) for b in _bullets(module["popis"])]
        body_h = sum(len(lines) * line_h + 8 for lines in bullets)
        blocks.append((module, bullets, 2 * card_pad + 56 + body_h))
    height = header_h + PAD + sum(h + 20 for *_, h in blocks) + 70

    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    _header(
        draw, category["nazev"] or "Bez názvu",
        f"{len(modules)} modulů · výukový materiál pro kadety", color, header_h,
    )
    y = header_h + PAD
    for number, (module, bullets, h) in enumerate(blocks, start=1):
        draw.rounded_rectangle([PAD, y, WIDTH - PAD, y + h], radius=16, fill="white", outline=BORDER)
        draw.rounded_rectangle([PAD, y, PAD + 10, y + h], radius=5, fill=color)
        x, ty = PAD + 12 + card_pad, y + card_pad
        draw.ellipse([x, ty, x + 40, ty + 40], fill=color)
        draw.text((x + 20, ty + 20), str(number), font=f_num, fill="white", anchor="mm")
        draw.text((x + 56, ty + 20), module["nazev"] or "", font=f_title, fill=TEXT, anchor="lm")
        ty += 56
        for lines in bullets:
            draw.ellipse([x + 6, ty + 10, x + 16, ty + 20], fill=color)
            for line in lines:
                draw.text((text_x, ty), line, font=f_body, fill=TEXT)
                ty += line_h
            ty += 8
        y += h + 20
    _footer(draw, height)
    return _save(img)


def render_overview(categories):
    """Table of contents: every category with its modules."""
    f_cat, f_mod = _font(26, True), _font(22)
    header_h, row_h, col_w = 200, 36, (WIDTH - 2 * PAD - 40) // 2
    blocks = []
    for category in categories:
        rows = (len(category["modules"]) + 1) // 2
        blocks.append((category, 60 + 18 + rows * row_h + 10))
    height = header_h + PAD + sum(h + 22 for _, h in blocks) + 70
    total = sum(len(c["modules"]) for c in categories)

    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    _header(draw, "Obsah výcviku", f"{len(categories)} kategorií · {total} modulů", GOLD, header_h)
    y = header_h + PAD
    for category, h in blocks:
        color = category["barva"]
        draw.rounded_rectangle([PAD, y, WIDTH - PAD, y + h], radius=16, fill="white", outline=BORDER)
        draw.rounded_rectangle([PAD, y, WIDTH - PAD, y + 60], radius=16, fill=color)
        draw.rectangle([PAD, y + 40, WIDTH - PAD, y + 60], fill=color)
        draw.text((PAD + 24, y + 30), category["nazev"] or "Bez názvu", font=f_cat, fill="white", anchor="lm")
        draw.text(
            (WIDTH - PAD - 24, y + 30), f"{len(category['modules'])} modulů",
            font=_font(20, True), fill="white", anchor="rm",
        )
        rows = (len(category["modules"]) + 1) // 2
        for i, module in enumerate(category["modules"]):
            col, row = divmod(i, rows) if rows else (0, 0)
            mx = PAD + 24 + col * (col_w + 20)
            my = y + 78 + row * row_h
            draw.ellipse([mx, my + 8, mx + 10, my + 18], fill=color)
            draw.text((mx + 22, my), f"{i + 1}. {module['nazev'] or ''}", font=f_mod, fill=TEXT)
        y += h + 22
    _footer(draw, height)
    return _save(img)
