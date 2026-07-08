from odoo import models, fields

class TrendAd(models.Model):
    _name = 'trend.ad'
    _description = 'Publicité des produits tendances'

    # Identifiants
    ad_ref = fields.Char(string='ID Publicité (Réseau Social)', required=True)
    
    # Lien vers le produit (Dépendance Epic 1.A)
    product_id = fields.Many2one(
        'trend.product', 
        string='Produit concerné', 
        required=True, 
        ondelete='cascade'
    )
    
    # Informations géographiques et sources
    country = fields.Char(
        string='Pays cible (Code ISO)', 
        size=2, 
        required=True, 
        help="Code ISO 2 lettres, ex: MA, FR" 
    ) #
    
    social_network = fields.Selection(
        [
            ('facebook', 'Facebook'), 
            ('tiktok', 'TikTok'), 
            ('instagram', 'Instagram')
        ], 
        string="Réseau social d'origine", 
        required=True
    ) #
    
    # Métriques d'engagement avec valeurs par défaut
    likes_count = fields.Integer(string='Nombre de likes', default=0) #
    shares_count = fields.Integer(string='Nombre de partages', default=0) #