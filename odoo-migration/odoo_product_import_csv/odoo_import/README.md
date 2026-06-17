# O&A Beauty — Product Import Files

Import order matters. Do this in Odoo.sh / your staging branch, AFTER
the `oa_beauty_theme` module is installed (it creates the `Shade`
attribute and the four public categories these CSVs reference by
external ID).

## 1. `01_product_attribute_values.csv`
Inventory (or Sales) → Configuration → Attributes → open **Shade** →
**Values** → **Import**, or Settings → Technical → Database Structure
→ Attribute Values → Import.
Creates the 29 named, colour-swatched shade values (Rose Petal, Onyx,
Champagne Gold, etc.) with their hex colours so the swatches render
correctly before any product references them.

## 2. `02_product_template_import.csv`
Inventory → Products → Products → **Import**.
32 rows = 9 products. Six products have multiple rows (one per shade)
using Odoo's standard "repeat the row, vary only the attribute column"
technique for importing several variants of the same product — Odoo
merges rows that share the same Name into a single template with one
attribute line per distinct Shade value, then generates the variants.

**Before running the full import:** run it once with only the 5 rows
for "Velvet Lip Rouge", confirm in the UI that exactly one template was
created with 5 variants (not 5 separate templates), then import the
remaining rows. This catches any duplicate-detection mismatch (e.g.
trailing whitespace in `name`) early instead of after 32 rows.

## What is intentionally NOT in these CSVs
* **Images** — the original ZIP contains no actual product photography
  (`img/`, `products/`, `gallery/` referenced in the HTML/JS are empty
  paths). Upload real photos to each product's `image_1920` field and
  extra images after import; the swatch-circle `<i class="fa-...">`
  icons used as a placeholder in the static site should not be carried
  into production.
* **Star ratings / review counts** (`rating: 4.8, reviews: 214`, etc.)
  — these were static, fabricated numbers in `data.js`. Do not import
  them as seed reviews. Either leave ratings empty and let Odoo's
  native "Comments & Ratings" feature accumulate real customer
  reviews, or seed a small number of clearly-attributed internal
  tester reviews if early social proof is required — fabricating
  anonymous 5-star counts is a reputational and, in some jurisdictions,
  legal risk.
