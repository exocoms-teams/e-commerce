# -*- coding: utf-8 -*-
"""
Migration 19.0.2.1.0 — Création table sinistre_certification
S'exécute automatiquement à chaque mise à jour du module.
"""
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Crée la table sinistre_certification si absente."""

    # Table certification
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

    # Enregistrer le modèle dans ir_model si absent
    cr.execute("""
        INSERT INTO ir_model (model, name, state, transient)
        SELECT 'sinistre.certification', 'Certification Intervenant', 'base', false
        WHERE NOT EXISTS (
            SELECT 1 FROM ir_model WHERE model = 'sinistre.certification'
        )
    """)

    # Données de démo — Thomas Moreau
    cr.execute("""
        SELECT id FROM res_users WHERE login = 'thomas.moreau@artisanpro.fr' LIMIT 1
    """)
    row = cr.fetchone()
    if not row:
        return

    user_id = row[0]
    cr.execute("""
        SELECT id FROM sinistre_intervenant WHERE user_id = %s LIMIT 1
    """, (user_id,))
    iv_row = cr.fetchone()
    if not iv_row:
        return

    iv_id = iv_row[0]

    # Spécialités — s'assurer qu'elles existent
    for nom, type_iv in [
        ('Serrurerie',  'serrurerie'),
        ('Plomberie',   'plomberie'),
        ('Electricite', 'electricite'),
    ]:
        cr.execute("""
            INSERT INTO sinistre_specialite (name, type_intervention)
            SELECT %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM sinistre_specialite WHERE name = %s
            )
        """, (nom, type_iv, nom))

        # Lier à l'intervenant
        cr.execute("SELECT id FROM sinistre_specialite WHERE name = %s LIMIT 1", (nom,))
        spec = cr.fetchone()
        if spec:
            cr.execute("""
                INSERT INTO sinistre_intervenant_sinistre_specialite_rel
                    (sinistre_intervenant_id, sinistre_specialite_id)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM sinistre_intervenant_sinistre_specialite_rel
                    WHERE sinistre_intervenant_id = %s
                    AND sinistre_specialite_id = %s
                )
            """, (iv_id, spec[0], iv_id, spec[0]))

    # Certifications — insérer si absentes
    for nom, annee in [
        ('Assurance RC Pro',  2027),
        ('Qualibat Plomberie', 2026),
        ('Kbis verifie',       None),
    ]:
        date_val = f"{annee}-12-31" if annee else None
        cr.execute("""
            INSERT INTO sinistre_certification
                (intervenant_id, name, date_validite, create_uid, write_uid)
            SELECT %s, %s, %s, 1, 1
            WHERE NOT EXISTS (
                SELECT 1 FROM sinistre_certification
                WHERE intervenant_id = %s AND name = %s
            )
        """, (iv_id, nom, date_val, iv_id, nom))

    _logger.info("[sinistre_services] ✓ Données Thomas Moreau migrées")
