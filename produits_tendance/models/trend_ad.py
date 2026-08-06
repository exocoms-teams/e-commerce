from odoo import models, fields, api

def latest_ads_by_ref(ad_ids):
    latest_by_ref = {}
    for ad in ad_ids.sorted('collected_at'):
        latest_by_ref[ad.ad_ref] = ad
    return ad_ids.browse([ad.id for ad in latest_by_ref.values()])
class TrendAd(models.Model):
    _name = 'trend.ad'
    _description = 'Publicité des produits tendances (TrendTracker)'

    # Identifiants
    ad_ref = fields.Char(string='ID Publicité (Réseau Social)', required=True)
    
    # Données entrantes pour la liaison automatique
    product_ref = fields.Char(string="Référence Produit Brute", help="Référence reçue avant liaison.")
    product_name = fields.Char(string="Nom du Produit Brute", help="Nom du produit s'il doit être créé.")

    # Liaison vers le produit
    product_id = fields.Many2one(
        'trend.product', 
        string='Produit concerné', 
        ondelete='cascade'
    )
    
    # Informations géographiques et sources
    country = fields.Char(
        string='Pays cible (Code ISO)', 
        size=2, 
        required=True, 
        help="Code ISO 2 lettres, ex: MA, FR" 
    )
    
    social_network = fields.Selection(
        [
            ('facebook', 'Facebook'), 
            ('tiktok', 'TikTok'), 
            ('instagram', 'Instagram')
        ], 
        string="Réseau social d'origine", 
        required=True,
        default='facebook'
    )

    # =========================================================
    # NOUVEAUX CHAMPS TRENDTRACKER (Intelligence Concurrentielle)
    # =========================================================
    days_active = fields.Integer(
        string="Jours d'activité", 
        default=0, 
        help="Nombre de jours de diffusion continue (Métrique clé de rentabilité)"
    )
    ad_start_date = fields.Date(string="Date de lancement")
    competitor_page = fields.Char(string="Boutique / Page Facebook", help="Nom de la page concurrente")
    snapshot_url = fields.Char(string="Aperçu Publicité (URL)", help="Lien de la vidéo/image sur Meta")
    platforms = fields.Char(string="Plateformes", help="Ex: facebook, instagram")
    is_active = fields.Boolean(string="Publicité Active", default=True)

    # Anciennes métriques conservées pour compatibilité
    likes_count = fields.Integer(string='Nombre de likes', default=0)
    shares_count = fields.Integer(string='Nombre de partages', default=0)

    collected_at = fields.Datetime(
        string="Date de collecte",
        default=fields.Datetime.now,
    )

    # Surcharge de la méthode de création pour la gestion automatique des produits
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('product_ref') and not vals.get('product_id'):
                ref = vals.get('product_ref')
                name = vals.get('product_name') or f"Produit sans nom ({ref})"
                
                product = self.env['trend.product'].search([('product_ref', '=', ref)], limit=1)
                
                if not product:
                    product = self.env['trend.product'].create({
                        'name': name,
                        'product_ref': ref,
                        'source': 'api'
                    })
                
                vals['product_id'] = product.id
                
        return super(TrendAd, self).create(vals_list)