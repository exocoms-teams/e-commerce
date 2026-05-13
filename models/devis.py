# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SinistreDevis(models.Model):
    """
    Devis établi par l'intervenant avant de démarrer les travaux.
    Le client doit accepter ou refuser avant toute intervention.
    """
    _name = 'sinistre.devis'
    _description = 'Devis Intervention'
    _inherit = ['mail.thread']
    _order = 'date_devis desc'

    name = fields.Char(
        string='Référence Devis',
        required=True,
        default=lambda self: _('Nouveau'),
        copy=False,
    )
    mission_id = fields.Many2one(
        'sinistre.mission',
        string='Mission',
        required=True,
        ondelete='cascade',
    )
    intervenant_id = fields.Many2one(
        related='mission_id.intervenant_id',
        string='Intervenant',
        store=True,
    )
    client_id = fields.Many2one(
        related='mission_id.client_id',
        string='Client',
        store=True,
    )

    date_devis = fields.Datetime(
        string='Date Devis',
        default=fields.Datetime.now,
    )
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('envoye', 'Envoyé au Client'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ], string='État', default='brouillon', tracking=True)

    # ─── Lignes de devis ─────────────────────────────────────────────
    ligne_ids = fields.One2many('sinistre.devis.ligne', 'devis_id', string='Lignes')

    # ─── Totaux ──────────────────────────────────────────────────────
    currency_id = fields.Many2one(
        related='mission_id.currency_id',
        string='Devise',
    )
    montant_ht = fields.Monetary(
        string='Montant HT',
        compute='_compute_montants',
        store=True,
        currency_field='currency_id',
    )
    tva = fields.Float(string='TVA (%)', default=20.0)
    montant_tva = fields.Monetary(
        string='Montant TVA',
        compute='_compute_montants',
        store=True,
        currency_field='currency_id',
    )
    montant_total = fields.Monetary(
        string='Total TTC',
        compute='_compute_montants',
        store=True,
        currency_field='currency_id',
    )

    note_client = fields.Text(string='Note pour le Client')
    motif_refus = fields.Text(string='Motif du Refus')

    # ─── Signature client ────────────────────────────────────────────
    signature_client = fields.Binary(string='Signature Client')
    date_signature = fields.Datetime(string='Date de Signature')

    @api.depends('ligne_ids', 'ligne_ids.montant_total', 'tva')
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
        self.ensure_one()
        if not self.ligne_ids:
            raise UserError(_("Ajoutez au moins une ligne au devis avant d'envoyer."))
        self.write({'state': 'envoye'})
        self.mission_id.write({'state': 'devis_envoye'})

    def action_accepter(self):
        self.ensure_one()
        self.write({
            'state': 'accepte',
            'date_signature': fields.Datetime.now(),
        })
        self.mission_id.write({'state': 'devis_accepte'})

    def action_refuser(self):
        self.ensure_one()
        self.write({'state': 'refuse'})
        self.mission_id.write({'state': 'devis_refuse'})


class SinistreDevisLigne(models.Model):
    """Ligne de devis : prestation ou fourniture."""
    _name = 'sinistre.devis.ligne'
    _description = 'Ligne de Devis'

    devis_id = fields.Many2one('sinistre.devis', string='Devis', ondelete='cascade')
    sequence = fields.Integer(string='Séquence', default=10)

    description = fields.Char(string='Description', required=True)
    quantite = fields.Float(string='Quantité', default=1.0)
    unite = fields.Char(string='Unité', default='forfait')
    prix_unitaire = fields.Monetary(
        string='Prix Unitaire',
        currency_field='currency_id',
    )
    montant_total = fields.Monetary(
        string='Total',
        compute='_compute_total',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='devis_id.currency_id',
    )

    @api.depends('quantite', 'prix_unitaire')
    def _compute_total(self):
        for rec in self:
            rec.montant_total = rec.quantite * rec.prix_unitaire
