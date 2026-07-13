# -*- coding: utf-8 -*-
from odoo import fields, models


class MatelasAvis(models.Model):
    """Avis clients laissés sur le site (page /avis). 
    """
    _name = 'matelas.avis'
    _description = "Avis client"
    _order = 'create_date desc'

    name = fields.Char(string="Nom / Pseudonyme", required=True)
    note = fields.Integer(string="Note (sur 5)", required=True)
    titre = fields.Char(string="Titre / Produit")
    commentaire = fields.Text(string="Commentaire", required=True)
    partner_id = fields.Many2one('res.partner', string="Client")
    is_published = fields.Boolean(string="Publié", default=True)
