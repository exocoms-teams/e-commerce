# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    mandat_ids = fields.One2many(
        'mandat.administratif',
        'invoice_id',
        string='Mandats administratifs',
    )
    mandat_count = fields.Integer(
        string='Nombre de mandats',
        compute='_compute_mandat_count',
    )

    def _compute_mandat_count(self):
        for rec in self:
            rec.mandat_count = len(rec.mandat_ids)

    def action_voir_mandats(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mandats administratifs',
            'res_model': 'mandat.administratif',
            'view_mode': 'list,form',
            'domain': [('invoice_id', '=', self.id)],
            'context': {'default_invoice_id': self.id},
        }

    def action_creer_mandat(self):
        """Crée un mandat à partir de la facture"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Créer un mandat administratif',
            'res_model': 'mandat.administratif',
            'view_mode': 'form',
            'context': {
                'default_invoice_id': self.id,
                'default_creancier_id': self.partner_id.id,
                'default_montant_ht': self.amount_untaxed,
                'default_montant_tva': self.amount_tax,
            },
        }
