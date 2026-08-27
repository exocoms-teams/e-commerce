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

    # --- GOOGLE TRENDS (purement informatif) ---
    # Décision d'équipe : le search_volume est affiché à titre indicatif sur
    # la fiche produit mais n'entre JAMAIS dans le calcul de computed_score.
    # Voir models/trend_score_calculator.py : la formule ne référence pas
    # ce champ.
    search_volume = fields.Integer(
        string="Volume de recherche Google Trends",
        default=0,
        help="Intérêt de recherche Google Trends au moment du calcul. "
             "Purement informatif : n'influence pas le score de tendance "
             "ni le classement (rank).",
    )

    # --- SNAPSHOT DES MÉTRIQUES (période T de ce calcul) ---
    # Ces champs "gèlent" les valeurs de V_T, L_T, P_T, A_T au moment du calcul.
    # Nécessaire car trend.product/trend.ad sont mutables (les compteurs
    # évoluent dans le temps) : sans ce snapshot, il serait impossible de
    # reconstituer Vol_T_prev lors du calcul suivant pour obtenir Growth_T.
    metric_sales = fields.Integer(
        string="Ventes de la période (V_T)",
        default=0,
    )
    metric_likes = fields.Integer(
        string="Likes de la période (L_T)",
        default=0,
    )
    metric_shares = fields.Integer(
        string="Partages de la période (P_T)",
        default=0,
    )
    metric_ads_count = fields.Integer(
        string="Publicités actives de la période (A_T)",
        default=0,
    )
    #unicité trend.score par produit + date du jour
    score_date = fields.Date(
        string="Date du score",
        required=True,
        default=fields.Date.context_today,
        index=True,
    )
    _product_score_date_uniq = models.Constraint(
        'unique(product_id, score_date)',
        "Un seul score est autorisé par produit et par jour.",
    )