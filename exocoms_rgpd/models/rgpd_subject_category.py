# -*- coding: utf-8 -*-
from odoo import fields, models


class RgpdSubjectCategory(models.Model):
    """Catégories de personnes concernées (art. 30.1.c)."""

    _name = "exocoms.rgpd.subject.category"
    _description = "RGPD - Catégorie de personnes concernées"
    _order = "sequence, name"

    name = fields.Char(string="Catégorie", required=True, translate=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(string="Description", translate=True)
    minor = fields.Boolean(
        string="Inclut des mineurs",
        help="Déclenche des obligations renforcées (art. 8 du RGPD).",
    )
    active = fields.Boolean(default=True)

    _rgpd_subject_category_name_uniq = models.Constraint(
        "unique(name)",
        "Cette catégorie de personnes existe déjà.",
    )
