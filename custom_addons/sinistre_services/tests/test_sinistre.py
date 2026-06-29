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
        self.assertEqual(interv.taux_commission, 20.0)

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

    def test_04_zone_matching(self):
        """Vérifie le matching géographique secteur artisan ↔ adresse mission."""
        from odoo.addons.sinistre_services.models import zone_utils

        self.assertTrue(
            zone_utils.adresse_dans_zone('12 rue Test, 75011 Paris', 'Paris 75')
        )
        self.assertTrue(
            zone_utils.adresse_dans_zone('7 rue Oberkampf, Paris 11e', '75011')
        )
        self.assertFalse(
            zone_utils.adresse_dans_zone('10 rue de Lyon, 69001 Lyon', 'Paris 75')
        )
        self.assertTrue(
            zone_utils.adresse_dans_zone('10 rue de Lyon, 69001 Lyon', '')
        )

        partner = self.env['res.partner'].create({'name': 'Artisan Zone'})
        artisan_paris = self.env['sinistre.intervenant'].create({
            'name': 'Artisan Paris',
            'partner_id': partner.id,
            'zone_intervention': '75, 75011',
            'disponible': True,
            'actif': True,
        })
        artisan_lyon = self.env['sinistre.intervenant'].create({
            'name': 'Artisan Lyon',
            'partner_id': self.env['res.partner'].create({'name': 'P Lyon'}).id,
            'zone_intervention': '69',
            'disponible': True,
            'actif': True,
        })
        self.assertTrue(artisan_paris.couvre_adresse('45 av. Parmentier, 75011 Paris'))
        self.assertFalse(artisan_paris.couvre_adresse('10 rue de Lyon, 69001 Lyon'))
        self.assertTrue(artisan_lyon.couvre_adresse('10 rue de Lyon, 69001 Lyon'))
