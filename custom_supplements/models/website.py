from odoo import models
from odoo.http import request

class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        # 1. On récupère le domaine de base strict (produits publiés, disponibles, etc.)
        domain = super().sale_product_domain()
        
        # 2. Vérification sécurisée : sommes-nous dans une requête web contenant "?vegan=1" ?
        # L'utilisation de hasattr évite les plantages lors des tâches CRON internes
        if request and hasattr(request, 'params') and request.params.get('vegan'):
            domain.append(('is_vegan', '=', True))
            
        return domain