# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mandat_ordonnateur_id = fields.Many2one(
        'res.partner',
        string='Ordonnateur par défaut',
        config_parameter='mandat_administratif.ordonnateur_id',
    )
    mandat_comptable_id = fields.Many2one(
        'res.partner',
        string='Comptable public par défaut',
        config_parameter='mandat_administratif.comptable_id',
    )
    mandat_delai_paiement = fields.Integer(
        string='Délai de paiement (jours)',
        default=30,
        config_parameter='mandat_administratif.delai_paiement',
        help="Délai réglementaire de paiement des mandats (30 jours par défaut).",
    )
    mandat_nomenclature = fields.Selection(
        [
            ('m14', 'M14 - Communes'),
            ('m57', 'M57 - Collectivités'),
            ('m4', 'M4 - Services industriels'),
            ('m9', 'M9 - Établissements d\'enseignement'),
            ('m21', 'M21 - Établissements hospitaliers'),
        ],
        string='Nomenclature comptable',
        default='m57',
        config_parameter='mandat_administratif.nomenclature',
    )
