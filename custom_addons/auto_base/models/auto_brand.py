from odoo import fields, models


class AutoBrand(models.Model):
    _name = "auto.brand"
    _description = "Automotive Brand"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    website_published = fields.Boolean(default=True)
    logo = fields.Image(max_width=1024, max_height=1024)
    description = fields.Html(translate=True)
    vehicle_ids = fields.One2many("auto.vehicle", "brand_id", string="Vehicles")
    vehicle_count = fields.Integer(compute="_compute_vehicle_count")

    _sql_constraints = [
        ("auto_brand_name_uniq", "unique(name)", "Brand name must be unique."),
    ]

    def _compute_vehicle_count(self):
        data = self.env["auto.vehicle"].read_group(
            [("brand_id", "in", self.ids)], ["brand_id"], ["brand_id"]
        )
        mapped = {row["brand_id"][0]: row["brand_id_count"] for row in data}
        for brand in self:
            brand.vehicle_count = mapped.get(brand.id, 0)

    def action_open_vehicles(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Vehicles",
            "res_model": "auto.vehicle",
            "view_mode": "list,form",
            "domain": [("brand_id", "=", self.id)],
            "context": {"default_brand_id": self.id},
        }
