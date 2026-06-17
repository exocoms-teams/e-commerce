# LUMIÈRE → O&A Beauty: Odoo 19 / Odoo.sh Migration Blueprint

**Source analyzed:** `index.html`, `product.html`, `style.css`, `script.js`, `product.js`, `data.js` (9 products, localStorage cart, EmailJS contact form, anchor-link single-page nav).

**Note on the upload:** the ZIP also contained unrelated leftover modules (`travel_agency`, `luxury_services`, `monetique_theme`, `e-commerce-Exocoms` — a French fintech/travel scaffold with no connection to LUMIÈRE). They are ignored entirely in this blueprint and should not be deployed.

**Companion files delivered alongside this document:**
- `oa_beauty_theme_addon.zip` — the only custom Odoo module this migration needs, ready to drop into your Odoo.sh repo
- `odoo_product_import_csv.zip` — the 9 products, fully expanded to their shade variants, ready to import

The central finding driving this whole blueprint: **website_sale already implements ~80% of script.js/product.js.** Cart state, quantity stepping, variant/shade selection, related products, and checkout are native. The custom module is deliberately thin — four product fields and one QWeb extension. Resist the urge to port the JavaScript 1:1; that would mean rebuilding (and then maintaining) a cart and variant engine Odoo already gives you for free, badly, in parallel with the real one.

---

## 1. Odoo Architecture Design

### 1.1 Modules

| Module | Role |
|---|---|
| `website` | Page builder, menus, anchors, mobile nav, theme colors |
| `website_sale` | Shop listing (`/shop`), product page, cart, checkout, variants |
| `website_sale_wishlist` | Real persistent wishlist (replaces the decorative, non-persistent heart toggle in `product.js`) |
| `mail` | Backbone for the contact form (auto-depended by `website`) |
| `oa_beauty_theme` (custom, provided) | Brand SCSS tokens + 4 cosmetic spec fields + their display on the product page |

Nothing else is required. Do **not** install `website_sale_comparison`, `website_sale_loyalty`, etc. unless the business actually asks for product comparison or coupons — every extra module is more upgrade surface on Odoo.sh.

### 1.2 Website structure & routing

| Original anchor (SPA) | Odoo page/route | How it's built |
|---|---|---|
| `index.html#home` | `/` (Website homepage) | Website Builder snippet (Cover/Banner) |
| `index.html#about` | `/` anchor `#about` | Website Builder snippet (Text-Image), named anchor set via block settings |
| `index.html#shop` | `/shop` (separate page, **not** an anchor) | Native eCommerce shop page |
| `index.html#gallery` | `/` anchor `#gallery` | Website Builder Image Gallery snippet |
| `index.html#contact` | `/` anchor `#contact` | Website Builder "Form" snippet |
| `product.html?id=N` | `/shop/<product-slug>-N` | Native `website_sale.product` page |

**Deliberate divergence:** the original site was a single HTML page with an in-page `#shop` section; Odoo eCommerce needs its own dedicated `/shop` listing page with filtering, pagination, and SEO-indexable URLs per product. The top menu's "Shop" entry should point at `/shop`, not an anchor — this is a strict UX upgrade (shareable URLs, browser back/forward, SEO), not a compromise.

Menu configuration: **Website → Site → Menus** — five entries (Home, About, Shop, Gallery, Contact) wired to the routes above. No code.

### 1.3 eCommerce structure

- **Internal category** (`product.category`, accounting/stock grouping): one catalog-wide category, e.g. "Cosmetics", is enough — this field doesn't drive the storefront filters.
- **Website category** (`product.public.category`, what customers filter by): Lips, Face, Skincare, Eyes — one-to-one with the original `data-filter` buttons. Shipped as module data (`oa_beauty_theme`), see §5.
- **Attribute:** `Shade`, `display_type='color'`, `create_variant='always'` — replaces the entire custom shade-circle picker in `product.js` with Odoo's native color-swatch variant selector.
- **Pricing:** single price list, currency from company settings. The static site had no tax logic at all (`$28` flat) — confirm with the business whether that was tax-included pricing and configure Fiscal Position / tax-included display accordingly; this is a real gap the static prototype never had to solve.

