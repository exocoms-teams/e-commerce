# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    exocoms_activation_ttl_hours = fields.Integer(
        string="Validité du lien d'activation (heures)",
        default=24,
        config_parameter='exocoms_signup_activation.token_ttl_hours',
        help="Durée au-delà de laquelle le lien d'activation n'est plus valable.")
    exocoms_activation_purge_days = fields.Integer(
        string="Purge des inscriptions non activées (jours)",
        default=7,
        config_parameter='exocoms_signup_activation.purge_days',
        help="Les comptes jamais activés sont supprimés après ce délai. "
             "Mettre 0 pour désactiver la purge.")
    exocoms_activation_resend_interval = fields.Integer(
        string="Délai minimum entre deux envois (secondes)",
        default=120,
        config_parameter='exocoms_signup_activation.resend_interval')
    exocoms_activation_max_resend = fields.Integer(
        string="Nombre maximum d'emails d'activation",
        default=5,
        config_parameter='exocoms_signup_activation.max_resend',
        help="Nombre maximum d'envois pour une même inscription. "
             "Mettre 0 pour ne pas limiter.")
    exocoms_activation_reveal_pending = fields.Boolean(
        string="Signaler « compte non activé » à la connexion",
        default=True,
        config_parameter='exocoms_signup_activation.reveal_pending',
        help="Affiche un message explicite et un bouton de renvoi lorsqu'un "
             "visiteur tente de se connecter avec un compte non activé.\n"
             "Décochez cette option si vous souhaitez éviter toute confirmation "
             "de l'existence d'une adresse email (énumération de comptes).")
