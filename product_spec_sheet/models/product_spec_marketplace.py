# -*- coding: utf-8 -*-
import base64
import csv
import io
import json
import logging
import secrets
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductSpecMarketplace(models.Model):
    """
    Canal d'export marketplace : définit le format, le mapping des champs
    et les filtres de sélection des produits.
    """
    _name        = "product.spec.marketplace"
    _description = "Canal marketplace"
    _order       = "sequence, name"

    name     = fields.Char(string="Canal", required=True)
    sequence = fields.Integer(default=10)
    active   = fields.Boolean(default=True)

    channel_type = fields.Selection(
        [
            ("google",     "Google Shopping (XML)"),
            ("amazon",     "Amazon (CSV plat)"),
            ("cdiscount",  "Cdiscount (CSV)"),
            ("rakuten",    "Rakuten / PriceMinister (CSV)"),
            ("facebook",   "Facebook / Meta (CSV)"),
            ("generic_csv","CSV personnalisé"),
            ("generic_json","JSON personnalisé"),
        ],
        string="Type de flux", required=True, default="generic_csv",
    )

    # ── Sélection des produits ────────────────────────────────────
    categ_ids = fields.Many2many(
        "product.category", string="Catégories produit",
        help="Laisser vide pour inclure toutes les catégories.",
    )
    only_published   = fields.Boolean(string="Produits publiés uniquement", default=True)
    only_in_stock    = fields.Boolean(string="En stock uniquement", default=False)
    only_complete    = fields.Boolean(
        string="Fiches complètes uniquement", default=True,
        help="Exclut les produits sans poids, dimensions, photo ou caractéristiques.",
    )
    exclude_eol      = fields.Boolean(
        string="Exclure les produits en fin de vie", default=True,
        help="Exclut les statuts Arrêté et Obsolète.",
    )
    min_price        = fields.Float(string="Prix minimum")

    # ── Paramètres de flux ────────────────────────────────────────
    currency_id = fields.Many2one(
        "res.currency", string="Devise",
        default=lambda self: self.env.company.currency_id,
    )
    price_markup = fields.Float(
        string="Majoration prix (%)", default=0.0,
        help="Majoration appliquée au prix de vente sur ce canal.",
    )
    include_specs = fields.Boolean(
        string="Inclure les caractéristiques", default=True,
    )
    spec_format = fields.Selection(
        [("columns", "Une colonne par caractéristique"),
         ("inline",  "Regroupées dans une colonne"),
         ("json",    "Objet JSON")],
        string="Format des caractéristiques", default="columns",
    )
    csv_delimiter = fields.Selection(
        [(";", "Point-virgule (;)"), (",", "Virgule (,)"), ("\t", "Tabulation")],
        string="Séparateur CSV", default=";",
    )

    # ── Accès au flux ─────────────────────────────────────────────
    feed_token = fields.Char(
        string="Jeton du flux", readonly=True, copy=False,
        default=lambda self: secrets.token_urlsafe(24),
    )
    feed_url = fields.Char(string="URL du flux", compute="_compute_feed_url")
    auto_publish = fields.Boolean(
        string="Flux accessible en ligne", default=False,
        help="Rend le flux accessible par URL pour que la marketplace vienne le chercher.",
    )

    mapping_ids = fields.One2many(
        "product.spec.marketplace.mapping", "marketplace_id",
        string="Correspondance des champs",
    )
    export_ids  = fields.One2many(
        "product.spec.marketplace.export", "marketplace_id", string="Exports",
    )
    product_count = fields.Integer(string="Produits éligibles", compute="_compute_product_count")

    @api.depends("feed_token", "auto_publish")
    def _compute_feed_url(self):
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        for rec in self:
            if rec.auto_publish and rec.feed_token:
                ext = "xml" if rec.channel_type == "google" else (
                    "json" if rec.channel_type == "generic_json" else "csv"
                )
                rec.feed_url = f"{base}/marketplace/feed/{rec.feed_token}.{ext}"
            else:
                rec.feed_url = False

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec._get_products())

    def action_regenerate_token(self):
        """Régénère le jeton — invalide l'ancienne URL."""
        for rec in self:
            rec.feed_token = secrets.token_urlsafe(24)
        return True

    # ── Sélection des produits ────────────────────────────────────
    def _get_products(self):
        """Renvoie les produits éligibles selon les filtres du canal."""
        self.ensure_one()
        domain = [("sale_ok", "=", True)]

        if self.only_published:
            domain.append(("website_published", "=", True))
        if self.categ_ids:
            domain.append(("categ_id", "child_of", self.categ_ids.ids))
        if self.only_complete:
            domain.append(("spec_quality_level", "=", "complete"))
        if self.exclude_eol:
            domain.append(("lifecycle_state", "not in", ["eol", "obsolete"]))
        if self.min_price:
            domain.append(("list_price", ">=", self.min_price))

        products = self.env["product.template"].sudo().search(domain, order="name")

        if self.only_in_stock:
            products = products.filtered(lambda p: p.qty_available > 0)

        return products

    # ── Valeur d'un champ pour un produit ─────────────────────────
    def _get_field_value(self, product, mapping):
        """Résout la valeur d'un mapping pour un produit donné."""
        self.ensure_one()
        src = mapping.source_type

        if src == "field":
            value = product
            for part in (mapping.field_path or "").split("."):
                if not part:
                    break
                value = getattr(value, part, "")
                if not value:
                    break
            if hasattr(value, "display_name"):
                value = value.display_name
            return value or ""

        if src == "spec":
            if not mapping.spec_attribute_id:
                return ""
            return product._get_spec_value(mapping.spec_attribute_id) or ""

        if src == "static":
            return mapping.static_value or ""

        if src == "price":
            price = product.list_price or 0.0
            if self.price_markup:
                price = price * (1 + self.price_markup / 100.0)
            return f"{price:.2f}"

        if src == "url":
            base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
            return f"{base}{product.website_url}" if product.website_url else ""

        if src == "image":
            base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
            return f"{base}/web/image/product.template/{product.id}/image_1920"

        if src == "specs_all":
            parts = []
            for line in product.spec_line_ids:
                parts.append(f"{line.attribute_id.name}: {line.value}")
            return " | ".join(parts)

        return ""

    # ── Génération des flux ───────────────────────────────────────
    def generate_feed(self):
        """Point d'entrée : renvoie (contenu_bytes, nom_fichier, mimetype)."""
        self.ensure_one()
        products = self._get_products()

        if self.channel_type == "google":
            return self._generate_google_xml(products)
        if self.channel_type == "generic_json":
            return self._generate_json(products)
        return self._generate_csv(products)

    def _get_effective_mappings(self):
        """Mappings configurés, ou mapping par défaut selon le type de canal."""
        self.ensure_one()
        if self.mapping_ids:
            return self.mapping_ids.sorted("sequence")
        return self._default_mappings()

    def _default_mappings(self):
        """Crée un mapping en mémoire adapté au type de canal."""
        self.ensure_one()
        M = self.env["product.spec.marketplace.mapping"]
        defaults = [
            ("id",          "field", "default_code",     None),
            ("title",       "field", "name",             None),
            ("description", "field", "description_sale", None),
            ("link",        "url",   None,               None),
            ("image_link",  "image", None,               None),
            ("price",       "price", None,               None),
            ("brand",       "field", "categ_id.name",    None),
            ("condition",   "static", None,              "new"),
        ]
        records = M
        for i, (col, src, path, static) in enumerate(defaults):
            records |= M.new({
                "marketplace_id": self.id,
                "sequence":       (i + 1) * 10,
                "column_name":    col,
                "source_type":    src,
                "field_path":     path,
                "static_value":   static,
            })
        return records

    def _generate_csv(self, products):
        """Flux CSV avec le mapping configuré."""
        self.ensure_one()
        mappings = self._get_effective_mappings()
        output   = io.StringIO()
        delim    = self.csv_delimiter or ";"

        headers = [m.column_name for m in mappings]

        # Colonnes de caractéristiques
        spec_attrs = self.env["product.spec.attribute"]
        if self.include_specs and self.spec_format == "columns":
            spec_attrs = products.mapped("spec_line_ids.attribute_id").sorted(
                lambda a: (a.category_id.sequence, a.sequence, a.name or "")
            )
            headers += [f"spec_{a.name}" for a in spec_attrs]
        elif self.include_specs and self.spec_format == "inline":
            headers.append("caracteristiques")
        elif self.include_specs and self.spec_format == "json":
            headers.append("specs_json")

        writer = csv.writer(output, delimiter=delim, quoting=csv.QUOTE_MINIMAL,
                            lineterminator="\n")
        writer.writerow(headers)

        for product in products:
            row = [self._get_field_value(product, m) for m in mappings]

            if self.include_specs and self.spec_format == "columns":
                for attr in spec_attrs:
                    row.append(product._get_spec_value(attr) or "")
            elif self.include_specs and self.spec_format == "inline":
                row.append(" | ".join(
                    f"{l.attribute_id.name}: {l.value}" for l in product.spec_line_ids
                ))
            elif self.include_specs and self.spec_format == "json":
                row.append(json.dumps({
                    l.attribute_id.name: l.value for l in product.spec_line_ids
                }, ensure_ascii=False))

            writer.writerow(row)

        content  = output.getvalue().encode("utf-8-sig")
        filename = f"{self.name.replace(' ', '_')}_{datetime.now():%Y%m%d}.csv"
        return content, filename, "text/csv"

    def _generate_google_xml(self, products):
        """Flux Google Shopping au format RSS 2.0."""
        self.ensure_one()
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        company = self.env.company
        currency = (self.currency_id or company.currency_id).name

        def esc(text):
            if text is None:
                return ""
            return (str(text).replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;").replace('"', "&quot;"))

        items = []
        for p in products:
            price = p.list_price or 0.0
            if self.price_markup:
                price = price * (1 + self.price_markup / 100.0)

            availability = "in stock" if (not self.only_in_stock or p.qty_available > 0) else "out of stock"

            specs_xml = ""
            if self.include_specs:
                for line in p.spec_line_ids[:10]:
                    specs_xml += (
                        f"\n      <g:product_detail>"
                        f"<g:section_name>{esc(line.category_id.name)}</g:section_name>"
                        f"<g:attribute_name>{esc(line.attribute_id.name)}</g:attribute_name>"
                        f"<g:attribute_value>{esc(line.value)}</g:attribute_value>"
                        f"</g:product_detail>"
                    )

            shipping_weight = f"{p.weight:.3f} kg" if p.weight else ""

            items.append(f"""    <item>
      <g:id>{esc(p.default_code or p.id)}</g:id>
      <g:title>{esc(p.name)}</g:title>
      <g:description>{esc(p.description_sale or p.name)}</g:description>
      <g:link>{esc(base + (p.website_url or ''))}</g:link>
      <g:image_link>{esc(base)}/web/image/product.template/{p.id}/image_1920</g:image_link>
      <g:availability>{availability}</g:availability>
      <g:price>{price:.2f} {currency}</g:price>
      <g:brand>{esc(company.name)}</g:brand>
      <g:condition>new</g:condition>
      <g:product_type>{esc(p.categ_id.complete_name)}</g:product_type>
      <g:shipping_weight>{shipping_weight}</g:shipping_weight>{specs_xml}
    </item>""")

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
  <channel>
    <title>{esc(company.name)} — {esc(self.name)}</title>
    <link>{esc(base)}</link>
    <description>Catalogue produits {esc(company.name)}</description>
{chr(10).join(items)}
  </channel>
</rss>"""

        filename = f"{self.name.replace(' ', '_')}_{datetime.now():%Y%m%d}.xml"
        return xml.encode("utf-8"), filename, "application/xml"

    def _generate_json(self, products):
        """Flux JSON structuré."""
        self.ensure_one()
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        data = []
        for p in products:
            price = p.list_price or 0.0
            if self.price_markup:
                price = price * (1 + self.price_markup / 100.0)
            data.append({
                "id":          p.default_code or str(p.id),
                "name":        p.name,
                "description": p.description_sale or "",
                "price":       round(price, 2),
                "currency":    (self.currency_id or self.env.company.currency_id).name,
                "url":         f"{base}{p.website_url}" if p.website_url else "",
                "image":       f"{base}/web/image/product.template/{p.id}/image_1920",
                "category":    p.categ_id.complete_name,
                "weight_kg":   p.weight or None,
                "volume_m3":   p.volume or None,
                "lifecycle":   p.lifecycle_state,
                "in_stock":    p.qty_available > 0,
                "specs": {
                    l.attribute_id.name: l.value for l in p.spec_line_ids
                } if self.include_specs else {},
            })

        payload = {
            "generated_at": datetime.now().isoformat(),
            "channel":      self.name,
            "count":        len(data),
            "products":     data,
        }
        content  = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        filename = f"{self.name.replace(' ', '_')}_{datetime.now():%Y%m%d}.json"
        return content, filename, "application/json"

    # ── Actions ───────────────────────────────────────────────────
    def action_export_now(self):
        """Génère le flux et l'attache comme pièce jointe téléchargeable."""
        self.ensure_one()
        products = self._get_products()
        if not products:
            raise UserError(_("Aucun produit ne correspond aux critères de ce canal."))

        content, filename, mimetype = self.generate_feed()

        attachment = self.env["ir.attachment"].create({
            "name":      filename,
            "type":      "binary",
            "datas":     base64.b64encode(content),
            "res_model": self._name,
            "res_id":    self.id,
            "mimetype":  mimetype,
        })

        self.env["product.spec.marketplace.export"].create({
            "marketplace_id": self.id,
            "product_count":  len(products),
            "file_size":      len(content),
            "attachment_id":  attachment.id,
            "state":          "done",
        })

        return {
            "type": "ir.actions.act_url",
            "url":  f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }

    @api.model
    def cron_generate_feeds(self):
        """Régénère tous les flux publiés (action planifiée)."""
        for mp in self.search([("active", "=", True), ("auto_publish", "=", True)]):
            try:
                mp.action_export_now()
            except Exception as e:
                _logger.warning("Export marketplace %s échoué : %s", mp.name, e)
        return True


class ProductSpecMarketplaceMapping(models.Model):
    """Correspondance entre une colonne du flux et une donnée Odoo."""
    _name        = "product.spec.marketplace.mapping"
    _description = "Correspondance de champ marketplace"
    _order       = "marketplace_id, sequence"

    marketplace_id = fields.Many2one(
        "product.spec.marketplace", required=True, ondelete="cascade",
    )
    sequence    = fields.Integer(default=10)
    column_name = fields.Char(
        string="Nom de colonne", required=True,
        help="Nom attendu par la marketplace (ex : id, title, price).",
    )
    source_type = fields.Selection(
        [
            ("field",     "Champ produit"),
            ("spec",      "Caractéristique"),
            ("price",     "Prix (avec majoration)"),
            ("url",       "URL du produit"),
            ("image",     "URL de l'image"),
            ("specs_all", "Toutes les caractéristiques"),
            ("static",    "Valeur fixe"),
        ],
        string="Source", required=True, default="field",
    )
    field_path = fields.Char(
        string="Chemin du champ",
        help="Ex : name, default_code, categ_id.name, weight",
    )
    spec_attribute_id = fields.Many2one(
        "product.spec.attribute", string="Caractéristique",
    )
    static_value = fields.Char(string="Valeur fixe")


class ProductSpecMarketplaceExport(models.Model):
    """Historique des exports générés."""
    _name        = "product.spec.marketplace.export"
    _description = "Export marketplace"
    _order       = "create_date desc"

    marketplace_id = fields.Many2one(
        "product.spec.marketplace", string="Canal", required=True, ondelete="cascade",
    )
    export_date   = fields.Datetime(
        string="Date", default=fields.Datetime.now, readonly=True,
    )
    product_count = fields.Integer(string="Produits exportés", readonly=True)
    file_size     = fields.Integer(string="Taille (octets)", readonly=True)
    attachment_id = fields.Many2one("ir.attachment", string="Fichier", readonly=True)
    state         = fields.Selection(
        [("done", "Généré"), ("error", "Erreur")], default="done", readonly=True,
    )
    error_message = fields.Char(string="Erreur", readonly=True)

    def action_download(self):
        self.ensure_one()
        if not self.attachment_id:
            raise UserError(_("Aucun fichier associé à cet export."))
        return {
            "type": "ir.actions.act_url",
            "url":  f"/web/content/{self.attachment_id.id}?download=true",
            "target": "self",
        }
