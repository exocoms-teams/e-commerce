from odoo import models, fields


class SerruproFaqQuestion(models.Model):
	_name = 'serrupro.faq.question'
	_description = 'SerruPro FAQ Question'

	name = fields.Char('Question', required=True)
	answer = fields.Text('Réponse')
	contact_email = fields.Char('Email')
	state = fields.Selection([
		('new', 'Nouvelle question'),
		('answered', 'Répondu'),
	], string='Statut', default='new')
	published = fields.Boolean('Publié', default=False)