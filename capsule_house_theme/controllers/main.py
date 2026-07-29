# -*- coding: utf-8 -*-
import datetime

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class CapsuleHouseWebsite(Website):
    """Contrôleurs frontend du site Capsule House.

    Pages livrées pour l'instant : Accueil (/) et Boutique (/shop, gérée
    nativement par website_sale — pas de route custom nécessaire ici, on se
    contente d'y ajouter du contexte si besoin plus tard). Les autres pages
    (Services, Contact, À propos) seront ajoutées au fur et à mesure.

    Règle de sécurité multi-site : `request.website` est déjà résolu par
    Odoo selon le domaine HTTP entrant, donc systématiquement NOTRE site
    (ou un autre site de la base mutualisée si le contrôleur venait à être
    appelé dans un autre contexte). On ne suppose donc jamais qu'un produit
    ou une donnée est "à nous" sans filtrer explicitement par
    `request.website.id`.
    """

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

    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def homepage(self, **kwargs):
        website = request.website
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

    @http.route('/newsletter/subscribe', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def newsletter_subscribe(self, email=None, **kwargs):
        """Inscription newsletter (footer).

        'mass_mailing' n'est pas dans les dépendances de ce thème : on
        détecte s'il est installé (mailing.list/mailing.contact
        disponibles) et on s'en sert si oui : sinon, on retombe sur un
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