### 1.4 Theme/asset structure

Two SCSS bundles, both already wired into `oa_beauty_theme/__manifest__.py`:

```
web._assets_primary_variables  →  primary_variables.scss   (brand tokens)
web.assets_frontend            →  components.scss          (component restyle)
```

---

## 2. HTML → Odoo Website Conversion

### 2.1 `index.html` (homepage), section by section

| Section | Odoo approach | Drag-and-drop only? | Needs custom module? |
|---|---|---|---|
| `<header>` nav, logo, cart icon, mobile burger | Native Website header (Header template "Default" or "Hamburger"); cart icon is the native mini-cart, already shows live count | Yes — configure in Website Builder header options | No |
| `.home` hero (`Feel Beautiful`, social icons) | "Cover" or "Banner" snippet, social icons via native Social Media snippet/footer block | Yes | No |
| `.about` (image + 4 paragraphs + CTA) | "Text - Image" snippet | Yes | No |
| `.shop` heading + filter buttons + grid | **Replaced**, not rebuilt: native `/shop` page already renders the grid; the "filter buttons" become the native **Categories** filter (top pills or left sidebar, configurable in Website Builder → Shop page → Customize) bound to the 4 public categories | Yes, once categories exist | No |
| `.gallery` (3 image cards with captions) | "Image Gallery" or "Big Boxes" snippet, populated via Media Library | Yes | No |
| `.contact` form (name/email/phone/subject/message + EmailJS) | Native **Form** snippet. Default "Contact Us" form posts to the built-in contact handler; add the Phone and Subject fields via the form editor's **+ Field** button | Yes | No — this fully replaces the EmailJS `<script>` block and the bespoke `controllers/main.py` you'd otherwise have to write |
| `<footer>` (socials, link list, copyright) | Native footer template, customized links/copy | Yes | No |
| Cart sidebar / overlay / toast | Native mini-cart drawer (`website_sale`) | N/A — don't rebuild, it's automatic | No |

**Net result for the homepage: zero custom templates.** Every section is an out-of-the-box snippet. The only place code is justified is the product page (next).

### 2.2 `product.html`, section by section

| Section | Odoo approach | Drag-and-drop only? | Needs custom module? |
|---|---|---|---|
| Breadcrumb | Native (`website_sale` renders Home / category / product automatically) | N/A | No |
| Image gallery + thumbnails | Native multi-image product gallery (`product.image`) | Upload-only | No |
| Category label, name, price | Native product page fields | N/A | No |
| Star rating + review count | Native "Comments & Ratings" (Website → eCommerce settings → enable Customer Reviews) — **do not** seed the static `rating: 4.8, reviews: 214` numbers as fake reviews (see §7 Risks) | Toggle in settings | No |
| Description | Native `description_sale` field, shown on the page | Content entry | No |
| **Specs row** (Type / Finish / Best For) | New fields + QWeb xpath insert — `oa_beauty_theme` module | No | **Yes** |
| **Key Ingredients** | Same module, same xpath block | No | **Yes** |
| Shade picker (circles) | Native color-attribute variant selector | No code once attribute exists | No |
| Quantity stepper + Add to Bag | Native `add_to_cart` widget | N/A | No |
| Wishlist heart | `website_sale_wishlist` (real, persistent) replacing the decorative non-persistent toggle | Module install only | No |
| **Trust badges** (delivery / returns / cruelty-free) | Same QWeb xpath block as specs (static content, hard-coded in the template) | No | **Yes** |
| Related products | Native "Suggested Products" / cross-sell, configured per product or via category fallback (the original's "same category, else fill with others" logic is essentially what Odoo's optional/accessory products + category fallback already does) | Configuration | No |

So the entire custom-code footprint of this migration is: **4 fields + 1 QWeb template extension.** That's `oa_beauty_theme`.

