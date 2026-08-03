# -*- coding: utf-8 -*-
from odoo import fields, models, _


class SinistreNoteInterneWizard(models.TransientModel):
    _name = 'sinistre.note.interne.wizard'
    _description = 'Ajouter une note interne'

    mission_id = fields.Many2one('sinistre.mission', required=True)
    note = fields.Text(string='Note interne', required=True)

    def action_enregistrer(self):
        self.ensure_one()
        existing = self.mission_id.commentaire_interne or ''
        sep = '\n---\n' if existing else ''
        self.mission_id.write({
            'commentaire_interne': existing + sep + self.note,
        })
        self.mission_id.message_post(body=_("Note interne ajoutée : %s") % self.note[:200])
        return {'type': 'ir.actions.act_window_close'}


class SinistreMessagePlateformeWizard(models.TransientModel):
    _name = 'sinistre.message.plateforme.wizard'
    _description = 'Message plateforme vers artisan'

    mission_id = fields.Many2one('sinistre.mission', required=True)
    contenu = fields.Text(string='Message', required=True)

    def action_envoyer(self):
        self.ensure_one()
        self.env['sinistre.message'].create({
            'mission_id':   self.mission_id.id,
            'auteur_type':  'plateforme',
            'auteur_nom':   'Plateforme',
            'contenu':      self.contenu,
            'lu_artisan':   False,
        })
        self.mission_id.message_post(body=_("Message plateforme : %s") % self.contenu[:200])
        return {'type': 'ir.actions.act_window_close'}
