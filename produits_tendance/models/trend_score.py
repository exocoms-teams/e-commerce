from odoo import api, fields, models


class TrendScore(models.Model):
    _name = "trend.score"
    _description = "Score de tendance d'un produit"
    _order = "rank asc"

    _unique_product_score_date = models.Constraint(
        "UNIQUE(product_id, score_date)",
        "Un seul score de tendance est autorisé par produit et par jour.",
    )

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
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    score_date = fields.Date(
        string="Date du score",
        compute="_compute_score_date",
        store=True,
        precompute=True,
        index=True,
    )
    rank = fields.Integer(
        string="Classement",
        default=0,
    )

        # Google Trends returns relative search interest (0–100),
    # not an absolute search count. Kept under the existing field name.
    # Informational only: excluded from scoring_engine.py and ranking.
    # Default 0 also represents unavailable data; collection failures
    # and missing readings are logged by the collector.
    search_volume = fields.Integer(
        string="Intérêt Google Trends",
        default=0,
        help="Indice relatif de recherche Google Trends (0–100). "
             "La valeur du jour peut être partielle. "
             "0 peut également indiquer des données indisponibles. "
             "N'influence ni le score de tendance ni le classement.",
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

    @api.depends("computed_at")
    def _compute_score_date(self):
        """Stocke le jour UTC de calcul pour l'unicité quotidienne.

        ``computed_at`` est enregistré en UTC par Odoo et c'est déjà ce jour
        qui est utilisé par l'historique du tableau de bord. Le stocker dans
        un champ ``Date`` permet de faire appliquer l'unicité directement par
        PostgreSQL, y compris lorsque deux workers créent un score en même
        temps.
        """
        for score in self:
            computed_at = (
                fields.Datetime.to_datetime(score.computed_at)
                if score.computed_at else False
            )
            score.score_date = computed_at.date() if computed_at else False
