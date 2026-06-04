# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ValidationMandatWizard(models.TransientModel):
    _name = 'validation.mandat.wizard'
    _description = 'Assistant de validation des mandats'

    mandat_ids = fields.Many2many(
        'mandat.administratif',
        string='Mandats à valider',
        default=lambda self: self.env.context.get('active_ids', []),
    )
    nb_mandats = fields.Integer(
        string='Nombre de mandats',
        compute='_compute_nb_mandats',
    )
    total_net = fields.Monetary(
        string='Total net à payer',
        currency_field='currency_id',
        compute='_compute_nb_mandats',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.ref('base.EUR'),
    )
    commentaire = fields.Text(string='Commentaire de validation')
    creer_bordereau = fields.Boolean(
        string='Créer un bordereau automatiquement',
        default=True,
    )
    date_bordereau = fields.Date(
        string='Date du bordereau',
        default=fields.Date.today,
    )

    @api.depends('mandat_ids')
    def _compute_nb_mandats(self):
        for rec in self:
            rec.nb_mandats = len(rec.mandat_ids)
            rec.total_net = sum(rec.mandat_ids.mapped('montant_net'))

    def action_valider(self):
        """Valider tous les mandats sélectionnés."""
        self.ensure_one()
        mandats_a_valider = self.mandat_ids.filtered(
            lambda m: m.state == 'a_valider'
        )
        if not mandats_a_valider:
            raise UserError(_('Aucun mandat en attente de validation parmi la sélection.'))

        for mandat in mandats_a_valider:
            mandat.action_valider()
            if self.commentaire:
                mandat.message_post(body=_('Commentaire : %s') % self.commentaire)

        if self.creer_bordereau and mandats_a_valider:
            bordereau = self.env['bordereau.mandat'].create({
                'date_bordereau': self.date_bordereau,
                'note': self.commentaire or '',
            })
            mandats_a_valider.write({'bordereau_id': bordereau.id})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'bordereau.mandat',
                'res_id': bordereau.id,
                'view_mode': 'form',
                'target': 'current',
            }

        return {'type': 'ir.actions.act_window_close'}
