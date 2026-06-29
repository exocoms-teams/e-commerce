# -*- coding: utf-8 -*-
"""
post_install.py — Crée automatiquement :
  - Droits admin
  - Utilisateur intervenant de démo avec fiche complète
  - Mission de démo cohérente
"""
import logging
_logger = logging.getLogger(__name__)


def post_install_hook(env):
    _ensure_certification_table(env)
    _ensure_planning_schema(env)
    _ensure_admin_phone_param(env)
    _ensure_firebase_params(env)
    _setup_admin_rights(env)
    _setup_demo_intervenant(env)
    _cleanup_menus(env)
    _logger.info("[sinistre_services] Post-install hook terminé ✓")


def uninstall_hook(env):
    pass


def _setup_admin_rights(env):
    try:
        admin = env['res.users'].browse(2)
        group = env.ref('sinistre_services.group_sinistre_admin')
        env.cr.execute(
            "INSERT INTO res_groups_users_rel (gid, uid) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (group.id, admin.id)
        )
        _logger.info(f"[sinistre_services] Droits admin → {admin.name}")
    except Exception as e:
        _logger.warning(f"[sinistre_services] Admin rights: {e}")


def _ensure_certification_table(env):
    """Crée la table sinistre_certification si absente (idempotent)."""
    env.cr.execute("""
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
            create_uid      INTEGER,
            write_uid       INTEGER
        )
    """)


