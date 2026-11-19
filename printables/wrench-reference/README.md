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

## SAE wrench sizes

[Print the fraction chart](fraction-size-order.pdf) for a smallest-to-largest reference covering every 1/32 inch from 3/16 through 1 1/4.
Each row shows the size and equivalent fractions where applicable.
Shaded rows mark 1/8-inch steps.
Read down the left column, then down the right.

[View the fraction chart preview](fraction-size-order.png).
Use the same US Letter, portrait, 100% print settings as the wrench chart.

To regenerate this chart:

```sh
uv run --script build_fraction_reference.py
```
