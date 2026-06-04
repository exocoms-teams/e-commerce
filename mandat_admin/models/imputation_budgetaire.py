# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ImputationBudgetaire(models.Model):
    _name = 'imputation.budgetaire'
    _description = 'Imputation Budgétaire'
    _order = 'mandat_id, chapitre, article'

    mandat_id = fields.Many2one(
        'mandat.administratif',
        string='Mandat',
        required=True,
        ondelete='cascade',
    )
    chapitre = fields.Char(string='Chapitre', required=True)
    article = fields.Char(string='Article', required=True)
    rubrique = fields.Char(string='Rubrique')
    fonction = fields.Char(string='Fonction / Programme')
    libelle = fields.Char(string='Libellé budgétaire')

    credit_ouvert = fields.Monetary(
        string='Crédit ouvert',
        currency_field='currency_id',
        help='Crédit budgétaire disponible sur cette imputation',
    )
    credit_engage = fields.Monetary(
        string='Crédit engagé',
        currency_field='currency_id',
    )
    montant_impute = fields.Monetary(
        string='Montant imputé',
        currency_field='currency_id',
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.EUR'),
    )
    credit_disponible = fields.Monetary(
        string='Crédit disponible',
        currency_field='currency_id',
        compute='_compute_credit_disponible',
        store=True,
    )
    compte_pcg = fields.Char(
        string='Compte PCG',
        help='Compte du Plan Comptable Général associé',
    )
    display_name = fields.Char(
        string='Nom affiché',
        compute='_compute_display_name',
        store=True,
    )

    @api.depends('chapitre', 'article', 'rubrique')
    def _compute_display_name(self):
        for rec in self:
            name = f'{rec.chapitre}/{rec.article}' if rec.chapitre and rec.article else ''
            if rec.rubrique:
                name += f'/{rec.rubrique}'
            rec.display_name = name or '/'

    @api.depends('credit_ouvert', 'credit_engage')
    def _compute_credit_disponible(self):
        for rec in self:
            rec.credit_disponible = rec.credit_ouvert - rec.credit_engage

    @api.constrains('montant_impute', 'credit_disponible')
    def _check_disponibilite_credits(self):
        for rec in self:
            if (rec.credit_disponible > 0 and
                    rec.montant_impute > rec.credit_disponible):
                raise ValidationError(_(
                    'Crédit insuffisant sur l\'imputation %s/%s. '
                    'Disponible : %.2f € – Demandé : %.2f €'
                ) % (rec.chapitre, rec.article,
                     rec.credit_disponible, rec.montant_impute))
