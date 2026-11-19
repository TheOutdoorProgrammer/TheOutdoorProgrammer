# /// script
# requires-python = ">=3.11"
# dependencies = ["reportlab>=4,<5", "pymupdf>=1.24,<2"]
# ///
"""Generate a printable SAE wrench size chart and its PNG preview."""

from fractions import Fraction
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
SHADE = HexColor("#EAF0F3")
WIDTH, HEIGHT = 612, 792


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
C.setTitle("SAE Wrench Sizes | Shop Reference")
C.setSubject("Every 1/32 inch from 3/16 to 1 1/4, with equivalent fractions")
C.setFillColor(INK)
C.setFont("Helvetica-Bold", 8.5)
C.drawString(30, HEIGHT - 32, "SHOP REFERENCE  /  ALL SIZES IN INCHES")
C.setFont("Helvetica-Bold", 26)
C.drawString(30, HEIGHT - 62, "SAE WRENCH SIZES")


def column(x, title, sizes):
    C.setFillColor(INK)
    C.setFont("Helvetica-Bold", 10.5)
    C.drawString(x, HEIGHT - 95, title)
    C.setStrokeColor(INK)
    C.setLineWidth(1)
    C.line(x, HEIGHT - 103, x + 266, HEIGHT - 103)
    row_height = 36
    for index, size in enumerate(sizes):
        top = 111 + index * row_height
        if (size * 8).denominator == 1:
            C.setFillColor(SHADE)
            C.rect(x, HEIGHT - top - row_height, 266, row_height, stroke=0, fill=1)
        C.setFillColor(INK)
        C.setFont("Helvetica-Bold", 22)
        C.drawString(x + 10, HEIGHT - top - 21, mixed(size))
        C.setFillColor(MUTED)
        C.setFont("Helvetica", 10)
        C.drawString(x + 10, HEIGHT - top - 33, " = ".join(equivalents(size)))
        C.setStrokeColor(RULE)
        C.setLineWidth(0.4)
        C.line(x, HEIGHT - top - row_height, x + 266, HEIGHT - top - row_height)


column(30, '3/16" TO 23/32"', SIZES[:18])
column(316, '3/4" TO 1 1/4"', SIZES[18:])
C.showPage()
C.save()

doc = pymupdf.open(PDF)
assert len(doc) == 1
assert tuple(doc[0].rect) == (0, 0, WIDTH, HEIGHT)
for block in doc[0].get_text("blocks"):
    assert 26 <= block[0] < block[2] <= 586, block
    assert 20 <= block[1] < block[3] <= 767, block
doc[0].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False).save(
    OUT / "fraction-size-order.png"
)
print(f"Built {PDF}: 1 US Letter page, {len(SIZES)} sizes.")
