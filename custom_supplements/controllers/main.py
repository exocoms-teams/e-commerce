from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleSupplements(WebsiteSale):
    
    # On surcharge la méthode qui prépare la recherche des produits
    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        # 1. On récupère le domaine de recherche standard d'Odoo
        domain = super(WebsiteSaleSupplements, self)._get_search_domain(
            search, category, attrib_values, search_in_description
        )
        
        # 2. Si le paramètre 'vegan' est détecté dans l'URL (ex: /shop?vegan=1)
        if request.params.get('vegan'):
            # On ajoute notre propre condition : le champ is_vegan doit être True
            domain.append(('is_vegan', '=', True))

        # 3. On gère le filtre par allergène
        if request.params.get('allergens_exclude'):

            domain.append(('allergens','not ilike', request.params.get('allergens_exclude')))

        return domain

    def _get_search_options(self, **kwargs):
        options = super()._get_search_options(**kwargs)
        allergen_ids = request.httprequest.args.getlist('allergens_exclude')
        options['allergens_exclude_ids'] = [int(i) for i in allergen_ids if i.isdigit()]
        return options

    def _get_additional_shop_values(self, values, **kwargs):
        values = super()._get_additional_shop_values(values, **kwargs)
        values['allergens_exclude_ids'] = request.httprequest.args.getlist('allergens_exclude')
        return values