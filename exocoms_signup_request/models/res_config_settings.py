# -*- coding: utf-8 -*-
from odoo import fields, models

PREFIX = 'exocoms_signup_request.'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    exocoms_block_disposable = fields.Boolean(
        string="Refuser les adresses jetables",
        config_parameter=PREFIX + 'block_disposable', default=True)
    exocoms_check_mx = fields.Boolean(
        string="Vérifier le domaine (DNS)",
        config_parameter=PREFIX + 'check_mx', default=True,
        help="Sans effet si la bibliothèque dnspython n'est pas installée : "
             "la demande n'est alors jamais bloquée pour cette raison.")
    exocoms_restrict_allowed = fields.Boolean(
        string="Limiter aux domaines autorisés",
        config_parameter=PREFIX + 'restrict_allowed', default=False,
        help="Sans effet tant qu'aucun domaine autorisé n'est enregistré.")

    exocoms_token_ttl_hours = fields.Integer(
        string="Validité du lien (heures)",
        config_parameter=PREFIX + 'token_ttl_hours', default=24)
    exocoms_resend_interval = fields.Integer(
        string="Délai entre deux envois (secondes)",
        config_parameter=PREFIX + 'resend_interval', default=120)
    exocoms_max_resend = fields.Integer(
        string="Nombre maximum d'emails",
        config_parameter=PREFIX + 'max_resend', default=5,
        help="0 pour un nombre illimité.")

    exocoms_max_per_ip = fields.Integer(
        string="Demandes maximum par origine",
        config_parameter=PREFIX + 'max_per_ip', default=5,
        help="Plafonne le nombre de demandes déposées depuis une même "
             "connexion sur la période ci-dessous. 0 désactive le "
             "plafonnement.")
    exocoms_ip_window_minutes = fields.Integer(
        string="Période du plafond (minutes)",
        config_parameter=PREFIX + 'ip_window_minutes', default=60)

    exocoms_keep_expired_days = fields.Integer(
        string="Conserver les demandes expirées (jours)",
        config_parameter=PREFIX + 'keep_expired_days', default=7,
        help="0 conserve indéfiniment.")
    exocoms_keep_confirmed_days = fields.Integer(
        string="Conserver les demandes confirmées (jours)",
        config_parameter=PREFIX + 'keep_confirmed_days', default=30,
        help="Le compte créé n'est jamais concerné : seule la trace de la "
             "demande est supprimée. 0 conserve indéfiniment.")
    exocoms_keep_rejected_days = fields.Integer(
        string="Conserver les demandes refusées (jours)",
        config_parameter=PREFIX + 'keep_rejected_days', default=3,
        help="0 conserve indéfiniment.")
