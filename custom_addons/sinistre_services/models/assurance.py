# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import secrets


# ═══════════════════════════════════════════════════════════════════════
# ASSURANCE
# ═══════════════════════════════════════════════════════════════════════

class SinistreAssurance(models.Model):
    _name = 'sinistre.assurance'
    _description = "Compagnie d'Assurance"
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    code = fields.Char(string='Code Assurance', help="Ex: AXA, MAIF, ALLIANZ")
    api_key = fields.Char(string='Clé API', copy=False)
    api_key_active = fields.Boolean(default=True)
    webhook_url = fields.Char(string='URL Webhook Retour')
    format_api = fields.Selection([
        ('json_rest', 'JSON REST'), ('xml_soap', 'XML SOAP'),
        ('csv_ftp', 'CSV FTP'), ('custom', 'Personnalisé'),
    ], default='json_rest')
    delai_paiement = fields.Integer(default=30)
    note = fields.Text()
    actif = fields.Boolean(default=True)

    # ── Portail / Compte ──────────────────────────────────────────────
    portal_user_id   = fields.Many2one('res.users', string='Compte Portail', readonly=True)
    inscription_date = fields.Datetime(string="Date d'inscription", readonly=True)
    statut_compte    = fields.Selection([
        ('en_attente', 'En attente de validation'),
        ('actif',      'Actif'),
        ('suspendu',   'Suspendu'),
    ], default='en_attente', string='Statut compte', tracking=True)
    peut_annuler      = fields.Boolean(string='Peut annuler des missions', default=True)
    delai_annulation  = fields.Integer(
        string="Délai max annulation sans frais (h)", default=2,
        help="Nombre d'heures avant le RDV en-deçà duquel l'annulation génère des frais"
    )

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    mission_ids = fields.One2many('sinistre.mission', 'assurance_id')
    mission_count = fields.Integer(compute='_compute_stats')
    ca_assurance = fields.Monetary(compute='_compute_stats', currency_field='currency_id')

    @api.depends('mission_ids', 'mission_ids.montant_garanti')
    def _compute_stats(self):
        for rec in self:
            rec.mission_count = len(rec.mission_ids)
            rec.ca_assurance = sum(rec.mission_ids.mapped('montant_garanti'))

    def action_valider_compte(self):
        self.ensure_one()
        if not self.portal_user_id:
            self._creer_compte_portail()
        self.write({'statut_compte': 'actif'})
        self.message_post(body=f"Compte assurance activé")

    def _creer_compte_portail(self):
        import secrets as _secrets
        if not self.partner_id.email:
            from odoo.exceptions import UserError
            raise UserError("L'assurance doit avoir un email pour créer un compte portail.")
        group_portal = self.env.ref('base.group_portal')
        user = self.env['res.users'].create({
            'name':       self.name,
            'login':      self.partner_id.email,
            'partner_id': self.partner_id.id,
            'groups_id':  [(4, group_portal.id)],
            'password':   _secrets.token_urlsafe(12),
        })
        if not self.api_key:
            self.api_key = _secrets.token_urlsafe(32)
        self.write({'portal_user_id': user.id, 'inscription_date': fields.Datetime.now()})
        return user

    def action_suspendre(self):
        self.write({'statut_compte': 'suspendu'})
        if self.portal_user_id:
            self.portal_user_id.write({'active': False})

    def _check_annulation_autorisee(self, mission):
        if not mission.date_rdv:
            return True, 0
        from datetime import datetime
        delta = (mission.date_rdv - datetime.now()).total_seconds() / 3600
        return (delta >= self.delai_annulation), delta

    def action_generer_api_key(self):
        self.ensure_one()
        self.api_key = secrets.token_urlsafe(32)
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': _('Clé API générée'), 'message': _(f'Nouvelle clé pour {self.name}'), 'type': 'success'}}

    def action_copier_api_key(self):
        """Affiche la clé dans une notification pour pouvoir la copier."""
        self.ensure_one()
        if not self.api_key:
            return {'type': 'ir.actions.client', 'tag': 'display_notification',
                    'params': {'title': 'Aucune clé', 'message': 'Générez d\'abord une clé API.', 'type': 'warning'}}
        return {
            'type': 'ir.actions.client',
            'tag':  'display_notification',
            'params': {
                'title':   '🔑 Clé API',
                'message': self.api_key,
                'type':    'info',
                'sticky':  True,
            }
        }

    def action_revoquer_api_key(self):
        self.write({'api_key': False, 'api_key_active': False})

    def action_voir_missions(self):
        return {'type': 'ir.actions.act_window', 'name': f"Missions {self.name}",
                'res_model': 'sinistre.mission', 'view_mode': 'list,kanban,form',
                'domain': [('assurance_id', '=', self.id)]}


# ═══════════════════════════════════════════════════════════════════════
# PHOTO DOSSIER
# ═══════════════════════════════════════════════════════════════════════

class SinistrePhoto(models.Model):
    _name = 'sinistre.photo'
    _description = 'Photo Dossier Sinistre'
    _order = 'date_prise desc'

    mission_id = fields.Many2one('sinistre.mission', required=True, ondelete='cascade')
    type_photo = fields.Selection([
        ('avant', 'Avant Intervention'),
        ('pendant', 'Pendant'),
        ('apres', 'Après Intervention'),
    ], required=True, default='avant')
    image = fields.Binary(required=True)
    image_filename = fields.Char()
    description = fields.Char()
    date_prise = fields.Datetime(default=fields.Datetime.now)
    intervenant_id = fields.Many2one(related='mission_id.intervenant_id', store=True)
    latitude = fields.Float(digits=(10, 7))
    longitude = fields.Float(digits=(10, 7))


# ═══════════════════════════════════════════════════════════════════════
# COMMISSION
# ═══════════════════════════════════════════════════════════════════════

class SinistreCommission(models.Model):
    _name = 'sinistre.commission'
    _description = 'Commission Plateforme'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='/')
    mission_id = fields.Many2one('sinistre.mission', required=True)
    intervenant_id = fields.Many2one(related='mission_id.intervenant_id', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    montant_intervention = fields.Monetary(currency_field='currency_id')
    taux_commission = fields.Float()
    montant_commission = fields.Monetary(currency_field='currency_id')
    state = fields.Selection([('due', 'Due'), ('facturee', 'Facturée'), ('payee', 'Payée')], default='due', tracking=True)
    date_echeance = fields.Date()
    facture_id = fields.Many2one('account.move')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('sinistre.commission') or '/'
        return super().create(vals_list)


# ═══════════════════════════════════════════════════════════════════════
# CERTIFICATION INTERVENANT
# ═══════════════════════════════════════════════════════════════════════

class SinistreCertification(models.Model):
    _name        = 'sinistre.certification'
    _description = 'Certification / Document Intervenant'
    _order       = 'sequence, id'

    intervenant_id = fields.Many2one('sinistre.intervenant', required=True, ondelete='cascade')
    name           = fields.Char(string='Libellé', required=True)
    date_validite  = fields.Date(string='Valide jusqu\'au')
    sequence       = fields.Integer(default=10)

    def _date_label(self):
        if not self.date_validite:
            return 'À jour'
        return f"Valide jusqu'en {self.date_validite.strftime('%Y')}"
