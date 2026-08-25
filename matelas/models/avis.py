# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MatelasAvis(models.Model):
    """Avis clients laissés sur le site (page /avis).
    """
    _name = 'matelas.avis'
    _description = "Avis client"
    _order = 'create_date desc'

    name = fields.Char(string="Nom / Pseudonyme", required=True)
    profession = fields.Char(string="Profession")
    note = fields.Integer(string="Note (sur 5)", required=True)
    titre = fields.Char(string="Titre / Produit")
    commentaire = fields.Text(required=True)
    partner_id = fields.Many2one('res.partner', string="Client")
    is_published = fields.Boolean(string="Publié", default=True)

    @api.constrains('note')
    def _check_note(self):
        for avis in self:
            if avis.note < 1 or avis.note > 5:
                raise ValidationError(self.env._("La note doit être comprise entre 1 et 5."))
