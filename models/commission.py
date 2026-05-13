# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SinistreCommission(models.Model):
    """
    Suivi des commissions dues par les intervenants à la plateforme.
    Générées automatiquement à la clôture d'une mission.
    """
    _name = 'sinistre.commission'
    _description = 'Commission Plateforme'
    _inherit = ['mail.thread']

    name = fields.Char(string='Référence', required=True, default='/')
    mission_id = fields.Many2one('sinistre.mission', string='Mission', required=True)
    intervenant_id = fields.Many2one(
        related='mission_id.intervenant_id',
        store=True,
        string='Intervenant',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    montant_intervention = fields.Monetary(
        string='Montant Intervention',
        currency_field='currency_id',
    )
    taux_commission = fields.Float(string='Taux (%)')
    montant_commission = fields.Monetary(
        string='Commission',
        currency_field='currency_id',
    )
    state = fields.Selection([
        ('due', 'Due'),
        ('facturee', 'Facturée'),
        ('payee', 'Payée'),
    ], default='due', tracking=True)
    date_echeance = fields.Date(string="Date d'Échéance")
    facture_id = fields.Many2one('account.move', string='Facture Commission')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('sinistre.commission') or '/'
        return super().create(vals_list)
