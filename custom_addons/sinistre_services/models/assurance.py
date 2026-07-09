# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import secrets


# ═══════════════════════════════════════════════════════════════════════
# ASSURANCE
# ═══════════════════════════════════════════════════════════════════════

class SinistreAssurance(models.Model):
    _name = 'sinistre.assurance'
    _description = "Compagnie d'Assurance"
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    code = fields.Char(string='Code Assurance', help="Ex: AXA, MAIF, ALLIANZ")
    api_key = fields.Char(string='Clé API', copy=False)
    api_key_active = fields.Boolean(default=True)
    webhook_url = fields.Char(string='URL Webhook Retour')
    format_api = fields.Selection([
        ('json_rest', 'JSON REST'), ('xml_soap', 'XML SOAP'),
        ('csv_ftp', 'CSV FTP'), ('custom', 'Personnalisé'),
    ], default='json_rest')
    delai_paiement = fields.Integer(default=30)
    note = fields.Text()
    actif = fields.Boolean(default=True)

    # ── Portail / Compte ──────────────────────────────────────────────
    portal_user_id   = fields.Many2one('res.users', string='Compte Portail', readonly=True)
    inscription_date = fields.Datetime(string="Date d'inscription", readonly=True)
    statut_compte    = fields.Selection([
        ('en_attente', 'En attente de validation'),
        ('actif',      'Actif'),
        ('suspendu',   'Suspendu'),
    ], default='en_attente', string='Statut compte', tracking=True)
    peut_annuler      = fields.Boolean(string='Peut annuler des missions', default=True)
    delai_annulation  = fields.Integer(
        string="Délai max annulation sans frais (h)", default=2,
        help="Nombre d'heures avant le RDV en-deçà duquel l'annulation génère des frais"
    )

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    mission_ids = fields.One2many('sinistre.mission', 'assurance_id')
    mission_count = fields.Integer(compute='_compute_stats')
    ca_assurance = fields.Monetary(compute='_compute_stats', currency_field='currency_id')

    @api.depends('mission_ids', 'mission_ids.montant_garanti')
    def _compute_stats(self):
        for rec in self:
            rec.mission_count = len(rec.mission_ids)
            rec.ca_assurance = sum(rec.mission_ids.mapped('montant_garanti'))

    def action_valider_compte(self):
        self.ensure_one()
        if not self.portal_user_id:
            self._creer_compte_portail()
        self.write({'statut_compte': 'actif'})
        self.message_post(body=f"Compte assurance activé")

    def _creer_compte_portail(self):
        import secrets as _secrets
        if not self.partner_id.email:
            from odoo.exceptions import UserError
            raise UserError("L'assurance doit avoir un email pour créer un compte portail.")
        group_portal = self.env.ref('base.group_portal')
        user = self.env['res.users'].create({
            'name':       self.name,
            'login':      self.partner_id.email,
            'partner_id': self.partner_id.id,
            'groups_id':  [(4, group_portal.id)],
            'password':   _secrets.token_urlsafe(12),
        })
        if not self.api_key:
            self.api_key = _secrets.token_urlsafe(32)
        self.write({'portal_user_id': user.id, 'inscription_date': fields.Datetime.now()})
        return user

    def action_suspendre(self):
        self.write({'statut_compte': 'suspendu'})
        if self.portal_user_id:
            self.portal_user_id.write({'active': False})

    def _check_annulation_autorisee(self, mission):
        if not mission.date_rdv:
            return True, 0
        from datetime import datetime
        delta = (mission.date_rdv - datetime.now()).total_seconds() / 3600
        return (delta >= self.delai_annulation), delta

    def action_generer_api_key(self):
        self.ensure_one()
        self.api_key = secrets.token_urlsafe(32)
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': _('Clé API générée'), 'message': _(f'Nouvelle clé pour {self.name}'), 'type': 'success'}}

    def action_copier_api_key(self):
        """Affiche la clé dans une notification pour pouvoir la copier."""
        self.ensure_one()
        if not self.api_key:
            return {'type': 'ir.actions.client', 'tag': 'display_notification',
                    'params': {'title': 'Aucune clé', 'message': 'Générez d\'abord une clé API.', 'type': 'warning'}}
        return {
            'type': 'ir.actions.client',
            'tag':  'display_notification',
            'params': {
                'title':   '🔑 Clé API',
                'message': self.api_key,
                'type':    'info',
                'sticky':  True,
            }
        }

    def action_revoquer_api_key(self):
        self.write({'api_key': False, 'api_key_active': False})

    def action_voir_missions(self):
        return {'type': 'ir.actions.act_window', 'name': f"Missions {self.name}",
                'res_model': 'sinistre.mission', 'view_mode': 'list,kanban,form',
                'domain': [('assurance_id', '=', self.id)]}


