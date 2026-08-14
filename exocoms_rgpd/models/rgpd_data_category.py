# -*- coding: utf-8 -*-
from odoo import fields, models


class RgpdDataCategory(models.Model):
    """Catégories de données personnelles traitées (art. 30.1.c)."""

    _name = "exocoms.rgpd.data.category"
    _description = "RGPD - Catégorie de données personnelles"
    _order = "sensitive desc, sequence, name"

    name = fields.Char(string="Catégorie", required=True, translate=True)
    sequence = fields.Integer(default=10)
    code = fields.Char(string="Code technique")
    description = fields.Text(string="Description", translate=True)
    sensitive = fields.Boolean(
        string="Donnée sensible",
        help="Catégorie particulière au sens de l'article 9 du RGPD "
        "(santé, origine, opinions, biométrie, orientation sexuelle...) "
        "ou données relatives aux condamnations pénales (art. 10).",
    )
    color = fields.Integer(string="Couleur")
    active = fields.Boolean(default=True)

    _rgpd_data_category_name_uniq = models.Constraint(
        "unique(name)",
        "Cette catégorie de données existe déjà.",
    )
