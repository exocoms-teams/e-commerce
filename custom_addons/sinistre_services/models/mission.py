# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SinistreMission(models.Model):
    _name        = 'sinistre.mission'
    _description = 'Mission d\'intervention'
    _inherit     = ['mail.thread', 'mail.activity.mixin']
    _order       = 'date_reception desc'

    # ── Référence ───────────────────────────────────────────────────
    reference = fields.Char(
        string='Référence', readonly=True, copy=False,
        default='Nouveau', tracking=True,
    )

    source = fields.Selection([
        ('assurance', 'Ordre de mission Assurance'),
        ('particulier', 'Demande Particulier'),
        ('entreprise', 'Demande Entreprise'),
    ], string='Source', required=True, default='particulier', tracking=True)

    # ── Assurance ────────────────────────────────────────────────────
    assurance_id      = fields.Many2one('sinistre.assurance', string='Compagnie Assurance', tracking=True)
    ref_assurance     = fields.Char(string='Référence Assurance', tracking=True)
    contrat_assurance = fields.Char(string="N° Contrat Assuré")
    montant_garanti   = fields.Monetary(string='Montant Garanti', currency_field='currency_id', tracking=True)
    franchise         = fields.Monetary(string='Franchise', currency_field='currency_id')

    # ── Client ───────────────────────────────────────────────────────
    client_id            = fields.Many2one('res.partner', string='Client / Assuré', required=True, tracking=True)
    adresse_intervention = fields.Char(string="Adresse d'Intervention", required=True, tracking=True)
    contact_sur_place    = fields.Char(string="Contact sur place")
    tel_sur_place        = fields.Char(string="Téléphone sur place")

    # ── Type ─────────────────────────────────────────────────────────
    type_intervention = fields.Selection([
        ('serrurerie',    'Serrurerie'),
        ('plomberie',     'Plomberie'),
        ('menuiserie_int','Menuiserie Intérieure'),
        ('menuiserie_ext','Menuiserie Extérieure'),
        ('vitrerie',      'Vitrerie'),
        ('electricite',   'Électricité'),
        ('autre',         'Autre'),
    ], string="Type d'Intervention", required=True, tracking=True)

    urgence = fields.Selection([
        ('normale',      'Normale'),
        ('urgente',      'Urgente'),
        ('tres_urgente', 'Très Urgente'),
    ], string='Urgence', default='normale', tracking=True)

    priority = fields.Selection([
        ('0','Normal'), ('1','Urgent'), ('2','Très Urgent'), ('3','Critique'),
    ], default='0')

    description_sinistre = fields.Text(string='Description du sinistre', required=True, tracking=True)
    commentaire_interne  = fields.Text(string='Commentaire Interne')

    # ── Dates ────────────────────────────────────────────────────────
    date_reception      = fields.Datetime(string='Date de Réception', default=fields.Datetime.now, readonly=True)
    date_rdv            = fields.Datetime(string='Date RDV', tracking=True)
    date_debut_travaux  = fields.Datetime(string='Début des Travaux')
    date_cloture        = fields.Datetime(string='Date Clôture', readonly=True)

    # ── Intervenant ──────────────────────────────────────────────────
    intervenant_id = fields.Many2one('sinistre.intervenant', string='Intervenant', tracking=True)

    # ── État ─────────────────────────────────────────────────────────
    state = fields.Selection([
        ('nouveau',          'Nouveau'),
        ('assigne',          'Assigné'),
        ('rdv_planifie',     'RDV Planifié'),
        ('en_cours',         'En Cours'),
        ('devis_envoye',     'Devis Envoyé'),
        ('devis_accepte',    'Devis Accepté'),
        ('devis_refuse',     'Devis Refusé'),
        ('travaux_en_cours', 'Travaux en Cours'),
        ('termine',          'Terminé'),
        ('facture',          'Facturé'),
        ('clos',             'Clos'),
        ('annule',           'Annulé'),
    ], string='État', default='nouveau', tracking=True)

    # ── Annulation ───────────────────────────────────────────────────
    motif_annulation = fields.Selection([
        ('client_annule',       'Client annulé'),
        ('assurance_annule',    "Assurance annulée"),
        ('artisan_absent',      'Artisan absent'),
        ('doublon',             'Doublon'),
        ('autre',               'Autre'),
    ], string="Motif d'annulation", tracking=True)

    annule_par = fields.Selection([
        ('client',    'Client'),
        ('assurance', 'Assurance'),
        ('plateforme','Plateforme'),
    ], string='Annulé par', tracking=True)

    artisan_sur_place   = fields.Boolean(string='Artisan déjà sur place', default=False)
    frais_deplacement   = fields.Monetary(string='Frais de déplacement', currency_field='currency_id')
    facturer_deplacement = fields.Boolean(string='Facturer les frais de déplacement', default=False)
    facturation_deplacement_a = fields.Selection([
        ('assurance', 'Assurance'),
        ('client',    'Client'),
    ], string='Facturer déplacement à', default='client')

    # ── Financier ────────────────────────────────────────────────────
    currency_id  = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    devis_ids    = fields.One2many('sinistre.devis', 'mission_id', string='Devis')
    devis_count  = fields.Integer(compute='_compute_devis_count')
    photo_ids    = fields.One2many('sinistre.photo', 'mission_id', string='Photos')
    photos_avant_count = fields.Integer(compute='_compute_photos_count', string='Photos Avant')
    photos_apres_count = fields.Integer(compute='_compute_photos_count', string='Photos Après')

    facture_client_id = fields.Many2one('account.move', string='Facture Client', readonly=True)
    token_api = fields.Char(string='Token API', readonly=True, copy=False)

    commission_plateforme = fields.Monetary(
        string='Commission Plateforme', compute='_compute_commission',
        store=True, currency_field='currency_id',
    )

    montant_devis = fields.Monetary(
        string='Montant Devis Accepté', compute='_compute_montant_devis',
        store=True, currency_field='currency_id',
    )
    reste_a_charge = fields.Monetary(
        string='Reste à Charge Client', compute='_compute_montant_devis',
        store=True, currency_field='currency_id',
    )

    facture_assurance_id = fields.Many2one('account.move', string='Facture Assurance', readonly=True)

    # ── Estimation tarifaire (visible artisan avant acceptation) ─────
    montant_estime = fields.Monetary(
        string='Montant Estimé',
        currency_field='currency_id',
        help='Fourchette de prix communiquée à l\'artisan avant acceptation de la mission',
    )
    montant_estime_max = fields.Monetary(
        string='Montant Estimé Maximum',
        currency_field='currency_id',
    )

    # ── Messagerie mission ────────────────────────────────────────────
    sinistre_message_ids = fields.One2many('sinistre.message', 'mission_id', string='Messages Mission')

    # ── Signatures intervention ───────────────────────────────────────
    signature_avant = fields.Text(
        string='Signature Avant Intervention',
        help='Signature base64 du client autorisant le démarrage des travaux',
        copy=False,
    )
    signature_apres = fields.Text(
        string='Signature Après Intervention',
        help='Signature base64 du client validant la fin des travaux',
        copy=False,
    )

    # ── Notes artisan ────────────────────────────────────────────────
    notes_artisan = fields.Text(
        string='Notes Artisan',
        help="Notes internes de l'artisan (non visibles du client)",
    )


    # ── Séquence ─────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'Nouveau') == 'Nouveau':
                vals['reference'] = self.env['ir.sequence'].next_by_code('sinistre.mission') or 'MSN-????'
        return super().create(vals_list)

    # ── Compute ──────────────────────────────────────────────────────
    @api.depends('montant_devis', 'intervenant_id', 'intervenant_id.taux_commission')
    def _compute_commission(self):
        for rec in self:
            taux = rec.intervenant_id.taux_commission if rec.intervenant_id else 0
            rec.commission_plateforme = rec.montant_devis * (taux / 100)

    @api.depends('photo_ids', 'photo_ids.type_photo')
    def _compute_photos_count(self):
        for rec in self:
            rec.photos_avant_count = len(rec.photo_ids.filtered(lambda p: p.type_photo == 'avant'))
            rec.photos_apres_count = len(rec.photo_ids.filtered(lambda p: p.type_photo == 'apres'))

    @api.depends('devis_ids', 'devis_ids.state', 'devis_ids.montant_total')
    def _compute_montant_devis(self):
        for rec in self:
            accepted = rec.devis_ids.filtered(lambda d: d.state == 'accepte')
            montant  = sum(accepted.mapped('montant_total'))
            rec.montant_devis   = montant
            if rec.source == 'assurance':
                rec.reste_a_charge = max(0, (rec.franchise or 0))
            else:
                rec.reste_a_charge = montant

    @api.depends('devis_ids')
    def _compute_devis_count(self):
        for rec in self:
            rec.devis_count = len(rec.devis_ids)

    def _expand_states(self, records, values, domain, order=None):
        return [key for key, _ in self._fields['state'].selection]

    # ── Actions workflow ─────────────────────────────────────────────
    def action_assigner(self):
        self.write({'state': 'assigne'})
        self.message_post(body=f"Mission assignée à {self.intervenant_id.name}")

    def action_planifier_rdv(self):
        self.write({'state': 'rdv_planifie'})

    def action_demarrer(self):
        self.write({'state': 'en_cours', 'date_debut_travaux': fields.Datetime.now()})

    def action_terminer(self):
        self.write({'state': 'termine', 'date_cloture': fields.Datetime.now()})
        self._notify_assurance('termine')

    def action_annuler(self):
        """Annulation avec gestion des frais de déplacement."""
        if self.artisan_sur_place and not self.facturer_deplacement:
            raise UserError(
                "L'artisan est sur place. Confirmez si des frais de déplacement doivent être facturés "
                "(cochez 'Facturer les frais de déplacement' puis relancez)."
            )
        self.write({'state': 'annule'})
        if self.artisan_sur_place and self.facturer_deplacement:
            self._creer_facture_deplacement()
        self._notify_assurance('annule')
        self.message_post(
            body=f"Mission annulée par : {dict(self._fields['annule_par'].selection).get(self.annule_par, '?')} "
                 f"— Motif : {dict(self._fields['motif_annulation'].selection).get(self.motif_annulation, '?')}"
        )

    def _creer_facture_deplacement(self):
        """Crée une facture pour frais de déplacement si artisan annulé sur place."""
        if not self.frais_deplacement:
            return
        partner = self.assurance_id.partner_id if (
            self.facturation_deplacement_a == 'assurance' and self.assurance_id
        ) else self.client_id
        facture = self.env['account.move'].sudo().create({
            'move_type':  'out_invoice',
            'partner_id': partner.id,
            'ref':        f"Frais déplacement — {self.reference}",
            'invoice_line_ids': [(0, 0, {
                'name':      f"Frais de déplacement annulation mission {self.reference}",
                'quantity':  1,
                'price_unit': self.frais_deplacement,
            })],
        })
        self.write({'facture_assurance_id': facture.id})
        self.message_post(body=f"Facture frais déplacement créée : {facture.name}")

    # Alias pour compatibilité avec les vues XML existantes
    def action_creer_facture_assurance(self):
        return self.action_facturer_assurance()

    def action_creer_facture_client(self):
        """Facture le reste à charge au client."""
        self.ensure_one()
        if not self.client_id:
            from odoo.exceptions import UserError
            raise UserError("Pas de client lié à cette mission.")
        facture = self.env['account.move'].sudo().create({
            'move_type':  'out_invoice',
            'partner_id': self.client_id.id,
            'ref':        f"Reste à charge {self.reference}",
            'invoice_line_ids': [(0, 0, {
                'name':       f"Reste à charge — {self.reference}",
                'quantity':   1,
                'price_unit': self.reste_a_charge,
            })],
        })
        self.message_post(body=f"Facture client créée : {facture.name}")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': facture.id,
            'view_mode': 'form',
        }

    def action_facturer_assurance(self):
        self.ensure_one()
        if not self.assurance_id:
            raise UserError("Pas de compagnie d'assurance liée à cette mission.")
        facture = self.env['account.move'].sudo().create({
            'move_type':  'out_invoice',
            'partner_id': self.assurance_id.partner_id.id,
            'ref':        f"Mission {self.reference}",
            'invoice_line_ids': [(0, 0, {
                'name':      f"Prestation {self.reference} — {self.description_sinistre or ''}",
                'quantity':  1,
                'price_unit': self.montant_garanti or self.montant_devis,
            })],
        })
        self.write({'facture_assurance_id': facture.id, 'state': 'facture'})

    def _notifier_artisans_zone(self):
        """Envoie une notification push aux artisans disponibles dans la zone."""
        intervenants = self.env['sinistre.intervenant'].sudo().search([
            ('disponible', '=', True),
            ('actif',      '=', True),
        ])
        # Filtrer par spécialité
        if self.type_intervention:
            intervenants = intervenants.filtered(
                lambda iv: any(
                    s.type_intervention == self.type_intervention
                    for s in iv.specialites
                )
            ) or intervenants  # Si aucun spécialiste, notifier tous

        for iv in intervenants:
            if not hasattr(iv, 'fcm_token') or not iv.fcm_token:
                continue
            self.env['sinistre.message'].sudo()._push_notification(
                iv.fcm_token,
                title=f"🚨 Nouvelle mission {'URGENTE' if self.urgence != 'normale' else ''}",
                body=f"{self.type_intervention} — {self.adresse_intervention or ''}",
                data={'type': 'new_mission', 'mission_id': str(self.id)},
            )

    def action_voir_devis(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Devis',
            'res_model': 'sinistre.devis',
            'view_mode': 'list,form',
            'domain': [('mission_id', '=', self.id)],
            'context': {'default_mission_id': self.id},
        }

    def action_voir_photos(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Photos',
            'res_model': 'sinistre.photo',
            'view_mode': 'list,form',
            'domain': [('mission_id', '=', self.id)],
            'context': {'default_mission_id': self.id},
        }

    def _notify_assurance(self, event):
        """Notifie l'assurance via webhook si configuré."""
        if not self.assurance_id or not self.assurance_id.webhook_url:
            return
        import requests, json
        payload = {
            'event':      event,
            'reference':  self.reference,
            'ref_assurance': self.ref_assurance or '',
            'state':      self.state,
            'timestamp':  str(fields.Datetime.now()),
        }
        try:
            requests.post(
                self.assurance_id.webhook_url,
                json=payload,
                headers={'Authorization': f'Bearer {self.assurance_id.api_key}'},
                timeout=10,
            )
        except Exception as e:
            _logger.warning(f"[sinistre] Webhook assurance échoué: {e}")
