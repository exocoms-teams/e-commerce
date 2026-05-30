# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import secrets


# ═══════════════════════════════════════════════════════════════════════
# INTERVENANT
# ═══════════════════════════════════════════════════════════════════════

class SinistreIntervenant(models.Model):
    _name = 'sinistre.intervenant'
    _description = 'Intervenant / Artisan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Fiche Contact', required=True)
    user_id = fields.Many2one('res.users', string='Compte Utilisateur (PWA)')
    specialites = fields.Many2many('sinistre.specialite', string='Spécialités')
    zone_intervention = fields.Char(string="Zone d'Intervention", help="Ex: 75, 92, 93…")
    taux_commission = fields.Float(string='Commission Plateforme (%)', default=15.0)
    actif = fields.Boolean(default=True, tracking=True)
    disponible = fields.Boolean(default=True, tracking=True)
    note = fields.Text(string='Notes')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    mission_ids = fields.One2many('sinistre.mission', 'intervenant_id', string='Missions')
    mission_count = fields.Integer(compute='_compute_stats')
    ca_total = fields.Monetary(compute='_compute_stats', currency_field='currency_id')
    commission_due = fields.Monetary(compute='_compute_stats', currency_field='currency_id')

    @api.depends('mission_ids', 'mission_ids.state', 'mission_ids.montant_devis')
    def _compute_stats(self):
        for rec in self:
            done = rec.mission_ids.filtered(lambda m: m.state in ('termine', 'facture', 'clos'))
            rec.mission_count = len(rec.mission_ids)
            rec.ca_total = sum(done.mapped('montant_devis'))
            rec.commission_due = sum(done.mapped('commission_plateforme'))

    def action_voir_missions(self):
        return {'type': 'ir.actions.act_window', 'name': f"Missions de {self.name}",
                'res_model': 'sinistre.mission', 'view_mode': 'list,kanban,form',
                'domain': [('intervenant_id', '=', self.id)]}


class SinistreSpecialite(models.Model):
    _name = 'sinistre.specialite'
    _description = 'Spécialité Intervenant'

    name = fields.Char(required=True)
    type_intervention = fields.Selection([
        ('serrurerie', 'Serrurerie'), ('plomberie', 'Plomberie'),
        ('menuiserie_int', 'Menuiserie Intérieure'), ('menuiserie_ext', 'Menuiserie Extérieure'),
        ('vitrerie', 'Vitrerie'), ('electricite', 'Électricité'), ('autre', 'Autre'),
    ])
    color = fields.Integer(default=0)


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
    api_key = fields.Char(string='Clé API', copy=False, readonly=True)
    api_key_active = fields.Boolean(default=True)
    webhook_url = fields.Char(string='URL Webhook Retour')
    format_api = fields.Selection([
        ('json_rest', 'JSON REST'), ('xml_soap', 'XML SOAP'),
        ('csv_ftp', 'CSV FTP'), ('custom', 'Personnalisé'),
    ], default='json_rest')
    delai_paiement = fields.Integer(default=30)
    note = fields.Text()
    actif = fields.Boolean(default=True)

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    mission_ids = fields.One2many('sinistre.mission', 'assurance_id')
    mission_count = fields.Integer(compute='_compute_stats')
    ca_assurance = fields.Monetary(compute='_compute_stats', currency_field='currency_id')

    @api.depends('mission_ids', 'mission_ids.montant_garanti')
    def _compute_stats(self):
        for rec in self:
            rec.mission_count = len(rec.mission_ids)
            rec.ca_assurance = sum(rec.mission_ids.mapped('montant_garanti'))

    def action_generer_api_key(self):
        self.ensure_one()
        self.api_key = secrets.token_urlsafe(32)
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': _('Clé API générée'), 'message': _(f'Nouvelle clé pour {self.name}'), 'type': 'success'}}

    def action_revoquer_api_key(self):
        self.write({'api_key': False, 'api_key_active': False})

    def action_voir_missions(self):
        return {'type': 'ir.actions.act_window', 'name': f"Missions {self.name}",
                'res_model': 'sinistre.mission', 'view_mode': 'list,kanban,form',
                'domain': [('assurance_id', '=', self.id)]}


# ═══════════════════════════════════════════════════════════════════════
# DEVIS
# ═══════════════════════════════════════════════════════════════════════

class SinistreDevis(models.Model):
    _name = 'sinistre.devis'
    _description = 'Devis Intervention'
    _inherit = ['mail.thread']
    _order = 'date_devis desc'

    name = fields.Char(required=True, default=lambda self: _('Nouveau'), copy=False)
    mission_id = fields.Many2one('sinistre.mission', required=True, ondelete='cascade')
    intervenant_id = fields.Many2one(related='mission_id.intervenant_id', store=True)
    client_id = fields.Many2one(related='mission_id.client_id', store=True)
    date_devis = fields.Datetime(default=fields.Datetime.now)
    state = fields.Selection([
        ('brouillon', 'Brouillon'), ('envoye', 'Envoyé'),
        ('accepte', 'Accepté'), ('refuse', 'Refusé'),
    ], default='brouillon', tracking=True)

    ligne_ids = fields.One2many('sinistre.devis.ligne', 'devis_id', string='Lignes')
    currency_id = fields.Many2one(related='mission_id.currency_id')
    tva = fields.Float(default=20.0)
    montant_ht = fields.Monetary(compute='_compute_montants', store=True, currency_field='currency_id')
    montant_tva = fields.Monetary(compute='_compute_montants', store=True, currency_field='currency_id')
    montant_total = fields.Monetary(compute='_compute_montants', store=True, currency_field='currency_id')
    note_client = fields.Text()
    motif_refus = fields.Text()
    signature_client = fields.Binary()
    date_signature = fields.Datetime()

    @api.depends('ligne_ids.montant_total', 'tva')
    def _compute_montants(self):
        for rec in self:
            rec.montant_ht = sum(rec.ligne_ids.mapped('montant_total'))
            rec.montant_tva = rec.montant_ht * (rec.tva / 100)
            rec.montant_total = rec.montant_ht + rec.montant_tva

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sinistre.devis') or _('Nouveau')
        return super().create(vals_list)

    def action_envoyer(self):
        from odoo.exceptions import UserError
        if not self.ligne_ids:
            raise UserError(_("Ajoutez au moins une ligne."))
        self.write({'state': 'envoye'})
        self.mission_id.write({'state': 'devis_envoye'})

    def action_accepter(self):
        self.write({'state': 'accepte', 'date_signature': fields.Datetime.now()})
        self.mission_id.write({'state': 'devis_accepte'})

    def action_refuser(self):
        self.write({'state': 'refuse'})
        self.mission_id.write({'state': 'devis_refuse'})


class SinistreDevisLigne(models.Model):
    _name = 'sinistre.devis.ligne'
    _description = 'Ligne de Devis'

    devis_id = fields.Many2one('sinistre.devis', ondelete='cascade')
    sequence = fields.Integer(default=10)
    description = fields.Char(required=True)
    quantite = fields.Float(default=1.0)
    unite = fields.Char(default='forfait')
    prix_unitaire = fields.Monetary(currency_field='currency_id')
    montant_total = fields.Monetary(compute='_compute_total', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='devis_id.currency_id')

    @api.depends('quantite', 'prix_unitaire')
    def _compute_total(self):
        for rec in self:
            rec.montant_total = rec.quantite * rec.prix_unitaire


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
