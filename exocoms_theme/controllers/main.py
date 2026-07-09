# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale

WEBSITE_NAME = 'Exocoms'  # doit correspondre à WEBSITE_NAME dans __init__.py

RECENT_HISTORY_KEY = 'website_sale_history'
RECENT_HISTORY_MAX = 20


def _is_our_site(request):
    """Vrai UNIQUEMENT si le site actuellement résolu (request.website,
    déterminé par domaine/URL) est bien le site Exocoms. Sur une base
    partagée à plusieurs sites, ce test est OBLIGATOIRE avant de rendre
    le moindre contenu personnalisé Exocoms."""
    website = request.website
    return bool(website) and website.name == WEBSITE_NAME


class ExocomsWebsite(Website):
    """CORRECTIF MAJEUR (cause du bug 'le site Exocoms s'affiche sur
    tous les autres sites') :

    La version originale de ce contrôleur créait une TOUTE NOUVELLE
    route Python sur '/', '/nos-services', '/mentions-legales' et
    '/boutique' via une classe `http.Controller` indépendante.

    En Odoo, les routes HTTP sont enregistrées au niveau de TOUTE LA
    BASE DE DONNÉES, jamais par site : elles ignorent complètement
    quel site (website_id) a été résolu pour la requête. Résultat :
    dès que ce module était installé sur la base partagée à 17 sites,
    CETTE route interceptait TOUTES les requêtes vers '/', quel que
    soit le site réellement visité (Agence de voyage, Matelas,
    Crypto...), et rendait systématiquement le template Exocoms.

    Le correctif consiste à ne JAMAIS redéclarer ces routes depuis
    zéro, mais à HÉRITER du contrôleur natif `website.Website` et à
    ne surcharger le rendu QUE si le site résolu est bien Exocoms.
    Pour tous les autres sites, on délègue via `super()` au
    comportement standard d'Odoo, qui va lui correctement chercher la
    page/vue spécifique à CE site (website_id du bon site).
    """

    def _get_home_avis_context(self):
        """Avis publiés du site, pour le carousel témoignages de la home
        (même source que la page /avis). Les stats portent sur TOUS les
        avis publiés, mais seuls les 6 plus récents sont affichés en
        cartes. Scopé website_id comme partout ailleurs."""
        Avis = request.env['exocoms.avis'].sudo()
        website = request.website
        all_avis = Avis.search([
            ('website_id', '=', website.id),
            ('state', '=', 'published'),
        ], order='date desc, id desc')

        home_avis_stats = False
        if all_avis:
            total = len(all_avis)
            avg = sum(a.rating for a in all_avis) / total
            home_avis_stats = {'avg': round(avg, 1), 'total': total}

        return {
            'home_avis_list': all_avis[:6],
            'home_avis_stats': home_avis_stats,
        }

    @http.route()
    def index(self, **kw):
        if not _is_our_site(request):
            # Pas notre site : on laisse Odoo faire son travail normal
            # (chargement de la page d'accueil propre au site demandé).
            return super().index(**kw)

        values = self._get_home_avis_context()

        frontend_lang = request.httprequest.cookies.get('frontend_lang')
        if not frontend_lang:
            response = request.render('exocoms_theme.home', values)
            response.set_cookie(
                'frontend_lang',
                'fr_FR',
                max_age=365 * 24 * 3600,
                path='/'
            )
            return response
        return request.render('exocoms_theme.home', values)

    # --- Routes propres au thème Exocoms (chemins peu susceptibles
    #     d'exister sur les autres sites, mais on garde la même
    #     sécurité par prudence : base partagée à 17 sites). ---

    @http.route('/nos-services', type='http', auth='public', website=True, sitemap=True)
    def services_page(self, **kw):
        if not _is_our_site(request):
            raise http.NotFound()
        return request.render('exocoms_theme.services_page', {})

    @http.route('/mentions-legales', type='http', auth='public', website=True, sitemap=True)
    def mentions_legales(self, **kw):
        if not _is_our_site(request):
            raise http.NotFound()
        return request.render('exocoms_theme.mentions_legales', {})

    @http.route('/boutique', type='http', auth='public', website=True, sitemap=True)
    def boutique(self, **kw):
        if not _is_our_site(request):
            raise http.NotFound()
        return request.redirect('/shop')

    @http.route('/avis', type='http', auth='public', website=True, sitemap=True)
    def avis_page(self, **kw):
        if not _is_our_site(request):
            raise http.NotFound()

        Avis = request.env['exocoms.avis'].sudo()
        website = request.website
        avis_list = Avis.search([
            ('website_id', '=', website.id),
            ('state', '=', 'published'),
        ], order='date desc, id desc')

        stats = False
        if avis_list:
            total = len(avis_list)
            avg = sum(a.rating for a in avis_list) / total
            dist = {}
            for star in (5, 4, 3, 2, 1):
                count = len(avis_list.filtered(lambda a: a.rating == star))
                dist[star] = round(count * 100 / total)
            stats = {'avg': round(avg, 1), 'total': total, 'dist': dist}

        return request.render('exocoms_theme.avis_page', {
            'avis_list': avis_list,
            'stats': stats,
            'sent': kw.get('sent') == '1',
        })

    @http.route('/avis/submit', type='http', auth='public', website=True,
                methods=['POST'], csrf=True, sitemap=False)
    def avis_submit(self, **post):
        if not _is_our_site(request):
            raise http.NotFound()

        name = (post.get('name') or '').strip()
        comment = (post.get('comment') or '').strip()
        product = (post.get('product') or '').strip()
        try:
            rating = int(post.get('rating') or 0)
        except ValueError:
            rating = 0
        rating = min(5, max(1, rating)) if rating else 5

        if name and comment:
            avis = request.env['exocoms.avis'].sudo().create({
                'name': name,
                'comment': comment,
                'product': product,
                'rating': rating,
                'website_id': request.website.id,
                'state': 'pending',
            })
            # Traduit tout de suite vers l'autre langue (fr<->en) à
            # partir de la langue de la page où le formulaire a été
            # rempli (request.env.lang). Best-effort : si le service de
            # traduction est indisponible, l'avis est quand même créé,
            # juste affiché uniquement dans sa langue d'origine pour le
            # moment (rattrapable via le bouton "Traduire" du backend).
            avis.action_translate_missing()

        return request.redirect('/avis?sent=1')


class ExocomsWebsiteSale(WebsiteSale):
    """CORRECTIF : le widget "Vus récemment" (dashbord.xml, section
    'Vus récemment') lit `request.session['website_sale_history']`,
    mais RIEN dans tout le code (ni ce module, ni Odoo lui-même) ne
    l'a jamais écrite — confirmé par recherche dans le code source
    natif d'Odoo (grep sur website_sale sans résultat). Ce widget
    était donc cassé depuis sa création, quel que soit le nombre de
    fiches produit consultées.

    On hérite ici de la méthode native `product()` (page fiche
    produit), sans créer de route concurrente (même principe que
    ExocomsWebsite ci-dessus), pour y ajouter l'enregistrement de
    chaque produit visité dans la session — le plus récent en
    premier, dédoublonné, plafonné à 20 entrées.
    """

    @http.route()
    def product(self, product, category=None, pricelist=None, **kwargs):
        response = super().product(product, category=category, pricelist=pricelist, **kwargs)

        history = request.session.get(RECENT_HISTORY_KEY, [])
        history = [pid for pid in history if pid != product.id]
        history.insert(0, product.id)
        request.session[RECENT_HISTORY_KEY] = history[:RECENT_HISTORY_MAX]
        return response