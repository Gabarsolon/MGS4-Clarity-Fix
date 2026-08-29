"""Generate Nexus page media for MGS4 Clarity Fix.

Deliberately diagrammatic, not photographic: a banner and an explanation of the
viewport-scaling mechanism. Nothing here imitates a gameplay screenshot.
Everything is drawn at 2x and downsampled for clean edges.
"""
from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample factor
F = 'C:/Windows/Fonts/'

BG      = (18, 19, 15)
PANEL   = (28, 30, 24)
PANEL2  = (36, 39, 31)
LINE    = (58, 61, 48)
TEXT    = (232, 230, 220)
DIM     = (150, 152, 136)
FAINT   = (98, 100, 88)
AMBER   = (212, 169, 78)
GREEN   = (134, 178, 90)
RED     = (192, 91, 69)


def font(name, size):
    return ImageFont.truetype(F + name, size * S)


def px(v):
    return v * S


def text(d, xy, s, f, fill, anchor='la', spacing=None):
    if spacing is None:
        d.text((px(xy[0]), px(xy[1])), s, font=f, fill=fill, anchor=anchor)
    else:
        d.multiline_text((px(xy[0]), px(xy[1])), s, font=f, fill=fill,
                         anchor=anchor, spacing=spacing * S)


def rect(d, box, fill=None, outline=None, width=1, radius=0):
    b = [px(v) for v in box]
    if radius:
        d.rounded_rectangle(b, radius=px(radius), fill=fill, outline=outline,
                            width=px(width))
    else:
        d.rectangle(b, fill=fill, outline=outline, width=px(width))


def scanlines(img, step=4, alpha=10):
    """Faint horizontal banding -- reads as a technical readout, not a photo."""
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, img.size[1], step * S):
        d.line([(0, y), (img.size[0], y)], fill=(0, 0, 0, alpha), width=S)
    return Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')


def new(w, h):
    img = Image.new('RGB', (px(w), px(h)), BG)
    return img, ImageDraw.Draw(img)


def finish(img, w, h, path):
    img = scanlines(img)
    img = img.resize((w, h), Image.LANCZOS)
    img.save(path, quality=95)
    print(f'  wrote {path}  {w}x{h}')


def width_of(d, s, f):
    """Rendered width in layout units (undoes the supersample factor)."""
    return d.textlength(s, font=f) / S


def fit(d, s, name, size, max_w):
    """Shrink a font until the string fits max_w layout units."""
    while size > 8:
        f = font(name, size)
        if width_of(d, s, f) <= max_w:
            return f
        size -= 1
    return font(name, 8)


# --------------------------------------------------------------- header 1300x372
def header(path):
    W, H = 1300, 372
    img, d = new(W, H)
    BOX_X = 872           # everything on the left must clear this
    LEFT = 58
    avail = BOX_X - LEFT - 30

    # accent rule down the left edge
    rect(d, [0, 0, 6, H], fill=AMBER)

    # measure "MGS4 " so "CLARITY FIX" starts after it instead of on top of it
    f_title = font('ARIALNB.TTF', 80)
    f_title2 = font('ARIALN.TTF', 80)
    w1 = width_of(d, 'MGS4 ', f_title)
    text(d, (LEFT, 82), 'MGS4', f_title, TEXT)
    text(d, (LEFT + w1, 82), 'CLARITY FIX', f_title2, AMBER)

    sub = 'Disable dynamic resolution scaling in Metal Gear Solid 4.'
    text(d, (LEFT + 2, 190), sub, fit(d, sub, 'segoeui.ttf', 25, avail), DIM)

    code = 'dynamicResolution = false   fxaa = false   MaxAniso = 16'
    text(d, (LEFT + 2, 240), code, fit(d, code, 'consolab.ttf', 20, avail), GREEN)

    foot = 'Master Collection Vol. 2   ·   PC and Steam Deck   ·   readable scripts, no .exe'
    text(d, (LEFT + 2, 306), foot, fit(d, foot, 'segoeui.ttf', 18, avail), FAINT)

    # right: render target with a shrunken 3D viewport inside it
    bx, by, bw, bh = BOX_X + 24, 104, 328, 178
    rect(d, [bx, by, bx + bw, by + bh], fill=PANEL, outline=LINE, width=2)
    text(d, (bx + bw / 2, by - 28), 'RENDER TARGET  3840 x 2160',
         font('consolab.ttf', 15), FAINT, anchor='ma')

    iw, ih = int(bw * 0.70), int(bh * 0.70)
    ix, iy = bx + (bw - iw) // 2, by + (bh - ih) // 2
    rect(d, [ix, iy, ix + iw, iy + ih], fill=(46, 40, 30), outline=RED, width=2)
    text(d, (ix + iw / 2, iy + ih / 2 - 22), '3D VIEWPORT',
         font('consolab.ttf', 15), RED, anchor='ma')
    text(d, (ix + iw / 2, iy + ih / 2 + 1), 'scaled down',
         font('consola.ttf', 14), RED, anchor='ma')
    text(d, (bx + bw / 2, by + bh + 14), 'HUD still composites at full resolution',
         font('consola.ttf', 14), DIM, anchor='ma')

    finish(img, W, H, path)


