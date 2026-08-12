# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAvis(TransactionCase):
    """Vérifie que la note d'un avis client est bornée entre 1 et 5."""

    def _create_avis(self, note):
        return self.env['matelas.avis'].create({
            'name': "Testeur",
            'note': note,
            'commentaire': "Commentaire de test",
        })

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
