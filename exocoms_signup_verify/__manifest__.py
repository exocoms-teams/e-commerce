# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS - Validation email à l'inscription",
    "summary": "Confirme l'adresse email avant l'activation du compte portail",
    "description": """
Validation de l'adresse email à la création de compte
=====================================================

Odoo n'impose aucune vérification de l'adresse email lors d'une inscription
libre sur le portail : le compte est créé et l'utilisateur est connecté
immédiatement, avec l'adresse de son choix.

Ce module modifie le flux :

* le visiteur saisit uniquement son **nom** et son **email** ;
* le compte est créé à l'état *Invité*, **sans mot de passe** ;
* un lien d'activation est envoyé à l'adresse saisie ;
* le mot de passe est défini au clic sur ce lien.

Tant que le lien n'est pas utilisé, le compte est inutilisable.

Contrôles supplémentaires :

* normalisation et validation syntaxique de l'adresse ;
* vérification de l'existence du domaine (enregistrement MX) si la librairie
  ``email_validator`` est installée ;
* liste noire de domaines (adresses jetables) configurable ;
* aucune énumération de comptes : le même écran est affiché que l'adresse
  existe déjà ou non.

Le parcours d'inscription sur invitation (lien avec jeton) reste inchangé.
""",
    "version": "19.0.1.0.0",
    "category": "Website/Website",
    "author": "EXOCOMS Group",
    "website": "https://www.exocoms.fr",
    "license": "LGPL-3",
    "depends": [
        "auth_signup",
        "base_setup",
    ],
    "data": [
        "views/auth_signup_templates.xml",
        "views/res_config_settings_views.xml",
    ],
    "external_dependencies": {
        # Optionnelle : sans elle, le contrôle MX est simplement désactivé.
        "python": [],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
