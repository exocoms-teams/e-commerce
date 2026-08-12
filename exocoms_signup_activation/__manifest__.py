# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS - Activation de compte par email",
    "version": "19.0.2.0.1",
    "category": "Website/Website",
    "summary": "Double opt-in : le compte portail n'est actif qu'apres clic sur le lien recu par email",
    "description": """
EXOCOMS - Activation de compte par email (double opt-in)
========================================================

A l'inscription sur le portail (/web/signup) :

* le compte est cree puis archive (active = False) ;
* un jeton d'activation a usage unique est genere (duree de vie parametrable) ;
* un email d'activation est envoye au client ;
* l'utilisateur n'est PAS connecte automatiquement ;
* le clic sur le lien active le compte et propose la page de connexion ;
* une tentative de connexion sur un compte non active affiche un message
  explicite avec un bouton de renvoi (protege contre le spam) ;
* un cron purge les inscriptions jamais activees apres N jours.

Les invitations emises depuis le back-office (jeton de signup Odoo) conservent
le comportement natif : elles ne sont pas soumises a la verification.
""",
    "author": "EXOCOMS Group",
    "website": "https://exocoms.fr",
    "license": "LGPL-3",
    "depends": ["auth_signup", "website", "mail"],
    "data": [
        "data/ir_config_parameter_data.xml",
        "data/mail_template_data.xml",
        "data/ir_cron_data.xml",
        "views/signup_activation_templates.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
