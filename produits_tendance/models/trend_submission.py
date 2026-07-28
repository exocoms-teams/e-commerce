from odoo import models, fields, api
from odoo.exceptions import UserError

class TrendSubmission(models.Model):
    _name = 'trend.submission'
    _description = 'Soumission de Produit Tendance'
    _order = 'create_date desc'


    name = fields.Char(string='Nom du produit', required=True)
    product_ref = fields.Char(string='Lien/Description du produit')
    category = fields.Char(string='Catégorie')
    country = fields.Char(string='Pays', size=2)
    submission_reason = fields.Selection([
        ('intuition', 'Intuition'),
        ('experience', 'Expérience'),
        ('spotted', 'Vu sur les réseaux')
    ], string='Raison')
    submitted_by = fields.Char(string='Soumis par (Nom)')
    email = fields.Char(string='Email du contributeur') 
    description = fields.Text(string='Description du produit')
    
    status = fields.Selection([
        ('pending', 'En attente'),
        ('validated', 'Validé'),
        ('rejected', 'Rejeté')
    ], string='Statut', default='pending')

    def action_reject(self):
        """ Rejette la soumission et envoie un email """
        for record in self:
            if record.status != 'pending':
                raise UserError("Vous ne pouvez rejeter qu'une soumission en attente.")
            
            # Mettre à jour le statut et notifier
            record.status = 'rejected'
            record._send_notification_email('rejected')

    def action_validate(self):
        """ Valide la soumission, crée le produit s'il n'existe pas, et envoie un email adapté """
        for record in self:
            if record.status != 'pending':
                raise UserError("Vous ne pouvez valider qu'une soumission en attente.")
            
            # --- LOGIQUE DE RECHERCHE ---
            # 1. Si product_ref contient un lien web valide (commence par http)
            if record.product_ref and record.product_ref.startswith('http'):
                domain = [
                    ('product_ref', '=', record.product_ref),
                    ('source', '=', 'crowdsourcing')
                ]
                actual_ref = record.product_ref # On garde le lien comme référence pour la BDD
                
            # 2. Sinon (c'est juste du texte / pas de lien), on cherche par NOM
            else:
                domain = [
                    # '=ilike' permet de chercher le nom sans être sensible aux majuscules/minuscules
                    ('name', '=ilike', record.name), 
                    ('source', '=', 'crowdsourcing')
                ]
                # On génère une référence technique propre (ex: montre-2026-07-27) pour satisfaire la contrainte SQL
                safe_name = record.name.replace(' ', '-').lower()
                actual_ref = f"{safe_name}-{fields.Date.today()}"

            # Exécution de la recherche
            existing_product = self.env['trend.product'].search(domain, limit=1)

            # --- LOGIQUE DE CREATION ET D'EMAIL ---
            record.status = 'validated'
            if not existing_product:
                # Création de la catégorie si besoin
                category_id = False
                if record.category:
                    Category = self.env['trend.category']
                    cat_record = Category.search([('name', '=', record.category)], limit=1)
                    if not cat_record:
                        cat_record = Category.create({'name': record.category})
                    category_id = cat_record.id
                    
                # Création du produit dans la table principale avec la référence déterminée (actual_ref)
                self.env['trend.product'].create({
                    'name': record.name,
                    'product_ref': actual_ref,
                    'category_id': category_id,
                    'country': record.country,
                    'source': 'crowdsourcing'
                })
                # Email pour un NOUVEAU produit
                record._send_notification_email('validated_new')
            else:
                # Email pour un produit DEJA EXISTANT
                record._send_notification_email('validated_existing')

    def _send_notification_email(self, action_type):
        """ Envoie l'email avec le texte approprié """
        for record in self:
            if not record.email:
                continue

            if action_type == 'validated_new':
                subject = f"🎉 Félicitations ! Votre produit '{record.name}' a été sélectionné"
                body = f"<p>Bonjour,</p><p>Merci beaucoup pour votre contribution ! Après validation par notre équipe, nous avons l'honneur de vous informer que votre produit <strong>{record.name}</strong> a été validé.</p><p>Il a été évalué avec un pourcentage très respectable en tant que produit tendance et a été officiellement ajouté à notre algorithme.</p><p>Nous serions fiers de recevoir d'autres suggestions de votre part !</p>"
            
            elif action_type == 'validated_existing':
                subject = f"💡 Merci pour votre suggestion '{record.name}' !"
                body = f"<p>Bonjour,</p><p>Nous vous remercions chaleureusement pour votre contribution. Vous avez l'œil ! Le produit <strong>{record.name}</strong> est effectivement très pertinent et figure d'ailleurs déjà dans notre base de données.</p><p>N'hésitez pas à nous soumettre d'autres pépites, nous serons ravis de découvrir vos prochaines propositions !</p>"
            
            elif action_type == 'rejected':
                subject = f"Mise à jour concernant votre produit '{record.name}'"
                body = f"<p>Bonjour,</p><p>Nous avons bien étudié votre suggestion pour <strong>{record.name}</strong>. Veuillez accepter nos excuses, mais elle n'a pas été retenue pour le moment.</p><p>N'hésitez pas à nous soumettre d'autres idées à l'avenir !</p>"

            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': record.email,
                'email_from': self.env.company.email or 'winners@exocoms.fr',
            }
            self.env['mail.mail'].sudo().create(mail_values).send()