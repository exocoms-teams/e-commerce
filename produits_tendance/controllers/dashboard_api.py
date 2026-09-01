# controllers/dashboard_api.py
import json
from collections import defaultdict

from werkzeug.exceptions import NotFound
from ..models.trend_ad import latest_ads_by_ref


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
        utilitaire est prêt à être branché
        (`if not TrendDashboardAPI.is_pro_user(request.env): ...`)
        par un futur contrôleur sans modifier de comportement déjà livré.
        """
        return env.user.has_group('produits_tendance.group_trend_pro')

    # ------------------------------------------------------------------
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

        # WIN-XX (mode historique trend.ad) : une publicité peut désormais
        # avoir plusieurs lignes horodatées (une par collecte). On ne garde
        # que la dernière par ad_ref pour l'affichage et les totaux, sinon
        # les compteurs likes/partages gonflent à chaque nouvelle collecte.
        ads = latest_ads_by_ref(product.ad_ids)
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

    # ------------------------------------------------------------------
    # Liste / filtres dynamiques (WIN-45 / WIN-49 / WIN-50 / WIN-77)
    # ------------------------------------------------------------------
    def get_product_list(
        self,
        category_id=None,
        country=None,
        price_max=None,
        source=None,
        search=None,
        limit=None,
        offset=0,
    ):
        """Retourne les produits triés par score de tendance décroissant,
        optionnellement filtrés par catégorie, pays, prix max, source et
        nom (recherche texte).

        :param int|None category_id: id d'un trend.category, ou None/0 pour
            ne pas filtrer sur la catégorie.
        :param str|None country: code pays (ex. 'MA'), ou None/'' pour ne
            pas filtrer sur le pays.
        :param float|None price_max: prix maximum, ou None/'' pour ne pas
            filtrer.
        :param str|None source: valeur de la Selection trend.product.source
            ('scraping', 'crowdsourcing', 'api'), ou None/'' pour ne pas
            filtrer.
        :param str|None search: texte de recherche sur le nom du produit
            (WIN-49), comparaison "ilike" insensible à la casse.
        :param int|None limit: passé tel quel à env['trend.product'].search().
            ATTENTION Odoo interprète limit=0 comme « aucune limite » (test
            de véracité Python côté ORM), donc on court-circuite ce cas
            explicitement ci-dessous plutôt que de laisser search()
            l'interpréter à sa manière — sinon un compte Gratuit ayant
            épuisé son quota (WIN-77, get_pagination_limit renvoie
            limit=0) repasserait en lecture illimitée.
        :param int offset: décalage pour la pagination (WIN-45/77, bouton
            « Charger plus »). Défaut 0 : un appel sans pagination
            (rendu initial, reset des filtres) doit toujours repartir
            du début — ne jamais remettre une valeur non nulle ici.
        :rtype: list[dict]
        """
        if limit == 0:
            return []

        env = self.env(su=True)
        domain = []

        if category_id:
            domain.append(('category_id', '=', int(category_id)))
        if country:
            domain.append(('country', '=', country))
        if price_max not in (None, ''):
            try:
                domain.append(('price', '<=', float(price_max)))
            except (TypeError, ValueError):
                pass  # paramètre invalide ignoré, comportement identique à l'absence du filtre
        if source:
            domain.append(('source', '=', source))
        if search:
            domain.append(('name', 'ilike', search.strip()))

        products = env['trend.product'].search(
            domain, order='current_score desc', limit=limit, offset=offset
        )

        return [
            {
                'id': product.id,
                'name': product.name,
                'category': product.category_id.name or '',
                'country': product.country or '',
                'score': round(product.current_score, 1),
                'sales_count': product.sales_count,
            }
            for product in products
        ]

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
        sources = env['trend.product']._fields['source'].selection
        return {
            'categories': [{'id': c.id, 'name': c.name} for c in categories],
            'countries': countries,
            'sources': [{'value': v, 'label': label} for v, label in sources],
        }

    def get_dashboard_stats(self):
        """Statistiques globales affichées en tuiles au-dessus du
        classement (nombre de produits suivis, score moyen). Basé sur les
        données déjà disponibles (pas de nouveau champ) : nombre de
        trend.product et moyenne de current_score.

        :rtype: dict {'total_products': int, 'avg_score': float}
        """
        env = self.env(su=True)
        products = env['trend.product'].search([])
        total_products = len(products)
        avg_score = (
            sum(products.mapped('current_score')) / total_products
            if total_products else 0.0
        )
        return {
            'total_products': total_products,
            'avg_score': round(avg_score, 1),
        }

    @staticmethod
    def is_freemium_user(env):
        """Vrai si l'utilisateur est un compte Gratuit (ni Standard ni Pro)."""
        return env.user.has_group('produits_tendance.group_trend_free') \
            and not env.user.has_group('produits_tendance.group_trend_standard')

    @staticmethod
    def get_pagination_limit(env, requested_offset=0, requested_limit=None):
        """Calcule (limit, offset) réels en clampant strictement au plafond
        Freemium (5 produits), quels que soient les paramètres reçus.

        :param int requested_offset: offset demandé côté client (query
            string /dashboard?offset=... ou /api/dashboard/filter?offset=...)
            — jamais fait confiance tel quel pour un compte Gratuit.
        :param int|None requested_limit: taille de page demandée. Aucun
            contrôleur de ce module n'expose ce paramètre côté client pour
            l'instant (seul `offset` est piloté par le bouton « Charger
            plus »).
        :rtype: tuple[int, int] — (limit, offset) à passer tels quels à
            TrendDashboardAPI.get_product_list().
        """
        requested_offset = max(0, requested_offset)
        is_free = TrendDashboardAPI.is_freemium_user(env)

        if is_free:
            # Le compte Gratuit ne peut jamais dépasser 5 résultats au
            # total, ni via offset ni via limit manipulés dans l'URL.
            if requested_offset >= 5:
                return 0, 0  # aucun résultat, plus de "page" possible
            return min(requested_limit or 5, 5 - requested_offset), requested_offset

        # Standard/Pro : pagination normale, taille de page par défaut 20.
        return requested_limit or 20, requested_offset