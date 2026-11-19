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
