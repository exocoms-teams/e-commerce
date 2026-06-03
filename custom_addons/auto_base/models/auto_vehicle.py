from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AutoVehicle(models.Model):
    _name = "auto.vehicle"
    _description = "Véhicule automobile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "featured desc, id desc"

    AVAILABILITY_SELECTION = [
        ("available", "Disponible"),
        ("reserved", "Réservé"),
        ("sold", "Vendu"),
        ("coming_soon", "Bientôt disponible"),
    ]

    name = fields.Char(string="Nom", required=True, tracking=True, translate=True)
    active = fields.Boolean(string="Actif", default=True)
    featured = fields.Boolean(string="Mis en avant", default=False)
    website_published = fields.Boolean(string="Publie sur le site", default=True, tracking=True)
    brand_id = fields.Many2one("auto.brand", string="Marque", required=True, tracking=True)
    product_template_id = fields.Many2one(
        "product.template",
        string="Produit eCommerce",
        ondelete="restrict",
        tracking=True,
        help="Produit de vente lie au vehicule. S'il est vide, il est cree automatiquement a l'enregistrement.",
    )
    category_id = fields.Many2one("auto.vehicle.category", string="Categorie", tracking=True)
    motorization_id = fields.Many2one("auto.motorization", string="Motorisation", tracking=True)
    year = fields.Integer(string="Annee", default=lambda self: date.today().year)
    seats = fields.Integer(string="Places", default=5)
    mileage_km = fields.Integer(string="Kilometrage (km)", default=0)
    range_km = fields.Integer(string="Autonomie (km)")
    consumption = fields.Float(string="Consommation")
    power_kw = fields.Float(string="Puissance (kW)")
    battery_capacity = fields.Float(string="Capacite batterie (kWh)")
    charging_time = fields.Char(string="Temps de charge")
    warranty_years = fields.Integer(string="Garantie (annees)", default=3)
    availability = fields.Selection(
        AVAILABILITY_SELECTION, default="available", required=True, tracking=True
    )
    availability_label = fields.Char(compute="_compute_availability_label")
    stock_qty = fields.Integer(string="Stock", default=1)
    short_description = fields.Text(string="Resume court", translate=True)
    description = fields.Html(string="Description", translate=True)
    color_ids = fields.Many2many(
        "auto.vehicle.color",
        "auto_vehicle_color_rel",
        "vehicle_id",
        "color_id",
        string="Couleurs disponibles",
    )
    option_ids = fields.Many2many(
        "auto.vehicle.option",
        "auto_vehicle_option_rel",
        "vehicle_id",
        "option_id",
        string="Options",
    )
    image_ids = fields.One2many("auto.vehicle.image", "vehicle_id", string="Galerie")
    specification_ids = fields.One2many(
        "auto.specification", "vehicle_id", string="Spécifications"
    )

    currency_id = fields.Many2one(
        "res.currency", string="Devise", related="product_template_id.currency_id", readonly=True
    )
    list_price = fields.Float(string="Prix de vente", related="product_template_id.list_price", readonly=False)
    main_image = fields.Image(
        string="Image principale",
        compute="_compute_main_image", store=False, max_width=1920, max_height=1920
    )
    website_url = fields.Char(string="URL site", compute="_compute_website_url")

    seo_title = fields.Char(string="Titre SEO", translate=True)
    seo_description = fields.Text(string="Description SEO", translate=True)
    compare_enabled = fields.Boolean(string="Comparaison activee", default=True)

    favorite_partner_ids = fields.Many2many(
        "res.partner",
        "auto_vehicle_favorite_rel",
        "vehicle_id",
        "partner_id",
        string="Partenaires favoris",
    )
    favorite_count = fields.Integer(string="Favoris", compute="_compute_favorite_count")

    _sql_constraints = [
        (
            "auto_vehicle_product_uniq",
            "unique(product_template_id)",
            "Chaque produit ne peut être lié qu'à un seul véhicule.",
        )
    ]

    @api.depends("availability")
    @api.depends_context("lang")
    def _compute_availability_label(self):
        labels = dict(self._fields["availability"]._description_selection(self.env))
        for vehicle in self:
            vehicle.availability_label = labels.get(vehicle.availability)

    @api.depends("product_template_id.image_1920", "image_ids.image_1920", "image_ids.sequence")
    def _compute_main_image(self):
        for vehicle in self:
            image = vehicle.product_template_id.image_1920
            if not image and vehicle.image_ids:
                image = vehicle.image_ids.sorted("sequence")[0].image_1920
            vehicle.main_image = image

    def _compute_website_url(self):
        for vehicle in self:
            vehicle.website_url = f"/cars/{vehicle.id}" if vehicle.id else False

    @api.depends("favorite_partner_ids")
    def _compute_favorite_count(self):
        for vehicle in self:
            vehicle.favorite_count = len(vehicle.favorite_partner_ids)

    def _get_product_display_name(self):
        self.ensure_one()
        parts = []
        if self.brand_id and self.brand_id.name and self.brand_id.name not in (self.name or ""):
            parts.append(self.brand_id.name)
        if self.name:
            parts.append(self.name)
        return " ".join(parts) or _("Vehicule")

    def _prepare_product_template_values(self, vals):
        brand_name = ""
        if vals.get("brand_id"):
            brand = self.env["auto.brand"].browse(vals["brand_id"])
            brand_name = brand.name or ""
        vehicle_name = vals.get("name") or _("Vehicule")
        product_name = vehicle_name
        if brand_name and brand_name not in vehicle_name:
            product_name = f"{brand_name} {vehicle_name}"
        values = {
            "name": product_name,
            "sale_ok": True,
            "purchase_ok": False,
            "list_price": vals.get("list_price") or 0.0,
            "description_sale": vals.get("short_description") or "",
        }
        if "website_published" in self.env["product.template"]._fields:
            values["website_published"] = vals.get("website_published", True)
        return values

    @api.model_create_multi
    def create(self, vals_list):
        product_model = self.env["product.template"]
        for vals in vals_list:
            if not vals.get("product_template_id"):
                product = product_model.create(self._prepare_product_template_values(vals))
                vals["product_template_id"] = product.id
        vehicles = super().create(vals_list)
        vehicles._sync_product_template_from_vehicle()
        return vehicles

    def write(self, vals):
        result = super().write(vals)
        if {"name", "brand_id", "short_description", "website_published"} & set(vals):
            self._sync_product_template_from_vehicle()
        return result

    def _sync_product_template_from_vehicle(self):
        for vehicle in self.filtered("product_template_id"):
            values = {
                "name": vehicle._get_product_display_name(),
                "sale_ok": True,
                "purchase_ok": False,
            }
            if "website_published" in vehicle.product_template_id._fields:
                values["website_published"] = vehicle.website_published
            if vehicle.short_description:
                values["description_sale"] = vehicle.short_description
            vehicle.product_template_id.sudo().write(values)

    @api.constrains("year")
    def _check_year(self):
        current_year = date.today().year + 1
        for vehicle in self:
            if vehicle.year and (vehicle.year < 1990 or vehicle.year > current_year):
                raise ValidationError(
                    _("L'année du véhicule doit être comprise entre 1990 et l'année prochaine.")
                )

    def action_set_available(self):
        self.write({"availability": "available"})

    def action_set_reserved(self):
        self.write({"availability": "reserved"})

    def action_set_sold(self):
        self.write({"availability": "sold"})

    def action_set_coming_soon(self):
        self.write({"availability": "coming_soon"})

    def action_open_product(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Produit",
            "res_model": "product.template",
            "view_mode": "form",
            "res_id": self.product_template_id.id,
        }

    def action_toggle_favorite(self):
        partner = self.env.user.partner_id
        for vehicle in self:
            if partner in vehicle.favorite_partner_ids:
                vehicle.favorite_partner_ids = [(3, partner.id)]
            else:
                vehicle.favorite_partner_ids = [(4, partner.id)]

    def name_get(self):
        result = []
        for vehicle in self:
            label = vehicle.name
            if vehicle.brand_id:
                label = f"{vehicle.brand_id.name} {vehicle.name}"
            result.append((vehicle.id, label))
        return result




