from odoo import fields, models


class TrendScore(models.Model):
    _name = "trend.score"
    _description = "Score de tendance d'un produit"
    _order = "rank asc"

    product_id = fields.Many2one(
        comodel_name="trend.product",
        string="Produit",
        required=True,
        ondelete="cascade",
        index=True,
    )
    ad_ids = fields.Many2many(
        comodel_name="trend.ad",
        relation="trend_score_trend_ad_rel",
        column1="score_id",
        column2="ad_id",
        string="Publicités liées",
    )
    computed_score = fields.Float(
        string="Score calculé",
        digits=(16, 4),
        default=0.0,
    )
    computed_at = fields.Datetime(
        string="Calculé le",
    )
    rank = fields.Integer(
        string="Classement",
        default=0,
    )