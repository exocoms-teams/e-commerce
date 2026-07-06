# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_mandat_administratif = fields.Boolean(
        'Facture sous mandat administratif', default=False, copy=False)
    mandat_numero           = fields.Char('N° de mandat', copy=False)
    mandat_sale_order_id    = fields.Many2one(
        'sale.order', 'BCA source', copy=False,
        domain=[('is_mandat_administratif', '=', True)])

    # Champs engagement repris du BCA
    numero_engagement       = fields.Char('N° engagement juridique')
    acheteur_siret          = fields.Char('SIRET acheteur public')
    reference_bon_commande  = fields.Char('Référence BCA organisme')
    ordonnateur             = fields.Char('Ordonnateur')
    qualite_ordonnateur     = fields.Char("Qualité de l'ordonnateur")
    comptable_public        = fields.Char('Comptable public assignataire')
    structure_chorus        = fields.Char('Structure Chorus Pro')
    service_chorus          = fields.Char('Code service Chorus Pro')

    # Dates
    date_mandatement = fields.Date('Date de mandatement', copy=False)
    date_pec         = fields.Date('Date de prise en charge', copy=False)

    # Service fait
    service_fait_certifie = fields.Boolean('Service fait certifié', copy=False)
    date_service_fait     = fields.Date('Date du service fait', copy=False)
    certificateur_sf      = fields.Char('Certifié par', copy=False)

    # Sous-objets
    imputation_ids = fields.One2many(
        'mandat.imputation', 'invoice_id', 'Imputations budgétaires')
    pj_ids = fields.One2many(
        'mandat.pj', 'invoice_id', 'Pièces justificatives')

    # Chorus
    statut_chorus = fields.Selection([
        ('non_envoye', 'Non envoyé'), ('depose',  'Déposé'),
        ('en_cours',   'En cours'),   ('integre', 'Intégré'),
        ('rejete',     'Rejeté'),
    ], default='non_envoye', copy=False)
    numero_chorus = fields.Char('N° dépôt Chorus', copy=False)

    # Bordereaux
    bordereau_ids = fields.Many2many(
        'mandat.bordereau',
        'bordereau_invoice_rel', 'invoice_id', 'bordereau_id',
        string='Bordereaux')

    @api.onchange('mandat_sale_order_id')
    def _onchange_bca_source(self):
        so = self.mandat_sale_order_id
        if so:
            self.is_mandat_administratif = True
            self.mandat_numero           = so.mandat_numero
            self.numero_engagement       = so.numero_engagement
            self.acheteur_siret          = so.acheteur_siret
            self.reference_bon_commande  = so.reference_bon_commande
            self.ordonnateur             = so.ordonnateur
            self.qualite_ordonnateur     = so.qualite_ordonnateur
            self.comptable_public        = so.comptable_public
            self.structure_chorus        = so.structure_chorus
            self.service_chorus          = so.service_chorus
            self.service_fait_certifie   = so.service_fait_certifie
            self.date_service_fait       = so.date_service_fait
            self.certificateur_sf        = so.certificateur_service_fait
