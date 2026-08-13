# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.79.

Retire le bandeau "Valeurs indicatives basées sur un standard du
marché — à ajuster dès réception des données réelles du fournisseur"
de la page détail de gamme (/nos-gammes/<slug>) — demande client
directe, capture d'écran à l'appui : "pas besoin d'indiquer cela sur la
page".

Le flag `gamme['indicative']` reste dans GAMMES_DATA (__init__.py,
gamme Capsule) pour usage interne/futur — seul l'affichage du bandeau
est retiré (views/pages/nos_gammes.xml). Règle CSS
`.ch-gamme-indicative-banner` (pages.css) supprimée, plus aucun
consommateur.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.79 — bandeau 'valeurs "
        "indicatives' retiré de la page détail de gamme (demande client)."
    )
    run_theme_maintenance(env)
