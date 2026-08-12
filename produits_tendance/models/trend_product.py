from odoo import models, fields, api
from odoo.exceptions import ValidationError
from .trend_ad import latest_ads_by_ref
from odoo.addons.produits_tendance.services.scoring_engine import ScoringEngine


class TrendProduct(models.Model):
    _name = 'trend.product'
    _description = 'Produit collecté sur un site e-commerce'

    name = fields.Char(string="Nom du produit", required=True)
    product_ref = fields.Char(string="Référence produit (site source)")
    category_id = fields.Many2one('trend.category', string="Catégorie")
    sales_count = fields.Integer(string="Nombre de ventes")
    price = fields.Float(string="Prix", help="Prix du produit sur le site source, utilisé pour le filtre price_max (WIN-45/76).")
    date = fields.Date(string="Date de collecte")
    score_site_x = fields.Float(string="Score site source")
    country = fields.Char(string="Pays")
    image_url = fields.Char(string="URL de l'image")

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
    rank_number = fields.Integer(
        string="Classement",
        compute="_compute_rank_number",
        help="Position dans le classement général par score décroissant"
    )
    is_top_10 = fields.Boolean(
        string="Dans le Top 10",
        compute="_compute_rank_number",
        search="_search_is_top_10",
        help="Vrai si le produit fait partie des 10 meilleurs scores"
    )
    is_top_3 = fields.Boolean(
        string="Dans le Top 3",
        compute="_compute_rank_number",
        search="_search_is_top_3",
        help="Vrai si le produit fait partie des 3 meilleurs scores"
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

    @api.depends('current_score')
    def _compute_rank_number(self):
        """Compute the rank of each product based on current_score (highest first).
        Also computes whether the product is in the top 10 and top 3.
        """
        if not self:
            return
        # Get all products ordered by score descending to compute ranks
        all_products = self.search([], order='current_score desc, id')
        # Create a mapping from product ID to rank
        rank_map = {product.id: idx + 1 for idx, product in enumerate(all_products)}
        for product in self:
            product.rank_number = rank_map.get(product.id, 0)
            product.is_top_10 = (product.rank_number <= 10)
            product.is_top_3 = (product.rank_number <= 3)

    # Search methods to make non‑stored boolean fields usable in domains.
    # Basées sur les ids du top N (pas sur un score de coupure comparé en
    # SQL) : évite tout souci d'égalité/précision flottante entre le score
    # calculé côté Python et la valeur stockée en base.
    @api.model
    def _search_is_top_n(self, operator, value, limit):
        if isinstance(value, (list, tuple)):
            want_true = True in value
        else:
            want_true = bool(value)
        if operator in ('!=', 'not in'):
            want_true = not want_true
        elif operator not in ('=', 'in'):
            # For other operators (<, >, etc.) we fall back to false domain (should not appear in UI)
            return []
        top_ids = self.search([], order='current_score desc', limit=limit).ids
        if want_true:
            return [('id', 'in', top_ids)]
        else:
            return [('id', 'not in', top_ids)]

    @api.model
    def _search_is_top_10(self, operator, value):
        """Convert a domain on is_top_10 into an equivalent domain on ids."""
        return self._search_is_top_n(operator, value, 10)

    @api.model
    def _search_is_top_3(self, operator, value):
        """Convert a domain on is_top_3 into an equivalent domain on ids."""
        return self._search_is_top_n(operator, value, 3)

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
        # Create ScoringEngine instance
        scoring_engine = ScoringEngine()

        # Handle the case where previous_metrics is None (convert to required dict)
        if previous_metrics is None:
            previous_metrics = {'ventes': 0, 'likes': 0, 'partages': 0, 'ads': 0}
        # FILTRER LES PUBLICITÉS EN DOUBLE AVANT LE CALCUL
        latest_ads = latest_ads_by_ref(self.ad_ids)
        # Build current metrics (same logic as in trend_score_calculator.build_current_metrics)
        current_metrics = {
            'ventes': self.sales_count or 0,
            'likes': sum(latest_ads.mapped('likes_count')),
            'partages': sum(latest_ads.mapped('shares_count')),
            'ads': len(latest_ads),
        }

        # Normalize source score (same logic as in trend_score_calculator.normalize_source_score)
        source_score = 0.0
        if self.score_site_x:
            source_score = max(0.0, min(self.score_site_x / 10.0, 1.0))

        self.ensure_one()
        # Calculate score using ScoringEngine
        return scoring_engine.calculate_trend_score(current_metrics, previous_metrics, source_score)