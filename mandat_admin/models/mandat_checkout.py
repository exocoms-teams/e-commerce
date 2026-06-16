# -*- coding: utf-8 -*-
from odoo import fields, models

class SaleOrderMandatCheckout(models.Model):
    _inherit = 'sale.order'

    mandat_checkout_siret = fields.Char('SIRET acheteur public')
    mandat_checkout_iban = fields.Char('IBAN')
    mandat_checkout_ordonnateur = fields.Char('Ordonnateur')
    mandat_checkout_qualite = fields.Char("Qualité de l'ordonnateur")
    mandat_checkout_comptable = fields.Char('Comptable public assignataire')
    mandat_checkout_ej = fields.Char("N° d'engagement juridique (EJ)")
    mandat_checkout_service = fields.Char('Service / Direction')
    mandat_checkout_reference = fields.Char('Référence bon de commande')
    mandat_checkout_filled = fields.Boolean('Formulaire mandat rempli', default=False)
