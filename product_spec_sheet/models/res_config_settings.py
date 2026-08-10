# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_spec_anthropic_api_key = fields.Char(
        string="Clé API Anthropic",
        config_parameter="product_spec_sheet.anthropic_api_key",
        help="Améliore la précision de la récupération automatique des caractéristiques.",
    )
    product_spec_autofetch_enabled = fields.Boolean(
        string="Récupération automatique planifiée",
        config_parameter="product_spec_sheet.autofetch_enabled",
        help="Complète chaque nuit les fiches produit incomplètes.",
    )
    product_spec_autofetch_batch = fields.Integer(
        string="Produits par exécution",
        config_parameter="product_spec_sheet.autofetch_batch",
        default=20,
        help="Nombre de produits traités à chaque passage. "
             "Une valeur élevée allonge la durée d'exécution.",
    )
    product_spec_autofetch_published_only = fields.Boolean(
        string="Limiter aux produits publiés",
        config_parameter="product_spec_sheet.autofetch_published_only",
        default=True,
    )
    product_spec_autofetch_notify_uid = fields.Many2one(
        "res.users",
        string="Notifier",
        config_parameter="product_spec_sheet.autofetch_notify_uid",
        help="Utilisateur averti du résultat de chaque exécution.",
    )
