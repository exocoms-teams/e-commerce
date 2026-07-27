from odoo import models, fields, api

class TrendSubmission(models.Model):
    _name = 'trend.submission'
    _description = 'Soumission de produit tendance'
    _order = 'create_date desc'

    name = fields.Char(string="Nom du produit", required=True)
    product_ref = fields.Char(string="Référence / URL", required=True)
    category = fields.Char(string="Catégorie", required=True)
    country = fields.Char(string="Code Pays (ISO 2)", required=True, size=2)
    
    # Notre fameux champ orienté UX
    submission_reason = fields.Selection([
        ('intuition', "J'ai ce produit en tête (Intuition)"),
        ('experience', "Par expérience (Je vends déjà ce type de produit)"),
        ('spotted', "Je l'ai repéré sur les réseaux sociaux")
    ], string="Contexte de la soumission", default='intuition')
    
    submitted_by = fields.Char(string="Soumis par", default=lambda self: self.env.user.name)
    
    status = fields.Selection([
        ('pending', 'En attente'),
        ('validated', 'Validé'),
        ('rejected', 'Rejeté')
    ], string="Statut", default='pending', required=True)

    def action_validate(self):
        """ Copie les données pour instancier un nouveau trend.product """
        for record in self:
            if record.status == 'pending':
                
                # 1. Chercher ou créer la catégorie cible
                category_record = self.env['trend.category'].search([('name', '=', record.category)], limit=1)
                if not category_record:
                    category_record = self.env['trend.category'].create({'name': record.category})

                # 2. Instanciation du produit final avec category_id
                self.env['trend.product'].create({
                    'name': record.name,
                    'product_ref': record.product_ref,
                    'category_id': category_record.id,
                    'country': record.country,
                    'source': 'crowdsourcing',
                })
                
                # 3. Mise à jour du statut
                record.status = 'validated'
    def action_reject(self):
        """ Rejette la soumission """
        for record in self:
            if record.status == 'pending':
                record.status = 'rejected'