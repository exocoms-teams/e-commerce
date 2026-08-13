# -*- coding: utf-8 -*-
import datetime
import json

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class CapsuleHouseWebsite(Website):
    """Contrôleurs frontend du site Capsule House.

    Pages livrées pour l'instant : Accueil et Boutique (/shop, gérée
    nativement par website_sale — pas de route custom nécessaire ici). Les
    autres pages (Services, Contact, À propos) seront ajoutées au fur et à
    mesure.

    RÈGLE DE SÉCURITÉ MULTI-SITE CRITIQUE, apprise à la dure : une route
    HTTP Python enregistrée sur le chemin '/' s'applique à TOUTE la base
    mutualisée (~17 sites), pas seulement à Capsule House — contrairement
    aux vues QWeb et aux ir.asset, qui eux sont scopables via website_id.
    Une première version de ce contrôleur redéclarait '/' comme une route
    TOUTE NEUVE (pas une surcharge héritée) et cassait donc la page
    d'accueil des 16 autres sites (et tentait d'appeler
    `super().homepage()`, qui n'existe même pas sur le contrôleur
    `Website` natif — `AttributeError` en prod).

    HISTORIQUE (jusqu'à la 19.0.1.0.56) : pour éviter de retoucher '/',
    l'accueil était servi sur une route dédiée (`/capsule-house/home`),
    atteinte via `website.homepage_url` + le redirect natif Odoo de '/'
    vers cette URL. Ça évitait tout risque de casser les autres sites,
    mais avait un effet de bord découvert en 19.0.1.0.56 : ce redirect
    (un vrai aller-retour HTTP, confirmé par capture DevTools client)
    empêchait le Website Builder de reconnaître correctement la section
    hero comme un bloc sélectionnable (panneau Style vide), alors que le
    même hero sur /avis — servie en un seul rendu, sans redirect —
    fonctionnait normalement. Comparaison directe des deux thèmes
    (capsule_house_theme vs exocoms_theme, analyse complète du
    19.0.1.0.57) : exocoms_theme sert '/' en HÉRITANT du contrôleur
    natif `Website` et en surchargeant `index()` via un `@http.route()`
    SANS argument (donc réutilisant la route native, pas une nouvelle),
    avec une garde stricte `_is_our_site()` et un `super().index(**kw)`
    pour tous les autres sites — pattern déjà éprouvé en production sur
    17 sites sans jamais avoir cassé personne. C'est ce même pattern
    (hérité, gardé, avec fallback super()) qui est repris ci-dessous
    pour `index()`, à la différence de la première tentative fautive :
    ici on N'ENREGISTRE PAS de nouvelle route, on ne fait QUE surcharger
    la méthode héritée, et le fallback vers les 16 autres sites est
    systématique.
    """

    def _is_our_website(self, website):
        """True seulement si `website` est CELUI créé par ce module.

        Même logique que `_get_website()` dans __init__.py : comparaison
        stricte à l'id mémorisé dans ir.config_parameter
        (`capsule_house_theme.website_id`), jamais par nom ni par
        déduction implicite.
        """
        icp = request.env['ir.config_parameter'].sudo()
        our_id = icp.get_param('capsule_house_theme.website_id')
        try:
            return bool(our_id) and int(our_id) == website.id
        except (TypeError, ValueError):
            return False

    def _serialize_products(self, products):
        """Aplati les product.template en dicts simples pour les templates.

        Utilise `getattr(product, field, default)` pour les champs qui
        n'existent pas forcément selon les modules installés
        (`compare_list_price`, `rating_avg`, `rating_count` dépendent de
        modules non listés dans `depends` de ce thème) : on n'affiche
        jamais un vieux/faux prix barré ou une fausse note, on masque
        simplement l'élément si la donnée réelle n'existe pas.
        """
        now = datetime.datetime.now()
        items = []
        for product in products:
            compare_price = getattr(product, 'compare_list_price', 0) or 0
            has_discount = bool(compare_price and compare_price > product.list_price)
            rating_count = int(getattr(product, 'rating_count', 0) or 0)
            rating_avg = getattr(product, 'rating_avg', 0) or 0
            is_new = bool(
                product.create_date
                and (now - product.create_date).days <= 30
            )
            category = product.public_categ_ids[:1]
            items.append({
                'product': product,
                'name': product.name,
                'url': product.website_url,
                'id': product.id,
                'price': product.list_price,
                'currency': product.currency_id,
                'compare_price': compare_price if has_discount else 0,
                'has_discount': has_discount,
                'rating_avg': rating_avg,
                'rating_count': rating_count,
                'is_new': is_new,
                'category_name': category.name if category else '',
            })
        return items

    @http.route()
    def index(self, **kw):
        """Surcharge héritée de la route native '/' (voir docstring de
        classe pour l'historique complet). Aucun nouveau chemin
        enregistré : `@http.route()` sans argument réutilise la route
        exacte du parent `Website.index()`. Le guard `_is_our_website`
        + le fallback `super().index(**kw)` garantissent que les 16
        autres sites de la base mutualisée continuent d'être servis
        exactement comme avant, sans aucun changement de comportement.
        """
        website = request.website
        if not self._is_our_website(website):
            return super().index(**kw)

        Product = request.env['product.template'].sudo()
        domain = [
            ('website_id', '=', website.id),
            ('is_published', '=', True),
        ]
        featured_products = Product.search(domain, limit=8, order='website_sequence asc')

        # Métriques de la maquette de référence : "4 modèles disponibles"
        # est un vrai comptage (sûr à afficher). "2 340 pods installés" et
        # la note "4.9 · X avis" étaient des chiffres fixes de la maquette,
        # non vérifiés par ce module — on ne les fabrique pas.
        #
        # Depuis l'ajout du système d'avis réels (capsule.house.avis,
        # voir models/avis.py, réplique du mécanisme observé sur
        # exocoms_theme) : la note/le nombre d'avis du badge hero sont
        # calculés à partir des VRAIS avis publiés sur notre site s'il y
        # en a. Si aucun avis n'est encore publié, on retombe sur
        # l'ancien réglage manuel (ir.config_parameter) — utile si le
        # client a une note vérifiée ailleurs (Google, Trustpilot...)
        # mais pas encore de vrais avis sur le site lui-même.
        rating_value, rating_count = self._get_avis_stats(website)
        ICP = request.env['ir.config_parameter'].sudo()
        if rating_value is None:
            rating_value = ICP.get_param('capsule_house_theme.rating_value')
            rating_count = ICP.get_param('capsule_house_theme.rating_count')
        units_installed_count = ICP.get_param('capsule_house_theme.units_installed_count')

        return request.render('capsule_house_theme.page_home', {
            'featured_products': self._serialize_products(featured_products),
            'published_products_count': Product.search_count(domain),
            'rating_value': rating_value,
            'rating_count': rating_count,
            'units_installed_count': units_installed_count,
        })

    @http.route('/capsule-house/hero-data.json', type='http', auth='public',
                website=True, sitemap=False)
    def hero_data(self, **kw):
        """Valeurs dynamiques du hero (note, comptages, produits vedettes),
        en JSON — récupérées côté client par static/src/js/main.js
        (initHeroDynamicContent) après le chargement de la page.

        CAUSE DE CE CHANGEMENT (v19.0.1.0.60, voir README "Cause réelle
        #3") : ces valeurs étaient auparavant rendues via t-esc
        directement dans hero.xml. Analyse comparative directe (bloc
        natif Odoo vs notre hero, dans la même session d'édition) a
        montré qu'Odoo refuse de marquer comme "bloc" sélectionnable
        (data-oe-model, panneau Style) tout conteneur dont le sous-arbre
        contient une expression dynamique (t-esc/t-foreach) — confirmé
        en comparant avec le hero d'exocoms_theme (0% de contenu
        dynamique dans son arch) et la doc officielle Odoo 19 sur les
        "Dynamic Content templates", qui montre que les snippets
        dynamiques NATIFS d'Odoo (ex: Articles de blog) gardent leur
        <section> 100% statique et injectent le contenu réel via JS
        après coup — jamais via t-esc dans l'arch. Reproduit ici à
        l'identique : hero.xml ne contient plus aucune expression
        dynamique, cette route fournit les vraies valeurs (aucune
        donnée fabriquée, mêmes calculs qu'avant) pour affichage
        post-chargement.
        """
        website = request.website

        Product = request.env['product.template'].sudo()
        domain = [
            ('website_id', '=', website.id),
            ('is_published', '=', True),
        ]
        featured_products = Product.search(domain, limit=8, order='website_sequence asc')
        published_products_count = Product.search_count(domain)

        rating_value, rating_count = self._get_avis_stats(website)
        ICP = request.env['ir.config_parameter'].sudo()
        if rating_value is None:
            rating_value = ICP.get_param('capsule_house_theme.rating_value')
            rating_count = ICP.get_param('capsule_house_theme.rating_count')
        units_installed_count = ICP.get_param('capsule_house_theme.units_installed_count')

        # v19.0.1.0.61 : le badge de note reste maintenant TOUJOURS affiché
        # (retour client : "affiche quand même en mettant 0 ... aucun
        # élément pour le moment"), plutôt que masqué tant qu'aucun avis
        # n'existe. Toujours un vrai chiffre (0 si aucun avis publié),
        # jamais de note fabriquée.
        if not rating_value:
            rating_value = 0
            rating_count = 0
        if request.env.lang == 'fr_FR':
            rating_message = '%s avis' % rating_count
        else:
            rating_message = '%s reviews' % rating_count

        hero_products = self._serialize_products(featured_products)[:2]
        featured_json = [{
            'id': item['id'],
            'url': item['url'],
            'name': item['name'],
            'image_url': '/web/image/product.template/%d/image_128' % item['id'],
            'price_formatted': self._format_price_display(item['currency'], item['price']),
            'is_new': item['is_new'],
            'has_discount': item['has_discount'],
        } for item in hero_products]

        cart_product_id = hero_products[1]['id'] if len(hero_products) > 1 else None

        try:
            units_installed_count = int(units_installed_count) if units_installed_count else None
        except (TypeError, ValueError):
            units_installed_count = None

        data = {
            'rating_value': rating_value,
            'rating_message': rating_message,
            'published_products_count': published_products_count,
            'units_installed_count': units_installed_count,
            'featured_products': featured_json,
            'cart_product_id': cart_product_id,
            'csrf_token': request.csrf_token(),
        }
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
        )

    def _format_price_display(self, currency, amount):
        """Formatage simple prix+devise pour les cartes flottantes du hero
        (affichage uniquement — jamais utilisé pour une transaction
        réelle, le vrai prix/devise reste géré nativement par
        website_sale à l'achat).
        """
        decimals = currency.decimal_places or 2
        amount_str = '{:,.{}f}'.format(amount, decimals)
        if request.env.lang == 'fr_FR':
            amount_str = amount_str.replace(',', ' ').replace('.', ',')
        symbol = currency.symbol or currency.name
        if currency.position == 'before':
            return '%s%s' % (symbol, amount_str)
        return '%s %s' % (amount_str, symbol)

    @http.route('/capsule-house/home', type='http', auth='public',
                website=True, sitemap=False)
    def homepage_legacy_redirect(self, **kw):
        """Ancienne route dédiée de l'accueil (jusqu'à la 19.0.1.0.56),
        remplacée en 19.0.1.0.57 par une surcharge directe de '/' (voir
        `index()` ci-dessus). Conservée uniquement en redirect permanent
        pour ne pas casser d'éventuels favoris/liens déjà partagés vers
        cette URL — jamais réutilisée comme page réelle.
        """
        return request.redirect('/', code=301)

    def _get_avis_stats(self, website):
        """Note moyenne + nombre d'avis PUBLIÉS de notre site, ou
        (None, None) si aucun avis publié. Jamais de valeur fabriquée :
        calcul direct sur les enregistrements réels capsule.house.avis.
        """
        Avis = request.env['capsule.house.avis'].sudo()
        published = Avis.search([
            ('website_id', '=', website.id),
            ('state', '=', 'published'),
        ])
        if not published:
            return None, None
        avg = sum(a.rating for a in published) / len(published)
        return round(avg, 1), len(published)

    @http.route('/boutique', type='http', auth='public', website=True,
                sitemap=True)
    def boutique(self, **kw):
        """Alias FR de /shop — même route que sur exocoms_theme.

        Route neuve (jamais utilisée ailleurs dans la base mutualisée) :
        pas de risque de collision avec un autre site, pas besoin de
        garde `_is_our_website`. Simple redirect vers la page boutique
        native (`/shop`, gérée par website_sale) : on ne duplique jamais
        la logique de la page boutique elle-même ici.
        """
        return request.redirect('/shop')

    @http.route('/nos-modeles', type='http', auth='public', website=True,
                sitemap=True)
    def nos_modeles(self, **kw):
        """Page vitrine des 4 gammes de pods (Studio/Duo/Panorama/
        Accessoires), ajoutée en 19.0.1.0.67.

        Origine de la demande : le client a montré la page "Application"
        de guosegroup.com (fabricant chinois de maisons capsules) et
        demandé un équivalent. Analyse : leurs cartes cliquables ("loger",
        "bureau", "boutique"...) montrent de VRAIES photos de leurs
        propres installations — impossible à répliquer ici sans inventer
        des usages que Capsule House n'a jamais publiés (voir échange
        précédent : aucune mention de bureau/boutique/salle d'exposition
        nulle part sur ce site). Le client a alors précisé : "c'est comme
        ma page service sur exocoms, indique juste leur domaine
        d'expertise" — et confirmé ensuite vouloir cette page-là comme
        modèle ("la page service devrait être la page application").

        Chez exocoms_theme, `/nos-services` est justement une grille de
        cartes qui ne fait QUE présenter chaque domaine en une ou deux
        phrases, sans fabriquer de contenu propre à chaque carte : ce
        sont les vraies pages catégorie de la boutique qui font foi.
        Reproduit ici à l'identique : chaque carte pointe vers le VRAI
        filtre boutique (/shop/category/<id>, déjà utilisé par le menu
        de nav, voir _setup_menus) — aucune page de contenu inventée par
        catégorie.

        Contenu textuel strictement réel :
        - Tailles (18 m² Studio, jusqu'à 40 m² Panorama) : déjà publiées
          sur /faq (aide_faq.xml).
        - Trilogie "Studio, duo ou famille" : déjà publiée sur /shop
          (shop.xml, sous-titre du hero boutique).
        - "Duo" : aucune surface publiée nulle part sur ce site — la
          carte se limite donc à ce que le nom affirme de lui-même
          (format pensé pour deux), sans inventer de m².
        """
        website = request.website
        Category = request.env['product.public.category'].sudo()
        Product = request.env['product.template'].sudo()

        # Import différé (après chargement complet du module) — évite tout
        # risque d'import circulaire avec __init__.py, même principe que
        # les migrations qui font `from odoo.addons.capsule_house_theme
        # import run_theme_maintenance` à l'intérieur de migrate().
        from odoo.addons.capsule_house_theme import SHOP_CATEGORIES

        # Descriptions strictement réelles (voir docstring ci-dessus) :
        # Studio/Panorama reprennent les surfaces déjà publiées sur /faq,
        # "Duo" ne reprend QUE ce que le nom affirme de lui-même (aucune
        # surface publiée nulle part sur ce site pour ce modèle).
        if request.env.lang == 'fr_FR':
            descriptions = {
                'Studio': "Le format compact, 18 m² — pour une personne ou un usage indépendant.",
                'Duo': "Le format intermédiaire de la gamme, pensé pour deux.",
                'Panorama': "Le plus grand de la gamme, jusqu'à 40 m² — pensé pour un usage familial.",
                'Accessoires': "Équipements et options pour compléter votre pod.",
            }
        else:
            descriptions = {
                'Studio': "The compact format, 18 sqm — for one person or standalone use.",
                'Duo': "The mid-size format in the range, designed for two.",
                'Panorama': "The largest in the range, up to 40 sqm — designed for family use.",
                'Accessoires': "Equipment and options to complete your pod.",
            }

        model_cards = []
        for name in SHOP_CATEGORIES:
            category = Category.search([
                ('name', '=', name),
                '|', ('website_id', '=', website.id), ('website_id', '=', False),
            ], limit=1)
            if not category:
                continue
            domain = [
                ('website_id', '=', website.id),
                ('is_published', '=', True),
                ('public_categ_ids', 'child_of', category.id),
            ]
            first_product = Product.search(domain, limit=1, order='website_sequence asc')
            # "Accessoires" est un nom commun (contrairement à Studio/Duo/
            # Panorama, nom de gamme = nom propre, jamais traduit ailleurs
            # dans ce module) : traduit ici en anglais, même exception que
            # EN_MENU_NAMES dans _setup_menus() (__init__.py).
            display_name = 'Accessories' if (name == 'Accessoires' and request.env.lang != 'fr_FR') else name
            model_cards.append({
                'name': display_name,
                'description': descriptions.get(name, ''),
                'url': '/shop/category/%d' % category.id,
                'count': Product.search_count(domain),
                'image_id': first_product.id if first_product else None,
            })

        return request.render('capsule_house_theme.page_nos_modeles', {
            'model_cards': model_cards,
        })

    @http.route('/avis', type='http', auth='public', website=True, sitemap=True)
    def avis_page(self, **kw):
        """Page publique listant les vrais avis publiés + formulaire de
        dépôt. Route neuve (pas de collision possible avec un autre site
        de la base mutualisée) : pas besoin de garde `_is_our_website`,
        même logique que /boutique et /newsletter/subscribe ci-dessous.
        """
        website = request.website
        Avis = request.env['capsule.house.avis'].sudo()
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

        return request.render('capsule_house_theme.avis_page', {
            'avis_list': avis_list,
            'stats': stats,
            'sent': kw.get('sent') == '1',
        })

    @http.route('/avis/submit', type='http', auth='public', website=True,
                methods=['POST'], csrf=True, sitemap=False)
    def avis_submit(self, **post):
        """Crée un avis en attente de modération ('pending') — jamais
        publié directement : un admin doit le valider dans Avis clients
        (Capsule House) avant qu'il n'apparaisse sur /avis ou dans le
        badge de note du hero. Aucune donnée fabriquée : uniquement ce
        que le visiteur soumet lui-même.
        """
        name = (post.get('name') or '').strip()
        comment = (post.get('comment') or '').strip()
        product = (post.get('product') or '').strip()
        try:
            rating = int(post.get('rating') or 0)
        except ValueError:
            rating = 0
        rating = min(5, max(1, rating)) if rating else 5

        if name and comment:
            request.env['capsule.house.avis'].sudo().create({
                'name': name,
                'comment': comment,
                'product': product,
                'rating': rating,
                'website_id': request.website.id,
                'state': 'pending',
            })

        return request.redirect('/avis?sent=1')

    @http.route('/livraison', type='http', auth='public', website=True, sitemap=True)
    def aide_livraison(self, **kw):
        """Page d'aide "Livraison & installation". Route neuve (pas de
        collision possible avec un autre site de la base mutualisée) :
        pas besoin de garde `_is_our_website`, même logique que /avis.
        """
        return request.render('capsule_house_theme.aide_livraison_page', {})

    @http.route('/retours', type='http', auth='public', website=True, sitemap=True)
    def aide_retours(self, **kw):
        """Page d'aide "Retours & rétractation"."""
        return request.render('capsule_house_theme.aide_retours_page', {})

    @http.route('/garantie', type='http', auth='public', website=True, sitemap=True)
    def aide_garantie(self, **kw):
        """Page d'aide "Garantie constructeur"."""
        return request.render('capsule_house_theme.aide_garantie_page', {})

    @http.route('/faq', type='http', auth='public', website=True, sitemap=True)
    def aide_faq(self, **kw):
        """Page d'aide "Questions fréquentes"."""
        return request.render('capsule_house_theme.aide_faq_page', {})

    @http.route('/a-propos', type='http', auth='public', website=True, sitemap=True)
    def entreprise_apropos(self, **kw):
        """Page Entreprise "À propos". Route neuve (19.0.1.0.47), même
        logique que /livraison etc. : pas de garde `_is_our_website`.
        """
        return request.render('capsule_house_theme.entreprise_apropos_page', {})

    @http.route('/le-concept', type='http', auth='public', website=True, sitemap=True)
    def entreprise_concept(self, **kw):
        """Page Entreprise "Le concept"."""
        return request.render('capsule_house_theme.entreprise_concept_page', {})

    @http.route('/mentions-legales', type='http', auth='public', website=True, sitemap=True)
    def mentions_legales(self, **kw):
        """Page légale — créée en v19.0.1.0.64, liens du footer cassés
        depuis le début du projet (détecté par l'outil SEO natif d'Odoo,
        voir README "Écart connu, non corrigé pour l'instant").
        """
        return request.render('capsule_house_theme.mentions_legales_page', {})

    @http.route('/cgv', type='http', auth='public', website=True, sitemap=True)
    def cgv(self, **kw):
        """Conditions générales de vente — voir mentions_legales() ci-dessus."""
        return request.render('capsule_house_theme.cgv_page', {})

    @http.route('/confidentialite', type='http', auth='public', website=True, sitemap=True)
    def confidentialite(self, **kw):
        """Politique de confidentialité — voir mentions_legales() ci-dessus."""
        return request.render('capsule_house_theme.confidentialite_page', {})

    @http.route('/newsletter/subscribe', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def newsletter_subscribe(self, email=None, **kwargs):
        """Inscription newsletter (footer).

        Route neuve (pas de collision possible avec un autre site) : pas
        besoin de garde `_is_our_website`, elle n'est de toute façon
        appelée que depuis notre propre template de footer.

        'mass_mailing' n'est pas dans les dépendances de ce thème : on
        détecte s'il est installé (mailing.list/mailing.contact
        disponibles) et on s'en sert si oui, sinon on retombe sur un
        simple mail.mail de notification à l'adresse du site, pour que le
        formulaire reste fonctionnel sans dépendance supplémentaire.
        Idempotent : ne crée pas de doublon de contact pour un même email.
        """
        email = (email or '').strip()
        website = request.website
        if not email:
            return request.redirect('/?newsletter=error')

        env = request.env
        # Registry se comporte comme un Mapping {nom_modele: classe} : c'est
        # la façon standard de tester si un modèle optionnel est disponible
        # sans dépendre du module qui le fournit.
        has_mass_mailing = 'mailing.list' in env.registry
        if has_mass_mailing:
            MailingList = env['mailing.list'].sudo()
            mailing_list = MailingList.search([
                ('name', '=', 'Capsule House - Newsletter'),
            ], limit=1)
            if not mailing_list:
                mailing_list = MailingList.create({
                    'name': 'Capsule House - Newsletter',
                })
            Contact = env['mailing.contact'].sudo()
            existing = Contact.search([
                ('email', '=', email),
                ('list_ids', 'in', mailing_list.ids),
            ], limit=1)
            if not existing:
                Contact.create({
                    'email': email,
                    'list_ids': [(4, mailing_list.id)],
                })
        else:
            env['mail.mail'].sudo().create({
                'subject': '[Capsule House] Nouvelle inscription newsletter',
                'body_html': '<p>Nouvelle inscription newsletter : %s</p>' % email,
                'email_from': website.email or 'contact@capsule-house.fr',
                'email_to': website.email or 'contact@capsule-house.fr',
            }).send()

        return request.redirect('/?newsletter=ok')
