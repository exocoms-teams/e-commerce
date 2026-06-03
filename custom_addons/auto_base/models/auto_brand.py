from odoo import fields, models


class AutoBrand(models.Model):
    _name = "auto.brand"
    _description = "Marque automobile"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    website_published = fields.Boolean(default=True)
    logo = fields.Image(max_width=1024, max_height=1024)
    description = fields.Html(translate=True)
    vehicle_ids = fields.One2many("auto.vehicle", "brand_id", string="Véhicules")
    vehicle_count = fields.Integer(compute="_compute_vehicle_count")

    _name_uniq = models.Constraint(
        "unique(name)",
        "Le nom de la marque doit être unique.",
    )

    def _compute_vehicle_count(self):
        vehicle_model = self.env["auto.vehicle"]
        domain = [("brand_id", "in", self.ids)]
        if hasattr(vehicle_model, "formatted_read_group"):
            data = vehicle_model.formatted_read_group(domain, ["brand_id"], ["__count"])
        else:
            data = vehicle_model.read_group(domain, ["brand_id"], ["brand_id"])
        mapped = {
            row["brand_id"][0]: row.get("__count", row.get("brand_id_count", 0))
            for row in data
            if row.get("brand_id")
        }
        for brand in self:
            brand.vehicle_count = mapped.get(brand.id, 0)

    def action_open_vehicles(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Véhicules",
            "res_model": "auto.vehicle",
            "view_mode": "list,form",
            "domain": [("brand_id", "=", self.id)],
            "context": {"default_brand_id": self.id},
        }
