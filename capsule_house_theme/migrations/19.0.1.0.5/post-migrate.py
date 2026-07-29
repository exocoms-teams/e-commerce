# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.5.

Deux correctifs dans cette version :

1. VRAIE cause racine du bug CSS enfin identifiée et corrigée à la
   source : variables.css chargeait Google Fonts via
   "@import url('...css2?family=Inter:wght@400;500;600;700;800;900...')"
   — syntaxe css2 à poids variable qui utilise des POINTS-VIRGULES dans
   l'URL. Le minifieur CSS d'Odoo scanne le fichier de façon naïve et
   coupe la règle @import au premier ';' rencontré, y compris ceux DANS
   l'URL, produisant un @import tronqué qui cassait le parsing de TOUT
   le reste du bundle compilé (nos règles .ch-*, mais aussi Bootstrap et
   le CSS natif Odoo pour ce site). Remplacé par la syntaxe historique
   (virgules, sans point-virgule dans l'URL) qui se compile correctement.
   Le contournement <link> direct ajouté en 19.0.1.0.3 reste en place
   par sécurité, mais n'est plus la seule protection.

2. Nouveau fichier odoo-integration.css (+ ir.asset + <link> de secours) :
   harmonise les éléments 100% natifs Odoo que le thème ne couvrait pas
   encore (en-tête grille boutique, panier, checkout, formulaires,
   alertes, badges/notes, portail client /my/*), inspiré du même fichier
   du module de référence exocoms_theme.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.5 — rejeu de "
        "run_theme_maintenance() (vraie cause racine du bug CSS corrigée "
        "dans variables.css + nouveau odoo-integration.css)."
    )
    run_theme_maintenance(env)
