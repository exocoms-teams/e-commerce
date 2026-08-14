# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS - Demande d'inscription portail",
    "version": "19.0.2.0.0",
    "category": "Website/Website",
    "summary": "Confirmation de l'adresse email avant toute creation de compte",
    "description": """
EXOCOMS - Demande d'inscription portail
=======================================

Aucun utilisateur, aucun contact n'est cree tant que l'adresse email n'a pas
ete confirmee. La demande est stockee dans une table dediee
(`exocoms.signup.request`), puis le parcours bascule sur le mecanisme
d'invitation natif d'Odoo.

Deroule
-------
1. Le visiteur saisit son nom et son adresse email.
2. L'adresse est controlee : format, domaine jetable, enregistrement DNS,
   liste blanche facultative.
3. Une demande est enregistree et un lien a usage unique est envoye.
   **Aucun `res.users` ni `res.partner` n'existe a ce stade.**
4. Le clic sur le lien cree le contact, prepare un jeton d'invitation Odoo et
   redirige vers `/web/signup?token=...`.
5. Le visiteur choisit son mot de passe sur la page **native** d'Odoo, qui
   cree le compte et ouvre la session.

Consequences
------------
* Le POST de `/web/signup` reste integralement natif : aucune reecriture de la
  validation du formulaire, aucune manipulation du cycle de vie de `res.users`.
* Aucun compte archive a debloquer, aucun mot de passe en attente stocke.
* Le cron de purge ne touche que `exocoms.signup.request` : aucun risque pour
  les comptes et contacts existants.
* Une adresse non confirmee n'occupe jamais la base contacts.

Les invitations emises depuis le back-office conservent le comportement natif.
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
        "views/signup_request_views.xml",
        "views/signup_domain_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
