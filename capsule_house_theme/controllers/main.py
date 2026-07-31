# -*- coding: utf-8 -*-
import datetime

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
    Une première version de ce contrôleur surchargeait directement '/' et
    cassait donc la page d'accueil des 16 autres sites (et tentait
    d'appeler `super().homepage()`, qui n'existe même pas sur le
    contrôleur `Website` natif — `AttributeError` en prod).

    La page d'accueil est donc servie sur une route dédiée et unique
    (`/capsule-house/home`, jamais réutilisée ailleurs dans la base), et
    c'est le champ natif `website.homepage_url` — déjà scopé par site,
    aucun risque de fuite — qui indique à Odoo de servir cette route
    quand un visiteur de NOTRE site demande '/'. Posé par
    `_setup_homepage()` dans __init__.py. On ne touche donc JAMAIS au
    routing partagé du contrôleur Website natif.
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

    @http.route('/capsule-house/home', type='http', auth='public',
                website=True, sitemap=False)
    def homepage(self, **kwargs):
        website = request.website
        if not self._is_our_website(website):
            # Route unique à ce module : ne devrait jamais être atteinte
            # pour un autre site. Filet de sécurité si jamais un admin
            # pointait par erreur le homepage_url d'un autre site ici.
            return request.redirect('/')

        Product = request.env['product.template'].sudo()
        domain = [
            ('website_id', '=', website.id),
            ('is_published', '=', True),
        ]
        featured_products = Product.search(domain, limit=8, order='website_sequence asc')

        # Métriques de la maquette de référence : "4 modèles disponibles"
        # est un vrai comptage (sûr à afficher). "2 340 pods installés" et
        # la note "4.9 · X avis" étaient des chiffres fixes de la maquette,
        # non vérifiés par ce module — on ne les fabrique pas : ils restent
        # masqués tant qu'un admin ne les a pas renseignés explicitement
        # via ir.config_parameter (à exposer dans Réglages > Technique si
        # besoin d'un vrai écran de configuration plus tard).
        ICP = request.env['ir.config_parameter'].sudo()
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
            return request.redirect('/capsule-house/home?newsletter=error')

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

        return request.redirect('/capsule-house/home?newsletter=ok')
