# /// script
# requires-python = ">=3.11"
# dependencies = ["reportlab>=4,<5", "pymupdf>=1.24,<2"]
# ///
"""Build a one-page shop reference from Missouri Extension's wrench chart.

Run from this directory: uv run --script build_reference.py
The PDF contains vector text and diagrams; the PNG is a preview.
"""

from math import cos, pi, sin
from pathlib import Path

import pymupdf
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent
SOURCE = (
    "https://extension.missouri.edu/media/wysiwyg/Extensiondata/Pro/AEE/"
    "AEE_Standard-metricWrenchChart.pdf"
)
# Preserve the source's pairings and blank bolt-diameter cells.
ROWS = [
    ("1/8", "5/16", 8),
    ("3/16", "3/8", 10),
    ("1/4", "7/16", 11),
    ("5/16", "1/2", 13),
    ("3/8", "9/16", 14),
    ("7/16", "5/8", 16),
    ("1/2", "3/4", 19),
    ("9/16", "13/16", 21),
    ("", "7/8", 22),
    ("5/8", "15/16", 24),
    ("", "1", 25),
    ("3/4", "1-1/8", 29),
    ("", "1-1/4", 32),
    ("7/8", "1-5/16", 34),
    ("", "1-3/8", 35),
    ("1", "1-1/2", 38),
    ("", "1-5/8", 41),
    ("1-1/8", "1-11/16", 43),
    ("", "1-3/4", 45),
    ("1-1/4", "1-7/8", 48),
    ("1-3/8", "2", 51),
    ("1-1/2", "2-1/4", 57),
    ("1-5/8", "2-1/2", 64),
    ("1-3/4", "2-5/8", 67),
    ("", "2-3/4", 70),
    ("1-7/8", "2-15/16", 75),
    ("", "3", 76),
    ("2", "3-1/8", 80),
    ("", "3-1/4", 83),
    ("2-1/4", "3-1/2", 89),
    ("", "3-3/4", 95),
    ("2-1/2", "3-7/8", 99),
    ("", "4", 102),
    ("2-3/4", "4-1/4", 108),
    ("", "4-1/2", 114),
    ("3", "4-5/8", 118),
    ("3-1/4", "5", 127),
    ("3-1/2", "5-3/8", 137),
    ("", "5-1/2", 140),
    ("3-3/4", "5-3/4", 146),
    ("", "6", 152),
    ("", "6-1/2", 165),
    ("", "7", 178),
]

WIDTH, HEIGHT = 612, 792
INK = HexColor("#172731")
MUTED = HexColor("#47545B")
RULE = HexColor("#C9CFD2")
STRIPE = HexColor("#F1F3F4")
PDF = OUT / "wrench-shop-reference.pdf"
C = canvas.Canvas(str(PDF), pagesize=(WIDTH, HEIGHT), pageCompression=1)
C.setTitle("SAE + Metric Wrench Sizes | Shop Reference")
C.setAuthor("Adapted from University of Missouri Extension")
C.setSubject("43 approximate wrench-size pairs and source bolt diameters")
C.setKeywords(SOURCE)


def text(x, y, value, size=10, bold=False, color=INK, align="left"):
    C.setFillColor(color)
    C.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    draw = {"left": C.drawString, "center": C.drawCentredString,
            "right": C.drawRightString}[align]
    draw(x, HEIGHT - y, value)


def line(x1, y1, x2, y2, color=RULE, width=0.6):
    C.setStrokeColor(color)
    C.setLineWidth(width)
    C.line(x1, HEIGHT - y1, x2, HEIGHT - y2)


def rect(x, y, w, h, fill):
    C.setFillColor(fill)
    C.rect(x, HEIGHT - y - h, w, h, stroke=0, fill=1)


def dimension(x1, y1, x2, y2):
    line(x1, y1, x2, y2, INK, 0.8)
    if y1 == y2:
        for x, direction in ((x1, 1), (x2, -1)):
            line(x, y1, x + 3 * direction, y1 - 2, INK, 0.8)
            line(x, y1, x + 3 * direction, y1 + 2, INK, 0.8)
    else:
        for y, direction in ((y1, 1), (y2, -1)):
            line(x1, y, x1 - 2, y + 3 * direction, INK, 0.8)
            line(x1, y, x1 + 2, y + 3 * direction, INK, 0.8)


