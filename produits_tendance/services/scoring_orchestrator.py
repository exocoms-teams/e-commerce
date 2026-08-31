from odoo import api, fields, models


class TrendScoringOrchestrator(models.AbstractModel):
    """Orchestre le calcul et la persistance des scores quotidiens."""

    _name = 'trend.scoring.orchestrator'
    _description = 'Orchestrateur du scoring quotidien des produits'

    @api.model
    def score_product(self, product, computed_at=None):
        """Calcule et persiste un nouveau score pour un produit.
        Cette méthode ne modifie jamais un trend.score existant.
        Chaque appel crée une nouvelle ligne d'historique.
        """
        product.ensure_one()
        latest_score = product.score_ids.sorted(
            'computed_at',
            reverse=True,
        )[:1]
        if latest_score:
            previous_metrics = {
                'ventes': latest_score.metric_sales,
                'likes': latest_score.metric_likes,
                'partages': latest_score.metric_shares,
                'ads': latest_score.metric_ads_count,
            }
        else:
            previous_metrics = None

        current_metrics = product.build_current_metrics()
        score_value = product.compute_trend_score(
            previous_metrics=previous_metrics,
            current_metrics=current_metrics,
        )
        
        score_values = {
            'product_id': product.id,
            'computed_score': score_value,
            'computed_at': computed_at or fields.Datetime.now(),
            'metric_sales': current_metrics['ventes'],
            'metric_likes': current_metrics['likes'],
            'metric_shares': current_metrics['partages'],
            'metric_ads_count': current_metrics['ads'],
        }
        return self.env['trend.score'].create(score_values)

    @api.model
    def run_daily_scoring(self,computed_at=None):
        """Calcule un nouveau score pour chaque produit,
        puis les classer."""
        products = self.env['trend.product'].search([])
        created_scores = self.env['trend.score']
        scoring_datetime = computed_at or fields.Datetime.now()

        for product in products:
            score = self.score_product(product,computed_at=scoring_datetime)
            created_scores |= score

        self._recompute_daily_ranks(scoring_datetime)
        return created_scores

    @api.model
    def _recompute_daily_ranks(self, computed_at):
        """Classe les scores d'une journée en une seule écriture SQL.

        Un appel ORM ``write()`` attribue la même valeur à tous les records;
        il ne permet donc pas d'écrire les rangs 1, 2, 3… en une seule fois.
        Cette requête paramétrée applique les valeurs distinctes en un unique
        ``UPDATE`` et conserve les performances du cron lorsque le catalogue
        contient beaucoup de produits.
        """
        score_date = fields.Datetime.to_datetime(computed_at).date()
        scores = self.env['trend.score'].search(
            [('score_date', '=', score_date)],
            order='computed_score desc, id asc',
        )
        if not scores:
            return scores

        ranks = [(score.id, rank) for rank, score in enumerate(scores, start=1)]
        placeholders = ', '.join(['(%s, %s)'] * len(ranks))
        parameters = [value for rank in ranks for value in rank]
        self.env.cr.execute(
            """
                UPDATE trend_score AS score
                   SET rank = ranked_score.rank
                  FROM (VALUES %s) AS ranked_score(id, rank)
                 WHERE score.id = ranked_score.id
            """ % placeholders,
            parameters,
        )
        scores.invalidate_recordset(['rank'])
        return scores