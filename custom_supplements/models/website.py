from odoo import models
from odoo.http import request
from odoo.osv import expression

class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        # 1. On récupère le domaine de base (qui est un objet DomainAnd)
        domain = super().sale_product_domain()
        
        # 2. Vérification sécurisée : l'URL contient-elle "?vegan=1" ?
        if request and hasattr(request, 'params') and request.params.get('vegan'):
            # 3. On utilise l'outil Odoo pour fusionner le domaine existant avec notre condition
            domain = expression.AND([domain, [('is_vegan', '=', True)]])
            
        return domain