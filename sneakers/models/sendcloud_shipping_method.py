from odoo import models, fields


class SendCloudShippingMethod(models.Model):
    _name = "sendcloud.shipping.method"
    _description = "SendCloud Shipping Method"

    name = fields.Char(
        required=True
    )

    sendcloud_id = fields.Integer(
        string="SendCloud ID",
        required=True,
        index=True
    )

    carrier = fields.Char()

    min_weight = fields.Float()

    max_weight = fields.Float()

    price = fields.Float(
        string="Default Price"
    )

    country_prices = fields.Text(
        string="Country Prices"
    )
