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

    name = fields.Char(required=True, tracking=True, translate=True)
    active = fields.Boolean(default=True)
    featured = fields.Boolean(default=False)
    website_published = fields.Boolean(default=True, tracking=True)
    brand_id = fields.Many2one("auto.brand", required=True, tracking=True)
    product_template_id = fields.Many2one(
        "product.template", required=True, ondelete="restrict", tracking=True
    )
    category_id = fields.Many2one("auto.vehicle.category", tracking=True)
    motorization_id = fields.Many2one("auto.motorization", tracking=True)
    year = fields.Integer(default=lambda self: date.today().year)
    seats = fields.Integer(default=5)
    mileage_km = fields.Integer(default=0)
    range_km = fields.Integer(string="Range (km)")
    consumption = fields.Float(string="Consumption")
    power_kw = fields.Float(string="Power (kW)")
    battery_capacity = fields.Float(string="Battery Capacity (kWh)")
    charging_time = fields.Char()
    warranty_years = fields.Integer(default=3)
    availability = fields.Selection(
        AVAILABILITY_SELECTION, default="available", required=True, tracking=True
    )
    stock_qty = fields.Integer(default=1)
    short_description = fields.Text(translate=True)
    description = fields.Html(translate=True)
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
        "res.currency", related="product_template_id.currency_id", readonly=True
    )
    list_price = fields.Float(related="product_template_id.list_price", readonly=False)
    main_image = fields.Image(
        compute="_compute_main_image", store=False, max_width=1920, max_height=1920
    )
    website_url = fields.Char(compute="_compute_website_url")

    seo_title = fields.Char(translate=True)
    seo_description = fields.Text(translate=True)
    compare_enabled = fields.Boolean(default=True)

    favorite_partner_ids = fields.Many2many(
        "res.partner",
        "auto_vehicle_favorite_rel",
        "vehicle_id",
        "partner_id",
        string="Partenaires favoris",
    )
    favorite_count = fields.Integer(compute="_compute_favorite_count")

    _sql_constraints = [
        (
            "auto_vehicle_product_uniq",
            "unique(product_template_id)",
            "Chaque produit ne peut être lié qu'à un seul véhicule.",
        )
    ]

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




