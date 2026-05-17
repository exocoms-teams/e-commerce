# -*- coding: utf-8 -*-
"""
post_install.py — Hook exécuté après chaque installation/mise à jour du module
Configure automatiquement :
  - Droits admin pour l'utilisateur Administrator
  - Compte intervenant de test
  - Correction URLs PWA selon la base active
"""
import logging
import os

_logger = logging.getLogger(__name__)


def post_install_hook(env):
    """Appelé automatiquement après installation du module."""
    _setup_admin_rights(env)
    _setup_test_intervenant(env)
    _logger.info("[sinistre_services] Post-install hook terminé")


def uninstall_hook(env):
    pass


def _setup_admin_rights(env):
    """Donne les droits Sinistre Admin à l'utilisateur Administrator."""
    try:
        admin = env['res.users'].browse(2)
        group = env.ref('sinistre_services.group_sinistre_admin')
        env.cr.execute(
            "INSERT INTO res_groups_users_rel (gid, uid) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (group.id, admin.id)
        )
        _logger.info(f"[sinistre_services] Droits admin ajoutés à {admin.name}")
    except Exception as e:
        _logger.warning(f"[sinistre_services] Impossible d'ajouter droits admin: {e}")


def _setup_test_intervenant(env):
    """Crée un compte intervenant de test si inexistant."""
    try:
        existing = env['res.users'].search([('login', '=', 'intervenant@test.fr')])
        if existing:
            _logger.info("[sinistre_services] Intervenant test déjà existant")
            return

        # Créer l'utilisateur
        user = env['res.users'].create({
            'name':     'Test Intervenant',
            'login':    'intervenant@test.fr',
            'password': 'intervenant123',
            'email':    'intervenant@test.fr',
        })

        # Créer le partenaire
        partner = env['res.partner'].create({
            'name':  'Test Intervenant',
            'email': 'intervenant@test.fr',
            'phone': '0600000000',
        })

        # Créer la fiche intervenant
        interv = env['sinistre.intervenant'].create({
            'name':             'Test Intervenant',
            'partner_id':       partner.id,
            'user_id':          user.id,
            'taux_commission':  15.0,
            'disponible':       True,
            'actif':            True,
        })

        # Ajouter le groupe intervenant
        group_interv = env.ref('sinistre_services.group_sinistre_intervenant')
        env.cr.execute(
            "INSERT INTO res_groups_users_rel (gid, uid) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (group_interv.id, user.id)
        )

        # Créer un client test
        client = env['res.partner'].create({
            'name':  'Client Test',
            'phone': '0612345678',
            'email': 'client@test.fr',
        })

        # Créer une mission test
        mission = env['sinistre.mission'].create({
            'source':               'particulier',
            'client_id':            client.id,
            'type_intervention':    'plomberie',
            'urgence':              'urgente',
            'description_sinistre': 'Fuite sous évier cuisine — mission de test',
            'adresse_intervention': '5 rue de la Paix, 75001 Paris',
            'tel_sur_place':        '0612345678',
            'intervenant_id':       interv.id,
            'state':                'rdv_planifie',
        })

        _logger.info(f"[sinistre_services] Intervenant test créé: {user.login}")
        _logger.info(f"[sinistre_services] Mission test créée: {mission.reference}")

    except Exception as e:
        _logger.warning(f"[sinistre_services] Erreur création intervenant test: {e}")
