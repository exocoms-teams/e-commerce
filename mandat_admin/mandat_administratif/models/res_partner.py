# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_organisme_public = fields.Boolean(
        string='Organisme public (MA)',
        default=False,
        help='Cocher pour activer le mode Mandat Administratif sur ce partenaire.',
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

    siret_public     = fields.Char('SIRET public (14 chiffres)', size=14)
    code_collectivite= fields.Char('Code collectivité INSEE')
    service_public   = fields.Char('Service / Direction émetteur')
    comptable_public = fields.Char('Comptable public / Trésorerie assignataire')
    iban_comptable   = fields.Char('IBAN comptable public (DFT)')

    # Chorus Pro
    code_tiers_chorus  = fields.Char('Code tiers Chorus Pro')
    structure_chorus   = fields.Char('Structure Chorus Pro (SIRET)')
    service_chorus     = fields.Char('Code service Chorus Pro')

    # Régime TVA
    regime_tva_public = fields.Selection([
        ('non_assujetti',     'Non assujetti'),
        ('assujetti_partiel', 'Assujetti partiel (prorata)'),
        ('assujetti_total',   'Assujetti total'),
        ('fctva',             'FCTVA'),
    ], string='Régime TVA public', default='non_assujetti')

    taux_prorata_tva = fields.Float('Prorata TVA (%)', digits=(5, 2))

    @api.constrains('siret_public')
    def _check_siret(self):
        for p in self:
            if p.siret_public:
                s = re.sub(r'\s', '', p.siret_public)
                if not s.isdigit() or len(s) != 14:
                    raise ValidationError(_('Le SIRET doit contenir exactement 14 chiffres.'))
