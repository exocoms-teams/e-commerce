# -*- coding: utf-8 -*-
"""
run_setup.py — Setup données de démo ArtisanPro
Détecte automatiquement la base de données active.

Usage depuis n'importe quel dossier :
  odoo-bin shell --no-http << 'PYEOF'
  exec(open('/home/odoo/src/user/custom_addons/sinistre_services/run_setup.py').read())
  PYEOF

Ou directement :
  odoo-bin shell -d $(psql -U odoo -tAc "SELECT datname FROM pg_database WHERE datname LIKE 'exocoms%' LIMIT 1") --no-http < /home/odoo/src/user/custom_addons/sinistre_services/run_setup.py
"""

from odoo import fields as F

LOGIN    = 'thomas.moreau@artisanpro.fr'
PASSWORD = 'artisan123'

print("=" * 60)
print("SETUP ARTISANPRO")
db_name = env.cr.dbname
print(f"Base de données : {db_name}")
print("=" * 60)

# 1. Utilisateur
user = env['res.users'].search([('login', '=', LOGIN)], limit=1)
if not user:
    partner = env['res.partner'].create({
        'name': 'Thomas Moreau', 'email': LOGIN,
        'phone': '+33 6 12 34 56 78', 'street': '12 rue Oberkampf',
        'city': 'Paris', 'zip': '75011',
    })
    user = env['res.users'].create({
        'name': 'Thomas Moreau', 'login': LOGIN,
        'password': PASSWORD, 'email': LOGIN, 'partner_id': partner.id,
    })
    print(f"Utilisateur cree: {LOGIN}")
else:
    user._change_password(PASSWORD)
    print(f"Utilisateur existant, mdp reinitialise: {PASSWORD}")

# 2. Groupe
try:
    g = env.ref('sinistre_services.group_sinistre_intervenant')
    env.cr.execute(
        "INSERT INTO res_groups_users_rel (gid,uid) VALUES (%s,%s) ON CONFLICT DO NOTHING",
        (g.id, user.id)
    )
    print("Groupe intervenant OK")
except Exception as e:
    print(f"Groupe: {e}")

# 3. Intervenant
iv = env['sinistre.intervenant'].search([('user_id', '=', user.id)], limit=1)
if not iv:
    iv = env['sinistre.intervenant'].create({
        'name': 'Thomas Moreau', 'partner_id': user.partner_id.id,
        'user_id': user.id, 'taux_commission': 15.0,
        'disponible': True, 'actif': True, 'zone_intervention': 'Paris 75011',
    })
    print(f"Intervenant cree id={iv.id}")
else:
    print(f"Intervenant existant id={iv.id}")

# 4. Missions
n_existing = env['sinistre.mission'].search_count([('intervenant_id', '=', iv.id)])
if not n_existing:
    cl = {}
    for nom, email, tel in [
        ('Mme Laurent',    'laurent@client.fr',  '+33 6 11 22 33 44'),
        ('M. Dubois',      'dubois@client.fr',   '+33 6 55 44 33 22'),
        ('SCI Belleville', 'sci@belleville.fr',  '+33 1 40 00 11 22'),
        ('M. Karam',       'karam@client.fr',    '+33 6 77 88 99 00'),
        ('Mme Petit',      'petit@client.fr',    '+33 6 22 33 44 55'),
    ]:
        p = env['res.partner'].search([('email', '=', email)], limit=1)
        if not p:
            p = env['res.partner'].create({'name': nom, 'email': email, 'phone': tel})
        cl[nom] = p

    missions = [
        {'source':'assurance','client_id':cl['Mme Laurent'].id,'type_intervention':'serrurerie','urgence':'urgente','description_sinistre':'Ouverture porte claquee — porte 3 points, cle cassee','adresse_intervention':'12 rue de la Republique, Paris 11e','tel_sur_place':'+33 6 11 22 33 44','intervenant_id':iv.id,'state':'assigne'},
        {'source':'particulier','client_id':cl['M. Dubois'].id,'type_intervention':'plomberie','urgence':'normale','description_sinistre':'Fuite sous evier cuisine — joint siphon a remplacer','adresse_intervention':'45 av. Parmentier, Paris 11e','tel_sur_place':'+33 6 55 44 33 22','intervenant_id':iv.id,'state':'en_cours'},
        {'source':'entreprise','client_id':cl['SCI Belleville'].id,'type_intervention':'electricite','urgence':'normale','description_sinistre':'Mise aux normes tableau electrique 2 rangees','adresse_intervention':'8 rue des Pyrenees, Paris 20e','tel_sur_place':'+33 1 40 00 11 22','intervenant_id':iv.id,'state':'rdv_planifie'},
        {'source':'assurance','client_id':cl['M. Karam'].id,'type_intervention':'chauffage','urgence':'normale','description_sinistre':'Depannage chaudiere gaz — code erreur E01','adresse_intervention':'23 bd Voltaire, Paris 11e','tel_sur_place':'+33 6 77 88 99 00','intervenant_id':iv.id,'state':'rdv_planifie'},
        {'source':'assurance','client_id':cl['Mme Petit'].id,'type_intervention':'vitrerie','urgence':'normale','description_sinistre':'Remplacement vitre cassee — double vitrage 80x120','adresse_intervention':'7 rue Oberkampf, Paris 11e','tel_sur_place':'+33 6 22 33 44 55','intervenant_id':iv.id,'state':'en_cours'},
    ]
    created = 0
    for d in missions:
        try:
            m = env['sinistre.mission'].create(d)
            print(f"  Mission {m.reference} — {d['type_intervention']}")
            created += 1
        except Exception as e:
            print(f"  ERREUR: {e}")
    print(f"{created} missions creees")
else:
    print(f"{n_existing} missions existantes")

env.cr.commit()
print(f"\n{'='*60}\nBase    : {db_name}\nLogin   : {LOGIN}\nPassword: {PASSWORD}\n{'='*60}\n")
