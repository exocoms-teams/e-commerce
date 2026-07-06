# -*- coding: utf-8 -*-
from odoo import fields, models


class MandatImputation(models.Model):
    _name        = 'mandat.imputation'
    _description = 'Imputation budgétaire (mandat administratif)'

    name          = fields.Char('Libellé', required=True)
    sale_order_id = fields.Many2one('sale.order', ondelete='cascade')
    invoice_id    = fields.Many2one('account.move', ondelete='cascade')

    section = fields.Selection([
        ('fonctionnement', 'Section de fonctionnement'),
        ('investissement',  "Section d'investissement"),
    ], required=True, default='fonctionnement')

    chapitre      = fields.Char('Chapitre', required=True)
    article       = fields.Char('Article',  required=True)
    sous_article  = fields.Char('Sous-article')
    operation     = fields.Char('Opération / Fonction')
    exercice      = fields.Char('Exercice', default=lambda self: str(fields.Date.today().year))

    montant_engage  = fields.Monetary('Montant engagé',  currency_field='currency_id')
    montant_mandate = fields.Monetary('Montant mandaté', currency_field='currency_id')
    credit_ouvert   = fields.Monetary('Crédit ouvert',   currency_field='currency_id')
    disponible      = fields.Monetary('Disponible',      currency_field='currency_id')
    currency_id     = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    visa_controleur = fields.Char('Réf. visa contrôleur budgétaire')
    date_visa       = fields.Date('Date du visa')
