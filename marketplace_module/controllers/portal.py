from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class VendorPortal(http.Controller):
    """
    Controleur du portail vendeur.
    Toutes les routes commencent par /vendor/
    Toutes requierent auth='user' (connexion obligatoire).
    """

    # ── Methode utilitaire interne ─────────────────────────────────────────
    def _get_vendor_or_redirect(self):
        """
        Retourne le vendeur associe a l'utilisateur connecte.
        Si l'utilisateur n'est pas un vendeur, redirige vers /shop.
        Implemention: blocage acces portail sans profil vendeur.
        """
        vendor = request.env['marketplace.vendor'].sudo()._get_vendor_for_user(
            request.env.user
        )
        if not vendor:
            _logger.warning(
                'Tentative acces portail vendeur par utilisateur non-vendeur: %s',
                request.env.user.login
            )
            return None
        return vendor

    # ── Route 1 : Tableau de bord ──────────────────────────────────────────
    @http.route(
        '/vendor/dashboard',
        type='http',
        auth='user',        # connexion requise (F-04-04)
        website=True,       # compatible multi-website (F-03-05)
        sitemap=False,      # ne pas indexer dans le sitemap public
    )
    def vendor_dashboard(self, **kw):
        """
        Page principale du portail vendeur.
        Affiche les stats et la liste des produits du vendeur connecte.
        """
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')

        # Produits du vendeur (filtre vendor_id = ce vendeur)
        products = request.env['product.template'].sudo().search(
            [('vendor_id', '=', vendor.id)],
            order='name asc'
        )

        # Comptage des commandes du mois en cours
        from datetime import datetime, timedelta
        first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        product_ids = products.mapped('product_variant_ids').ids
        orders_count = 0
        if product_ids:
            order_lines = request.env['sale.order.line'].sudo().search([
                ('product_id', 'in', product_ids),
                ('order_id.state', 'in', ['sale', 'done']),
                ('order_id.date_order', '>=', first_day),
            ])
            orders_count = len(order_lines.mapped('order_id'))

        return request.render(
            'marketplace_module.vendor_dashboard',
            {
                'vendor': vendor,
                'products': products,
                'orders_count': orders_count,
            }
        )

    # ── Route 2 : Liste complete des produits ─────────────────────────────
    @http.route(
        '/vendor/products',
        type='http',
        auth='user',
        website=True,
        sitemap=False,
    )
    def vendor_products(self, page=1, **kw):
        """
        Liste paginee des produits du vendeur (F-02-02).
        Parametre GET : page (numero de page pour la pagination)
        """
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')

        # Pagination : 12 produits par page
        ITEMS_PER_PAGE = 12
        offset = (int(page) - 1) * ITEMS_PER_PAGE

        products = request.env['product.template'].sudo().search(
            [('vendor_id', '=', vendor.id)],
            limit=ITEMS_PER_PAGE,
            offset=offset,
            order='name asc'
        )
        total = request.env['product.template'].sudo().search_count(
            [('vendor_id', '=', vendor.id)]
        )

        # Reutilise le template vendor_dashboard avec tous les produits
        return request.render(
            'marketplace_module.vendor_dashboard',
            {
                'vendor': vendor,
                'products': products,
                'orders_count': 0,
                'page': int(page),
                'total': total,
                'items_per_page': ITEMS_PER_PAGE,
            }
        )

    # ── Route 3 : Edition d'un produit (GET + POST) ───────────────────────
    @http.route(
        '/vendor/product/<int:product_id>/edit',
        type='http',
        auth='user',
        website=True,
        sitemap=False,
        methods=['GET', 'POST'],
    )
    def vendor_product_edit(self, product_id, **kw):
        """
        Formulaire d'edition d'un produit (F-02-03).
        GET  : affiche le formulaire pre-rempli
        POST : traite la soumission du formulaire
        Le vendeur ne peut modifier QUE ses propres produits.
        """
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')

        # Charger le produit ET verifier qu'il appartient bien a ce vendeur
        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists() or product.vendor_id.id != vendor.id:
            # Produit inexistant ou appartenant a un autre vendeur : acces refuse
            _logger.warning(
                'Tentative edition produit non-autorisee: vendeur=%s produit=%s',
                vendor.id, product_id
            )
            return request.redirect('/vendor/dashboard')

        error = None
        success = False

        # Traitement du formulaire POST (soumission)
        if request.httprequest.method == 'POST':
            try:
                # Recuperer et valider les donnees du formulaire
                new_price = float(kw.get('list_price', 0))
                new_desc  = kw.get('description_sale', '').strip()

                if new_price < 0:
                    error = 'Le prix ne peut pas etre negatif.'
                else:
                    # Mise a jour avec sudo() pour contourner les droits QWeb
                    product.sudo().write({
                        'list_price': new_price,
                        'description_sale': new_desc,
                    })
                    success = True
                    _logger.info(
                        'Produit %s mis a jour par vendeur %s',
                        product.name, vendor.name
                    )
            except (ValueError, TypeError) as e:
                error = 'Valeur invalide : verifiez le format du prix.'
                _logger.error('Erreur edition produit: %s', str(e))

        return request.render(
            'marketplace_module.vendor_product_edit',
            {
                'vendor': vendor,
                'product': product,
                'error': error,
                'success': success,
            }
        )

    # ── Route 4 : Commandes du vendeur (lecture seule) ────────────────────
    @http.route(
        '/vendor/orders',
        type='http',
        auth='user',
        website=True,
        sitemap=False,
    )
    def vendor_orders(self, **kw):
        """
        Affiche les commandes liees aux produits du vendeur (F-02-04).
        Lecture seule : le vendeur ne peut pas modifier les commandes.
        """
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')

        # Lignes de commande dont le produit appartient a ce vendeur
        product_ids = request.env['product.template'].sudo().search(
            [('vendor_id', '=', vendor.id)]
        ).mapped('product_variant_ids').ids

        orders = []
        if product_ids:
            orders = request.env['sale.order.line'].sudo().search(
                [
                    ('product_id', 'in', product_ids),
                    ('order_id.state', 'in', ['sale', 'done']),
                ],
                order='order_id desc',
                limit=50  # 50 commandes les plus recentes
            )

        return request.render(
            'marketplace_module.vendor_orders',
            {
                'vendor': vendor,
                'orders': orders,
            }
        )
