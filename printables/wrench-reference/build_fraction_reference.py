# /// script
# requires-python = ">=3.11"
# dependencies = ["reportlab>=4,<5", "pymupdf>=1.24,<2"]
# ///
"""Generate matching true-size SAE and metric socket references."""

from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from math import cos, pi, sin, sqrt
from pathlib import Path

import pymupdf
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent
SIZES = [Fraction(n, 32) for n in range(6, 41)]
METRIC_SIZES = sorted([Fraction(n) for n in range(4, 33)] + [Fraction("4.5"), Fraction("5.5")])
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


def equivalent_lines(value):
    lines = []
    current = ""
    for form in equivalents(value):
        candidate = current + " = " + form if current else "= " + form
        if stringWidth(candidate, "Helvetica", 8) > 58:
            lines.append(current)
            current = "= " + form
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def metric(value):
    millimeters = Decimal(value.numerator) * Decimal("25.4") / value.denominator
    rounded = millimeters.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"({rounded} mm)"


def inch_comparison(millimeters):
    steps = millimeters / Fraction("25.4") * 32
    nearest = (steps + Fraction(1, 2)).numerator // (steps + Fraction(1, 2)).denominator
    return f'(~{mixed(Fraction(nearest, 32))}")'


def column(c, x, sizes, metric_sheet):
    top = 82
    rows = []
    for size in sizes:
        details = [] if metric_sheet else equivalent_lines(size)
        diameter = float(size / Fraction("25.4") if metric_sheet else size) * 72
        rows.append((size, details, diameter, max(diameter + 2, 18 + 9 * len(details))))
    extra = (673 - sum(row[3] for row in rows)) / len(rows)
    assert extra >= 0
    for size, details, diameter, minimum_height in rows:
        row_height = minimum_height + extra
        center_y = HEIGHT - top - row_height / 2
        baseline = HEIGHT - top - 14
        label = f"{float(size):g} mm" if metric_sheet else mixed(size)
        comparison = inch_comparison(size) if metric_sheet else metric(size)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(x + 5, baseline, label)
        comparison_x = x + 8 + stringWidth(label, "Helvetica-Bold", 13)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7)
        c.drawString(comparison_x, baseline, comparison)
        c.setFont("Helvetica", 8)
        for index, detail in enumerate(details, start=1):
            c.drawString(x + 5, baseline - index * 9, detail)

        center_x = x + 119
        # The circle is inscribed: its diameter equals the hex's across-flats size.
        radius = diameter / sqrt(3)
        vertices = [
            (center_x + radius * cos(i * pi / 3),
             center_y + radius * sin(i * pi / 3))
            for i in range(6)
        ]
        assert abs(max(y for _, y in vertices) - min(y for _, y in vertices) - diameter) < 1e-9
        hexagon = c.beginPath()
        hexagon.moveTo(*vertices[0])
        for vertex in vertices[1:]:
            hexagon.lineTo(*vertex)
        hexagon.close()
        c.setStrokeColor(MUTED)
        c.setLineWidth(0.4)
        c.drawPath(hexagon, stroke=1, fill=0)
        c.setStrokeColor(INK)
        c.setLineWidth(0.6)
        c.circle(center_x, center_y, diameter / 2, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(center_x, center_y - 3.2, "C" if metric_sheet or size in COMMON else "U")
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.line(x, HEIGHT - top - row_height, x + 174, HEIGHT - top - row_height)
        top += row_height
    assert top <= HEIGHT - MARGIN - 0.3, top


def build_sheet(stem, title, columns, metric_sheet=False):
    pdf = OUT / f"{stem}.pdf"
    c = canvas.Canvas(str(pdf), pagesize=(WIDTH, HEIGHT), pageCompression=1)
    c.setTitle(f"{title.title()} | Shop Reference")
    c.setSubject("True-size socket opening guides; parenthetical comparisons are approximate")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(MARGIN, HEIGHT - 58, title)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, HEIGHT - 73, "Letter at 100% / Actual size   |   Comparisons approximate   |   C = common / U = uncommon")
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(530, HEIGHT - 45, '1" PRINT CHECK')
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(494, HEIGHT - 54, 566, HEIGHT - 54)
    for x in (494, 566):
        c.line(x, HEIGHT - 50, x, HEIGHT - 58)
    for x, sizes in zip((36, 219, 402), columns, strict=True):
        column(c, x, sizes, metric_sheet)
    c.showPage()
    c.save()

    with pymupdf.open(pdf) as doc:
        assert len(doc) == 1
        assert tuple(doc[0].rect) == (0, 0, WIDTH, HEIGHT)
        for block in doc[0].get_text("blocks"):
            assert MARGIN <= block[0] < block[2] <= WIDTH - MARGIN, block
            assert MARGIN <= block[1] < block[3] <= HEIGHT - MARGIN, block
        for drawing in doc[0].get_drawings():
            bounds = drawing["rect"]
            assert bounds.x0 >= MARGIN and bounds.x1 <= WIDTH - MARGIN, bounds
            assert bounds.y0 >= MARGIN and bounds.y1 <= HEIGHT - MARGIN, bounds
        doc[0].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False).save(OUT / f"{stem}.png")
    print(f"Built {pdf}: 1 US Letter page, {sum(map(len, columns))} sizes.")
    return pdf


if __name__ == "__main__":
    sheets = [
        build_sheet("fraction-size-order", "SAE SOCKET SIZES", [SIZES[:17], SIZES[17:27], SIZES[27:]]),
        build_sheet(
            "metric-socket-reference",
            "METRIC SOCKET SIZES",
            [METRIC_SIZES[:17], METRIC_SIZES[17:25], METRIC_SIZES[25:]],
            metric_sheet=True,
        ),
    ]
    with pymupdf.open() as combined:
        for sheet in sheets:
            with pymupdf.open(sheet) as doc:
                combined.insert_pdf(doc)
        combined.set_metadata({"title": "SAE and Metric Socket References"})
        assert len(combined) == 2
        combined.save(OUT / "socket-reference-sheets.pdf")
