# -*- coding: utf-8 -*-
"""Migration 2.4.16 — icône module + spécialités intervenants."""
import logging

_logger = logging.getLogger(__name__)

_DEMO_LOGIN = 'thomas.moreau@artisanpro.fr'
_DEMO_SPEC_XMLIDS = ('spec_serrurerie', 'spec_plomberie', 'spec_electricite')


def _link_specialite(cr, interv_id, spec_id):
    cr.execute("""
        INSERT INTO sinistre_intervenant_sinistre_specialite_rel
            (sinistre_intervenant_id, sinistre_specialite_id)
        SELECT %s, %s
         WHERE NOT EXISTS (
               SELECT 1
                 FROM sinistre_intervenant_sinistre_specialite_rel
                WHERE sinistre_intervenant_id = %s
                  AND sinistre_specialite_id = %s
           )
    """, (interv_id, spec_id, interv_id, spec_id))


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    demo_spec_ids = []
    for xml_id in _DEMO_SPEC_XMLIDS:
        try:
            demo_spec_ids.append(env.ref(f'sinistre_services.{xml_id}').id)
        except Exception:
            pass

    # ── Thomas Moreau (intervenant de démo) ──────────────────────────
    cr.execute("""
        SELECT i.id
          FROM sinistre_intervenant i
          JOIN res_users u ON u.id = i.user_id
         WHERE u.login = %s
         LIMIT 1
    """, (_DEMO_LOGIN,))
    row = cr.fetchone()
    if row and demo_spec_ids:
        for spec_id in demo_spec_ids:
            _link_specialite(cr, row[0], spec_id)
        _logger.info("[sinistre 2.4.16] spécialités démo → Thomas Moreau")

    # ── Autres intervenants : déduire depuis leurs missions ──────────
    cr.execute("""
        SELECT DISTINCT i.id, m.type_intervention
          FROM sinistre_intervenant i
          JOIN sinistre_mission m ON m.intervenant_id = i.id
         WHERE m.type_intervention IS NOT NULL
           AND NOT EXISTS (
               SELECT 1
                 FROM sinistre_intervenant_sinistre_specialite_rel r
                WHERE r.sinistre_intervenant_id = i.id
           )
    """)
    for interv_id, type_iv in cr.fetchall():
        cr.execute("""
            SELECT id FROM sinistre_specialite
             WHERE type_intervention = %s
             ORDER BY id
             LIMIT 1
        """, (type_iv,))
        spec = cr.fetchone()
        if spec:
            _link_specialite(cr, interv_id, spec[0])

    _logger.info("[sinistre 2.4.16] spécialités renseignées")
