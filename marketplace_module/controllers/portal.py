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
    auth='user',
    website=True,
    sitemap=False,
)
    def vendor_dashboard(self, **kw):
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')

        products = request.env['product.template'].sudo().search(
            [('vendor_id', '=', vendor.id)],
            order='name asc'
        )

        # Comptage commandes du mois — tous statuts sauf cancel
        from datetime import datetime
        first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        product_ids = products.mapped('product_variant_ids').ids
        orders_count = 0
        if product_ids:
            order_lines = request.env['sale.order.line'].sudo().search([
                ('product_id', 'in', product_ids),
                ('order_id.state', 'not in', ['cancel']),
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
    def vendor_orders(self, page=1, status=None, **kw):
        vendor = self._get_vendor_or_redirect()
        if not vendor:
            return request.redirect('/shop')

        ITEMS_PER_PAGE = 10

        product_ids = request.env['product.template'].sudo().search(
            [('vendor_id', '=', vendor.id)]
        ).mapped('product_variant_ids').ids

        # Domaine de base — tous statuts sauf cancel
        domain = [
            ('product_id', 'in', product_ids),
            ('order_id.state', 'not in', ['cancel']),
        ]

        # Filtre par statut
        if status:
            domain.append(('order_id.state', '=', status))

        # Total commandes pour le badge
        total_orders = len(
            request.env['sale.order.line'].sudo().search(domain).mapped('order_id')
        )

        # Total pour pagination
        total = request.env['sale.order.line'].sudo().search_count(domain)

        # Commandes paginées
        offset = (int(page) - 1) * ITEMS_PER_PAGE
        orders = request.env['sale.order.line'].sudo().search(
            domain,
            order='order_id desc',
            limit=ITEMS_PER_PAGE,
            offset=offset,
        )

        return request.render(
            'marketplace_module.vendor_orders',
            {
                'vendor': vendor,
                'orders': orders,
                'total': total,
                'total_orders': total_orders,
                'page': int(page),
                'items_per_page': ITEMS_PER_PAGE,
                'status': status or '',
            }
        )