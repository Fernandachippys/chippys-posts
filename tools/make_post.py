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


if __name__ == "__main__":
    photo, out, style, *args = sys.argv[1:]
    {"horario": horario}[style](photo, out, *args)
