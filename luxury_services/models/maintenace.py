from odoo import models, fields


class LuxuryMaintenanceRequest(models.Model):
    _name = 'luxury.maintenance.request'
    _description = 'Demande Maintenance VIP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        default='Nouveau'
    )

    # =========================
    # CLIENT
    # =========================

    client_name = fields.Char(string='Nom client', required=True)
    client_firstname = fields.Char(string='Prénom client', required=True)
    client_email = fields.Char(string='Email')
    client_phone = fields.Char(string='Téléphone')

    # =========================
    # VÉHICULE
    # =========================

    type_vehicule = fields.Selection([
        ('yacht', 'Yacht'),
        ('jet', 'Jet Privé'),
    ], string='Type véhicule')

    annee = fields.Integer(string='Année')
    modele = fields.Char(string='Modèle')

    # =========================
    # INTERVENTION
    # =========================

    type_intervention = fields.Selection([
        ('mecanique', 'Maintenance mécanique'),
        ('electronique', 'Électronique'),
        ('coque', 'Coque'),
        ('interieur', 'Intérieur'),
        ('avionique', 'Avionique'),
        ('revision', 'Révision complète'),
        ('autre', 'Autre'),
    ], string='Intervention')

    localisation = fields.Char(string='Localisation')
    description = fields.Text(string='Description')

    # =========================
    # STATUS
    # =========================

    state = fields.Selection([
        ('draft', 'Nouvelle'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancel', 'Annulée'),
    ], string='Statut', default='draft',tracking=True)

    def action_in_progress(self):
        self.state = 'in_progress'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def action_reset(self):
        self.state = 'draft'

    # =========================
    # SÉQUENCE
    # =========================

    def create(self, vals):

        if vals.get('name', 'Nouveau') == 'Nouveau':

            vals['name'] = self.env['ir.sequence'].next_by_code(
                'luxury.maintenance.request'
            ) or 'Nouveau'

        return super().create(vals)