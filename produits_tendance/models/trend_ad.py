from odoo import models, fields, api

def latest_ads_by_ref(ad_ids):
    latest_by_ref = {}
    for ad in ad_ids.sorted('collected_at'):
        latest_by_ref[ad.ad_ref] = ad
    return ad_ids.browse([ad.id for ad in latest_by_ref.values()])
class TrendAd(models.Model):
    _name = 'trend.ad'
    _description = 'Publicité des produits tendances'

    # Identifiants
    ad_ref = fields.Char(string='ID Publicité (Réseau Social)', required=True)
    
    # Nouveaux champs pour capter les données entrantes (API ou formulaire)
    product_ref = fields.Char(string="Référence Produit Brute", help="Référence reçue avant liaison.")
    product_name = fields.Char(string="Nom du Produit Brute", help="Nom du produit s'il doit être créé.")

    # Lien vers le produit
    # on enlève required=True ici, sinon Odoo bloquera la sauvegarde avant même de lancer notre fonction de création .
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
        required=True
    )
    
    # Métriques d'engagement avec valeurs par défaut
    likes_count = fields.Integer(string='Nombre de likes', default=0)
    shares_count = fields.Integer(string='Nombre de partages', default=0)

    # WIN-XX ("Étendre trend.ad avec un champ de date") : horodatage de la
    # collecte. Nécessaire pour passer trend.ad en mode historique (WIN-XX,
    # "Passer trend.ad en mode historique") : chaque nouvelle collecte crée
    # désormais une nouvelle ligne au lieu d'écraser likes_count/shares_count
    # sur la ligne existante, afin de pouvoir reconstituer Vol_T_prev pour
    # le calcul de croissance (voir models/trend_score_calculator.py).
    # NB : les lignes trend.ad créées avant ce changement n'ont pas de
    # valeur ici (collected_at=False) — prévoir une migration de données si
    # l'historique passé doit être exploité.
    collected_at = fields.Datetime(
        string="Date de collecte",
        default=fields.Datetime.now,
    )


    # Surcharge de la méthode de création
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # On vérifie si on a reçu une référence brute sans produit déjà lié
            if vals.get('product_ref') and not vals.get('product_id'):
                ref = vals.get('product_ref')
                
                # On récupère le nom envoyé, sinon on met un fallback de sécurité
                name = vals.get('product_name') or f"Produit sans nom ({ref})"
                
                # 1. Recherche du produit existant
                product = self.env['trend.product'].search([('product_ref', '=', ref)], limit=1)
                
                # 2. Création avec LE BON NOM s'il n'existe pas
                if not product:
                    product = self.env['trend.product'].create({
                        'name': name,
                        'product_ref': ref,
                        
                        'source': 'api'
                    })
                
                # 3. On rattache le produit à la publicité
                vals['product_id'] = product.id
                
        #
        return super(TrendAd, self).create(vals_list)