---

## 3. CSS → Odoo Theme Migration

### 3.1 Why CSS custom properties, not raw Odoo SCSS variable overrides

Odoo's internal SCSS variables (`$o-color-1`, theme font config maps, etc.) are refactored across versions as the website builder evolves. Hard-overriding them ties your theme to internals that can shift on an Odoo.sh upgrade. `primary_variables.scss` instead defines the brand as **CSS custom properties** at `:root` — stable, inspectable in devtools, readable from any future snippet or script — and `components.scss` consumes them. The same hex values should *also* be entered as Theme Colors 1–5 under **Website → Site → Configuration → Colors** so the point-and-click block editor offers matching swatches to non-developer editors. Belt and suspenders, zero fragility.

### 3.2 Token mapping (legacy → brand)

| Legacy `style.css` variable | Hex | New token | Hex | Role |
|---|---|---|---|---|
| `--bg-color` | `#faf7f3` | `--oa-ivory` | `#faf7f3` | Page background (kept — ivory was already the base) |
| `--second-bg-color` | `#f0ebe3` | `--oa-bg-secondary` | `#f0e9ee` | Alt section background, tinted toward lilac |
| `--text-color` | `#1a1714` | `--oa-prune` / `--oa-text` | `#4a2c3a` | Headings, primary text — deep prune instead of near-black |
| `--text-muted` | `#7a6f66` | `--oa-text-muted` | `#8a7480` | Secondary text |
| `--main-color` | `#b8925a` (gold) | `--oa-mauve` / `--oa-accent` | `#b08497` | Accent — links, active states, hover — **the single biggest visual change**, since the legacy brand was gold-toned and the target brand is mauve/lilac |
| `--border-color` | `#e2d8cc` | `--oa-border` | `#e3d5dc` | Dividers, input borders |
| (new) | — | `--oa-lilac` | `#c9b6d6` | Secondary accent for gradients/hover, not present in legacy palette |

Typography is unchanged: `Cormorant Garamond` (display/headings, italic accents) + `Jost` (body/UI, wide letter-spacing, uppercase labels) already read as "clean luxury" and there's no brand reason to replace them.

### 3.3 Component restyle strategy

`components.scss` re-skins native Odoo classes rather than rebuilding them: shop grid cards (`.oe_product`) get the original's hover lift + shadow treatment in mauve instead of gold; the native color-swatch attribute inputs get the 34px circle + outline-on-active look lifted directly from `.shade-circle`; primary CTA buttons (`#add_to_cart`, `.btn-primary`) get the dark-fill-to-accent-fill hover from `.add-bag-btn`/`.gradient-btn`. The selectors targeting Odoo's own presentational classes are flagged in-file with a reminder to confirm against the live DOM before sign-off — this is normal senior practice on any theming job, not specific to this migration.

