# -*- coding: utf-8 -*-
from odoo import fields, models


class MatelasContactMessage(models.Model):
    """Message envoyé depuis le formulaire de contact du site."""

    _name = 'matelas.contact_message'
    _description = "Message de contact"
    _order = 'create_date desc'
    _rec_name = 'email'

    nom = fields.Char(string="Nom", required=True)
    prenom = fields.Char(string="Prénom", required=True)
    email = fields.Char(string="Email", required=True)
    telephone = fields.Char(string="Téléphone")
    sujet = fields.Char(string="Sujet")
    message = fields.Text(string="Message", required=True)
