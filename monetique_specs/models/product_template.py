# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    """Ajoute la fiche technique monétique sur le produit."""
    _inherit = 'product.template'

    monetique_category = fields.Selection(
        selection=[
            ('tpe_fixe', 'TPE Fixe'),
            ('tpe_portable', 'TPE Portable'),
            ('tpe_mobile', 'TPE Mobile'),
            ('borne', 'Borne Libre-Service'),
            ('accessoire', 'Accessoire / Consommable'),
        ],
        string='Catégorie monétique',
        help="Type d'équipement monétique, utilisé pour le filtrage "
             "sur la boutique et l'affichage des badges produit.",
    )

    pci_dss_certified = fields.Boolean(
        string='Certifié PCI-DSS',
        help="Coché si l'équipement est certifié PCI-DSS / EMV, "
             "affiché en badge de confiance sur la fiche produit.",
    )

    connectivity_type = fields.Selection(
        selection=[
            ('wifi', 'Wifi'),
            ('4g', '4G / LTE'),
            ('ethernet', 'Ethernet'),
            ('bluetooth', 'Bluetooth'),
            ('nfc', 'Sans contact (NFC)'),
            ('multi', 'Multi-connectivité'),
        ],
        string='Connectivité',
        help="Mode de connexion principal du terminal ou de la borne.",
    )

    battery_life_hours = fields.Integer(
        string='Autonomie batterie (h)',
        help="Autonomie annoncée en heures d'utilisation continue. "
             "Laisser à 0 pour les équipements fixes / secteur.",
    )

    warranty_months = fields.Integer(
        string='Garantie (mois)',
        default=24,
        help="Durée de garantie constructeur, affichée sur la fiche produit.",
    )

    bank_certified_model = fields.Char(
        string='Modèle certifié banque',
        help="Référence du modèle tel que certifié par les réseaux bancaires "
             "(ex: référence agréée CB / Visa / Mastercard).",
    )
