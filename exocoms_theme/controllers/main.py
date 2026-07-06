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

    @http.route()
    def index(self, **kw):
        if not _is_our_site(request):
            # Pas notre site : on laisse Odoo faire son travail normal
            # (chargement de la page d'accueil propre au site demandé).
            return super().index(**kw)

        frontend_lang = request.httprequest.cookies.get('frontend_lang')
        if not frontend_lang:
            response = request.render('exocoms_theme.home', {})
            response.set_cookie(
                'frontend_lang',
                'fr_FR',
                max_age=365 * 24 * 3600,
                path='/'
            )
            return response
        return request.render('exocoms_theme.home', {})

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