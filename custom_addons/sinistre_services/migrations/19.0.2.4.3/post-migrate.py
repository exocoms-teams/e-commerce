# -*- coding: utf-8 -*-
"""Migration 2.4.3 — vérifie la table sinistre_proposition_reponse."""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute("""
        SELECT 1 FROM information_schema.tables
         WHERE table_name = 'sinistre_proposition_reponse'
    """)
    if cr.fetchone():
        _logger.info("[sinistre 2.4.3] table sinistre_proposition_reponse OK")
    else:
        _logger.warning(
            "[sinistre 2.4.3] table sinistre_proposition_reponse absente — "
            "relancer la mise à jour du module sinistre_services"
        )