The `html { font-size: 60% }` + rem-based scaling pattern from the legacy CSS is **not** carried over: Odoo's own grid and typography already operate on a consistent rem/Bootstrap scale, and forcing a global root font-size override is one of the most common sources of broken third-party snippet styling on Odoo sites. Express sizes in the brand's actual rem values (e.g. the legacy `6rem` heading is really "60px at the legacy 60% root," i.e. real-world ~3.75rem at Odoo's default 16px root) — recalibrate visually rather than porting the multiplier.

---

## 4. JavaScript Migration

### 4.1 Classification

| Feature (script.js / product.js) | Disposition | Why |
|---|---|---|
| `getCart` / `saveCart` / `addToCart` / `removeFromCart` / `changeQty` (localStorage cart) | **Remove entirely** | `website_sale`'s `sale.order` cart is server-side, survives across devices/sessions, and is what checkout/payment actually need. A localStorage cart cannot connect to real payment providers or stock. |
| `updateCartUI` (cart drawer render) | **Remove** | Native mini-cart widget already does this, including the live header badge |
| `openCart` / `closeCart` | **Remove** | Native |
| `showToast` ("Added to bag") | **Remove**, optionally restyle | `website_sale` already shows an add-to-cart confirmation (mini-cart auto-open / animation). If the exact toast aesthetic matters, it's a 10-line CSS restyle of the native notification, not new JS logic. |
| Mobile menu burger toggle | **Remove** | Native responsive header handles this |
| `renderProducts` + filter buttons | **Remove** | Native `/shop` listing + category filtering |
| Contact form `emailjs.sendForm(...)` | **Remove entirely** | Native Website Form snippet posts server-side; no third-party JS SDK, no exposed public key in page source (the legacy code ships `emailjs.init("YOUR_PUBLIC_KEY")`, a placeholder key client-side, which is itself a minor information-exposure smell worth retiring) |
| `renderStars` | **Remove** | Native ratings widget renders its own stars |
| Shade circle picker + `selectedShade` state | **Remove** | Native color-attribute variant selector |
| Quantity stepper (`qty-minus`/`qty-plus`) | **Remove** | Native `add_to_cart` widget ships its own qty stepper |
| `renderRelated` / `quickAdd` | **Remove** | Native related/suggested products + native add-to-cart |
| Wishlist toggle (decorative, `classList.toggle`, no persistence) | **Replace**, don't port | `website_sale_wishlist` gives a *real* persistent wishlist; porting the decorative version would be shipping a regression |
| Product-not-found fallback message | **Remove** | Native 404/`NotFound` handling on invalid product slugs |

**Net result: zero lines of the original JS are migrated.** This is the correct outcome, not an oversight — every interactive behavior in `script.js`/`product.js` exists, server-backed and more robust, in `website_sale` already. If after go-live a genuinely new interaction is needed that Odoo doesn't cover (none identified in this codebase), it would be added as a `publicWidget` JS module registered through the asset bundle, following Odoo's `@odoo-module` ES6 + `publicWidget.registry.add(...)` convention — not inline `<script>` tags.

### 4.2 Event-hook replacement strategy

| Legacy pattern | Odoo replacement |
|---|---|
| Inline `onclick="..."` attributes | Avoided entirely — native widgets bind via `publicWidget` selectors, none needed here |
| `document.getElementById(...).addEventListener` | N/A, no custom JS shipped |
| Global `products` array baked into the page | Server-rendered QWeb from `product.template` recordset — no client-side data duplication, no risk of stale catalog data |

---

## 5. data.js → Odoo Product Import

Full field mapping:

| `data.js` field | Odoo destination | Notes |
|---|---|---|
| `id` | (dropped) | Odoo generates its own `id`; `default_code` (SKU) used instead for human reference |
| `name` | `product.template.name` | |
| `category` | `product.public.category` (M2M `public_categ_ids`) | 4 categories, shipped as module data |
| `price` | `product.template.list_price` | |
| `img` | `product.template.image_1920` + `product.image` (gallery) | **No image files exist in the source ZIP** — these are placeholder paths only; real photography must be sourced and uploaded post-import (see §7 Risks) |
| `icon` (FontAwesome class) | dropped | Was a fallback for missing photography; not meaningful once real photos exist |
| `shade` (single hex on the product) | dropped at template level | Was the swatch fallback color; the real per-variant colors live on `shades[]` below |
| `description` | `product.template.description_sale` | |
| `type`, `finish`, `bestFor` | `oa_type`, `oa_finish`, `oa_best_for` (custom fields, `oa_beauty_theme`) | |
| `keyIngredients` | `oa_key_ingredients` (custom field) | Kept as one display line; move to structured INCI fields later if compliance needs it |
| `rating`, `reviews` | **Not migrated as static data** | Native `rating.mixin` reviews; see Risks |
| `shades[].color` / `.name` | `product.attribute.value` (`Shade` attribute, `html_color` + `name`) | 29 distinct values across the 6 shaded products |

### Delivered files

- `01_product_attribute_values.csv` — 29 shade values with hex colors, external-ID-linked to the `Shade` attribute defined by the module
- `02_product_template_import.csv` — all 9 products, 32 rows (6 shaded products expanded one row per shade using Odoo's documented "repeat the row, vary the attribute column" variant-import technique; 3 non-shaded products as single rows)
- `README.md` — import order and a call-out not to seed fake review counts

Import order: install `oa_beauty_theme` first (creates the `Shade` attribute + 4 categories these CSVs reference by external ID) → import `01_...` → import `02_...`, doing a 5-row dry run on Velvet Lip Rouge first to confirm Odoo merges the rows into one template with 5 variants before committing the full batch.

---

## 6. Odoo.sh Implementation Steps

1. **Odoo.sh setup**
   - Create the project, connect the GitHub repo, confirm the branch is on **Odoo 19.0**.
   - Push `oa_beauty_theme/` into the repo at the standard custom-addons path (commonly `<repo-root>/addons/oa_beauty_theme` — match whatever path your `odoo.conf`/branch already scans).
   - Let Odoo.sh build the staging branch; confirm the build is green before touching modules.

2. **Module installation** (staging branch, via Apps)
   - Install `website_sale` (pulls in `website` as a dependency).
   - Install `website_sale_wishlist`.
   - Install `oa_beauty_theme` last — it depends on the above and will fail cleanly if installed out of order.

3. **Theme/asset verification**
   - Visit any frontend page, hard-refresh, confirm `primary_variables.scss`/`components.scss` are present in the compiled `web.assets_frontend.min.css` (Settings → Technical → Assets, with developer mode, or just inspect computed CSS custom properties in devtools — `--oa-mauve` should resolve to `#b08497` on `:root`).
   - Set Theme Colors 1–5 to the brand hex values under Website → Configuration → Colors.

4. **Product import**
   - Run the dry run, then full import, exactly as described in §5/README.
   - Spot-check 2–3 products: correct category, correct shade swatches with correct colors, correct specs block rendering on the product page (confirms the QWeb xpath in `oa_beauty_theme` matched correctly on this Odoo 19 build — see §7 Risk #1).
   - Upload real product photography (replacing the non-existent placeholder paths).

5. **Website assembly**
   - Build the homepage with native snippets per §2.1 (Cover, Text-Image, Image Gallery, Form, Footer).
   - Set anchors on the About/Gallery/Contact blocks; wire the top menu (Home/About/Shop/Gallery/Contact) per §1.2.
   - Configure the `/shop` page's category filter UI to surface Lips/Face/Skincare/Eyes.
   - Enable Customer Reviews if the business wants the ratings feature live (empty until real reviews accrue).

6. **Testing**
   - Full guest checkout end-to-end on a test payment provider (Odoo.sh staging should have a sandbox provider, e.g. test mode of whatever gateway is targeted for production).
   - Shade variant selection updates price/image/SKU correctly; out-of-stock variants (once stock tracking is configured) behave correctly.
   - Mobile breakpoints (header burger menu, shop grid, product page layout) — the legacy CSS had explicit breakpoints at 1285px/1100px/1000px/768px/600px; spot-check those widths since real users will hit them.
   - Contact form submission delivers mail to the configured website email.
   - Run Lighthouse/PageSpeed on the homepage and `/shop` — confirm the Google Fonts `@import` in `primary_variables.scss` isn't blocking render; consider self-hosting the two fonts if score is an issue.

7. **Deployment**
   - Merge staging → production branch through Odoo.sh's normal promote flow (never push directly to production).
   - Re-run the same module install order on production if it's a fresh database; if staging was a duplicate of production, the merge alone ships code, and module install/data load happens automatically via the manifest's `data` list on upgrade.
   - Re-verify Theme Colors and a live test order against the **live** payment provider (switch from sandbox before going live, then immediately back to confirm no stray sandbox transactions on the real gateway).

---

## 7. Final Output: Architecture, File Structure, Order, Risks

### 7.1 Custom addon file structure (delivered as `oa_beauty_theme_addon.zip`)

```
oa_beauty_theme/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── product_template.py          # oa_type, oa_finish, oa_best_for, oa_key_ingredients
├── views/
│   ├── product_template_backend_views.xml   # exposes the 4 fields on the backend product form
│   └── website_sale_product_templates.xml   # QWeb xpath: specs + ingredients + trust badges
├── data/
│   ├── product_attribute_data.xml   # "Shade" attribute (display_type=color)
│   └── product_public_category_data.xml   # Lips / Face / Skincare / Eyes
└── static/src/scss/
    ├── primary_variables.scss       # brand tokens (mauve/lilac/ivory/prune) as CSS vars
    └── components.scss              # re-skins native shop/product/cart elements
```

### 7.2 Implementation order (condensed)

1. Push & install `oa_beauty_theme` (and its deps) on staging.
2. Verify theme tokens render.
3. Import attribute values → import products (dry run first).
4. Upload real photography.
5. Assemble homepage from native snippets; wire menu/anchors.
6. Configure shop category filter, reviews, wishlist.
7. Full checkout test on sandbox payment provider.
8. Promote to production; switch to live payment provider; smoke-test.

### 7.3 Risk points & pitfalls

1. **QWeb xpath fragility.** The `website_sale.product` template's internal structure (the `id="product_details"` anchor targeted in `website_sale_product_templates.xml`) has been incrementally modularized across recent Odoo versions as the website builder gained more block-level editing of the product page. Confirm the anchor still matches on your specific Odoo 19.0 build *before* relying on it — the file includes inline instructions for doing this via developer-mode template inspection. If it's moved, only that one xpath `expr` needs updating; nothing else in the module is affected.
2. **No product photography exists in the source.** Every `img:`/`gallery/`/`products/` path in the static site is a placeholder that 404s. Treat real photography as a hard blocker for go-live, not a nice-to-have — the FontAwesome icon fallback (`fa-heart`, `fa-droplet`, etc.) currently masking this should not ship to production.
3. **Fabricated ratings/reviews.** `data.js` hard-codes `rating` and `reviews` per product (e.g. 4.8 / 214 reviews) as static design filler. Importing these as seed review counts with no underlying reviews is a deceptive-practice risk (and in some jurisdictions a regulatory one, e.g. FTC guidance on fake testimonials). Launch with reviews empty and let them accrue, or clearly label any seeded internal-tester reviews as such.
4. **EmailJS public key & third-party JS removed, not hidden.** The legacy site ships an EmailJS public key and service/template ID placeholders client-side in plain text (`emailjs.init("YOUR_PUBLIC_KEY")`, `YOUR_SERVICE_ID`, `YOUR_TEMPLATE_ID`). The Odoo replacement removes this dependency entirely — there's no equivalent secret to manage, which is itself a security improvement worth calling out to the business.
5. **`html { font-size: 60% }` root override.** If anyone is tempted to literally drop the old CSS file onto the Odoo frontend asset bundle "for speed," don't — a global root font-size override of this kind reliably breaks third-party/native Odoo snippet styling that assumes a 16px root. Recalibrate the few real px/rem values that matter (headings, spacing) instead of porting the multiplier.
6. **Tax/pricing ambiguity.** The static prototype has flat USD prices with no tax model at all. Confirm with the business whether `$28` etc. is meant tax-included or tax-excluded before going live — this is a genuine business decision the prototype never had to make, not a migration detail.
7. **Variant-import duplicate detection.** The CSV technique in §5/§6 relies on Odoo's row-merging-by-Name behavior for variant import. Always dry-run the first product (5 rows) and visually confirm one template / five variants before running the full batch — a stray trailing space or punctuation difference between rows for the same product (e.g. an em-dash vs hyphen in "Mixed — Matte & Shimmer") will silently create duplicate templates instead of merging.
8. **Currency/locale of the legacy "$".** Confirm the actual target currency for O&A Beauty in Odoo's Company settings before import — `list_price` is currency-less in the CSV and will simply take on whatever the database's company currency is at import time.
