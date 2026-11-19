# /// script
# requires-python = ">=3.11"
# dependencies = ["reportlab>=4,<5", "pymupdf>=1.24,<2"]
# ///
"""Generate a true-size SAE socket reference and its PNG preview."""

from fractions import Fraction
from math import cos, pi, sin, sqrt
from pathlib import Path

import pymupdf
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent
PDF = OUT / "fraction-size-order.pdf"
SIZES = [Fraction(n, 32) for n in range(6, 41)]
INK = HexColor("#172731")
MUTED = HexColor("#47545B")
RULE = HexColor("#D3D9DC")
WIDTH, HEIGHT = 612, 792
MARGIN = 36
COMMON = {size for size in SIZES if (size * 16).denominator == 1}
COMMON.update(Fraction(n, 32) for n in (7, 9, 11))


def mixed(value):
    whole, remainder = divmod(value.numerator, value.denominator)
    if not remainder:
        return str(whole)
    fractional = f"{remainder}/{value.denominator}"
    return f"{whole} {fractional}" if whole else fractional


def equivalents(value):
    forms = []
    for denominator in (32, 16, 8, 4, 2):
        numerator = value * denominator
        if numerator.denominator != 1 or denominator <= value.denominator:
            continue
        whole, remainder = divmod(numerator.numerator, denominator)
        if whole and remainder:
            forms.append(f"{whole} {remainder}/{denominator}")
        else:
            forms.append(f"{numerator.numerator}/{denominator}")
    return forms


C = canvas.Canvas(str(PDF), pagesize=(WIDTH, HEIGHT), pageCompression=1)
C.setTitle("SAE Socket Sizes | Shop Reference")
C.setSubject("True-size opening guides from 3/16 to 1 1/4 inch; common sizes labeled")
C.setFillColor(INK)
C.setFont("Helvetica-Bold", 20)
C.drawString(MARGIN, HEIGHT - 58, "SAE SOCKET SIZES")
C.setFont("Helvetica", 8.5)
C.drawString(MARGIN, HEIGHT - 73, "Letter at 100% / Actual size   |   Match the socket opening   |   C = common / U = uncommon")
C.setFont("Helvetica-Bold", 7.5)
C.drawCentredString(530, HEIGHT - 45, '1" PRINT CHECK')
C.setStrokeColor(INK)
C.setLineWidth(0.6)
C.line(494, HEIGHT - 54, 566, HEIGHT - 54)
for x in (494, 566):
    C.line(x, HEIGHT - 50, x, HEIGHT - 58)


def column(x, sizes):
    top = 82
    for size in sizes:
        forms = equivalents(size)
        diameter = float(size) * 72
        row_height = max(diameter + 2, 18 + 9 * len(forms))
        center_y = HEIGHT - top - row_height / 2
        baseline = center_y + (14 + 9 * len(forms)) / 2 - 12
        C.setFillColor(INK)
        C.setFont("Helvetica-Bold", 14)
        C.drawString(x + 5, baseline, mixed(size))
        C.setFillColor(MUTED)
        C.setFont("Helvetica", 8.5)
        for index, form in enumerate(forms, start=1):
            C.drawString(x + 5, baseline - index * 9, "= " + form)

        center_x = x + 119
        # The circle is inscribed: its diameter equals the hex's across-flats size.
        radius = diameter / sqrt(3)
        vertices = [
            (center_x + radius * cos(i * pi / 3),
             center_y + radius * sin(i * pi / 3))
            for i in range(6)
        ]
        assert abs(max(y for _, y in vertices) - min(y for _, y in vertices) - diameter) < 1e-9
        hexagon = C.beginPath()
        hexagon.moveTo(*vertices[0])
        for vertex in vertices[1:]:
            hexagon.lineTo(*vertex)
        hexagon.close()
        C.setStrokeColor(MUTED)
        C.setLineWidth(0.4)
        C.drawPath(hexagon, stroke=1, fill=0)
        C.setStrokeColor(INK)
        C.setLineWidth(0.6)
        C.circle(center_x, center_y, diameter / 2, stroke=1, fill=0)
        C.setFillColor(INK)
        C.setFont("Helvetica-Bold", 9)
        C.drawCentredString(center_x, center_y - 3.2, "C" if size in COMMON else "U")
        C.setStrokeColor(RULE)
        C.setLineWidth(0.4)
        C.line(x, HEIGHT - top - row_height, x + 174, HEIGHT - top - row_height)
        top += row_height
    assert top <= HEIGHT - MARGIN - 0.3, top


column(36, SIZES[:17])
column(219, SIZES[17:27])
column(402, SIZES[27:])
C.showPage()
C.save()

doc = pymupdf.open(PDF)
assert len(doc) == 1
assert tuple(doc[0].rect) == (0, 0, WIDTH, HEIGHT)
for block in doc[0].get_text("blocks"):
    assert MARGIN <= block[0] < block[2] <= WIDTH - MARGIN, block
    assert MARGIN <= block[1] < block[3] <= HEIGHT - MARGIN, block
for drawing in doc[0].get_drawings():
    bounds = drawing["rect"]
    assert bounds.x0 >= MARGIN and bounds.x1 <= WIDTH - MARGIN, bounds
    assert bounds.y0 >= MARGIN and bounds.y1 <= HEIGHT - MARGIN, bounds
doc[0].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False).save(
    OUT / "fraction-size-order.png"
)
print(f"Built {PDF}: 1 US Letter page, {len(SIZES)} sizes.")
