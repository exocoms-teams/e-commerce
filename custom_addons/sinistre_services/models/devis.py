# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SinistreDevis(models.Model):
    _name = 'sinistre.devis'
    _description = 'Devis Intervention'
    _inherit = ['mail.thread']
    _order = 'date_devis desc'

    name = fields.Char(required=True, default=lambda self: _('Nouveau'), copy=False)
    ref_externe = fields.Char(string='Référence externe (logiciel artisan)', copy=False)
    import_externe = fields.Boolean(string='Importé depuis logiciel externe', default=False)
    mission_id = fields.Many2one('sinistre.mission', required=True, ondelete='cascade')
    intervenant_id = fields.Many2one(related='mission_id.intervenant_id', store=True)
    client_id = fields.Many2one(related='mission_id.client_id', store=True)
    date_devis = fields.Datetime(default=fields.Datetime.now)
    state = fields.Selection([
        ('brouillon',   'Brouillon'),
        ('envoye',      'Envoyé'),
        ('en_revision', 'En Révision'),
        ('accepte',     'Accepté'),
        ('refuse',      'Refusé'),
    ], default='brouillon', tracking=True)

    ligne_ids = fields.One2many('sinistre.devis.ligne', 'devis_id', string='Lignes')
    currency_id = fields.Many2one(related='mission_id.currency_id')
    tva = fields.Float(default=20.0)
    tva_selection = fields.Selection([
        ('10', '10%'),
        ('20', '20%'),
        ('0',  'Hors taxe'),
    ], string='TVA appliquée', default='20')
    montant_ht = fields.Monetary(compute='_compute_montants', store=True, currency_field='currency_id')
    montant_tva = fields.Monetary(compute='_compute_montants', store=True, currency_field='currency_id')
    montant_total = fields.Monetary(compute='_compute_montants', store=True, currency_field='currency_id')
    note_client = fields.Text()
    motif_refus = fields.Text()
    signature_client = fields.Binary()
    signature_client_modif = fields.Text(
        string='Re-Signature Devis Modifié',
        help='Signature base64 du client après modification du devis',
        copy=False,
    )
    date_signature = fields.Datetime()

    @api.depends('ligne_ids.montant_total', 'tva', 'tva_selection')
    def _compute_montants(self):
        tva_map = {'10': 10.0, '20': 20.0, '0': 0.0}
        for rec in self:
            rec.montant_ht = sum(rec.ligne_ids.mapped('montant_total'))
            taux = tva_map.get(rec.tva_selection, rec.tva or 20.0)
            rec.tva = taux
            rec.montant_tva = rec.montant_ht * (taux / 100)
            rec.montant_total = rec.montant_ht + rec.montant_tva

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sinistre.devis') or _('Nouveau')
        return super().create(vals_list)

    def action_envoyer(self):
        if not self.ligne_ids and not self.import_externe:
            raise UserError(_("Ajoutez au moins une ligne."))
        self.write({'state': 'envoye'})
        self.mission_id.write({'state': 'devis_envoye'})
        self._envoyer_email_devis_client()

    def _envoyer_email_devis_client(self):
        self.ensure_one()
        mission = self.mission_id
        email = mission.client_email or (mission.client_id.email if mission.client_id else '')
        if not email:
            return
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        sign_url = f"{base}/devis/signer/{mission.token_api}/{self.id}"
        suivi = f"{base}/suivi/{mission.token_api}"
        body = f"""
            <p>Bonjour {mission.client_id.name or ''},</p>
            <p>Votre artisan vous a transmis un devis pour la mission <strong>{mission.reference}</strong>.</p>
            <p>Montant total : <strong>{self.montant_total:.2f} €</strong></p>
            <p><strong>Code d'accès application : {mission.code_acces}</strong></p>
            <p><a href="{sign_url}">Signer le devis sur votre téléphone</a></p>
            <p><a href="{suivi}">Suivre ma mission</a></p>
        """
        if mission.source == 'assurance':
            garanti = mission.montant_garanti or 150
            body += (
                f"<p>Prise en charge assurance : <strong>{garanti:.0f} € HT</strong>. "
                f"Signature obligatoire même en cas de garantie.</p>"
            )
            if self.montant_total > garanti:
                rac = mission.reste_a_charge
                body += f"<p>Reste à charge client : <strong>{rac:.2f} €</strong> (si acceptation).</p>"
        try:
            self.env['mail.mail'].sudo().create({
                'subject': f"[Sinistre Services] Devis {self.name} — {mission.reference}",
                'body_html': body,
                'email_to': email,
                'email_from': self.env.company.email or 'noreply@sinistre-services.fr',
            }).send()
        except Exception:
            pass

    def action_accepter(self):
        if self.state not in ('envoye', 'en_revision'):
            raise UserError(_("Le devis doit être dans l'état Envoyé ou En Révision."))
        self.write({'state': 'accepte', 'date_signature': fields.Datetime.now()})
        self.mission_id.write({'state': 'devis_accepte'})

    def action_refuser(self):
        self.write({'state': 'refuse'})
        self.mission_id.write({'state': 'devis_refuse'})


class SinistreDevisLigne(models.Model):
    _name = 'sinistre.devis.ligne'
    _description = 'Ligne de Devis'

    devis_id = fields.Many2one('sinistre.devis', ondelete='cascade')
    sequence = fields.Integer(default=10)
    description = fields.Char(required=True)
    quantite = fields.Float(default=1.0)
    unite = fields.Char(default='forfait')
    prix_unitaire = fields.Monetary(currency_field='currency_id')
    montant_total = fields.Monetary(compute='_compute_total', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='devis_id.currency_id')

    @api.depends('quantite', 'prix_unitaire')
    def _compute_total(self):
        for rec in self:
            rec.montant_total = rec.quantite * rec.prix_unitaire
