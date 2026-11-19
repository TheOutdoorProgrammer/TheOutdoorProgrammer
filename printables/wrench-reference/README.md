# Wrench shop reference

A one-page SAE and metric wrench chart for printing and keeping in the shop.

[Print the PDF](wrench-shop-reference.pdf) on US Letter paper, portrait, at actual size (100%).
The chart also works in black and white.

[View the preview](wrench-shop-reference.png).

The 43 size pairs and listed bolt diameters come from the [University of Missouri Extension chart](https://extension.missouri.edu/media/wysiwyg/Extensiondata/Pro/AEE/AEE_Standard-metricWrenchChart.pdf).
Metric pairings are approximate, and bolt-head sizes can vary.
A dash means the source did not list a bolt diameter.

To regenerate the PDF and preview, run from this directory:

```sh
uv run --script build_reference.py
```

The script declares its dependencies and checks that the result fits on one US Letter page.

## SAE socket sizes

[Print the fraction chart](fraction-size-order.pdf) for a smallest-to-largest reference covering every 1/32 inch from 3/16 through 1 1/4.
Each row shows the size, equivalent fractions where applicable, and true-size circle and hexagon guides.
Read down each of the three columns, from left to right.

Each circle contains C for common or U for uncommon.
Common socket sizes are every 1/16-inch increment in this range, plus 7/32, 9/32, and 11/32.
This selection follows the contents of Tekton's [small-drive set](https://www.tekton.com/1-4-inch-drive-shallow-6-point-socket-set-shd90101) and [larger-drive set](https://www.tekton.com/1-2-inch-drive-shallow-and-deep-6-point-socket-and-ratchet-set-skt25302); individual sets vary.
Other sizes remain on the chart for reference.

[View the fraction chart preview](fraction-size-order.png).
Print on US Letter, portrait, at **100% / Actual size**, with **Fit to page disabled**.
All content stays inside half-inch margins.
Measure the calibration line between its end ticks: it must be exactly one inch.
The 1-inch circle also provides a check in both horizontal and vertical directions.
If either measurement is off, correct the printer scaling before using the outlines.

Each circle's diameter and each hexagon's distance across opposite flats equal the labeled size.
Compare the socket's internal working opening, not its outside diameter or square drive recess.
The guides show nominal dimensions; socket tolerances and entrance chamfers can affect a visual comparison.

To regenerate this chart:

```sh
uv run --script build_fraction_reference.py
```