def _ensure_planning_schema(env):
    """Colonnes planning + table absences (idempotent)."""
    cr = env.cr
    new_cols = [
        ("planning_slots",    "TEXT"),
        ("iban",              "VARCHAR(64)"),
        ("bic",               "VARCHAR(16)"),
        ("titulaire_compte",  "VARCHAR(128)"),
        ("banque",            "VARCHAR(128)"),
        ("fcm_token",         "VARCHAR(256)"),
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
            _logger.info("[sinistre_services] colonne %s ajoutée", col)

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
        _logger.info("[sinistre_services] table sinistre_intervenant_absence créée")


def _ensure_admin_phone_param(env):
    ICP = env['ir.config_parameter'].sudo()
    if not ICP.get_param('sinistre.admin_phone'):
        ICP.set_param('sinistre.admin_phone', '0X0X0X')


def _ensure_firebase_params(env):
    """Crée les clés de paramètres Firebase si absentes (valeurs à renseigner dans Odoo)."""
    ICP = env['ir.config_parameter'].sudo()
    defaults = {
        'sinistre.firebase_api_key':            '',
        'sinistre.firebase_auth_domain':        '',
        'sinistre.firebase_project_id':         '',
        'sinistre.firebase_storage_bucket':     '',
        'sinistre.firebase_messaging_sender_id': '',
        'sinistre.firebase_app_id':             '',
        'sinistre.firebase_vapid_key':          '',
        'sinistre.fcm_server_key':              '',
    }
    for key, default in defaults.items():
        if not ICP.get_param(key):
            ICP.set_param(key, default)


_DEMO_SPEC_XMLIDS = ('spec_serrurerie', 'spec_plomberie', 'spec_electricite')


def _assign_specialites(env, interv, xml_ids):
    """Assigne des spécialités à un intervenant via leurs XML IDs."""
    spec_ids = []
    for xml_id in xml_ids:
        try:
            spec_ids.append(env.ref(f'sinistre_services.{xml_id}').id)
        except Exception:
            pass
    if spec_ids:
        interv.write({'specialites': [(6, 0, spec_ids)]})


def _ensure_intervenant_specialites(env, interv):
    """Renseigne les spécialités si l'intervenant n'en a pas encore."""
    if interv.specialites:
        return
    login = interv.user_id.login if interv.user_id else ''
    if login == 'thomas.moreau@artisanpro.fr':
        _assign_specialites(env, interv, list(_DEMO_SPEC_XMLIDS))
        return
    # Déduire depuis les missions existantes
    type_ivs = set(
        interv.mission_ids.mapped('type_intervention')
    ) - {False}
    if not type_ivs:
        return
    specs = env['sinistre.specialite'].search([
        ('type_intervention', 'in', list(type_ivs)),
    ])
    if specs:
        interv.write({'specialites': [(6, 0, specs.ids)]})


def _setup_demo_intervenant(env):
    """Crée un intervenant de démo complet avec missions cohérentes."""
    try:
        LOGIN = 'thomas.moreau@artisanpro.fr'
        existing_user = env['res.users'].search([('login', '=', LOGIN)], limit=1)

        if existing_user:
            # S'assurer que la fiche intervenant existe
            interv = env['sinistre.intervenant'].search(
                [('user_id', '=', existing_user.id)], limit=1
            )
            if not interv:
                interv = _create_intervenant_for_user(env, existing_user)
            else:
                _ensure_intervenant_specialites(env, interv)
                # S'assurer qu'il a des missions
                missions = env['sinistre.mission'].search(
                    [('intervenant_id', '=', interv.id)]
                )
                if not missions:
                    _create_demo_missions(env, interv)
            _logger.info(f"[sinistre_services] Intervenant démo déjà existant: {LOGIN}")
            return

        # ── Créer le partenaire ──
        partner = env['res.partner'].create({
            'name':    'Thomas Moreau',
            'email':   LOGIN,
            'phone':   '+33 6 12 34 56 78',
            'street':  '12 rue Oberkampf',
            'city':    'Paris',
            'zip':     '75011',
        })

        # ── Créer l'utilisateur ──
        user = env['res.users'].create({
            'name':       'Thomas Moreau',
            'login':      LOGIN,
            'password':   'artisan123',
            'email':      LOGIN,
            'partner_id': partner.id,
        })

        # ── Ajouter groupe intervenant ──
        try:
            group_interv = env.ref('sinistre_services.group_sinistre_intervenant')
            env.cr.execute(
                "INSERT INTO res_groups_users_rel (gid, uid) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (group_interv.id, user.id)
            )
        except Exception:
            pass

        # ── Créer la fiche intervenant ──
        interv = _create_intervenant_for_user(env, user)

        # ── Créer les missions de démo ──
        _create_demo_missions(env, interv)

        _logger.info(f"[sinistre_services] ✓ Intervenant démo: {LOGIN} / artisan123")

    except Exception as e:
        _logger.warning(f"[sinistre_services] Erreur setup démo: {e}")


def _create_intervenant_for_user(env, user):
    """Crée ou retourne la fiche intervenant pour un utilisateur."""
    interv = env['sinistre.intervenant'].search(
        [('user_id', '=', user.id)], limit=1
    )
    if interv:
        return interv
    interv = env['sinistre.intervenant'].create({
        'name':               user.name,
        'partner_id':         user.partner_id.id,
        'user_id':            user.id,
        'taux_commission':    20.0,
        'disponible':         True,
        'actif':              True,
        'zone_intervention':  'Paris 75',
    })
    _ensure_intervenant_specialites(env, interv)
    return interv


def _create_demo_missions(env, interv):
    """Crée des missions de démo cohérentes."""
    from odoo.fields import Datetime
    import datetime

    now = Datetime.now()

    # Clients de démo
    clients = {}
    for nom, email, tel in [
        ('Mme Laurent',       'laurent@email.fr',      '+33 6 11 22 33 44'),
        ('M. Dubois',         'dubois@email.fr',       '+33 6 55 44 33 22'),
        ('SCI Belleville',    'sci.belleville@fr',     '+33 1 40 00 11 22'),
        ('M. Karam',          'karam@email.fr',        '+33 6 77 88 99 00'),
        ('Mme Petit',         'petit@email.fr',        '+33 6 22 33 44 55'),
    ]:
        p = env['res.partner'].search([('email', '=', email)], limit=1)
        if not p:
            p = env['res.partner'].create({'name': nom, 'email': email, 'phone': tel})
        clients[nom] = p

    # Missions actives
    missions_data = [
        {
            'source':               'assurance',
            'client_id':            clients['Mme Laurent'].id,
            'type_intervention':    'serrurerie',
            'urgence':              'urgente',
            'description_sinistre': 'Ouverture porte claquée',
            'adresse_intervention': '12 rue de la République, Paris 11e',
            'tel_sur_place':        '+33 6 11 22 33 44',
            'intervenant_id':       interv.id,
            'state':                'assigne',
            'date_rdv':             now + datetime.timedelta(hours=2),
        },
        {
            'source':               'particulier',
            'client_id':            clients['M. Dubois'].id,
            'type_intervention':    'plomberie',
            'urgence':              'normale',
            'description_sinistre': 'Fuite sous évier cuisine',
            'adresse_intervention': '45 av. Parmentier, Paris 11e',
            'tel_sur_place':        '+33 6 55 44 33 22',
            'intervenant_id':       interv.id,
            'state':                'en_cours',
            'date_rdv':             now + datetime.timedelta(hours=4),
        },
        {
            'source':               'entreprise',
            'client_id':            clients['SCI Belleville'].id,
            'type_intervention':    'electricite',
            'urgence':              'normale',
            'description_sinistre': 'Mise aux normes tableau électrique',
            'adresse_intervention': '8 rue des Pyrénées, Paris 20e',
            'tel_sur_place':        '+33 1 40 00 11 22',
            'intervenant_id':       interv.id,
            'state':                'rdv_planifie',
            'date_rdv':             now + datetime.timedelta(days=1),
        },
        {
            'source':               'assurance',
            'client_id':            clients['M. Karam'].id,
            'type_intervention':    'plomberie',
            'urgence':              'normale',
            'description_sinistre': 'Depannage chaudiere gaz — code erreur E01',
            'adresse_intervention': '23 bd Voltaire, Paris 11e',
            'tel_sur_place':        '+33 6 77 88 99 00',
            'intervenant_id':       interv.id,
            'state':                'rdv_planifie',
            'date_rdv':             now + datetime.timedelta(days=1, hours=3),
        },
        {
            'source':               'assurance',
            'client_id':            clients['Mme Petit'].id,
            'type_intervention':    'vitrerie',
            'urgence':              'normale',
            'description_sinistre': 'Remplacement vitre cassée — double vitrage 80×120 cm',
            'adresse_intervention': '7 rue Oberkampf, Paris 11e',
            'tel_sur_place':        '+33 6 22 33 44 55',
            'intervenant_id':       interv.id,
            'state':                'en_cours',
            'date_rdv':             now + datetime.timedelta(hours=6),
        },
    ]

    for data in missions_data:
        try:
            env['sinistre.mission'].with_context(skip_mission_push=True).create(data)
        except Exception as e:
            _logger.warning(f"[sinistre_services] Mission création: {e}")

    _logger.info(f"[sinistre_services] ✓ {len(missions_data)} missions de démo créées")


def _cleanup_menus(env):
    try:
        env['website.menu'].search([
            ('name', 'in', ['Home', 'Shop', 'Contact us', 'Contact Us'])
        ]).unlink()
    except Exception:
        pass
