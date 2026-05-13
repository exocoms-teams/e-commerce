# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import secrets


class SinistreAssurance(models.Model):
    """
    Compagnie d'assurance partenaire.
    Chaque assurance a une clé API unique pour envoyer ses ordres de mission.
    """
    _name = 'sinistre.assurance'
    _description = "Compagnie d'Assurance"
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(string='Nom Assurance', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Fiche Contact',
        required=True,
        help="Partenaire Odoo pour la facturation",
    )
    code = fields.Char(
        string='Code Assurance',
        help="Code court identifiant l'assurance (ex: AXA, MAIF, ALLIANZ)",
    )

    # ─── API ─────────────────────────────────────────────────────────
    api_key = fields.Char(
        string='Clé API',
        copy=False,
        readonly=True,
        help="Clé API pour l'intégration avec le SI assurance",
    )
    api_key_active = fields.Boolean(string='API Active', default=True)
    webhook_url = fields.Char(
        string='URL Webhook Retour',
        help="URL où envoyer les notifications de statut à l'assurance",
    )

    # ─── Format d'échange ────────────────────────────────────────────
    format_api = fields.Selection([
        ('json_rest', 'JSON REST (standard)'),
        ('xml_soap', 'XML SOAP'),
        ('csv_ftp', 'CSV FTP'),
        ('custom', 'Format Personnalisé'),
    ], string="Format d'échange", default='json_rest')

    # ─── Conditions financières ───────────────────────────────────────
    delai_paiement = fields.Integer(
        string='Délai de Paiement (jours)',
        default=30,
    )
    note = fields.Text(string='Notes et Conditions Particulières')
    actif = fields.Boolean(string='Active', default=True)

    # ─── Stats ───────────────────────────────────────────────────────
    mission_ids = fields.One2many('sinistre.mission', 'assurance_id', string='Missions')
    mission_count = fields.Integer(compute='_compute_stats', string='Nb Missions')
    ca_assurance = fields.Monetary(
        string='CA Assurance',
        compute='_compute_stats',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )

    @api.depends('mission_ids', 'mission_ids.montant_garanti')
    def _compute_stats(self):
        for rec in self:
            rec.mission_count = len(rec.mission_ids)
            rec.ca_assurance = sum(rec.mission_ids.mapped('montant_garanti'))

    # ─── Génération clé API ──────────────────────────────────────────
    def action_generer_api_key(self):
        self.ensure_one()
        self.api_key = secrets.token_urlsafe(32)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Clé API Générée'),
                'message': _(f'Nouvelle clé API générée pour {self.name}'),
                'type': 'success',
            }
        }

    def action_revoquer_api_key(self):
        self.ensure_one()
        self.write({'api_key': False, 'api_key_active': False})

    def action_voir_missions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"Missions {self.name}",
            'res_model': 'sinistre.mission',
            'view_mode': 'list,kanban,form',
            'domain': [('assurance_id', '=', self.id)],
        }
