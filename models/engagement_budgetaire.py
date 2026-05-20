# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EngagementBudgetaire(models.Model):
    _name = 'engagement.budgetaire'
    _description = 'Engagement Budgétaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(
        string='Numéro d\'engagement',
        required=True,
        copy=False,
        default='/',
        readonly=True,
    )
    intitule = fields.Char(string='Intitulé', required=True, tracking=True)
    date_engagement = fields.Date(
        string='Date d\'engagement',
        default=fields.Date.today,
        required=True,
    )
    exercice_budgetaire = fields.Integer(
        string='Exercice budgétaire',
        required=True,
        default=lambda self: fields.Date.today().year,
    )
    imputation_budgetaire = fields.Char(
        string='Imputation budgétaire',
        required=True,
        help="Chapitre-article-paragraphe (ex: 011-6064)",
    )
    fournisseur_id = fields.Many2one('res.partner', string='Fournisseur', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    montant_engage = fields.Monetary(
        string='Montant engagé',
        currency_field='currency_id',
        required=True,
        tracking=True,
    )
    montant_consomme = fields.Monetary(
        string='Montant consommé',
        currency_field='currency_id',
        compute='_compute_consomme',
        store=True,
    )
    montant_disponible = fields.Monetary(
        string='Montant disponible',
        currency_field='currency_id',
        compute='_compute_consomme',
        store=True,
    )
    taux_consommation = fields.Float(
        string='Taux de consommation (%)',
        compute='_compute_consomme',
        store=True,
    )
    mandat_ids = fields.One2many(
        'mandat.administratif',
        'engagement_id',
        string='Mandats liés',
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Bon de commande',
    )
    state = fields.Selection(
        [
            ('ouvert', 'Ouvert'),
            ('solde', 'Soldé'),
            ('annule', 'Annulé'),
        ],
        string='État',
        default='ouvert',
        tracking=True,
    )
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('mandat_ids', 'mandat_ids.montant_net_payer', 'mandat_ids.state', 'montant_engage')
    def _compute_consomme(self):
        for rec in self:
            mandats_payes = rec.mandat_ids.filtered(lambda m: m.state == 'paye')
            rec.montant_consomme = sum(mandats_payes.mapped('montant_net_payer'))
            rec.montant_disponible = rec.montant_engage - rec.montant_consomme
            rec.taux_consommation = (
                (rec.montant_consomme / rec.montant_engage * 100)
                if rec.montant_engage else 0.0
            )

    def _update_consomme(self, montant):
        """Appelé lors du paiement d'un mandat"""
        self.ensure_one()
        # Le calcul est automatique via le compute, mais on peut déclencher des alertes
        if self.montant_disponible < 0:
            self.message_post(
                body=_("⚠️ Dépassement de l'engagement budgétaire ! Disponible : %s %s") % (
                    self.montant_disponible, self.currency_id.symbol
                ),
                subtype_xmlid='mail.mt_note',
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('engagement.budgetaire') or '/'
        return super().create(vals_list)

    @api.constrains('montant_engage')
    def _check_montant(self):
        for rec in self:
            if rec.montant_engage <= 0:
                raise ValidationError(_("Le montant engagé doit être positif."))

    def action_solder(self):
        self.write({'state': 'solde'})

    def action_annuler(self):
        mandats_actifs = self.mandat_ids.filtered(
            lambda m: m.state not in ('annule', 'rejete', 'paye')
        )
        if mandats_actifs:
            raise ValidationError(_(
                "Impossible d'annuler cet engagement : des mandats actifs y sont rattachés."
            ))
        self.write({'state': 'annule'})
