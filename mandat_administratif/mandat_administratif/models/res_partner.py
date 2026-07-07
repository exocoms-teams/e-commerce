# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_public_entity = fields.Boolean(
        string="Entité publique (mandat administratif)",
        help="Administration, collectivité territoriale ou établissement "
             "public réglant par mandat administratif. Active le mode de "
             "paiement « Mandat administratif » au checkout et le bloc "
             "Chorus Pro sur les factures.",
    )
    chorus_siret = fields.Char(
        string="SIRET destinataire (Chorus Pro)",
        size=14,
        help="SIRET de la structure publique destinataire de la facture "
             "sur Chorus Pro (14 chiffres).",
    )
    chorus_service_code = fields.Char(
        string="Code service (Chorus Pro)",
        help="Code service exécutant tel que paramétré sur Chorus Pro "
             "(obligatoire pour certaines structures, ex. FACTURES_PUBLIQUES).",
    )
    chorus_engagement_required = fields.Boolean(
        string="Engagement juridique obligatoire",
        help="La structure exige un numéro d'engagement juridique (bon de "
             "commande) pour accepter la facture sur Chorus Pro.",
    )

    @api.constrains('chorus_siret')
    def _check_chorus_siret(self):
        for partner in self.filtered('chorus_siret'):
            siret = partner.chorus_siret.replace(' ', '')
            if not (siret.isdigit() and len(siret) == 14):
                raise ValidationError(
                    _("Le SIRET Chorus Pro doit comporter exactement "
                      "14 chiffres.")
                )
            # Exception La Poste : les SIRET commençant par 356000000
            # ne respectent pas la clé de Luhn.
            if not siret.startswith('356000000') and not self._luhn_valid(siret):
                raise ValidationError(
                    _("Le SIRET Chorus Pro « %s » est invalide "
                      "(clé de contrôle incorrecte).", siret)
                )

    @staticmethod
    def _luhn_valid(number):
        total = 0
        for i, digit in enumerate(reversed(number)):
            d = int(digit)
            if i % 2 == 1:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        return total % 10 == 0
