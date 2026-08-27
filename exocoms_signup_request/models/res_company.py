# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Les réglages généraux vivent dans ir.config_parameter, qui n'a pas de
    # dimension société. Ces champs permettent de déroger à la règle globale
    # pour une société donnée : laissés vides ou à zéro, la valeur générale
    # continue de s'appliquer.

    exocoms_signup_override = fields.Boolean(
        string="Politique d'inscription propre",
        help="Active les valeurs ci-dessous pour cette société. Décoché, les "
             "réglages généraux s'appliquent.")
    exocoms_token_ttl_hours = fields.Integer(
        string="Validité du lien (heures)",
        help="0 conserve la valeur générale.")
    exocoms_max_per_ip = fields.Integer(
        string="Demandes maximum par origine",
        help="0 conserve la valeur générale.")
    exocoms_block_disposable = fields.Selection(
        [('inherit', "Réglage général"),
         ('yes', "Refuser"),
         ('no', "Accepter")],
        string="Adresses jetables", default='inherit', required=True)
    exocoms_check_mx = fields.Selection(
        [('inherit', "Réglage général"),
         ('yes', "Vérifier"),
         ('no', "Ne pas vérifier")],
        string="Contrôle DNS", default='inherit', required=True)
    exocoms_restrict_allowed = fields.Selection(
        [('inherit', "Réglage général"),
         ('yes', "Limiter"),
         ('no', "Ne pas limiter")],
        string="Domaines autorisés", default='inherit', required=True)

    def _exocoms_int_override(self, field_name):
        """Valeur entière propre à la société, ou ``None`` si elle hérite."""
        self.ensure_one()
        if not self.exocoms_signup_override:
            return None
        value = self[field_name]
        return value if value and value > 0 else None

    def _exocoms_bool_override(self, field_name):
        """Valeur booléenne propre à la société, ou ``None`` si elle hérite."""
        self.ensure_one()
        if not self.exocoms_signup_override:
            return None
        value = self[field_name]
        if value == 'yes':
            return True
        if value == 'no':
            return False
        return None
