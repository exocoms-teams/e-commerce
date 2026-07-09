# -*- coding: utf-8 -*-
from odoo import fields, models


class SinistreDocumentArtisan(models.Model):
    _name = 'sinistre.document.artisan'
    _description = 'Document importé par artisan (logiciel externe)'
    _order = 'date_import desc'

    mission_id = fields.Many2one('sinistre.mission', required=True, ondelete='cascade')
    intervenant_id = fields.Many2one('sinistre.intervenant', required=True, ondelete='cascade')
    devis_id = fields.Many2one('sinistre.devis', string='Devis lié', ondelete='set null')
    type_document = fields.Selection([
        ('devis', 'Devis'),
        ('facture', 'Facture'),
    ], required=True)
    reference_externe = fields.Char(string='Référence externe', required=True)
    montant_ht = fields.Monetary(currency_field='currency_id', required=True)
    montant_ttc = fields.Monetary(currency_field='currency_id')
    fichier = fields.Binary(string='Fichier PDF', attachment=True)
    fichier_name = fields.Char(string='Nom du fichier')
    date_import = fields.Datetime(default=fields.Datetime.now, readonly=True)
    currency_id = fields.Many2one(related='mission_id.currency_id')

    def _label_type(self):
        return dict(self._fields['type_document'].selection).get(self.type_document, '')


class SinistreMission(models.Model):
    _inherit = 'sinistre.mission'

    document_artisan_ids = fields.One2many(
        'sinistre.document.artisan', 'mission_id', string='Documents importés',
    )
