# -*- coding: utf-8 -*-
from odoo import fields, models

PREFIX = 'exocoms_portal_signup.'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    exocoms_check_mx = fields.Boolean(
        string="Vérifier que le domaine reçoit des emails",
        config_parameter=PREFIX + 'check_mx', default=True,
        help="Interroge les enregistrements DNS du domaine. Sans effet si la "
             "bibliothèque dnspython n'est pas disponible : l'inscription "
             "n'est alors jamais bloquée pour cette raison.")
    exocoms_block_disposable = fields.Boolean(
        string="Refuser les adresses jetables",
        config_parameter=PREFIX + 'block_disposable', default=True)
    exocoms_restrict_allowed = fields.Boolean(
        string="Limiter aux domaines autorisés",
        config_parameter=PREFIX + 'restrict_allowed', default=False,
        help="N'accepte que les domaines marqués « Autorisé ». Sans effet tant "
             "qu'aucun domaine autorisé n'est enregistré.")
    exocoms_token_ttl_hours = fields.Integer(
        string="Validité du lien (heures)",
        config_parameter=PREFIX + 'token_ttl_hours', default=24)
    exocoms_purge_days = fields.Integer(
        string="Purge des inscriptions non activées (jours)",
        config_parameter=PREFIX + 'purge_days', default=7,
        help="0 désactive la purge : les comptes en attente sont conservés.")
    exocoms_resend_interval = fields.Integer(
        string="Délai minimum entre deux envois (secondes)",
        config_parameter=PREFIX + 'resend_interval', default=120)
    exocoms_max_resend = fields.Integer(
        string="Nombre maximum d'emails d'activation",
        config_parameter=PREFIX + 'max_resend', default=5,
        help="0 pour un nombre illimité.")
    exocoms_reveal_pending = fields.Boolean(
        string="Signaler « compte non activé » à la connexion",
        config_parameter=PREFIX + 'reveal_pending', default=True,
        help="Décoché, un échec de connexion sur un compte en attente affiche "
             "le message générique d'Odoo : l'existence de l'adresse n'est "
             "jamais confirmée à un tiers.")
