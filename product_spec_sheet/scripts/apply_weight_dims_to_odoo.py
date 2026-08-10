# -*- coding: utf-8 -*-
"""
product_spec_sheet/scripts/apply_weight_dims_to_odoo.py
========================================================
Lit le CSV généré par fetch_specs_shipping.py et met à jour :
  - product.template.weight       (poids en kg — champ standard Odoo)
  - product.template.volume       (volume en m³  — champ standard Odoo, optionnel)
  - product.template.spec_line_ids (Poids + Encombrement dans l'onglet Caractéristiques)

UTILISATION (depuis la racine Odoo) :
    odoo shell -d <base> -c /etc/odoo/odoo.conf \
        --no-http < addons/product_spec_sheet/scripts/apply_weight_dims_to_odoo.py

Modifiez CSV_PATH ci-dessous avant de lancer.
"""

import csv

# ------------------------------------------------------------------
# PARAMÈTRES — à adapter
# ------------------------------------------------------------------
CSV_PATH = "/tmp/resultats_specs.csv"   # généré par fetch_specs_shipping.py
UPDATE_ODOO_WEIGHT = True               # mettre à jour product.template.weight
UPDATE_ODOO_VOLUME = True               # mettre à jour product.template.volume
UPDATE_SPEC_LINES  = True               # créer/MàJ les lignes Poids + Encombrement
DRY_RUN = False                         # True = simulation sans écriture


# ------------------------------------------------------------------
def _float(val):
    try:
        return float(str(val).replace(",", ".").strip())
    except Exception:
        return None


def find_product(name, ref=""):
    """Recherche le product.template par référence ou nom."""
    Product = env["product.template"]
    if ref:
        p = Product.search([("default_code", "=", ref)], limit=1)
        if p:
            return p
    return Product.search([("name", "ilike", name)], limit=1)


def get_or_create_attribute(cat_name, attr_name):
    """Retourne (category, attribute) en créant les enregistrements si absents."""
    Category = env["product.spec.category"]
    Attribute = env["product.spec.attribute"]

    cat = Category.search([("name", "=", cat_name)], limit=1)
    if not cat:
        cat = Category.create({"name": cat_name, "sequence": 50})

    attr = Attribute.search([("name", "=", attr_name), ("category_id", "=", cat.id)], limit=1)
    if not attr:
        attr = Attribute.create({"name": attr_name, "category_id": cat.id})

    return cat, attr


def upsert_spec_line(product, attribute, value):
    """Crée ou met à jour une ligne de caractéristique."""
    SpecLine = env["product.template.spec.line"]
    line = SpecLine.search([
        ("product_tmpl_id", "=", product.id),
        ("attribute_id", "=", attribute.id),
    ], limit=1)
    if line:
        if line.value != value:
            line.value = value
            return "updated"
        return "unchanged"
    else:
        SpecLine.create({
            "product_tmpl_id": product.id,
            "attribute_id": attribute.id,
            "value": value,
        })
        return "created"


# ------------------------------------------------------------------
# LECTURE DU CSV ET APPLICATION
# ------------------------------------------------------------------
with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"CSV chargé : {len(rows)} ligne(s)")
print(f"Mode       : {'SIMULATION' if DRY_RUN else 'ÉCRITURE RÉELLE'}")
print("─" * 56)

created = updated = skipped = 0

for row in rows:
    name    = row.get("Produit", "").strip()
    ref     = row.get("Référence", "").strip()
    poids   = _float(row.get("Poids (kg)", ""))
    long_mm = _float(row.get("Long. (mm)", ""))
    larg_mm = _float(row.get("Larg. (mm)", ""))
    haut_mm = _float(row.get("Haut. (mm)", ""))
    vol_cm3 = _float(row.get("Volume (cm³)", ""))

    product = find_product(name, ref)
    if not product:
        print(f"  [SKIP] Produit introuvable dans Odoo : {name!r}")
        skipped += 1
        continue

    print(f"  [OK]   {product.name} (ID {product.id})")

    if not DRY_RUN:
        # 1. Champ poids standard Odoo (en kg)
        if poids and UPDATE_ODOO_WEIGHT:
            product.weight = poids
            print(f"         weight = {poids} kg")

        # 2. Champ volume standard Odoo (en m³)
        if vol_cm3 and UPDATE_ODOO_VOLUME:
            product.volume = round(vol_cm3 / 1_000_000, 6)    # cm³ → m³
            print(f"         volume = {product.volume} m³")

        # 3. Lignes de caractéristiques
        if UPDATE_SPEC_LINES:
            _, attr_poids = get_or_create_attribute("Dimensions et poids", "Poids")
            _, attr_dims  = get_or_create_attribute("Dimensions et poids", "Encombrement")

            if poids:
                status = upsert_spec_line(product, attr_poids, f"{poids:.3f} kg")
                print(f"         spec Poids → {status}")

            if all([long_mm, larg_mm, haut_mm]):
                dims_str = f"{long_mm:.0f} × {larg_mm:.0f} × {haut_mm:.0f} mm"
                status = upsert_spec_line(product, attr_dims, dims_str)
                print(f"         spec Encombrement → {status} ({dims_str})")

    created += 1

env.cr.commit()
print("─" * 56)
print(f"Terminé : {created} produit(s) mis à jour, {skipped} ignoré(s).")
