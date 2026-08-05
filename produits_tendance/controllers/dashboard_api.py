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
    # ------------------------------------------------------------------
    # Liste / filtres dynamiques (WIN-45 / WIN-50)
    # ------------------------------------------------------------------
    def get_product_list(self, category_id=None, country=None):
        """Retourne les produits triés par score de tendance décroissant,
        optionnellement filtrés par catégorie et/ou pays.

        :param int|None category_id: id d'un trend.category, ou None/0 pour
            ne pas filtrer sur la catégorie.
        :param str|None country: code pays (ex. 'MA'), ou None/'' pour ne
            pas filtrer sur le pays.
        :rtype: list[dict]
        """
        env = self.env(su=True)
        domain = []
        if category_id:
            domain.append(('category_id', '=', int(category_id)))
        if country:
            domain.append(('country', '=', country))

        products = env['trend.product'].search(domain, order='current_score desc')

        return [{
            'id': product.id,
            'name': product.name,
            'category': product.category_id.name or '',
            'country': product.country or '',
            'score': round(product.current_score, 1),
            'sales_count': product.sales_count,
        } for product in products]

    def get_filter_options(self):
        """Retourne les valeurs disponibles pour peupler les selects du
        panneau de filtres (.o_winners_filter_panel) : catégories connues
        et pays distincts déjà présents sur des trend.product.
        """
        env = self.env(su=True)
        categories = env['trend.category'].search([], order='name asc')

        # _read_group (API 19.0) remplace read_group (déprécié) : sans
        # aggregates, il renvoie directement une liste de tuples à 1 élément
        # (une entrée par valeur distincte de country).
        country_groups = env['trend.product']._read_group(
            [('country', '!=', False)], groupby=['country']
        )
        countries = sorted(country for (country,) in country_groups if country)

        return {
            'categories': [{'id': c.id, 'name': c.name} for c in categories],
            'countries': countries,
        }