# -*- coding: utf-8 -*-
{
    "name": "EXOCOMS - RGPD / Protection des données",
    "summary": "Registre des traitements, demandes de droits, consentements, "
               "durées de conservation, violations de données et journal d'audit.",
    "description": """
EXOCOMS RGPD
============

Module de mise en conformité RGPD / CNIL pour Odoo 19.

Fonctionnalités
---------------
* **Registre des traitements** (art. 30) avec base légale, catégories de données,
  destinataires, transferts hors UE, durées de conservation, AIPD et export PDF.
* **Demandes d'exercice des droits** (art. 15 à 22) : accès, portabilité,
  rectification, effacement, limitation, opposition, décision automatisée.
  Workflow complet, vérification d'identité, délai légal d'un mois avec
  prorogation de deux mois, relances automatiques.
* **Journal des consentements** horodaté, inaltérable (chaîne de hachage SHA-256),
  avec preuve technique (IP, user-agent, URL, libellé affiché) et endpoint JSON-RPC
  destiné aux CMP tiers (Axeptio, tarteaucitron, Didomi...).
* **Politique de conservation** : règles par modèle avec anonymisation,
  archivage ou suppression automatique via cron, avec simulation préalable.
* **Cartographie des données personnelles** avec auto-détection des modèles,
  moteur d'export (JSON + PDF) et moteur d'anonymisation respectant les
  obligations légales de conservation (comptabilité, paie...).
* **Registre des violations de données** (art. 33/34) avec compte à rebours 72 h.
* **Journal d'audit** configurable par modèle (création, modification,
  suppression, export).
* **Portail client** : consultation des données, gestion des consentements,
  dépôt d'une demande de droits.
* **Formulaire public** avec vérification d'identité par jeton e-mail.

Ce module fournit l'outillage. La conformité reste de la responsabilité du
responsable de traitement.
""",
    "author": "EXOCOMS Group",
    "website": "https://www.exocoms.fr",
    "maintainer": "EXOCOMS Group",
    "support": "contact@exocoms.fr",
    "category": "Productivity/Data Protection",
    "version": "19.0.2.0.0",
    "license": "LGPL-3",
    "depends": [
        "base",
        "base_setup",
        "mail",
        "portal",
        "web",
    ],
    "data": [
        "security/rgpd_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/rgpd_data_category_data.xml",
        "data/rgpd_consent_purpose_data.xml",
        "data/rgpd_data_map_data.xml",
        "data/mail_template_data.xml",
        "data/ir_cron.xml",
        "wizard/rgpd_export_wizard_views.xml",
        "wizard/rgpd_erase_wizard_views.xml",
        "wizard/rgpd_retention_preview_views.xml",
        "views/rgpd_data_category_views.xml",
        "views/rgpd_treatment_views.xml",
        "views/rgpd_data_map_views.xml",
        "views/rgpd_request_views.xml",
        "views/rgpd_consent_views.xml",
        "views/rgpd_retention_views.xml",
        "views/rgpd_breach_views.xml",
        "views/rgpd_audit_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/portal_templates.xml",
        "views/public_templates.xml",
        "report/rgpd_report_actions.xml",
        "report/rgpd_treatment_report.xml",
        "report/rgpd_request_report.xml",
        "report/rgpd_data_export_report.xml",
        "views/rgpd_menus.xml",
    ],
    "demo": [
        "demo/rgpd_demo.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "exocoms_rgpd/static/src/scss/rgpd_portal.scss",
            "exocoms_rgpd/static/src/js/rgpd_portal.js",
            "exocoms_rgpd/static/src/js/rgpd_cmp_bridge.js",
        ],
        "web.report_assets_common": [
            "exocoms_rgpd/static/src/scss/rgpd_report.scss",
        ],
    },
    "images": ["static/description/banner.png"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
    "auto_install": False,
}
