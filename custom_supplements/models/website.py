from odoo import models
from odoo.http import request
from odoo.fields import Domain

class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        # 1. On récupère le domaine de base
        domain = super().sale_product_domain()
        
        # 2. Vérification de l'URL
        if request and hasattr(request, 'params') and request.params.get('vegan'):
            # 3. Nouvelle syntaxe Odoo 18/19+ avec l'opérateur & (AND) et l'objet Domain
            domain = Domain(domain) & Domain([('is_vegan', '=', True)])
            
        return domain