text(30, 32, "SHOP REFERENCE  /  SIZES IN ASCENDING ORDER", 8.5, True)
text(30, 62, "SAE + METRIC WRENCH SIZES", 26, True)
text(30, 81, "Find a nearby size at a glance. Metric pairings are approximate.", 11)

rect(30, 96, 552, 80, STRIPE)
# Point-up hexagon leaves two vertical, opposite flats for the dimension.
points = [
    (72 + 23 * cos(-pi / 2 + i * pi / 3),
     133 + 23 * sin(-pi / 2 + i * pi / 3))
    for i in range(6)
]
p = C.beginPath()
p.moveTo(points[0][0], HEIGHT - points[0][1])
for x, y in points[1:]:
    p.lineTo(x, HEIGHT - y)
p.close()
C.setStrokeColor(INK)
C.setLineWidth(1.4)
C.drawPath(p, stroke=1, fill=0)
left, right = points[4][0], points[1][0]
line(left, 144.5, left, 168, MUTED)
line(right, 144.5, right, 168, MUTED)
dimension(left, 164, right, 164)
text(112, 119, "WRENCH SIZE", 9.5, True)
text(112, 137, "Across opposite flat faces", 10)
text(112, 153, "of the nut or bolt head.", 10)
line(305, 108, 305, 164)
# Side view distinguishes thread diameter from the hex head.
rect(325, 119, 12, 32, INK)
rect(337, 126, 32, 18, white)
line(337, 126, 369, 126, INK, 1)
line(337, 144, 369, 144, INK, 1)
line(369, 126, 369, 144, INK, 1)
for x in range(341, 368, 5):
    line(x, 128, x - 3, 142, MUTED, 0.6)
line(370, 126, 383, 126, MUTED)
line(370, 144, 383, 144, MUTED)
dimension(379, 126, 379, 144)
text(399, 119, "BOLT DIAMETER", 9.5, True)
text(399, 137, "Across the outer threads.", 10)
text(399, 153, "Head sizes can vary.", 10)


def table(x, title, rows):
    row_height = 23.5
    text(x, 199, title, 10.5, True)
    line(x, 207, x + 266, 207, INK, 1.1)
    centers = (x + 50, x + 140, x + 224)
    for center, label, unit in zip(
        centers,
        ("SAE WRENCH", "METRIC ~", "BOLT DIA."),
        ("inches", "millimeters", "inches"),
    ):
        text(center, 222, label, 9.5, True, align="center")
        text(center, 234, unit, 9.5, color=MUTED, align="center")
    for i, (bolt, sae, metric) in enumerate(rows):
        top = 242 + i * row_height
        if i % 2 == 0:
            rect(x, top, 266, row_height, STRIPE)
        text(centers[0], top + 17.5, sae, 17, True, align="center")
        text(centers[1], top + 17.5, str(metric), 17, True, align="center")
        text(centers[2], top + 16.5, bolt or "-", 13, color=MUTED, align="center")
    bottom = 242 + len(rows) * row_height
    line(x + 182, 213, x + 182, bottom)
    line(x, bottom, x + 266, bottom)


table(30, '01  /  5/16" TO 2-1/4"', ROWS[:22])
table(316, '02  /  2-1/2" TO 7"', ROWS[22:])
C.showPage()
C.save()

doc = pymupdf.open(PDF)
assert len(doc) == 1
assert tuple(doc[0].rect) == (0, 0, WIDTH, HEIGHT)
for block in doc[0].get_text("blocks"):
    assert 26 <= block[0] < block[2] <= 586, block
    assert 20 <= block[1] < block[3] <= 767, block
doc[0].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False).save(
    OUT / "wrench-shop-reference.png"
)
print(f"Built {PDF}: 1 US Letter page, {len(ROWS)} source rows.")
