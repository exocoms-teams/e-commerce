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

        score_value = product.compute_trend_score(
            previous_metrics=previous_metrics,
        )

        current_metrics = product.build_current_metrics()

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
    def run_daily_scoring(self):
        """Calcule un nouveau score pour chaque produit.

        Le classement n'est pas encore traité ici.
        Il fera partie de la tâche 2.
        """
        products = self.env['trend.product'].search([])
        created_scores = self.env['trend.score']

        for product in products:
            score = self.score_product(product)
            created_scores |= score

        return created_scores