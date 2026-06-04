# -*- coding: utf-8 -*-
import csv
import io
import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ExportHeliosWizard(models.TransientModel):
    """
    Export au format TUX/Indigo compatible Hélios (DGFiP).
    Format CSV simplifié – à adapter selon le protocole exact de la trésorerie.
    """
    _name = 'export.helios.wizard'
    _description = 'Export Hélios / Indigo'

    date_debut = fields.Date(string='Du', required=True,
                             default=lambda self: fields.Date.today().replace(day=1))
    date_fin = fields.Date(string='Au', required=True, default=fields.Date.today)
    state_filter = fields.Selection([
        ('mandate', 'Mandatés'),
        ('paye', 'Payés'),
        ('all', 'Tous (sauf brouillon)'),
    ], string='États inclus', default='mandate')
    collectivite_id = fields.Many2one(
        'res.company',
        string='Collectivité',
        default=lambda self: self.env.company,
    )
    fichier_export = fields.Binary(string='Fichier généré', readonly=True)
    nom_fichier = fields.Char(string='Nom du fichier', readonly=True)
    etat = fields.Selection([
        ('attente', 'En attente'),
        ('genere', 'Fichier généré'),
    ], default='attente')

    def action_generer_export(self):
        self.ensure_one()
        domain = [
            ('date_mandat', '>=', self.date_debut),
            ('date_mandat', '<=', self.date_fin),
            ('collectivite_id', '=', self.collectivite_id.id),
        ]
        if self.state_filter == 'mandate':
            domain.append(('state', '=', 'mandate'))
        elif self.state_filter == 'paye':
            domain.append(('state', '=', 'paye'))
        else:
            domain.append(('state', 'not in', ['brouillon', 'a_valider', 'annule']))

        mandats = self.env['mandat.administratif'].search(domain, order='name')
        if not mandats:
            raise UserError(_('Aucun mandat trouvé pour les critères sélectionnés.'))

        # Génération CSV Hélios (format simplifié)
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        # En-tête
        writer.writerow([
            'NUM_MANDAT', 'DATE_MANDAT', 'CREANCIER_NOM', 'SIRET',
            'IBAN', 'OBJET', 'CHAPITRE', 'ARTICLE', 'RUBRIQUE',
            'MONTANT_HT', 'TVA', 'MONTANT_TTC', 'NET_A_PAYER',
            'PIECE_JUSTIF', 'NUM_PIECE', 'TYPE_MANDAT', 'INSTRUCTION'
        ])

        for m in mandats:
            imputation = m.imputation_ids[:1] if m.imputation_ids else None
            writer.writerow([
                m.name,
                m.date_mandat.strftime('%d/%m/%Y') if m.date_mandat else '',
                m.creancier_id.name or '',
                m.siret_creancier or '',
                m.iban_creancier or '',
                m.objet or '',
                imputation.chapitre if imputation else (m.chapitre or ''),
                imputation.article if imputation else (m.article or ''),
                imputation.rubrique if imputation else (m.rubrique or ''),
                '%.2f' % m.montant_ht,
                '%.2f' % m.montant_tva,
                '%.2f' % m.montant_ttc,
                '%.2f' % m.montant_net,
                m.piece_justificative or '',
                m.numero_piece or '',
                m.type_mandat or '',
                m.instruction or '',
            ])

        csv_content = output.getvalue().encode('utf-8-sig')  # BOM pour Excel FR
        nom = 'export_helios_%s_%s.csv' % (
            self.date_debut.strftime('%Y%m%d'),
            self.date_fin.strftime('%Y%m%d'),
        )
        self.fichier_export = base64.b64encode(csv_content)
        self.nom_fichier = nom
        self.etat = 'genere'

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
