"""Genera posts 1080x1350 para Instagram de Chippys sobre fotos reales.

Uso: python make_post.py <foto> <salida.jpg> <estilo> [args...]
Estilos:
  horario  -> titulo + bloque de horario + dirección
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H = 1080, 1350
YELLOW = (255, 196, 0)
BLACK = (15, 15, 15)
WHITE = (255, 255, 255)
F = "C:/Windows/Fonts/"


def font(name, size):
    return ImageFont.truetype(F + name, size)


def cover(img, w=W, h=H, focus_y=0.5):
    img = ImageOps.exif_transpose(img).convert("RGB")
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = (img.width - w) // 2
    y = int((img.height - h) * focus_y)
    return img.crop((x, y, x + w, y + h))


def gradient(base, top=0.0, bottom=0.0, top_h=0.35, bottom_h=0.45):
    ov = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(ov)
    for y in range(H):
        a = 0
        if y < H * top_h:
            a = max(a, int(255 * top * (1 - y / (H * top_h))))
        if y > H * (1 - bottom_h):
            a = max(a, int(255 * bottom * ((y - H * (1 - bottom_h)) / (H * bottom_h))))
        d.line([(0, y), (W, y)], fill=a)
    black = Image.new("RGB", (W, H), BLACK)
    return Image.composite(black, base, ov)


def fit(d, txt, name, max_size, max_w=960):
    size = max_size
    while size > 20 and d.textlength(txt, font=font(name, size)) > max_w:
        size -= 4
    return font(name, size)


def text_c(d, y, txt, f, fill, stroke=0, stroke_fill=BLACK):
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def tag(d, x, y, txt, f, bg=YELLOW, fg=BLACK, pad=(22, 10)):
    w = d.textlength(txt, font=f)
    bb = f.getbbox(txt)
    h = bb[3] - bb[1]
    d.rounded_rectangle([x, y, x + w + pad[0] * 2, y + h + pad[1] * 2 + 6], radius=14, fill=bg)
    d.text((x + pad[0], y + pad[1] - bb[1] + 3), txt, font=f, fill=fg)
    return w + pad[0] * 2


def horario(photo, out, kicker, title):
    img = gradient(cover(Image.open(photo), focus_y=0.55), top=0.85, bottom=0.92, top_h=0.38, bottom_h=0.5)
    d = ImageDraw.Draw(img)
    text_c(d, 60, kicker, font("bahnschrift.ttf", 40), YELLOW)
    ft = fit(d, title, "impact.ttf", 150)
    text_c(d, 110, title, ft, WHITE, stroke=3)
    tw = d.textlength(title, font=ft)
    d.rectangle([(W - tw) / 2, 110 + ft.size + 18, (W + tw) / 2, 110 + ft.size + 30], fill=YELLOW)

    rows = [("LUNES", "CERRADO"), ("MAR a JUE", "14:00 - 23:00"),
            ("VIE y SÁB", "14:00 - 01:00"), ("DOMINGO", "15:00 - 23:00")]
    fl = font("seguibl.ttf", 42)
    fr = font("bahnschrift.ttf", 44)
    y = 960
    for i, (a, b) in enumerate(rows):
        col = (170, 170, 170) if b == "CERRADO" else WHITE
        d.text((150, y), a, font=fl, fill=YELLOW if b != "CERRADO" else (170, 170, 170))
        wb = d.textlength(b, font=fr)
        d.text((W - 150 - wb, y + 2), b, font=fr, fill=col)
        y += 62
        if i < len(rows) - 1:
            d.line([(150, y - 8), (W - 150, y - 8)], fill=(255, 255, 255, 60), width=1)
    fa = font("bahnschrift.ttf", 32)
    text_c(d, y + 22, "Loma Redonda 1 Pte. esq. Paso Alto · Puente Alto", fa, WHITE)
    img.save(out, quality=92)


RED = (200, 30, 30)
INK = (25, 25, 25)


def paper_sign(lines, w=640, angle=-4):
    """Cartel de cartulina con texto a mano. lines: [(texto, tamaño, color)]."""
    pad = 56
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    rows = []
    for txt, size, col in lines:
        f = font("Inkfree.ttf", size)
        while d0.textlength(txt, font=f) > w - pad * 2 and size > 20:
            size -= 4
            f = font("Inkfree.ttf", size)
        bb = f.getbbox(txt)
        rows.append((txt, f, col, bb[3] - bb[1], bb[1]))
    h = pad * 2 + sum(r[3] for r in rows) + 26 * (len(rows) - 1)
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, w, h], fill=(246, 241, 228, 255))
    # textura sutil de papel
    import random
    rnd = random.Random(7)
    for _ in range(2500):
        x, y = rnd.randrange(w), rnd.randrange(h)
        c = rnd.randint(225, 240)
        d.point((x, y), fill=(c, c - 4, c - 14, 255))
    y = pad
    for txt, f, col, th, top in rows:
        tw = d.textlength(txt, font=f)
        x = (w - tw) / 2
        weight = 3 if f.size >= 90 else 1.5  # trazo grueso tipo plumón
        steps = [(dx, dy) for dx in (0, weight / 2, weight) for dy in (0, weight / 2)]
        for dx, dy in steps:
            d.text((x + dx, y - top + dy), txt, font=f, fill=col)
        y += th + 26
    # cinta adhesiva
    full = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    full.alpha_composite(card, (40, 40))
    for cx in (40 + 10, 40 + w - 10):
        tape = Image.new("RGBA", (120, 38), (235, 225, 190, 200))
        tape = tape.rotate(40 if cx < w / 2 else -40, expand=True)
        full.alpha_composite(tape, (int(cx - tape.width / 2), 40 - tape.height // 2))
    card = full.rotate(angle, expand=True, resample=Image.BICUBIC)
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 150), mask=card.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    return card, shadow


def cartel(photo, out, *lines_spec):
    """lines_spec: 'texto|tamaño|r' (r=rojo, k=negro)."""
    img = cover(Image.open(photo), focus_y=0.4).convert("RGBA")
    img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 40)))
    lines = []
    for s in lines_spec:
        txt, size, c = s.split("|")
        lines.append((txt, int(size), RED if c == "r" else INK))
    card, shadow = paper_sign(lines)
    x = (W - card.width) // 2
    y = H - card.height - 70
    img.alpha_composite(shadow, (x + 12, y + 22))
    img.alpha_composite(card, (x, y))
    img.convert("RGB").save(out, quality=92)


if __name__ == "__main__":
    photo, out, style, *args = sys.argv[1:]
    {"horario": horario, "cartel": cartel}[style](photo, out, *args)
