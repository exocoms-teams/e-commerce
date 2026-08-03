# -*- coding: utf-8 -*-
"""Migration 2.4.17 — commission 20 %, spécialité maçonnerie."""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute("""
        UPDATE sinistre_intervenant
           SET taux_commission = 20.0
         WHERE taux_commission = 15.0
    """)
    _logger.info("[sinistre 2.4.17] taux commission 15 → 20 %%")

    cr.execute("""
        INSERT INTO sinistre_specialite (name, type_intervention, color)
        SELECT 'Maçonnerie', 'maconnerie', 7
         WHERE NOT EXISTS (
               SELECT 1 FROM sinistre_specialite WHERE type_intervention = 'maconnerie'
           )
    """)
    _logger.info("[sinistre 2.4.17] spécialité Maçonnerie OK")
