# -*- coding: utf-8 -*-
import logging
import secrets
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

TAUX_COMMISSION_VIREMENT = 0.5
MONTANT_GARANTIE_DEFAUT = 150.0


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
    ref_assurance     = fields.Char(string='Référence Assurance / N° dossier', tracking=True)
    numero_dossier    = fields.Char(
        string='N° Dossier', compute='_compute_numero_dossier', store=True, readonly=False,
        help='Numéro de dossier pour refacturation assurance',
    )
    contrat_assurance = fields.Char(string="N° Contrat Assuré")
    montant_garanti   = fields.Monetary(string='Montant Garanti', currency_field='currency_id', tracking=True)
    franchise         = fields.Monetary(string='Franchise', currency_field='currency_id')

    # ── Client ───────────────────────────────────────────────────────
    client_id            = fields.Many2one('res.partner', string='Client / Assuré', required=True, tracking=True)
    client_email         = fields.Char(
        string='Email client', compute='_compute_client_email', store=True, readonly=False,
    )
    adresse_intervention = fields.Char(string="Adresse d'Intervention", required=True, tracking=True)
    contact_sur_place    = fields.Char(string="Contact sur place")
    tel_sur_place        = fields.Char(string="Téléphone sur place")

    # ── Type ─────────────────────────────────────────────────────────
    type_intervention = fields.Selection([
        ('serrurerie',    'Serrurerie'),
        ('plomberie',     'Plomberie'),
        ('chauffagiste',  'Chauffagiste'),
        ('electricite',   'Électricité'),
        ('assainissement','Assainissement'),
        ('vitrerie',      'Vitrerie'),
        ('nuisibles',     'Nuisibles'),
        ('travaux',       'Travaux / Bricolage'),
        ('menuiserie_int','Menuiserie Intérieure'),
        ('menuiserie_ext','Menuiserie Extérieure'),
        ('maconnerie',    'Maçonnerie'),
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
    code_acces = fields.Char(
        string="Code d'accès application", readonly=True, copy=False,
        help="Code envoyé au client pour accéder au suivi et signer le devis",
    )

    # ── TVA & paiement ─────────────────────────────────────────────
    tva_client = fields.Selection([
        ('10', 'TVA 10%'),
        ('20', 'TVA 20%'),
        ('0',  'Hors taxe (assurance)'),
    ], string='TVA client', default='20', tracking=True)
    mode_paiement = fields.Selection([
        ('carte',            'Carte bancaire'),
        ('virement',         'Virement bancaire'),
        ('assurance',        'Prise en charge assurance'),
    ], string='Mode de paiement', tracking=True)
    ref_paiement = fields.Char(
        string='Référence paiement', readonly=True, copy=False,
        help='Référence bancaire (carte ou virement) — visible artisan',
    )
    commission_virement = fields.Monetary(
        string='Commission virement (0,5%)', currency_field='currency_id',
        compute='_compute_commission_virement', store=True,
    )
    date_credit_virement = fields.Date(
        string='Crédit virement (J+1)', readonly=True,
    )
    devis_depasse_garantie = fields.Boolean(
        string='Devis > garantie assurance', compute='_compute_montant_devis', store=True,
    )

    consommable_ids = fields.One2many('sinistre.consommable', 'mission_id', string='Consommables')
    pense_bete_ids = fields.One2many('sinistre.pense_bete', 'mission_id', string='Pense-bêtes')
    avis_ids = fields.One2many('sinistre.avis', 'mission_id', string='Avis client')

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
            if not vals.get('token_api'):
                vals['token_api'] = secrets.token_urlsafe(32)
            if not vals.get('code_acces'):
                vals['code_acces'] = secrets.token_hex(4).upper()
            if vals.get('source') == 'assurance' and not vals.get('montant_garanti'):
                vals['montant_garanti'] = MONTANT_GARANTIE_DEFAUT
            if vals.get('source') == 'assurance' and not vals.get('tva_client'):
                vals['tva_client'] = '0'
        missions = super().create(vals_list)
        if not self.env.context.get('skip_mission_push'):
            for mission in missions:
                if mission.state == 'nouveau' and not mission.intervenant_id:
                    mission._notifier_artisans_zone()
                mission._envoyer_email_creation_client()
        return missions

    @api.depends('client_id', 'client_id.email')
    def _compute_client_email(self):
        for rec in self:
            rec.client_email = rec.client_id.email if rec.client_id else ''

    @api.depends('ref_assurance', 'reference')
    def _compute_numero_dossier(self):
        for rec in self:
            rec.numero_dossier = rec.ref_assurance or rec.reference or ''

    @api.depends('montant_devis', 'mode_paiement')
    def _compute_commission_virement(self):
        for rec in self:
            if rec.mode_paiement in ('virement', 'carte'):
                rec.commission_virement = (rec.montant_devis or 0) * TAUX_COMMISSION_VIREMENT / 100
            else:
                rec.commission_virement = 0

    # ── Compute ──────────────────────────────────────────────────────
    @api.depends('montant_devis', 'intervenant_id', 'intervenant_id.taux_commission')
    def _compute_commission(self):
        for rec in self:
            taux = rec.intervenant_id.taux_commission if rec.intervenant_id else 0
            montant = rec.montant_devis or 0
            rec.commission_plateforme = montant * (taux / 100)

    @api.depends('photo_ids', 'photo_ids.type_photo')
    def _compute_photos_count(self):
        for rec in self:
            rec.photos_avant_count = len(rec.photo_ids.filtered(lambda p: p.type_photo == 'avant'))
            rec.photos_apres_count = len(rec.photo_ids.filtered(lambda p: p.type_photo == 'apres'))

    @api.depends('devis_ids', 'devis_ids.state', 'devis_ids.montant_total', 'montant_garanti', 'franchise', 'source')
    def _compute_montant_devis(self):
        for rec in self:
            accepted = rec.devis_ids.filtered(lambda d: d.state == 'accepte')
            montant  = sum(accepted.mapped('montant_total'))
            rec.montant_devis   = montant
            garanti = rec.montant_garanti or (MONTANT_GARANTIE_DEFAUT if rec.source == 'assurance' else 0)
            rec.devis_depasse_garantie = bool(
                rec.source == 'assurance' and montant > garanti
            )
            if rec.source == 'assurance':
                prise_en_charge = min(montant, garanti)
                rec.reste_a_charge = max(0, montant - prise_en_charge + (rec.franchise or 0))
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
        for rec in self:
            if not rec.photos_avant_count:
                raise UserError(_("Au moins une photo AVANT est obligatoire pour démarrer l'intervention."))
        self.write({'state': 'en_cours', 'date_debut_travaux': fields.Datetime.now()})

    def action_terminer(self):
        for rec in self:
            if not rec.photos_apres_count:
                raise UserError(_("Au moins une photo APRÈS est obligatoire pour clôturer la mission."))
            devis_rs = rec.devis_ids.sorted('date_devis', reverse=True)[:1]
            if devis_rs:
                devis = devis_rs[0]
                if devis.state == 'refuse':
                    if rec.source == 'assurance':
                        rec._facturer_assurance_deplacement()
                elif devis.state != 'accepte':
                    raise UserError(
                        _("Le client doit signer le devis avant clôture (même en cas de prise en charge assurance).")
                    )
        self.write({'state': 'termine', 'date_cloture': fields.Datetime.now()})
        self._notify_assurance('termine')
        for rec in self:
            if rec.source == 'assurance' and not rec.facture_assurance_id:
                rec._facturer_assurance_garantie()
            rec._envoyer_email_facture_client()

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
        self._envoyer_email_facture_client(facture)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': facture.id,
            'view_mode': 'form',
        }

    def action_facturer_assurance(self):
        self.ensure_one()
        if not self.assurance_id:
            raise UserError(_("Pas de compagnie d'assurance liée à cette mission."))
        if self.facture_assurance_id:
            return self.facture_assurance_id
        return self._creer_facture_assurance_ht(
            self.montant_garanti or MONTANT_GARANTIE_DEFAUT,
            ref_extra=self.numero_dossier or self.ref_assurance or '',
        )

    def _facturer_assurance_garantie(self):
        """Refacture la prise en charge assurance (150 € HT par défaut)."""
        self.ensure_one()
        if not self.assurance_id or self.facture_assurance_id:
            return self.facture_assurance_id
        montant = self.montant_garanti or MONTANT_GARANTIE_DEFAUT
        return self._creer_facture_assurance_ht(
            montant,
            ref_extra=self.numero_dossier or self.ref_assurance or self.reference,
        )

    def _facturer_assurance_deplacement(self):
        """Facture déplacement + temps à l'assurance si client refuse le devis."""
        self.ensure_one()
        if not self.assurance_id:
            return
        montant = self.frais_deplacement or 80.0
        if self.facture_assurance_id:
            return self.facture_assurance_id
        return self._creer_facture_assurance_ht(
            montant,
            libelle=f"Déplacement et temps — refus devis — {self.reference}",
            ref_extra=self.numero_dossier or self.ref_assurance or '',
        )

    def _creer_facture_assurance_ht(self, montant, libelle=None, ref_extra=''):
        """Crée une facture HT pour l'assurance."""
        self.ensure_one()
        if montant <= 0:
            raise UserError(_("Montant de facturation invalide."))
        desc = libelle or f"Prestation {self.reference} — {self.description_sinistre or ''}"
        if ref_extra:
            desc += f" — Dossier {ref_extra}"
        facture = self.env['account.move'].sudo().create({
            'move_type':  'out_invoice',
            'partner_id': self.assurance_id.partner_id.id,
            'ref':        f"Mission {self.reference}" + (f" — {ref_extra}" if ref_extra else ''),
            'invoice_line_ids': [(0, 0, {
                'name':      desc,
                'quantity':  1,
                'price_unit': montant,
                'tax_ids':   [(5, 0, 0)],
            })],
        })
        self.write({'facture_assurance_id': facture.id, 'state': 'facture'})
        self._envoyer_email_facture_assurance(facture)
        self.message_post(body=_("Facture assurance créée : %s") % facture.name)
        return facture

    def action_generer_facture(self):
        """Génère la facture adaptée à la source (assurance ou client B2C)."""
        self.ensure_one()
        if self.state not in ('termine', 'facture', 'clos'):
            raise UserError(_("La mission doit être terminée avant facturation."))
        if self.facture_assurance_id:
            return self.facture_assurance_id
        if self.facture_client_id:
            return self.facture_client_id

        if self.source == 'assurance' and self.assurance_id:
            return self.action_facturer_assurance()

        if self.client_id:
            montant = self.montant_devis or self.reste_a_charge or 0
            if montant <= 0:
                raise UserError(_("Montant de facturation invalide."))
            facture = self.env['account.move'].sudo().create({
                'move_type':  'out_invoice',
                'partner_id': self.client_id.id,
                'ref':        f"Mission {self.reference}",
                'invoice_line_ids': [(0, 0, {
                    'name':       f"Prestation {self.reference} — {self.description_sinistre or ''}",
                    'quantity':   1,
                    'price_unit': montant,
                })],
            })
            self.write({'facture_client_id': facture.id, 'state': 'facture'})
            self.message_post(body=_("Facture client créée : %s") % facture.name)
            self._envoyer_email_facture_client(facture)
            return facture

        raise UserError(_("Impossible de générer une facture pour cette mission."))

    def _notifier_artisans_zone(self):
        """Envoie une notification push aux artisans disponibles dans le secteur."""
        self.ensure_one()
        adresse = self.adresse_intervention or ''

        intervenants = self.env['sinistre.intervenant'].sudo().search([
            ('disponible', '=', True),
            ('actif',      '=', True),
        ])
        intervenants = intervenants.filtered(lambda iv: iv.couvre_adresse(adresse))

        if self.type_intervention:
            by_specialite = intervenants.filtered(
                lambda iv: any(
                    s.type_intervention == self.type_intervention
                    for s in iv.specialites
                )
            )
            if by_specialite:
                intervenants = by_specialite

        notified = 0
        for iv in intervenants:
            if not iv.fcm_token:
                continue
            self.env['sinistre.message'].sudo()._push_notification(
                iv.fcm_token,
                title=f"🚨 Nouvelle mission {'URGENTE' if self.urgence != 'normale' else ''}",
                body=f"{self.type_intervention} — {adresse}",
                data={'type': 'new_mission', 'mission_id': str(self.id)},
                data_only=True,
            )
            notified += 1

        _logger.info(
            "[sinistre] Push secteur mission %s : %d artisan(s) notifié(s) / %d éligible(s)",
            self.reference, notified, len(intervenants),
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

    def action_ouvrir_note_interne(self):
        """Ouvre l'onglet notes internes."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sinistre.mission',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_ouvrir_message_plateforme(self):
        """Ouvre l'onglet messages plateforme."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sinistre.mission',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_enregistrer_paiement(self, mode, ref_paiement=''):
        """Enregistre le paiement client (carte ou virement) avec commission 0,5%."""
        self.ensure_one()
        if mode == 'cheque':
            raise UserError(_("Les règlements par chèque ne sont pas acceptés."))
        from datetime import timedelta
        credit = fields.Date.today() + timedelta(days=1)
        self.write({
            'mode_paiement': mode,
            'ref_paiement': ref_paiement,
            'date_credit_virement': credit,
        })
        if self.reste_a_charge > 0 and mode in ('carte', 'virement'):
            self.action_creer_facture_client()

    def _get_base_url(self):
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')

    def _envoyer_email_creation_client(self):
        self.ensure_one()
        email = self.client_email or (self.client_id.email if self.client_id else '')
        if not email:
            return
        base = self._get_base_url()
        suivi = f"{base}/suivi/{self.token_api}"
        body = f"""
            <p>Bonjour {self.client_id.name or ''},</p>
            <p>Votre demande d'intervention <strong>{self.reference}</strong> a bien été enregistrée.</p>
            <p>Vous avez accès à l'application de suivi avec votre <strong>code d'accès : {self.code_acces}</strong></p>
            <p><a href="{suivi}">Suivre ma mission et signer mon devis</a></p>
        """
        if self.source == 'assurance':
            garanti = self.montant_garanti or MONTANT_GARANTIE_DEFAUT
            body += f"<p>Votre assurance prend en charge <strong>{garanti:.0f} € HT</strong> de garantie.</p>"
        self._send_mail(email, f"[Sinistre Services] Mission {self.reference}", body)

    def _envoyer_email_facture_client(self, facture=None):
        self.ensure_one()
        facture = facture or self.facture_client_id
        if not facture:
            return
        email = self.client_email or (self.client_id.email if self.client_id else '')
        if not email:
            return
        body = f"""
            <p>Bonjour {self.client_id.name or ''},</p>
            <p>Votre facture <strong>{facture.name}</strong> pour la mission {self.reference} est disponible.</p>
            <p>Montant : <strong>{facture.amount_total:.2f} €</strong></p>
        """
        self._send_mail(email, f"[Sinistre Services] Facture {facture.name}", body)

    def _envoyer_email_facture_assurance(self, facture):
        self.ensure_one()
        if not self.assurance_id or not self.assurance_id.partner_id.email:
            return
        body = f"""
            <p>Facture mission <strong>{self.reference}</strong></p>
            <p>N° dossier : <strong>{self.numero_dossier or self.ref_assurance or ''}</strong></p>
            <p>Montant HT : <strong>{facture.amount_untaxed:.2f} €</strong></p>
            <p>Référence facture : <strong>{facture.name}</strong></p>
        """
        self._send_mail(
            self.assurance_id.partner_id.email,
            f"[Sinistre Services] Facture assurance {self.reference}",
            body,
        )

    def _send_mail(self, email_to, subject, body_html):
        try:
            self.env['mail.mail'].sudo().create({
                'subject': subject,
                'body_html': body_html,
                'email_to': email_to,
                'email_from': self.env.company.email or 'noreply@sinistre-services.fr',
            }).send()
        except Exception as e:
            _logger.warning("[sinistre] email failed: %s", e)

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
