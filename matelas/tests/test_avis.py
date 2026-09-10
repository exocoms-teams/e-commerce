# -*- coding: utf-8 -*-
from types import SimpleNamespace
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..controllers import main as main_controller


class TestAvis(TransactionCase):
    """Teste la validation et la modération des avis clients."""

    def _create_avis(self, note=5, **values):
        vals = {
            'name': "Testeur",
            'note': note,
            'titre': "Avis de test",
            'commentaire': "Commentaire de test",
        }
        vals.update(values)
        return self.env['matelas.avis'].create(vals)

    def test_note_valide(self):
        for note in (1, 3, 5):
            avis = self._create_avis(note)
            self.assertEqual(avis.note, note)

    def test_note_trop_basse(self):
        with self.assertRaises(ValidationError):
            self._create_avis(0)

    def test_note_negative(self):
        with self.assertRaises(ValidationError):
            self._create_avis(-5)

    def test_note_trop_haute(self):
        with self.assertRaises(ValidationError):
            self._create_avis(27)

    def test_avis_non_publie_par_defaut(self):
        """Un nouvel avis doit rester en attente de modération."""
        avis = self._create_avis()

        self.assertFalse(
            avis.is_published,
            "Un nouvel avis ne doit pas être publié automatiquement.",
        )

    def test_avis_non_publie_absent_de_la_recherche_publique(self):
        """La recherche utilisée par /avis ne retourne que les avis publiés."""
        avis_non_publie = self._create_avis(
            titre="Avis non publié",
        )
        avis_publie = self._create_avis(
            titre="Avis publié",
            is_published=True,
        )

        avis_publics = self.env['matelas.avis'].search([
            ('is_published', '=', True),
            ('id', 'in', [avis_non_publie.id, avis_publie.id]),
        ])

        self.assertNotIn(avis_non_publie, avis_publics)
        self.assertIn(avis_publie, avis_publics)

    def test_soumission_cree_notification_administrateur(self):
        """Une soumission crée une activité pour chaque administrateur."""
        fake_request = SimpleNamespace(env=self.env)
        controller = main_controller.MatelasVente()

        with (
            patch.object(main_controller, 'request', fake_request),
            patch.object(
                main_controller.MatelasVente,
                '_partner_has_purchased',
                return_value=True,
            ),
        ):
            result = controller.avis_submit(
                name="Client Test",
                note=5,
                titre="Avis avec notification",
                commentaire="Avis soumis pendant un test automatisé.",
                profession="Testeur",
            )

        self.assertTrue(result['success'])

        avis = self.env['matelas.avis'].search([
            ('titre', '=', "Avis avec notification"),
        ], limit=1)

        self.assertTrue(avis)
        self.assertFalse(avis.is_published)

        administrators = (
            self.env.ref('base.group_system')
            .sudo()
            .all_user_ids
            .filtered(lambda user: user.active and not user.share)
        )

        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'matelas.avis'),
            ('res_id', '=', avis.id),
            ('activity_type_id', '=',
             self.env.ref('mail.mail_activity_data_todo').id),
            ('summary', '=', "Nouvel avis à modérer"),
        ])

        self.assertEqual(
            set(activities.user_id.ids),
            set(administrators.ids),
            "Chaque administrateur doit recevoir une activité de modération.",
        )
