# -*- coding: utf-8 -*-
"""
Migration 19.0.2.1.0 — Création table sinistre_certification + champs v2.2.0
"""
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):

    # ── Table certification ───────────────────────────────────────────
    cr.execute("""
        CREATE TABLE IF NOT EXISTS sinistre_certification (
            id              SERIAL PRIMARY KEY,
            intervenant_id  INTEGER NOT NULL
                            REFERENCES sinistre_intervenant(id)
                            ON DELETE CASCADE,
            name            VARCHAR(255) NOT NULL,
            date_validite   DATE,
            sequence        INTEGER DEFAULT 10,
            create_date     TIMESTAMP DEFAULT NOW(),
            write_date      TIMESTAMP DEFAULT NOW(),
            create_uid      INTEGER REFERENCES res_users(id),
            write_uid       INTEGER REFERENCES res_users(id)
        )
    """)
    _logger.info("[sinistre_services] ✓ Table sinistre_certification OK")

    cr.execute("""
        INSERT INTO ir_model (model, name, state, transient)
        SELECT 'sinistre.certification', 'Certification Intervenant', 'base', false
        WHERE NOT EXISTS (
            SELECT 1 FROM ir_model WHERE model = 'sinistre.certification'
        )
    """)

    # ── Données de démo — Thomas Moreau ──────────────────────────────
    cr.execute("SELECT id FROM res_users WHERE login = 'thomas.moreau@artisanpro.fr' LIMIT 1")
    row = cr.fetchone()
    if row:
        user_id = row[0]
        cr.execute("SELECT id FROM sinistre_intervenant WHERE user_id = %s LIMIT 1", (user_id,))
        iv_row = cr.fetchone()
        if iv_row:
            iv_id = iv_row[0]

            for nom, type_iv in [
                ('Serrurerie',  'serrurerie'),
                ('Plomberie',   'plomberie'),
                ('Electricite', 'electricite'),
            ]:
                cr.execute("""
                    INSERT INTO sinistre_specialite (name, type_intervention)
                    SELECT %s, %s WHERE NOT EXISTS (
                        SELECT 1 FROM sinistre_specialite WHERE name = %s
                    )
                """, (nom, type_iv, nom))
                cr.execute("SELECT id FROM sinistre_specialite WHERE name = %s LIMIT 1", (nom,))
                spec = cr.fetchone()
                if spec:
                    cr.execute("""
                        INSERT INTO sinistre_intervenant_sinistre_specialite_rel
                            (sinistre_intervenant_id, sinistre_specialite_id)
                        SELECT %s, %s WHERE NOT EXISTS (
                            SELECT 1 FROM sinistre_intervenant_sinistre_specialite_rel
                            WHERE sinistre_intervenant_id = %s AND sinistre_specialite_id = %s
                        )
                    """, (iv_id, spec[0], iv_id, spec[0]))

            for nom, annee in [
                ('Assurance RC Pro',   2027),
                ('Qualibat Plomberie', 2026),
                ('Kbis verifie',       None),
            ]:
                date_val = f"{annee}-12-31" if annee else None
                cr.execute("""
                    INSERT INTO sinistre_certification
                        (intervenant_id, name, date_validite, create_uid, write_uid)
                    SELECT %s, %s, %s, 1, 1 WHERE NOT EXISTS (
                        SELECT 1 FROM sinistre_certification
                        WHERE intervenant_id = %s AND name = %s
                    )
                """, (iv_id, nom, date_val, iv_id, nom))

            _logger.info("[sinistre_services] ✓ Données Thomas Moreau migrées")

    # ── Champs v2.2.0 ────────────────────────────────────────────────
    _logger.info("Migration 2.2.0 — ajout champs signature, notes, estimations")

    cr.execute("""
        ALTER TABLE sinistre_mission
        ADD COLUMN IF NOT EXISTS signature_avant        TEXT,
        ADD COLUMN IF NOT EXISTS signature_apres        TEXT,
        ADD COLUMN IF NOT EXISTS notes_artisan          TEXT,
        ADD COLUMN IF NOT EXISTS montant_estime         NUMERIC,
        ADD COLUMN IF NOT EXISTS montant_estime_max     NUMERIC
    """)

    cr.execute("""
        ALTER TABLE sinistre_devis
        ADD COLUMN IF NOT EXISTS signature_client_modif TEXT
    """)

    _logger.info("[sinistre_services] ✓ Migration 2.2.0 terminée")
