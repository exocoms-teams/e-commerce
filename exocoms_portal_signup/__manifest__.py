# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS - Inscription portail securisee",
    "version": "19.0.1.0.0",
    "category": "Website/Website",
    "summary": "Verification de l'adresse email et activation du compte par lien (double opt-in)",
    "description": """
EXOCOMS - Inscription portail securisee
=======================================

Module unique regroupant la verification de l'adresse email et l'activation
du compte par lien. Il remplace `exocoms_signup_verify` et
`exocoms_signup_activation`, qui ne doivent plus etre installes : deux modules
surchargeant `/web/signup` ne peuvent pas cohabiter de facon fiable.

Verification de l'adresse (avant creation du compte)
----------------------------------------------------
* controle du format ;
* refus des domaines jetables (liste editable dans l'interface) ;
* controle de l'enregistrement MX du domaine (optionnel, degradation propre
  si `dnspython` est absent) ;
* restriction facultative a une liste blanche de domaines.

Activation du compte (double opt-in)
-------------------------------------
* le compte est cree puis archive : aucune connexion possible ;
* un jeton a usage unique est envoye par email ;
* le clic sur le lien active le compte ;
* renvoi de l'email protege par un delai et un plafond ;
* purge automatique des inscriptions jamais activees.

Architecture
------------
Le controleur se greffe sur `_signup_with_values()`, point d'extension natif
appele par `do_signup()` **apres** la validation Odoo du formulaire. Toute la
validation native est donc conservee telle quelle.

Les invitations emises depuis le back-office (jeton de signup Odoo) conservent
le comportement natif : elles ne sont pas soumises a la verification.
""",
    "author": "EXOCOMS Group",
    "website": "https://exocoms.fr",
    "license": "LGPL-3",
    "depends": ["auth_signup", "website", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "data/signup_domain_data.xml",
        "data/mail_template_data.xml",
        "data/ir_cron_data.xml",
        "views/signup_templates.xml",
        "views/signup_domain_views.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
