# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import uuid


class SinistreMission(models.Model):
    """
    Ordre de Mission - Cœur du système.
    Peut être créé :
    - Via API assurance (source='assurance')
    - Via demande directe particulier/pro (source='direct')
    """
    _name = 'sinistre.mission'
    _description = 'Ordre de Mission Sinistre'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_reception desc, priority desc'
    _rec_name = 'reference'

    # ─── Identification ───────────────────────────────────────────────
    reference = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
        tracking=True,
    )
    token_api = fields.Char(
        string='Token API',
        copy=False,
        help="Token unique généré pour les échanges API avec les assurances",
    )

    # ─── Source de la demande ─────────────────────────────────────────
    source = fields.Selection([
        ('assurance', 'Ordre de mission Assurance'),
        ('particulier', 'Demande Particulier'),
        ('entreprise', 'Demande Entreprise'),
    ], string='Source', required=True, default='particulier', tracking=True)

    # ─── Assurance (si source = assurance) ───────────────────────────
    assurance_id = fields.Many2one(
        'sinistre.assurance',
        string='Compagnie Assurance',
        tracking=True,
    )
    ref_assurance = fields.Char(
        string='Référence Assurance',
        help="Numéro de dossier côté assurance",
        tracking=True,
    )
    contrat_assurance = fields.Char(string="N° Contrat Assuré")
    montant_garanti = fields.Monetary(
        string='Montant Garanti (Assurance)',
        currency_field='currency_id',
        tracking=True,
    )
    franchise = fields.Monetary(
        string='Franchise',
        currency_field='currency_id',
    )

    # ─── Client final ─────────────────────────────────────────────────
    client_id = fields.Many2one(
        'res.partner',
        string='Client / Assuré',
        required=True,
        tracking=True,
    )
    client_type = fields.Selection([
        ('particulier', 'Particulier'),
        ('entreprise', 'Entreprise'),
    ], string='Type Client', compute='_compute_client_type', store=True)
    adresse_intervention = fields.Char(
        string="Adresse d'Intervention",
        required=True,
        tracking=True,
    )
    contact_sur_place = fields.Char(string="Contact sur place")
    tel_sur_place = fields.Char(string="Téléphone sur place")

    # ─── Type d'intervention ─────────────────────────────────────────
    type_intervention = fields.Selection([
        ('serrurerie', '🔐 Serrurerie'),
        ('plomberie', '🔧 Plomberie'),
        ('menuiserie_int', '🪟 Menuiserie Intérieure'),
        ('menuiserie_ext', '🚪 Menuiserie Extérieure'),
        ('vitrerie', '🪟 Vitrerie'),
        ('electricite', '⚡ Électricité'),
        ('autre', '🔨 Autre'),
    ], string="Type d'Intervention", required=True, tracking=True)

    urgence = fields.Selection([
        ('normale', 'Normale'),
        ('urgente', 'Urgente'),
        ('tres_urgente', 'Très Urgente'),
    ], string='Niveau Urgence', default='normale', tracking=True)

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
        ('2', 'Très Urgent'),
        ('3', 'Critique'),
    ], default='0')

    description_sinistre = fields.Text(
        string='Description du sinistre',
        required=True,
        tracking=True,
    )
    commentaire_interne = fields.Text(string='Commentaire Interne')

    # ─── Dates ────────────────────────────────────────────────────────
    date_reception = fields.Datetime(
        string='Date de Réception',
        default=fields.Datetime.now,
        readonly=True,
    )
    date_rdv = fields.Datetime(string='Date RDV', tracking=True)
    date_debut_travaux = fields.Datetime(string='Début des Travaux')
    date_cloture = fields.Datetime(string='Date Clôture', readonly=True)

    # ─── Intervenant ─────────────────────────────────────────────────
    intervenant_id = fields.Many2one(
        'sinistre.intervenant',
        string='Intervenant',
        tracking=True,
    )

    # ─── Statut ───────────────────────────────────────────────────────
    state = fields.Selection([
        ('nouveau', 'Nouveau'),
        ('assigne', 'Assigné'),
        ('rdv_planifie', 'RDV Planifié'),
        ('en_cours', 'En Cours'),
        ('devis_envoye', 'Devis Envoyé'),
        ('devis_accepte', 'Devis Accepté'),
        ('devis_refuse', 'Devis Refusé'),
        ('travaux_en_cours', 'Travaux en Cours'),
        ('termine', 'Terminé'),
        ('facture', 'Facturé'),
        ('clos', 'Clos'),
        ('annule', 'Annulé'),
    ], string='État', default='nouveau', tracking=True, group_expand='_expand_states')

    # ─── Financier ────────────────────────────────────────────────────
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    devis_ids = fields.One2many('sinistre.devis', 'mission_id', string='Devis')
    devis_count = fields.Integer(compute='_compute_devis_count')
    montant_devis = fields.Monetary(
        string='Montant Devis Accepté',
        compute='_compute_montant_devis',
        store=True,
        currency_field='currency_id',
    )
    reste_a_charge = fields.Monetary(
        string='Reste à Charge Client',
        compute='_compute_reste_a_charge',
        store=True,
        currency_field='currency_id',
    )
    commission_plateforme = fields.Monetary(
        string='Commission Plateforme',
        compute='_compute_commission',
        store=True,
        currency_field='currency_id',
    )

    # ─── Factures ─────────────────────────────────────────────────────
    facture_assurance_id = fields.Many2one(
        'account.move', string='Facture Assurance',
        domain=[('move_type', '=', 'out_invoice')],
    )
    facture_client_id = fields.Many2one(
        'account.move', string='Facture Client (Reste à Charge)',
        domain=[('move_type', '=', 'out_invoice')],
    )

    # ─── Photos ───────────────────────────────────────────────────────
    photo_ids = fields.One2many('sinistre.photo', 'mission_id', string='Photos')
    photos_avant_count = fields.Integer(compute='_compute_photos_count', string='Photos Avant')
    photos_apres_count = fields.Integer(compute='_compute_photos_count', string='Photos Après')

    # ─── Computes ─────────────────────────────────────────────────────

    @api.depends('client_id', 'client_id.is_company')
    def _compute_client_type(self):
        for rec in self:
            rec.client_type = 'entreprise' if rec.client_id.is_company else 'particulier'

    def _compute_devis_count(self):
        for rec in self:
            rec.devis_count = len(rec.devis_ids)

    @api.depends('devis_ids', 'devis_ids.state', 'devis_ids.montant_total')
    def _compute_montant_devis(self):
        for rec in self:
            devis_ok = rec.devis_ids.filtered(lambda d: d.state == 'accepte')
            rec.montant_devis = sum(devis_ok.mapped('montant_total'))

    @api.depends('montant_devis', 'montant_garanti', 'franchise')
    def _compute_reste_a_charge(self):
        for rec in self:
            if rec.source == 'assurance':
                rec.reste_a_charge = max(0, rec.montant_devis - rec.montant_garanti) + rec.franchise
            else:
                rec.reste_a_charge = rec.montant_devis

    @api.depends('montant_devis', 'intervenant_id', 'intervenant_id.taux_commission')
    def _compute_commission(self):
        for rec in self:
            taux = rec.intervenant_id.taux_commission if rec.intervenant_id else 0.0
            rec.commission_plateforme = rec.montant_devis * (taux / 100)

    def _compute_photos_count(self):
        for rec in self:
            rec.photos_avant_count = len(rec.photo_ids.filtered(lambda p: p.type_photo == 'avant'))
            rec.photos_apres_count = len(rec.photo_ids.filtered(lambda p: p.type_photo == 'apres'))

    # ─── Kanban / Group expand ────────────────────────────────────────
    @api.model
    def _expand_states(self, states, domain, order):
        return [key for key, _ in self._fields['state'].selection]

    # ─── Séquence ────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('Nouveau')) == _('Nouveau'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('sinistre.mission') or _('Nouveau')
            if not vals.get('token_api'):
                vals['token_api'] = str(uuid.uuid4())
        return super().create(vals_list)

    # ─── Actions de workflow ─────────────────────────────────────────
    def action_assigner(self):
        self.ensure_one()
        if not self.intervenant_id:
            raise UserError(_("Veuillez d'abord assigner un intervenant."))
        self.write({'state': 'assigne'})
        # Notification à l'intervenant
        self.message_post(
            body=_("Mission assignée à %s") % self.intervenant_id.name,
            subtype_xmlid='mail.mt_note',
        )

    def action_planifier_rdv(self):
        self.ensure_one()
        if not self.date_rdv:
            raise UserError(_("Veuillez définir une date de RDV."))
        self.write({'state': 'rdv_planifie'})

    def action_demarrer(self):
        self.ensure_one()
        photos_avant = self.photo_ids.filtered(lambda p: p.type_photo == 'avant')
        if not photos_avant:
            raise UserError(_("L'intervenant doit prendre des photos AVANT de démarrer les travaux."))
        self.write({
            'state': 'en_cours',
            'date_debut_travaux': fields.Datetime.now(),
        })

    def action_terminer(self):
        self.ensure_one()
        photos_apres = self.photo_ids.filtered(lambda p: p.type_photo == 'apres')
        if not photos_apres:
            raise UserError(_("L'intervenant doit prendre des photos APRÈS les travaux pour clôturer."))
        self.write({
            'state': 'termine',
            'date_cloture': fields.Datetime.now(),
        })

    def action_annuler(self):
        self.ensure_one()
        self.write({'state': 'annule'})

    def action_creer_facture_assurance(self):
        """Crée la facture à destination de l'assurance."""
        self.ensure_one()
        if not self.assurance_id:
            raise UserError(_("Pas d'assurance liée à cette mission."))
        if self.facture_assurance_id:
            raise UserError(_("Une facture assurance existe déjà."))

        facture = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.assurance_id.partner_id.id,
            'ref': f"Mission {self.reference} - {self.ref_assurance or ''}",
            'invoice_line_ids': [(0, 0, {
                'name': f"Intervention {self.get_type_label()} - {self.reference}",
                'quantity': 1,
                'price_unit': self.montant_garanti,
            })],
        })
        self.write({
            'facture_assurance_id': facture.id,
            'state': 'facture',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': facture.id,
            'view_mode': 'form',
        }

    def action_creer_facture_client(self):
        """Crée la facture du reste à charge pour le client."""
        self.ensure_one()
        if self.reste_a_charge <= 0:
            raise UserError(_("Le reste à charge est nul, pas de facture client nécessaire."))
        if self.facture_client_id:
            raise UserError(_("Une facture client existe déjà."))

        facture = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.client_id.id,
            'ref': f"Reste à charge - Mission {self.reference}",
            'invoice_line_ids': [(0, 0, {
                'name': f"Reste à charge - {self.get_type_label()}",
                'quantity': 1,
                'price_unit': self.reste_a_charge,
            })],
        })
        self.write({'facture_client_id': facture.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': facture.id,
            'view_mode': 'form',
        }

    def get_type_label(self):
        types = dict(self._fields['type_intervention'].selection)
        return types.get(self.type_intervention, self.type_intervention)

    # ─── Smart buttons ────────────────────────────────────────────────
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
            'view_mode': 'kanban,list,form',
            'domain': [('mission_id', '=', self.id)],
            'context': {'default_mission_id': self.id},
        }

    # ─── Nom d'affichage ─────────────────────────────────────────────
    def name_get(self):
        result = []
        for rec in self:
            name = f"[{rec.reference}] {rec.client_id.name or ''}"
            result.append((rec.id, name))
        return result
