"""Generate Odoo catalog records and source documentation from catalog_expansion.json."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "tools" / "catalog_expansion.json"
XML_PATH = ROOT / "custom_addons" / "auto_base" / "data" / "catalog_expansion.xml"
DOC_PATH = ROOT / "docs" / "CATALOG_SOURCES.md"

BRAND_DESCRIPTION = (
    "Constructeur automobile chinois proposant une gamme moderne de véhicules électrifiés."
)

DESCRIPTIONS = {
    ("auto_category_compact", "auto_motorization_electric"): (
        "Compacte électrique pratique, efficiente et adaptée aux déplacements urbains."
    ),
    ("auto_category_compact", "auto_motorization_full_hybrid"): (
        "Compacte hybride efficiente, agréable en ville et simple à utiliser au quotidien."
    ),
    ("auto_category_sedan", "auto_motorization_electric"): (
        "Berline électrique élégante combinant efficience, performances et confort."
    ),
    ("auto_category_crossover", "auto_motorization_electric"): (
        "Crossover électrique polyvalent avec technologies connectées et conduite fluide."
    ),
    ("auto_category_suv", "auto_motorization_electric"): (
        "SUV électrique moderne offrant confort, technologie et autonomie pour tous les trajets."
    ),
    ("auto_category_suv", "auto_motorization_hybrid"): (
        "SUV hybride rechargeable polyvalent avec une grande autonomie combinée."
    ),
}


def field(name: str, value: object | None = None, *, ref: str | None = None) -> str:
    if ref:
        return f'        <field name="{name}" ref="{escape(ref)}"/>'
    text = escape(str(value)) if value is not None else ""
    return f'        <field name="{name}">{text}</field>'


def bool_field(name: str, value: bool) -> str:
    return field(name, "1" if value else "0")


def get_description(vehicle: dict) -> str:
    key = (vehicle["category_id"], vehicle["motorization_id"])
    return DESCRIPTIONS.get(
        key,
        "Véhicule électrifié moderne, confortable et adapté aux usages quotidiens.",
    )


def generate_xml(data: dict) -> str:
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<odoo>"]

    for brand in data["brands"]:
        lines.extend(
            [
                f'    <record id="{brand["id"]}" model="auto.brand">',
                field("name", brand["name"]),
                field("code", brand["code"]),
                field("sequence", brand["sequence"]),
                (
                    '        <field name="logo" type="base64" '
                    f'file="auto_base/static/src/img/brands/{brand["image"]}"/>'
                ),
                f"        <field name=\"description\"><![CDATA[<p>{BRAND_DESCRIPTION}</p>]]></field>",
                "    </record>",
                "",
            ]
        )

    for motorization in data["motorizations"]:
        lines.extend(
            [
                f'    <record id="{motorization["id"]}" model="auto.motorization">',
                field("name", motorization["name"]),
                field("code", motorization["code"]),
                bool_field("is_electrified", True),
                field("sequence", motorization["sequence"]),
                "    </record>",
                "",
            ]
        )

    for vehicle in data["vehicles"]:
        product_id = vehicle["id"].replace("vehicle_", "product_", 1)
        image_id = vehicle["id"].replace("vehicle_", "vehicle_image_", 1) + "_01"
        image_path = f'auto_base/static/src/img/vehicles/{vehicle["image"]}'
        description = get_description(vehicle)

        lines.extend(
            [
                f'    <record id="{product_id}" model="product.template">',
                field("name", vehicle["name"]),
                field("list_price", vehicle["price"]),
                field("default_code", vehicle["default_code"]),
                field("type", "consu"),
                bool_field("sale_ok", True),
                bool_field("purchase_ok", False),
                f'        <field name="image_1920" type="base64" file="{image_path}"/>',
                "    </record>",
                "",
                f'    <record id="{vehicle["id"]}" model="auto.vehicle">',
                field("name", vehicle["name"]),
                field("brand_id", ref=vehicle["brand_id"]),
                field("product_template_id", ref=product_id),
                field("category_id", ref=vehicle["category_id"]),
                field("motorization_id", ref=vehicle["motorization_id"]),
                field("availability", vehicle.get("availability", "available")),
                field("year", 2026),
                field("range_km", vehicle["range_km"]),
                field("power_kw", vehicle["power_kw"]),
                field("battery_capacity", vehicle["battery_capacity"]),
                field("charging_time", vehicle["charging_time"]),
                field("stock_qty", vehicle.get("stock_qty", 3)),
                bool_field("featured", vehicle.get("featured", False)),
                field("short_description", description),
                (
                    "        <field name=\"color_ids\" "
                    "eval=\"[(6, 0, [ref('auto_color_white'), ref('auto_color_black'), "
                    "ref('auto_color_grey')])]\"/>"
                ),
                (
                    "        <field name=\"option_ids\" "
                    "eval=\"[(6, 0, [ref('auto_option_fast_charge'), ref('auto_option_adas'), "
                    "ref('auto_option_camera_360')])]\"/>"
                ),
                "    </record>",
                "",
                f'    <record id="{image_id}" model="auto.vehicle.image">',
                field("vehicle_id", ref=vehicle["id"]),
                field("name", f'{vehicle["name"]} Exterior'),
                f'        <field name="image_1920" type="base64" file="{image_path}"/>',
                field("sequence", 10),
                bool_field("is_cover", True),
                "    </record>",
                "",
            ]
        )

    lines.append("</odoo>")
    return "\n".join(lines) + "\n"


def generate_docs(data: dict) -> str:
    lines = [
        "# Sources du catalogue automobile",
        "",
        (
            f"Catalogue enrichi le {data['catalog_date']}. Les prix sont des prix publics "
            "TTC indicatifs ou des prix de lancement européens, hors options et promotions."
        ),
        "",
        "Ils doivent être vérifiés avant toute publication commerciale définitive.",
        "",
        "## Marques",
        "",
        "| Marque | Source officielle |",
        "| --- | --- |",
    ]
    for brand in data["brands"]:
        lines.append(f'| {brand["name"]} | {brand["source"]} |')

    lines.extend(
        [
            "",
            "## Véhicules ajoutés",
            "",
            "| Marque | Modèle | Prix indicatif | Source officielle |",
            "| --- | --- | ---: | --- |",
        ]
    )
    brand_names = {brand["id"]: brand["name"] for brand in data["brands"]}
    brand_names.update(
        {
            "auto_brand_byd": "BYD",
            "auto_brand_mg": "MG",
            "auto_brand_xpeng": "XPeng",
            "auto_brand_nio": "NIO",
            "auto_brand_omoda": "OMODA",
            "auto_brand_zeekr": "Zeekr",
            "auto_brand_leapmotor": "Leapmotor",
        }
    )
    for vehicle in data["vehicles"]:
        price = f'{vehicle["price"]:,.0f} €'.replace(",", " ")
        lines.append(
            f'| {brand_names[vehicle["brand_id"]]} | {vehicle["name"]} | '
            f'{price} | {vehicle["source"]} |'
        )

    lines.extend(
        [
            "",
            "## Photos",
            "",
            (
                "Les photos réelles sont téléchargées depuis Wikimedia Commons par "
                "`tools/fetch_catalog_assets.py`. Le fichier "
                "`docs/CATALOG_IMAGE_SOURCES.md` contient les attributions exactes."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    data = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    XML_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    XML_PATH.write_text(generate_xml(data), encoding="utf-8")
    DOC_PATH.write_text(generate_docs(data), encoding="utf-8")
    print(f"Generated {XML_PATH.relative_to(ROOT)}")
    print(f"Generated {DOC_PATH.relative_to(ROOT)}")
    print(f"Vehicles added: {len(data['vehicles'])}")
    print(f"Brands added: {len(data['brands'])}")


if __name__ == "__main__":
    main()
