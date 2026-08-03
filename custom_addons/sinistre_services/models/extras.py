# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SinistreConsommable(models.Model):
    _name = 'sinistre.consommable'
    _description = 'Consommable mission'
    _order = 'id desc'

    mission_id = fields.Many2one('sinistre.mission', required=True, ondelete='cascade')
    intervenant_id = fields.Many2one(related='mission_id.intervenant_id', store=True)
    designation = fields.Char(string='Désignation', required=True)
    quantite = fields.Float(default=1.0)
    unite = fields.Char(default='pièce')
    commande_fournisseur = fields.Boolean(string='Commande fournisseur', default=False)
    fournisseur = fields.Char(string='Fournisseur')
    reference_commande = fields.Char(string='Réf. commande')
    state = fields.Selection([
        ('a_commander', 'À commander'),
        ('commande', 'Commandé'),
        ('recu', 'Reçu'),
    ], default='a_commander')
    note = fields.Text()


class SinistrePenseBete(models.Model):
    _name = 'sinistre.pense_bete'
    _description = 'Pense-bête artisan'
    _order = 'date_creation desc'

    mission_id = fields.Many2one('sinistre.mission', ondelete='cascade')
    intervenant_id = fields.Many2one('sinistre.intervenant', required=True, ondelete='cascade')
    contenu = fields.Char(required=True)
    fait = fields.Boolean(default=False)
    date_creation = fields.Datetime(default=fields.Datetime.now)
    date_fait = fields.Datetime()


class SinistreAvis(models.Model):
    _name = 'sinistre.avis'
    _description = 'Avis client sur artisan'
    _order = 'date_avis desc'

    mission_id = fields.Many2one('sinistre.mission', required=True, ondelete='cascade')
    intervenant_id = fields.Many2one(related='mission_id.intervenant_id', store=True)
    client_id = fields.Many2one(related='mission_id.client_id', store=True)
    note = fields.Integer(string='Note', required=True)
    commentaire = fields.Text()
    date_avis = fields.Datetime(default=fields.Datetime.now)

    @api.constrains('note')
    def _check_note(self):
        for rec in self:
            if rec.note < 1 or rec.note > 5:
                raise ValidationError(_("La note doit être comprise entre 1 et 5."))
