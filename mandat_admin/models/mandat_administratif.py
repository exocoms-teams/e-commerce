# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
import re


class MandatAdministratif(models.Model):
    _name = 'mandat.administratif'
    _description = 'Mandat Administratif Français'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_mandat desc, name desc'
    _rec_name = 'name'

    # ─── Identification ────────────────────────────────────────────────────────
    name = fields.Char(
        string='Numéro de mandat',
        readonly=True,
        copy=False,
        default='Nouveau',
        tracking=True,
    )
    display_name = fields.Char(
        string='Nom affiché',
        compute='_compute_display_name',
        store=True,
    )
    reference_creancier = fields.Char(
        string='Référence créancier',
        help='Référence interne ou numéro de facture du créancier',
    )
    objet = fields.Char(
        string='Objet du mandat',
        required=True,
        tracking=True,
    )

    # ─── Dates ─────────────────────────────────────────────────────────────────
    date_mandat = fields.Date(
        string='Date du mandat',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    date_piece = fields.Date(
        string='Date de la pièce justificative',
    )
    date_echeance = fields.Date(
        string='Date d\'échéance',
    )
    date_paiement = fields.Date(
        string='Date de paiement',
        readonly=True,
        tracking=True,
    )

    # ─── Ordonnateur / Comptable ────────────────────────────────────────────────
    ordonnateur_id = fields.Many2one(
        'res.users',
        string='Ordonnateur',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    comptable_id = fields.Many2one(
        'res.users',
        string='Comptable assignataire',
        tracking=True,
        help='Comptable public chargé du paiement (Trésorerie / DGFiP)',
    )
    collectivite_id = fields.Many2one(
        'res.company',
        string='Collectivité',
        required=True,
        default=lambda self: self.env.company,
    )

    # ─── Créancier ─────────────────────────────────────────────────────────────
    creancier_id = fields.Many2one(
        'res.partner',
        string='Créancier (bénéficiaire)',
        required=True,
        tracking=True,
    )
    siret_creancier = fields.Char(
        string='SIRET',
        compute='_compute_siret_creancier',
        store=True,
    )
    iban_creancier = fields.Char(
        string='IBAN',
        compute='_compute_iban_creancier',
        store=False,
    )

    # ─── Type et nomenclature ──────────────────────────────────────────────────
    type_mandat = fields.Selection([
        ('depense_ordinaire', 'Dépense ordinaire'),
        ('depense_investissement', 'Dépense d\'investissement'),
        ('virement', 'Virement de crédits'),
        ('remboursement', 'Remboursement'),
        ('avance', 'Avance sur marché'),
    ], string='Type de mandat', required=True, default='depense_ordinaire', tracking=True)

    instruction = fields.Selection([
        ('M14', 'M14 – Communes et groupements'),
        ('M52', 'M52 – Départements'),
        ('M57', 'M57 – Régions et métropoles'),
        ('M4', 'M4 – Services publics industriels et commerciaux'),
        ('M22', 'M22 – Établissements publics de santé'),
    ], string='Instruction comptable', required=True, default='M14')

    # ─── Imputation budgétaire ─────────────────────────────────────────────────
    imputation_ids = fields.One2many(
        'imputation.budgetaire',
        'mandat_id',
        string='Imputations budgétaires',
    )
    compte_budgetaire = fields.Char(
        string='Compte budgétaire principal',
        help='Chapitre / Article / Rubrique selon nomenclature M14/M52/M57',
    )
    chapitre = fields.Char(string='Chapitre')
    article = fields.Char(string='Article')
    rubrique = fields.Char(string='Rubrique')
    fonction = fields.Char(string='Fonction / Programme')

    # ─── Montants ─────────────────────────────────────────────────────────────
    montant_ht = fields.Monetary(
        string='Montant HT',
        currency_field='currency_id',
        tracking=True,
    )
    taux_tva = fields.Selection([
        ('0.0', 'Exonéré (0 %)'),
        ('2.1', 'TVA 2,1 %'),
        ('5.5', 'TVA 5,5 %'),
        ('10.0', 'TVA 10 %'),
        ('20.0', 'TVA 20 %'),
    ], string='Taux TVA', default='20.0')
    montant_tva = fields.Monetary(
        string='Montant TVA',
        currency_field='currency_id',
        compute='_compute_montants',
        store=True,
    )
    montant_ttc = fields.Monetary(
        string='Montant TTC',
        currency_field='currency_id',
        compute='_compute_montants',
        store=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.ref('base.EUR'),
    )
    retenue_garantie = fields.Monetary(
        string='Retenue de garantie',
        currency_field='currency_id',
    )
    montant_net = fields.Monetary(
        string='Montant net à payer',
        currency_field='currency_id',
        compute='_compute_montant_net',
        store=True,
    )

    # ─── Écriture comptable / Facture liée ────────────────────────────────────
    invoice_id = fields.Many2one(
        'account.move',
        string='Écriture / Facture liée',
        readonly=True,
        copy=False,
        ondelete='set null',
        help='Écriture comptable ou facture à l\'origine de ce mandat.',
    )

    # ─── Bordereau ─────────────────────────────────────────────────────────────
    bordereau_id = fields.Many2one(
        'bordereau.mandat',
        string='Bordereau de mandats',
        readonly=True,
        tracking=True,
    )

    # ─── Pièces justificatives ─────────────────────────────────────────────────
    piece_justificative = fields.Selection([
        ('facture', 'Facture'),
        ('memoire', 'Mémoire'),
        ('decompte', 'Décompte définitif'),
        ('etat_liquidatif', 'État liquidatif'),
        ('autre', 'Autre pièce justificative'),
    ], string='Nature de la pièce justificative', required=True, default='facture')

    numero_piece = fields.Char(string='Numéro de la pièce')
    pieces_count = fields.Integer(
        string='Pièces jointes',
        compute='_compute_pieces_count',
    )

    # ─── Marché public ─────────────────────────────────────────────────────────
    marche_public = fields.Boolean(string='Relatif à un marché public')
    numero_marche = fields.Char(string='Numéro du marché')
    lot_marche = fields.Char(string='Lot')

    # ─── État / Workflow ───────────────────────────────────────────────────────
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('a_valider', 'En attente de validation'),
        ('valide', 'Validé (ordonnancé)'),
        ('mandate', 'Mandaté'),
        ('paye', 'Payé'),
        ('annule', 'Annulé'),
        ('rejete', 'Rejeté'),
    ], string='État', default='brouillon', tracking=True, copy=False)

    motif_rejet = fields.Text(
        string='Motif de rejet / annulation',
        tracking=True,
    )

    # ─── Notes ─────────────────────────────────────────────────────────────────
    note_interne = fields.Html(string='Note interne')

    # ───────────────────────────────────────────────────────────────────────────
    # Calculs
    # ───────────────────────────────────────────────────────────────────────────

    @api.depends('name', 'objet')
    def _compute_display_name(self):
        for rec in self:
            n = rec.name if rec.name != 'Nouveau' else _('Nouveau mandat')
            rec.display_name = f'{n} – {rec.objet[:40]}' if rec.objet else n

    @api.depends('montant_ht', 'taux_tva')
    def _compute_montants(self):
        for rec in self:
            taux = float(rec.taux_tva or '0.0') / 100.0
            rec.montant_tva = rec.montant_ht * taux
            rec.montant_ttc = rec.montant_ht + rec.montant_tva

    @api.depends('montant_ttc', 'retenue_garantie')
    def _compute_montant_net(self):
        for rec in self:
            rec.montant_net = rec.montant_ttc - rec.retenue_garantie

    @api.depends('creancier_id')
    def _compute_iban_creancier(self):
        for rec in self:
            bank = self.env['res.partner.bank'].search(
                [('partner_id', '=', rec.creancier_id.id)], limit=1
            )
            rec.iban_creancier = bank.acc_number if bank else ''

    @api.depends('creancier_id')
    def _compute_siret_creancier(self):
        for rec in self:
            rec.siret_creancier = getattr(rec.creancier_id, 'siret', None) or ''

    def _compute_pieces_count(self):
        for rec in self:
            rec.pieces_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', self._name),
                ('res_id', '=', rec.id),
            ])

    # ───────────────────────────────────────────────────────────────────────────
    # Contraintes
    # ───────────────────────────────────────────────────────────────────────────

    @api.constrains('montant_ht')
    def _check_montant(self):
        for rec in self:
            if rec.montant_ht < 0:
                raise ValidationError(_('Le montant HT ne peut pas être négatif.'))

    @api.constrains('chapitre')
    def _check_chapitre(self):
        for rec in self:
            if rec.chapitre and not re.match(r'^\d{2,4}$', rec.chapitre):
                raise ValidationError(_('Le chapitre doit être composé de 2 à 4 chiffres.'))

    # ───────────────────────────────────────────────────────────────────────────
    # Actions du workflow
    # ───────────────────────────────────────────────────────────────────────────

    def action_soumettre_validation(self):
        """Soumettre le mandat à validation par l'ordonnateur."""
        for rec in self:
            if rec.state != 'brouillon':
                raise UserError(_('Seuls les mandats en brouillon peuvent être soumis.'))
            if not rec.imputation_ids and not rec.compte_budgetaire:
                raise UserError(_('Vous devez renseigner au moins une imputation budgétaire.'))
            rec.state = 'a_valider'
            rec.message_post(body=_('Mandat soumis pour validation.'))

    def action_valider(self):
        """Valider et ordonnancer le mandat (rôle ordonnateur)."""
        for rec in self:
            if rec.state != 'a_valider':
                raise UserError(_('Ce mandat ne peut pas être validé dans son état actuel.'))
            if not rec.name or rec.name == 'Nouveau':
                rec.name = self.env['ir.sequence'].next_by_code('mandat.administratif') or 'Nouveau'
            rec.state = 'valide'
            rec.message_post(body=_('Mandat validé et ordonnancé par %s.') % rec.ordonnateur_id.name)

    def action_mandater(self):
        """Transmettre au comptable pour paiement."""
        for rec in self:
            if rec.state != 'valide':
                raise UserError(_('Seuls les mandats validés peuvent être mandatés.'))
            rec.state = 'mandate'
            rec.message_post(body=_('Mandat transmis au comptable pour prise en charge.'))

    def action_marquer_paye(self):
        """Marquer comme payé par le comptable."""
        for rec in self:
            if rec.state != 'mandate':
                raise UserError(_('Le mandat doit être à l\'état "Mandaté" pour être payé.'))
            rec.date_paiement = fields.Date.today()
            rec.state = 'paye'
            rec.message_post(body=_('Paiement effectué le %s.') % rec.date_paiement)

    def action_annuler(self):
        """Annuler le mandat."""
        for rec in self:
            if rec.state == 'paye':
                raise UserError(_('Un mandat payé ne peut pas être annulé. Émettez un titre de recette.'))
            rec.state = 'annule'
            rec.message_post(body=_('Mandat annulé.'))

    def action_remettre_brouillon(self):
        """Remettre en brouillon (correction)."""
        for rec in self:
            if rec.state not in ('a_valider', 'rejete'):
                raise UserError(_('Seuls les mandats en attente ou rejetés peuvent être remis en brouillon.'))
            rec.state = 'brouillon'

    def action_voir_pieces(self):
        """Ouvrir les pièces jointes."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pièces justificatives'),
            'res_model': 'ir.attachment',
            'view_mode': 'list,form',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'context': {'default_res_model': self._name, 'default_res_id': self.id},
        }

    def action_imprimer_mandat(self):
        """Imprimer le mandat."""
        return self.env.ref('mandat_admin.action_report_mandat').report_action(self)

    # ───────────────────────────────────────────────────────────────────────────
    # Surcharges ORM
    # ───────────────────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                # La séquence est attribuée à la validation
                pass
        return super().create(vals_list)

    def copy(self, default=None):
        default = default or {}
        default.update({
            'name': 'Nouveau',
            'state': 'brouillon',
            'date_mandat': fields.Date.today(),
            'bordereau_id': False,
            'date_paiement': False,
        })
        return super().copy(default)

