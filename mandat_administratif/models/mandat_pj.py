# -*- coding: utf-8 -*-
from odoo import fields, models


class MandatPJ(models.Model):
    """Pièces justificatives – Décret n°2016-33 du 20 janvier 2016."""
    _name        = 'mandat.pj'
    _description = 'Pièce justificative – mandat administratif'
    _order       = 'sequence, id'

    sale_order_id = fields.Many2one('sale.order',       ondelete='cascade')
    invoice_id    = fields.Many2one('account.move',     ondelete='cascade')
    payment_id    = fields.Many2one('account.payment',  ondelete='cascade')
    sequence      = fields.Integer(default=10)

    type_pj = fields.Selection([
        ('bon_commande',        'Bon de commande signé'),
        ('devis_accepte',       'Devis accepté / offre'),
        ('facture',             'Facture ou mémoire du créancier'),
        ('service_fait',        'Certification du service fait'),
        ('rib_fournisseur',     'RIB / IBAN du fournisseur certifié'),
        ('marche_public',       "Acte d'engagement du marché public"),
        ('pv_reception',        'PV de réception'),
        ('bpu_dqe',             'BPU / DQE / Décomposition du prix'),
        ('situation_travaux',   'Situation de travaux'),
        ('retenue_garantie',    'Mainlevée retenue de garantie'),
        ('convention',          'Convention ou contrat'),
        ('deliberation',        "Délibération de l'organe délibérant"),
        ('rapport_activite',    "Rapport d'activité / compte rendu"),
        ('attestation_fiscale', 'Attestation fiscale et sociale (DC7)'),
        ('extrait_kbis',        'Extrait Kbis ou équivalent'),
        ('autre',               'Autre pièce justificative'),
    ], string='Type', required=True)

    libelle        = fields.Char('Libellé', required=True)
    reference      = fields.Char('Référence / N°')
    date_document  = fields.Date('Date du document')
    obligatoire    = fields.Boolean('Obligatoire', default=True)
    fournie        = fields.Boolean('Fournie', default=False)
    date_reception = fields.Date('Date de réception')
    note           = fields.Text('Observations')

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'mandat_pj_att_rel', 'pj_id', 'att_id',
        string='Fichiers joints',
    )