# ═══════════════════════════════════════════════════════════════════════
# DEVIS
# ═══════════════════════════════════════════════════════════════════════

class SinistreDevis(models.Model):
    _name = 'sinistre.devis'
    _description = 'Devis Intervention'
    _inherit = ['mail.thread']
    _order = 'date_devis desc'

    name = fields.Char(required=True, default=lambda self: _('Nouveau'), copy=False)
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
        from odoo.exceptions import UserError
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
        from odoo.exceptions import UserError
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


# ═══════════════════════════════════════════════════════════════════════
# PHOTO DOSSIER
# ═══════════════════════════════════════════════════════════════════════

class SinistrePhoto(models.Model):
    _name = 'sinistre.photo'
    _description = 'Photo Dossier Sinistre'
    _order = 'date_prise desc'

    mission_id = fields.Many2one('sinistre.mission', required=True, ondelete='cascade')
    type_photo = fields.Selection([
        ('avant', 'Avant Intervention'),
        ('pendant', 'Pendant'),
        ('apres', 'Après Intervention'),
    ], required=True, default='avant')
    image = fields.Binary(required=True)
    image_filename = fields.Char()
    description = fields.Char()
    date_prise = fields.Datetime(default=fields.Datetime.now)
    intervenant_id = fields.Many2one(related='mission_id.intervenant_id', store=True)
    latitude = fields.Float(digits=(10, 7))
    longitude = fields.Float(digits=(10, 7))


# ═══════════════════════════════════════════════════════════════════════
# COMMISSION
# ═══════════════════════════════════════════════════════════════════════

class SinistreCommission(models.Model):
    _name = 'sinistre.commission'
    _description = 'Commission Plateforme'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='/')
    mission_id = fields.Many2one('sinistre.mission', required=True)
    intervenant_id = fields.Many2one(related='mission_id.intervenant_id', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    montant_intervention = fields.Monetary(currency_field='currency_id')
    taux_commission = fields.Float()
    montant_commission = fields.Monetary(currency_field='currency_id')
    state = fields.Selection([('due', 'Due'), ('facturee', 'Facturée'), ('payee', 'Payée')], default='due', tracking=True)
    date_echeance = fields.Date()
    facture_id = fields.Many2one('account.move')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('sinistre.commission') or '/'
        return super().create(vals_list)


# ═══════════════════════════════════════════════════════════════════════
# CERTIFICATION INTERVENANT
# ═══════════════════════════════════════════════════════════════════════

class SinistreCertification(models.Model):
    _name        = 'sinistre.certification'
    _description = 'Certification / Document Intervenant'
    _order       = 'sequence, id'

    intervenant_id = fields.Many2one('sinistre.intervenant', required=True, ondelete='cascade')
    name           = fields.Char(string='Libellé', required=True)
    date_validite  = fields.Date(string='Valide jusqu\'au')
    sequence       = fields.Integer(default=10)

    def _date_label(self):
        if not self.date_validite:
            return 'À jour'
        return f"Valide jusqu'en {self.date_validite.strftime('%Y')}"
