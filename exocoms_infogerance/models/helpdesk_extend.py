from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    x_infogerance_contract_id = fields.Many2one(
        'exocoms.infogerance.contract',
        string='Contrat d\'infogérance')
    x_intervention_type = fields.Selection([
        ('remote', 'À distance (AnyDesk)'),
        ('on_site', 'Sur site'),
        ('both', 'Mixte'),
    ], string='Type d\'intervention', default='remote')
    x_is_paid_upfront = fields.Boolean('Payé à l\'avance')
    x_payment_date = fields.Date('Date de paiement')
    x_anydesk_id = fields.Char('ID AnyDesk')
    x_equipment_id = fields.Many2one('exocoms.infogerance.equipment',
                                     string='Équipement concerné')

    def action_validate_intervention(self):
        self.x_is_paid_upfront = True
        self.x_payment_date = fields.Date.today()
        self.message_post(body="Intervention validée et payée à l'avance.")

    def action_start_anydesk(self):
        action = self.env['ir.actions.act_url'].create({
            'name': 'Lancer AnyDesk',
            'url': 'anydesk://%s' % (self.x_anydesk_id or ''),
            'target': 'new',
        })
        return action
