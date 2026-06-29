# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SinistreCandidature(models.Model):
    _name = 'sinistre.candidature'
    _description = 'Candidature Artisan'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='Référence', readonly=True, copy=False, default='Nouveau')
    prenom = fields.Char(string='Prénom')
    nom = fields.Char(string='Nom', required=True)
    email = fields.Char(string='Email', required=True)
    telephone = fields.Char(string='Téléphone', required=True)
    specialites = fields.Char(string='Spécialités')
    zone_intervention = fields.Char(string="Départements d'intervention")
    siret = fields.Char(string='SIRET', required=True, size=14)
    statut_juridique = fields.Selection([
        ('auto_entrepreneur', 'Auto-entrepreneur'),
        ('sarl', 'SARL / EURL'),
        ('sas', 'SAS / SASU'),
        ('autre', 'Autre'),
    ], string='Statut juridique')
    experience = fields.Char(string='Expérience')
    message = fields.Text(string='Message')
    state = fields.Selection([
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours'),
        ('valide', 'Validé'),
        ('refuse', 'Refusé'),
    ], string='État', default='nouveau', tracking=True)

    doc_certification = fields.Binary(string='Certifications', attachment=True)
    doc_certification_filename = fields.Char(string='Fichier certifications')
    doc_assurance = fields.Binary(string='Assurance décennale / RC Pro', attachment=True)
    doc_assurance_filename = fields.Char(string='Fichier assurance')
    doc_identite = fields.Binary(string="Pièce d'identité", attachment=True)
    doc_identite_filename = fields.Char(string='Fichier identité')
    photo = fields.Binary(string='Photo', attachment=True)
    photo_filename = fields.Char(string='Fichier photo')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'sinistre.candidature'
                ) or 'CAND'
        return super().create(vals_list)
