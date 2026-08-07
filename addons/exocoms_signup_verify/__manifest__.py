# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS - Validation email à l'inscription",
    "summary": "Confirme l'adresse email avant l'activation du compte portail",
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