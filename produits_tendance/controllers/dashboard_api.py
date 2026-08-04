# controllers/dashboard_api.py
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
    # Garde-fou abonnement (WIN-66)
    # ------------------------------------------------------------------
    @staticmethod
    def is_pro_user(env):
        """Garde-fou réutilisable pour toute future fonctionnalité réservée
        aux abonnés Pro (ex: données prédictives du dashboard, WIN-66).

        N'est appelé par aucune page existante pour l'instant : le dashboard
        WIN-48 reste géré par sa propre logique de limite Freemium. Ce
        utilitaire est prêt à être branché (`if not TrendDashboardAPI.is_pro_user(request.env): ...`)
        par un futur contrôleur sans modifier de comportement déjà livré.
        """
        return env.user.has_group('produits_tendance.group_trend_pro')
    # Classement / dashboard (liste)
    # ------------------------------------------------------------------
    def get_dashboard_products(self, limit=None):
        """Retourne les trend.product triés par score de tendance décroissant.

        :param int|None limit: si fourni, plafonne le nombre de résultats
            (utilisé pour la restriction Freemium, WIN-48) — appliqué ici,
            côté ORM, jamais seulement côté template/JS.

        Utilise les droits de l'utilisateur connecté (pas de sudo) : le
        groupe group_trend_free implique group_trend_user (lecture seule),
        donc cette requête fonctionne aussi bien pour un compte Freemium.
        """
        return self.env['trend.product'].search(
            [], order='current_score desc', limit=limit
        )

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

        return {
            'product': product,
            'latest_score': latest_score,
            'trend_score': latest_score.computed_score if latest_score else product.current_score,
            'search_volume': latest_score.search_volume if latest_score else None,
            'ads': ads,
            'total_likes': sum(ads.mapped('likes_count')),
            'total_shares': sum(ads.mapped('shares_count')),
        }