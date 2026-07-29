# controllers/dashboard_api.py
import json
from collections import defaultdict

from werkzeug.exceptions import NotFound


class TrendDashboardAPI:
    """Façade regroupant les lectures ORM utilisées par les pages publiques
    du dashboard "Produits Tendance" (liste + fiche détaillée).

    Objectif : isoler les contrôleurs HTTP de la logique ORM afin que les
    futures pages du dashboard puissent réutiliser les mêmes méthodes sans
    dupliquer les requêtes ni la logique d'agrégation.

    NB : les pages publiques sont accessibles à des visiteurs non connectés
    (auth='public'), donc toutes les lectures passent en sudo() ici, comme
    déjà fait dans TrendIngestController.
    """

    def __init__(self, env):
        self.env = env

    # ------------------------------------------------------------------
    # Fiche produit détaillée
    # ------------------------------------------------------------------
    def get_product_detail(self, product_id):
        """Retourne les données nécessaires à la fiche produit détaillée.

        :param int product_id: id du trend.product demandé
        :raises werkzeug.exceptions.NotFound: si l'id n'existe pas en base
            (laisser remonter l'exception : Odoo intercepte NotFound sur
            les routes ``website=True`` et affiche la page 404 du thème,
            sans stacktrace).
        :rtype: dict
        """
        product = self.env(su=True)['trend.product'].browse(product_id).exists()
        if not product:
            raise NotFound()

        # Le dernier score calculé porte le score de tendance affiché
        # (o_winners_score_badge) ET, séparément, le search_volume Google
        # Trends (purement informatif, cf. trend.score.search_volume).
        latest_score = product.score_ids.sorted('computed_at', reverse=True)[:1]

        ads = product.ad_ids
        score_history = self.get_score_history(product)

        return {
            'product': product,
            'latest_score': latest_score,
            'trend_score': latest_score.computed_score if latest_score else product.current_score,
            'search_volume': latest_score.search_volume if latest_score else None,
            'ads': ads,
            'total_likes': sum(ads.mapped('likes_count')),
            'total_shares': sum(ads.mapped('shares_count')),
            'score_history': score_history,
            'score_history_json': json.dumps(score_history),
        }

    def get_score_history(self, product):
        """Historique agrégé du computed_score pour la courbe de tendance
        (WIN-52) : un point par date (moyenne si plusieurs trend.score le
        même jour), trié chronologiquement.

        Agrégation faite ici, côté ORM/Python, pour n'envoyer qu'un point
        par jour au JS plutôt qu'un par trend.score — cf. contrainte du
        ticket "alléger le rendu DOM".

        :param trend.product product: le produit (déjà chargé)
        :rtype: list[dict] — [{'date': 'YYYY-MM-DD', 'score': float}, ...]
        """
        by_date = defaultdict(list)
        for score in product.score_ids:
            if not score.computed_at:
                continue
            date_key = score.computed_at.date().isoformat()
            by_date[date_key].append(score.computed_score)

        return [
            {'date': date_key, 'score': sum(scores) / len(scores)}
            for date_key, scores in sorted(by_date.items())
        ]