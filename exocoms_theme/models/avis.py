# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ExocomsAvis(models.Model):
    """Avis client déposés depuis le formulaire public /avis.
    Scopé par website_id — OBLIGATOIRE sur cette base partagée à
    plusieurs sites (même logique que product.public.category,
    website.menu, etc. dans __init__.py) : sans ce champ, les avis
    d'un site s'afficheraient sur tous les autres."""
    _name = 'exocoms.avis'
    _description = "Avis client (Exocoms)"
    _order = 'date desc, id desc'

    name = fields.Char(string="Nom", required=True)
    rating = fields.Integer(string="Note (1 à 5)", required=True, default=5)
    comment = fields.Text(string="Commentaire", required=True)
    product = fields.Char(string="Produit acheté")
    date = fields.Date(string="Date", default=lambda self: fields.Date.context_today(self))
    state = fields.Selection([
        ('pending', "En attente de validation"),
        ('published', "Publié"),
    ], string="Statut", default='pending', required=True)
    website_id = fields.Many2one(
        'website', string="Site", required=True,
        default=lambda self: self.env['website'].get_current_website(),
    )

    @api.constrains('rating')
    def _check_rating(self):
        for rec in self:
            if rec.rating < 1 or rec.rating > 5:
                raise ValidationError("La note doit être comprise entre 1 et 5.")
