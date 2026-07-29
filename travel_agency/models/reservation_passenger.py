from odoo import models, fields


class TravelReservationPassenger(models.Model):
    _name = 'travel.reservation.passenger'
    _description = 'Travel Reservation Passenger'

    reservation_id = fields.Many2one('travel.reservation', string='Réservation',
                                      required=True, ondelete='cascade')
    prenom = fields.Char(string='Prénom', required=True)
    nom = fields.Char(string='Nom', required=True)
    date_naissance = fields.Date(string='Date de naissance')
    type = fields.Selection([
        ('adulte', 'Adulte'),
        ('enfant', 'Enfant'),
    ], string='Type', default='adulte', required=True)
