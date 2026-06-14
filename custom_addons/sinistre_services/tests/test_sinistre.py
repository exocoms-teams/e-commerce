# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestSinistreServices(TransactionCase):

    def test_01_mission_creation(self):
        """Vérifie qu'une mission peut être créée avec les champs requis."""
        partner = self.env['res.partner'].create({
            'name': 'Client Test',
            'email': 'test@client.fr',
        })
        mission = self.env['sinistre.mission'].create({
            'source':               'particulier',
            'client_id':            partner.id,
            'type_intervention':    'plomberie',
            'urgence':              'normale',
            'description_sinistre': 'Test fuite',
            'adresse_intervention': '1 rue Test, Paris',
        })
        self.assertTrue(mission.id)
        self.assertTrue(mission.reference)
        self.assertEqual(mission.state, 'nouveau')

    def test_02_intervenant_creation(self):
        """Vérifie qu'un intervenant peut être créé."""
        partner = self.env['res.partner'].create({
            'name': 'Artisan Test',
            'email': 'artisan@test.fr',
        })
        interv = self.env['sinistre.intervenant'].create({
            'name':       'Artisan Test',
            'partner_id': partner.id,
            'disponible': True,
            'actif':      True,
        })
        self.assertTrue(interv.id)
        self.assertEqual(interv.taux_commission, 15.0)

    def test_03_mission_state_workflow(self):
        """Vérifie les transitions d'état d'une mission."""
        partner = self.env['res.partner'].create({'name': 'Client WF'})
        mission = self.env['sinistre.mission'].create({
            'source':               'particulier',
            'client_id':            partner.id,
            'type_intervention':    'serrurerie',
            'urgence':              'urgente',
            'description_sinistre': 'Test workflow',
            'adresse_intervention': '2 rue Test, Paris',
        })
        self.assertEqual(mission.state, 'nouveau')
        mission.write({'state': 'en_cours'})
        self.assertEqual(mission.state, 'en_cours')
