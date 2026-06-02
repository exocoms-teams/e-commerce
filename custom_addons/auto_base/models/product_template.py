from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    auto_vehicle_ids = fields.One2many(
        "auto.vehicle", "product_template_id", string="Véhicules liés"
    )
    auto_vehicle_count = fields.Integer(compute="_compute_auto_vehicle_count")

    def _compute_auto_vehicle_count(self):
        for product in self:
            product.auto_vehicle_count = len(product.auto_vehicle_ids)

    def action_open_auto_vehicles(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Véhicule",
            "res_model": "auto.vehicle",
            "view_mode": "list,form",
            "domain": [("product_template_id", "=", self.id)],
            "context": {"default_product_template_id": self.id},
        }