# ------------------------------------------------------- diagram 1: the mechanism
def diagram_mechanism(path):
    W, H = 1920, 1080
    img, d = new(W, H)

    rect(d, [0, 0, W, 8], fill=AMBER)
    text(d, (96, 62), 'Why the world looks soft but the HUD looks sharp',
         font('segoeuib.ttf', 52), TEXT)
    text(d, (96, 134),
         'MGS4 ships with dynamic resolution scaling enabled. The engine watches GPU frame time and shrinks the 3D',
         font('segoeui.ttf', 27), DIM)
    text(d, (96, 172),
         'viewport inside the render target when it goes over budget. The HUD is composited afterwards, at full size.',
         font('segoeui.ttf', 27), DIM)

    panels = [
        (96,  'STOCK', 'dynamicResolution = true', RED, 0.68,
         'The 3D scene renders into a fraction of the', 'target, then stretches. The HUD does not.'),
        (992, 'WITH THIS FIX', 'dynamicResolution = false', GREEN, 1.0,
         'The 3D scene always fills the render target.', 'World and HUD match again.'),
    ]

    for x, label, code, colour, frac, l1, l2 in panels:
        pw, ph = 832, 520
        py = 250
        rect(d, [x, py, x + pw, py + ph], fill=PANEL, outline=LINE, width=2, radius=6)
        text(d, (x + 32, py + 28), label, font('segoeuib.ttf', 30), colour)
        text(d, (x + 32, py + 74), code, font('consolab.ttf', 22), DIM)

        # render target
        bx, by = x + 32, py + 128
        bw, bh = pw - 64, 300
        rect(d, [bx, by, bx + bw, by + bh], fill=(24, 26, 20), outline=LINE, width=2)
        text(d, (bx + 10, by + 8), 'RENDER TARGET  3840 x 2160',
             font('consola.ttf', 17), FAINT)

        # the 3D viewport inside it -- inset below the label so they never touch
        inner_h = bh - 54
        iw, ih = int(bw * frac), int(inner_h * frac)
        ix, iy = bx + (bw - iw) // 2, by + 42 + (inner_h - ih) // 2
        fillc = (46, 40, 30) if frac < 1 else (30, 42, 26)
        rect(d, [ix, iy, ix + iw, iy + ih], fill=fillc, outline=colour, width=3)
        pct = f'{int(frac * 100)}%'
        text(d, (ix + iw / 2, iy + ih / 2 - 34), '3D VIEWPORT',
             font('consolab.ttf', 26), colour, anchor='ma')
        text(d, (ix + iw / 2, iy + ih / 2 + 2), pct,
             font('consolab.ttf', 40), colour, anchor='ma')

        text(d, (x + 32, py + 452), l1, font('segoeui.ttf', 23), DIM)
        text(d, (x + 32, py + 484), l2, font('segoeui.ttf', 23), DIM)

    # footer note
    ny = 830
    rect(d, [96, ny, W - 96, ny + 150], fill=PANEL2, outline=LINE, width=2, radius=6)
    text(d, (130, ny + 26), 'The scaler is load-dependent.',
         font('segoeuib.ttf', 27), AMBER)
    text(d, (130, ny + 68),
         'On a GPU comfortably inside the frame budget it barely engages. The weaker the hardware, the more it takes',
         font('segoeui.ttf', 24), DIM)
    text(d, (130, ny + 104),
         'away, which is why Steam Deck and lower-end cards see the biggest difference.',
         font('segoeui.ttf', 24), DIM)

    text(d, (96, H - 52), 'github.com/Gabarsolon/MGS4-Clarity-Fix',
         font('consola.ttf', 22), FAINT)
    finish(img, W, H, path)


