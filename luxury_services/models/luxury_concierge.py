from odoo import models, fields


class LuxuryConciergeRequest(models.Model):
    _name = 'luxury.concierge.request'
    _description = 'Demande Conciergerie VIP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        default='Nouveau',
        readonly=True,
    )

    # =========================
    # CLIENT
    # =========================
    client_name  = fields.Char(string='Nom client', required=True)
    client_firstname = fields.Char(string='Prénom client', required=True)
    client_email = fields.Char(string='Email')
    client_phone = fields.Char(string='Téléphone / WhatsApp')

    # =========================
    # DEMANDE
    # =========================
    type_service = fields.Selection([
        ('hotel',     'Hôtel / Villa de luxe'),
        ('restaurant','Restaurant étoilé'),
        ('evenement', 'Événement privé'),
        ('combine',   'Combiné plusieurs services'),
    ], string='Type de service', tracking=True)

    destination    = fields.Char(string='Destination')
    date_souhaitee = fields.Date(string='Date souhaitée')
    nb_personnes   = fields.Integer(string='Nombre de personnes')
    description    = fields.Text(string='Description de la demande')

    budget = fields.Selection([
        ('5k-10k',  '5 000€ — 10 000€'),
        ('10k-25k', '10 000€ — 25 000€'),
        ('25k-50k', '25 000€ — 50 000€'),
        ('50k+',    '50 000€ et plus'),
    ], string='Budget estimé')

    # =========================
    # STATUT
    # =========================
    state = fields.Selection([
        ('draft',       'Nouvelle'),
        ('in_progress', 'En cours de traitement'),
        ('proposal',    'Proposition envoyée'),
        ('confirmed',   'Confirmée'),
        ('done',        'Terminée'),
        ('cancel',      'Annulée'),
    ], string='Statut', default='draft', tracking=True)

    notes_internes = fields.Text(string='Notes internes')

    # =========================
    # ACTIONS
    # =========================
    def action_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_proposal(self):
        self.write({'state': 'proposal'})

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reset(self):
        self.write({'state': 'draft'})

    # =========================
    # SÉQUENCE
    # =========================
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'luxury.concierge.request'
            ) or 'Nouveau'
        return super().create(vals)