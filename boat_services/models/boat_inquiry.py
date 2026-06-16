# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class BoatInquiry(models.Model):
    _name = 'boat.inquiry'
    _description = 'Demande bateau'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouvelle demande'),
    )

    inquiry_type = fields.Selection([
        ('price', 'Demande de prix'),
        ('catalog', 'Demande de catalogue'),
        ('contact', 'Contact'),
    ], string='Type de demande', required=True, default='price', tracking=True)

    product_id = fields.Many2one(
        'product.template',
        string='Bateau concerné',
        domain="[('is_boat_product', '=', True)]",
        tracking=True,
    )

    customer_name = fields.Char(string='Nom', required=True, tracking=True)
    customer_email = fields.Char(string='Email', required=True, tracking=True)
    customer_phone = fields.Char(string='Téléphone')
    customer_company = fields.Char(string='Société')
    country_id = fields.Many2one('res.country', string='Pays')

    expected_date = fields.Date(string='Date souhaitée')
    passenger_count = fields.Integer(string='Nombre de passagers')
    budget = fields.Char(string='Budget indicatif')
    message = fields.Text(string='Message')

    state = fields.Selection([
        ('new', 'Nouvelle'),
        ('in_progress', 'En traitement'),
        ('done', 'Traitée'),
        ('cancelled', 'Annulée'),
    ], string='Statut', default='new', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouvelle demande')) == _('Nouvelle demande'):
                vals['name'] = self.env['ir.sequence'].next_by_code('boat.inquiry') or _('Nouvelle demande')
        return super().create(vals_list)

    def action_set_in_progress(self):
        for record in self:
            record.state = 'in_progress'

    def action_done(self):
        for record in self:
            record.state = 'done'

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
