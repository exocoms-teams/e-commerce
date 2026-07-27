from odoo import models, fields, api
from odoo.exceptions import ValidationError

from .trend_score_calculator import compute_product_trend_score


class TrendProduct(models.Model):
    _name = 'trend.product'
    _description = 'Produit collecté sur un site e-commerce'

    name = fields.Char(string="Nom du produit", required=True)
    product_ref = fields.Char(string="Référence produit (site source)")
    category_id = fields.Many2one('trend.category', string="Catégorie")
    sales_count = fields.Integer(string="Nombre de ventes")
    date = fields.Date(string="Date de collecte")
    score_site_x = fields.Float(string="Score site source")
    country = fields.Char(string="Pays")

    source = fields.Selection([
        ('scraping', 'Scraping'),
        ('crowdsourcing', 'Crowdsourcing'),
        ('api', 'API'),
    ], string="Source", required=True, default='api')

    ad_ids = fields.One2many(
        'trend.ad',
        'product_id',
        string="Publicités liées"
    )

    # --- NOUVEAUX CHAMPS POUR LE SCORE ---
    
    score_ids = fields.One2many(
        'trend.score',
        'product_id',
        string="Historique des scores"
    )

    current_score = fields.Float(
        string="Score actuel",
        compute="_compute_current_score",
        store=True,
        help="Reflète toujours le dernier score calculé pour ce produit."
    )

    # --- CONTRAINTES SQL ---
    _product_ref_source_uniq = models.Constraint(
        'unique(product_ref)',
        "Ce produit est déjà enregistré. Impossible de le dupliquer.",
    )

    # --- MÉTHODES DE CALCUL (COMPUTE) ---
    
    @api.depends('score_ids.computed_score', 'score_ids.computed_at')
    def _compute_current_score(self):
        for product in self:
            if product.score_ids:
                # La méthode 'sorted' native de l'ORM gère très bien les valeurs vides.
                # reverse=True ramène le plus récent (la date la plus grande) en premier [0].
                latest_score = product.score_ids.sorted('computed_at', reverse=True)[:1]
                product.current_score = latest_score.computed_score if latest_score else 0.0
            else:
                product.current_score = 0.0

    # --- MÉTHODES DE VALIDATION ---
    @api.constrains('sales_count')
    def _check_sales_count_positive(self):
        for record in self:
            if record.sales_count is not None and record.sales_count < 0:
                raise ValidationError(
                    "Le nombre de ventes (sales_count) ne peut pas être négatif."
                )

    # --- SCORE DE TENDANCE ---
    def compute_trend_score(self, previous_metrics=None):
        """Calcule le score de tendance de ce produit (formule décrite dans
        score.md) en croisant sales_count/score_site_x (trend.product) avec
        les likes_count/shares_count agrégés des trend.ad liés.
        """
        self.ensure_one()
        return compute_product_trend_score(self, previous_metrics=previous_metrics)