# ------------------------------------------------ diagram 2: settings + the trap
def diagram_settings(path):
    W, H = 1920, 1080
    img, d = new(W, H)

    rect(d, [0, 0, W, 8], fill=AMBER)
    text(d, (96, 62), 'What it changes', font('segoeuib.ttf', 52), TEXT)
    text(d, (96, 134), 'Four values in two encrypted config files, plus the in-game FXAA toggle.',
         font('segoeui.ttf', 27), DIM)

    rows = [
        ('mgs4.ecf',                'dynamicResolution', 'true',  'false', 'stops the viewport scaler'),
        ('mgs4.ecf',                'fxaa',              'true',  'false', 'removes the post-process blur'),
        ('mgs4.scalability_PC.ecf', 'MaxAniso  [@3]',    '8',     '16',    'sharper oblique surfaces'),
        ('mgs4.scalability_PC.ecf', 'ShadowBufferSize',  '2048',  '4096',  'crisper shadow edges'),
        ('mgs4.savedsettings',      'enableFXAA',        'true',  'false', 'keeps the in-game toggle in sync'),
    ]

    ty = 216
    cols = [130, 700, 1080, 1240, 1430]
    heads = ['FILE', 'SETTING', 'STOCK', 'AFTER', 'EFFECT']
    for cx, h in zip(cols, heads):
        text(d, (cx, ty), h, font('consolab.ttf', 19), FAINT)
    d.line([(px(96), px(ty + 34)), (px(W - 96), px(ty + 34))], fill=LINE, width=px(2))

    for i, (f_, s_, a_, b_, e_) in enumerate(rows):
        y = ty + 62 + i * 62
        if i % 2 == 0:
            rect(d, [96, y - 12, W - 96, y + 40], fill=PANEL)
        text(d, (cols[0], y), f_, font('consola.ttf', 21), DIM)
        text(d, (cols[1], y), s_, font('consolab.ttf', 21), TEXT)
        text(d, (cols[2], y), a_, font('consola.ttf', 21), RED)
        text(d, (cols[3], y), b_, font('consolab.ttf', 21), GREEN)
        text(d, (cols[4], y), e_, font('segoeui.ttf', 21), DIM)

    # the warning panel -- the actually useful part
    wy, wh = 620, 356
    rect(d, [96, wy, W - 96, wy + wh], fill=(38, 26, 22), outline=RED, width=2, radius=6)
    text(d, (130, wy + 26), 'One thing this deliberately does not change',
         font('segoeuib.ttf', 32), RED)
    for i, line in enumerate([
            'bufferSizeX / bufferSizeY is the internal render target, not your display resolution. Konami ships a',
            'per-platform ladder that tracks GPU power, so on PC the game renders at 4K and downsamples to your',
            'monitor. That is supersampling, and it is the sharpest thing in the config.']):
        text(d, (130, wy + 82 + i * 36), line, font('segoeui.ttf', 24), TEXT)
    for i, line in enumerate([
            'Setting it to "match your native resolution" throws that away. It reads like a sharpening tweak and',
            'does the opposite. This mod leaves it at 3840 x 2160.']):
        text(d, (130, wy + 202 + i * 36), line, font('segoeui.ttf', 24), DIM)

    # per-platform ladder, on its own rule well clear of the copy above
    ry = wy + 292
    d.line([(px(130), px(ry)), (px(W - 130), px(ry))], fill=(70, 46, 38), width=px(2))
    plats = [('PC', '3840 x 2160'), ('Xbox Series S', '2560 x 1440'), ('Switch', '1920 x 1080')]
    for i, (p, r) in enumerate(plats):
        x = 130 + i * 330
        text(d, (x, ry + 18), p, font('segoeuib.ttf', 20), DIM)
        text(d, (x + 150, ry + 18), r, font('consolab.ttf', 20), FAINT)

    text(d, (96, H - 52), 'github.com/Gabarsolon/MGS4-Clarity-Fix',
         font('consola.ttf', 22), FAINT)
    finish(img, W, H, path)


if __name__ == '__main__':
    import sys
    out = sys.argv[1].rstrip('\\/')
    header(f'{out}/header-1300x372.png')
    diagram_mechanism(f'{out}/01-why-it-looks-soft.png')
    diagram_settings(f'{out}/02-what-it-changes.png')
