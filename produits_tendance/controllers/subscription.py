# controllers/subscription.py
"""WIN-66 : page de tarifs + bouton "Souscrire à l'abonnement Premium",
lié au module sale (eCommerce) via les pages produit standard de
website_sale_subscription (choix du plan mensuel/annuel géré nativement
par ce module sur la page /shop/<id>, pas de tunnel de paiement custom)."""
from odoo import http
from odoo.http import request


class TrendSubscriptionController(http.Controller):

    @http.route('/abonnement', type='http', auth='public', website=True)
    def pricing(self, **kwargs):
        Product = request.env['product.template'].sudo()
        standard_group = request.env.ref('produits_tendance.group_trend_standard')
        pro_group = request.env.ref('produits_tendance.group_trend_pro')

        return request.render('produits_tendance.template_subscription_pricing', {
            'standard_product': Product.search(
                [('winners_subscription_group_id', '=', standard_group.id)], limit=1
            ),
            'pro_product': Product.search(
                [('winners_subscription_group_id', '=', pro_group.id)], limit=1
            ),
        })
