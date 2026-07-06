# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_public_entity = fields.Boolean(
        string="Entité publique (mandat administratif)",
        help="Administration, collectivité territoriale ou établissement public réglant par mandat administratif. "
             "Active le mode de paiement au checkout et le bloc Chorus Pro.",
    )
    nature_juridique = fields.Selection([
        ('etat',        'État'),
        ('region',      'Région'),
        ('departement', 'Département'),
        ('commune',     'Commune'),
        ('epci',        'EPCI / Intercommunalité'),
        ('hopital',     'Hôpital / EHPAD (M22)'),
        ('universite',  "Université / École (M9)"),
        ('sdis',        'SDIS'),
        ('autre',       'Autre organisme public'),
    ], string='Nature juridique', default='commune')
    nomenclature_budgetaire = fields.Selection([
        ('M14', 'M14 – Communes et groupements'),
        ('M57', 'M57 – Collectivités (nouveau régime)'),
        ('M22', 'M22 – Établissements hospitaliers'),
        ('M9',  "M9 – Établissements d'enseignement"),
        ('M4',  'M4 – Services industriels et commerciaux'),
        ('M52', 'M52 – Départements'),
        ('M71', 'M71 – Régions'),
    ], string='Nomenclature budgétaire', default='M14')

    siret_public      = fields.Char('SIRET public (14 chiffres)', size=14)
    chorus_service_code = fields.Char('Code service (Chorus Pro)')
    code_tiers_chorus = fields.Char('Code tiers Chorus Pro')
    structure_chorus  = fields.Char('Structure Chorus Pro (SIRET)')
    chorus_engagement_required = fields.Boolean("Engagement juridique obligatoire")
    service_public    = fields.Char('Service / Direction émetteur')
    comptable_public  = fields.Char('Comptable public / Trésorerie assignataire')
    regime_tva_public = fields.Selection([
        ('non_assujetti',     'Non assujetti'),
        ('assujetti_partiel', 'Assujetti partiel'),
        ('assujetti_total',   'Assujetti total'),
        ('fctva',             'FCTVA'),
    ], string='Régime TVA public', default='non_assujetti')

    @api.constrains('siret_public')
    def _check_siret_public(self):
        for p in self:
            if p.siret_public:
                s = re.sub(r'\s', '', p.siret_public)
                if not (s.isdigit() and len(s) == 14):
                    raise ValidationError(_("Le SIRET doit contenir exactement 14 chiffres."))
                if not s.startswith('356000000') and not _luhn_valid(s):
                    raise ValidationError(_("Le SIRET « %s » est invalide (clé de contrôle incorrecte).", s))
