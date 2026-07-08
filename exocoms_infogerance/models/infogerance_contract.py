from odoo import api, fields, models, _


class InfogeranceContract(models.Model):
    _name = 'exocoms.infogerance.contract'
    _description = 'Contrat d\'infogérance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char('Référence', required=True, copy=False,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Client',
                                 required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Commercial',
                              default=lambda self: self.env.user,
                              tracking=True)
    date_start = fields.Date('Date de début', required=True,
                             default=fields.Date.today, tracking=True)
    date_end = fields.Date('Date de fin', tracking=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('cancelled', 'Résilié'),
    ], string='Statut', default='draft', tracking=True)

    subscription_id = fields.Many2one('sale.order',
                                       string='Abonnement lié',
                                       domain=[('is_subscription', '=', True)])
    contract_template_id = fields.Many2one('sale.order.template',
                                           string='Modèle de contrat',
                                           domain=[('is_subscription', '=', True)])
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Compte analytique')

    service_line_ids = fields.One2many('exocoms.infogerance.service',
                                       'contract_id',
                                       string='Services souscrits')
    equipment_ids = fields.One2many('exocoms.infogerance.equipment',
                                    'contract_id',
                                    string='Équipements couverts')

    ticket_ids = fields.One2many('helpdesk.ticket', 'x_infogerance_contract_id',
                                 string='Tickets associés')
    ticket_count = fields.Integer('Nb tickets',
                                  compute='_compute_ticket_count')

    note = fields.Html('Notes internes')
    terms = fields.Html('Conditions générales')

    company_id = fields.Many2one('res.company', string='Société',
                                 default=lambda self: self.env.company)

    @api.depends('ticket_ids')
    def _compute_ticket_count(self):
        data = self.env['helpdesk.ticket']._read_group(
            [('x_infogerance_contract_id', 'in', self.ids)],
            ['x_infogerance_contract_id'], ['__count']
        )
        counts = {r['x_infogerance_contract_id'][0]: r['__count']
                  for r in data}
        for c in self:
            c.ticket_count = counts.get(c.id, 0)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'exocoms.infogerance.contract') or _('New')
        return super().create(vals)

    def action_activate(self):
        self.state = 'active'

    def action_suspend(self):
        self.state = 'suspended'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_open_tickets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tickets'),
            'res_model': 'helpdesk.ticket',
            'view_mode': 'list,form',
            'domain': [('x_infogerance_contract_id', '=', self.id)],
            'context': {
                'default_x_infogerance_contract_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
        }
