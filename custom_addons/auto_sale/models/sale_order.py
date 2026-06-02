from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        result = super().action_confirm()
        for order in self:
            vehicles = order.order_line.mapped("auto_vehicle_id")
            vehicles.write({"availability": "sold", "stock_qty": 0})
        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    auto_vehicle_id = fields.Many2one("auto.vehicle", string="Véhicule")

    @api.onchange("product_template_id")
    def _onchange_product_template_id_auto_vehicle(self):
        for line in self:
            line.auto_vehicle_id = False
            if line.product_template_id:
                vehicle = self.env["auto.vehicle"].search(
                    [("product_template_id", "=", line.product_template_id.id)], limit=1
                )
                line.auto_vehicle_id = vehicle.id

    @api.onchange("product_id")
    def _onchange_product_id_auto_vehicle(self):
        for line in self:
            if not line.product_id:
                line.auto_vehicle_id = False
                continue
            vehicle = self.env["auto.vehicle"].search(
                [("product_template_id", "=", line.product_id.product_tmpl_id.id)], limit=1
            )
            line.auto_vehicle_id = vehicle.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("auto_vehicle_id"):
                continue
            product_template_id = vals.get("product_template_id")
            if not product_template_id and vals.get("product_id"):
                product = self.env["product.product"].browse(vals["product_id"])
                product_template_id = product.product_tmpl_id.id
            if product_template_id:
                vehicle = self.env["auto.vehicle"].search(
                    [("product_template_id", "=", product_template_id)], limit=1
                )
                if vehicle:
                    vals["auto_vehicle_id"] = vehicle.id
        return super().create(vals_list)
