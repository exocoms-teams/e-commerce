# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CapsuleHouseAvis(models.Model):
    """Avis client déposés depuis le formulaire public /avis.

    Reprend le mécanisme observé sur exocoms_theme (models/avis.py) :
    plutôt qu'un simple chiffre fixe en dur (ir.config_parameter
    'capsule_house_theme.rating_value'), on stocke de VRAIS avis
    soumis par de vrais clients, modérés avant publication, et la note
    moyenne/le nombre d'avis affichés partout (badge du hero, page
    /avis) sont calculés dynamiquement à partir de ces enregistrements
    réels — jamais fabriqués.

    Scopé par website_id — OBLIGATOIRE sur cette base mutualisée
    (~17 sites sur la même instance) : sans ce champ, les avis de
    Capsule House s'afficheraient sur tous les autres sites (même
    logique que product.public.category, website.menu, ir.ui.view
    ailleurs dans ce module). website_id est posé explicitement par le
    contrôleur (request.website.id) à la création, jamais par un
    default implicite `get_current_website()` — cohérent avec le reste
    du module qui ne fait jamais confiance à une résolution implicite
    du site sur une base partagée.
    """
    _name = 'capsule.house.avis'
    _description = "Avis client (Capsule House)"
    _order = 'date desc, id desc'

    name = fields.Char(string="Nom", required=True)
    rating = fields.Integer(string="Note (1 à 5)", required=True, default=5)
    comment = fields.Text(string="Commentaire", required=True)
    product = fields.Char(string="Modèle acheté")
    date = fields.Date(string="Date", default=lambda self: fields.Date.context_today(self))
    state = fields.Selection([
        ('pending', "En attente de validation"),
        ('published', "Publié"),
    ], string="Statut", default='pending', required=True)
    website_id = fields.Many2one(
        'website', string="Site", required=True,
    )

    @api.constrains('rating')
    def _check_rating(self):
        for rec in self:
            if rec.rating < 1 or rec.rating > 5:
                raise ValidationError("La note doit être comprise entre 1 et 5.")
