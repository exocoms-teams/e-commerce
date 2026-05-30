# -*- coding: utf-8 -*-
"""
run_setup.py — Script à exécuter via odoo-bin shell pour créer les données de démo.

Usage Odoo.sh :
  odoo-bin shell -d VOTRE_DB --no-http < run_setup.py

Ou dans le terminal Odoo.sh :
  python run_setup.py  (depuis un shell connecté à la base)
"""

import sys
import logging
_logger = logging.getLogger(__name__)

def run(env):
    """Point d'entrée — appeler avec env Odoo."""
    print("=" * 60)
    print("SETUP ARTISANPRO — Création données de démo")
    print("=" * 60)

    LOGIN    = 'thomas.moreau@artisanpro.fr'
    PASSWORD = 'artisan123'

    # ── 1. Utilisateur ────────────────────────────────────────────
    user = env['res.users'].search([('login', '=', LOGIN)], limit=1)
    if not user:
        partner = env['res.partner'].create({
            'name':   'Thomas Moreau',
            'email':  LOGIN,
            'phone':  '+33 6 12 34 56 78',
            'street': '12 rue Oberkampf',
            'city':   'Paris',
            'zip':    '75011',
        })
        user = env['res.users'].create({
            'name':       'Thomas Moreau',
            'login':      LOGIN,
            'password':   PASSWORD,
            'email':      LOGIN,
            'partner_id': partner.id,
        })
        print(f"✓ Utilisateur créé : {LOGIN} / {PASSWORD}")
    else:
        # Réinitialiser le mot de passe
        user.write({'password': PASSWORD})
        print(f"✓ Utilisateur existant — mot de passe réinitialisé : {PASSWORD}")

    # ── 2. Groupe intervenant ──────────────────────────────────────
    try:
        group = env.ref('sinistre_services.group_sinistre_intervenant')
        env.cr.execute(
            "INSERT INTO res_groups_users_rel (gid, uid) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (group.id, user.id)
        )
        print(f"✓ Groupe intervenant assigné")
    except Exception as e:
        print(f"⚠ Groupe : {e}")

    # ── 3. Fiche intervenant ───────────────────────────────────────
    interv = env['sinistre.intervenant'].search([('user_id', '=', user.id)], limit=1)
    if not interv:
        interv = env['sinistre.intervenant'].create({
            'name':              'Thomas Moreau',
            'partner_id':        user.partner_id.id,
            'user_id':           user.id,
            'taux_commission':   15.0,
            'disponible':        True,
            'actif':             True,
            'zone_intervention': 'Paris 75011',
        })
        print(f"✓ Fiche intervenant créée (id={interv.id})")
    else:
        print(f"✓ Fiche intervenant existante (id={interv.id})")

    # ── 4. Missions de démo ────────────────────────────────────────
    existing = env['sinistre.mission'].search([('intervenant_id', '=', interv.id)])
    if existing:
        print(f"✓ {len(existing)} missions existantes — pas de recréation")
    else:
        import datetime
        now = fields.Datetime.now() if hasattr(fields, 'Datetime') else __import__('datetime').datetime.now()

        clients_data = [
            ('Mme Laurent',    'laurent@client.fr',   '+33 6 11 22 33 44'),
            ('M. Dubois',      'dubois@client.fr',    '+33 6 55 44 33 22'),
            ('SCI Belleville', 'sci@belleville.fr',   '+33 1 40 00 11 22'),
            ('M. Karam',       'karam@client.fr',     '+33 6 77 88 99 00'),
            ('Mme Petit',      'petit@client.fr',     '+33 6 22 33 44 55'),
        ]
        clients = {}
        for nom, email, tel in clients_data:
            p = env['res.partner'].search([('email', '=', email)], limit=1)
            if not p:
                p = env['res.partner'].create({'name': nom, 'email': email, 'phone': tel})
            clients[nom] = p

        missions_data = [
            {
                'source':               'assurance',
                'client_id':            clients['Mme Laurent'].id,
                'type_intervention':    'serrurerie',
                'urgence':              'urgente',
                'description_sinistre': 'Ouverture porte claquée — porte 3 points classique, clé cassée dans la serrure',
                'adresse_intervention': '12 rue de la République, Paris 11e',
                'tel_sur_place':        '+33 6 11 22 33 44',
                'intervenant_id':       interv.id,
                'state':                'assigne',
            },
            {
                'source':               'particulier',
                'client_id':            clients['M. Dubois'].id,
                'type_intervention':    'plomberie',
                'urgence':              'normale',
                'description_sinistre': 'Fuite sous évier cuisine — joint siphon à remplacer, fuite active',
                'adresse_intervention': '45 av. Parmentier, Paris 11e',
                'tel_sur_place':        '+33 6 55 44 33 22',
                'intervenant_id':       interv.id,
                'state':                'en_cours',
            },
            {
                'source':               'entreprise',
                'client_id':            clients['SCI Belleville'].id,
                'type_intervention':    'electricite',
                'urgence':              'normale',
                'description_sinistre': 'Mise aux normes tableau électrique 2 rangées — NF C 15-100',
                'adresse_intervention': '8 rue des Pyrénées, Paris 20e',
                'tel_sur_place':        '+33 1 40 00 11 22',
                'intervenant_id':       interv.id,
                'state':                'rdv_planifie',
            },
            {
                'source':               'assurance',
                'client_id':            clients['M. Karam'].id,
                'type_intervention':    'chauffage',
                'urgence':              'normale',
                'description_sinistre': 'Dépannage chaudière gaz — code erreur E01, plus eau chaude',
                'adresse_intervention': '23 bd Voltaire, Paris 11e',
                'tel_sur_place':        '+33 6 77 88 99 00',
                'intervenant_id':       interv.id,
                'state':                'rdv_planifie',
            },
            {
                'source':               'assurance',
                'client_id':            clients['Mme Petit'].id,
                'type_intervention':    'vitrerie',
                'urgence':              'normale',
                'description_sinistre': 'Remplacement vitre cassée — double vitrage 80×120 cm, tentative effraction',
                'adresse_intervention': '7 rue Oberkampf, Paris 11e',
                'tel_sur_place':        '+33 6 22 33 44 55',
                'intervenant_id':       interv.id,
                'state':                'en_cours',
            },
        ]

        created = 0
        for data in missions_data:
            try:
                m = env['sinistre.mission'].create(data)
                print(f"  ✓ Mission {m.reference} — {data['description_sinistre'][:40]}…")
                created += 1
            except Exception as e:
                print(f"  ✗ Erreur mission: {e}")

        print(f"✓ {created} missions créées")

    env.cr.commit()

    print()
    print("=" * 60)
    print("RÉSUMÉ")
    print(f"  Login    : {LOGIN}")
    print(f"  Mot de passe : {PASSWORD}")
    print(f"  Intervenant  : {interv.name} (id={interv.id})")
    missions_count = env['sinistre.mission'].search_count([('intervenant_id', '=', interv.id)])
    print(f"  Missions     : {missions_count}")
    print("=" * 60)
    print()
    print("Accès PWA : /pwa/ ou /sinistre_services/static/pwa/index.html")
    print()


# ── Auto-exécution si lancé via odoo-bin shell ──────────────────
try:
    from odoo import fields
    run(env)
except NameError:
    print("Ce script doit être exécuté via : odoo-bin shell -d VOTRE_DB --no-http < run_setup.py")
