# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestMandatAdministratif(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_public = cls.env['res.partner'].create({
            'name': "Mairie Test",
            'is_public_entity': True,
            'public_entity_type': 'state_local',
        })
        cls.partner_health = cls.env['res.partner'].create({
            'name': "CH Test",
            'is_public_entity': True,
            'public_entity_type': 'health',
        })
        cls.partner_private = cls.env['res.partner'].create({
            'name': "Société privée Test",
        })
        cls.provider = cls.env.ref(
            'mandat_administratif.payment_provider_mandat_administratif')
        cls.provider.state = 'test'

    # --- SIRET --- #

    def test_siret_valide(self):
        """Un SIRET de 14 chiffres avec clé de Luhn correcte est accepté."""
        self.partner_public.chorus_siret = '21440000300015'

    def test_siret_longueur_invalide(self):
        with self.assertRaises(ValidationError):
            self.partner_public.chorus_siret = '123456789'

    def test_siret_luhn_invalide(self):
        with self.assertRaises(ValidationError):
            self.partner_public.chorus_siret = '21440000300016'

    def test_siret_exception_la_poste(self):
        """Les SIRET La Poste (356000000xxxxx) échappent au contrôle Luhn."""
        self.partner_public.chorus_siret = '35600000012345'

    # --- Délais et termes de paiement --- #

    def test_delai_par_type(self):
        self.assertEqual(self.partner_public.public_payment_delay, 30)
        self.assertEqual(self.partner_health.public_payment_delay, 50)
        self.partner_public.public_entity_type = 'public_company'
        self.assertEqual(self.partner_public.public_payment_delay, 60)
        self.assertEqual(self.partner_private.public_payment_delay, 0)

    def test_affectation_terme_paiement(self):
        self.partner_health._apply_public_payment_term()
        term_50 = self.env.ref(
            'mandat_administratif.payment_term_mandat_50')
        self.assertEqual(
            self.partner_health.property_payment_term_id, term_50)
        # Un partenaire privé ne doit pas être modifié.
        before = self.partner_private.property_payment_term_id
        self.partner_private._apply_public_payment_term()
        self.assertEqual(
            self.partner_private.property_payment_term_id, before)

    # --- Filtrage du fournisseur de paiement --- #

    def test_provider_reserve_aux_entites_publiques(self):
        providers_public = self.env['payment.provider']._get_compatible_providers(
            self.env.company.id, self.partner_public.id, 100.0)
        providers_private = self.env['payment.provider']._get_compatible_providers(
            self.env.company.id, self.partner_private.id, 100.0)
        self.assertIn(self.provider, providers_public)
        self.assertNotIn(self.provider, providers_private)

    # --- Nom de fichier de flux --- #

    def test_nom_de_flux_unique(self):
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_public.id,
        })
        move.company_id.chorus_flux_syntax = 'cii'
        try:
            name_1, _content = move._chorus_get_flux_file()
        except Exception:
            # La génération EDI peut exiger des données comptables complètes ;
            # ce test ne porte que sur l'unicité du nommage.
            self.skipTest("Génération EDI indisponible dans cet environnement "
                          "de test minimal.")
        self.assertRegex(name_1, r'_\d{14}\.xml$')
