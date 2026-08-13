# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.70.

Confirmation client du service "démarches administratives" — suite à
la version 19.0.1.0.69 (voir cette migration pour l'historique complet).

Le client a explicitement confirmé : "c'est confirmé, les formalités
administratives sont gérées par nous et nous accompagnons complètement
nos clients." Ceci lève le point bloquant de la 19.0.1.0.69 (le client
avait dit "j'en sais rien en fait" sur le niveau d'engagement possible).

Réponse FAQ "Ai-je besoin d'un permis de construire ?"
(views/pages/aide_faq.xml, chFaq1/chFaq1en) remise à jour pour affirmer
la prise en charge complète des démarches par Capsule House (montage du
dossier + dépôt en mairie), en conservant les seuils réels vérifiés
(Code de l'urbanisme art. R.421-14 b, CERFA 16702/16703) appliqués aux
tailles Studio (18 m²) / Panorama (jusqu'à 40 m²).

Contenu FR et EN mis à jour en parallèle.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.70 — confirmation "
        "client : Capsule House prend en charge les démarches "
        "administratives (permis de construire / déclaration préalable) "
        "pour ses clients. Réponse FAQ mise à jour en conséquence."
    )
    run_theme_maintenance(env)
