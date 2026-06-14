# -*- coding: utf-8 -*-
"""
Migration 2.3.0 — Ajout :
  - sinistre_intervenant : planning_slots, iban, bic, titulaire_compte, banque
  - sinistre_intervenant_absence : nouvelle table
"""
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("[sinistre 2.3.0] pre-migrate START")

    # ── Colonnes sur sinistre_intervenant ────────────────────────────
    new_cols = [
        ("planning_slots",    "TEXT"),
        ("iban",              "VARCHAR(64)"),
        ("bic",               "VARCHAR(16)"),
        ("titulaire_compte",  "VARCHAR(128)"),
        ("banque",            "VARCHAR(128)"),
    ]
    for col, col_type in new_cols:
        cr.execute("""
            SELECT 1 FROM information_schema.columns
             WHERE table_name = 'sinistre_intervenant' AND column_name = %s
        """, (col,))
        if not cr.fetchone():
            cr.execute(
                f"ALTER TABLE sinistre_intervenant ADD COLUMN {col} {col_type}"
            )
            _logger.info(f"[sinistre 2.3.0] colonne {col} ajoutée")

    # ── Table sinistre_intervenant_absence ───────────────────────────
    cr.execute("""
        SELECT 1 FROM information_schema.tables
         WHERE table_name = 'sinistre_intervenant_absence'
    """)
    if not cr.fetchone():
        cr.execute("""
            CREATE TABLE sinistre_intervenant_absence (
                id              SERIAL PRIMARY KEY,
                intervenant_id  INTEGER NOT NULL
                                REFERENCES sinistre_intervenant(id) ON DELETE CASCADE,
                date_debut      DATE NOT NULL,
                date_fin        DATE NOT NULL,
                motif           VARCHAR(256),
                create_uid      INTEGER REFERENCES res_users(id),
                write_uid       INTEGER REFERENCES res_users(id),
                create_date     TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                write_date      TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            )
        """)
        cr.execute("""
            CREATE INDEX idx_absence_intervenant
                ON sinistre_intervenant_absence(intervenant_id)
        """)
        cr.execute("""
            CREATE INDEX idx_absence_dates
                ON sinistre_intervenant_absence(date_debut, date_fin)
        """)
        _logger.info("[sinistre 2.3.0] table sinistre_intervenant_absence créée")

    _logger.info("[sinistre 2.3.0] pre-migrate END")
