# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.93.

CORRECTIF CRITIQUE — débloque le déploiement : "Validation Error /
Element '<xpath expr="//div[@id='footer']">' cannot be located in
parent view", qui empêchait TOUTE mise à jour du module depuis
plusieurs versions.

Diagnostic (inspection en direct via Réglages > Technique > Vues,
filtrées sur Inherited View = website.layout) : cette erreur ne
venait ni de capsule_house_theme, ni d'un autre site de la base
mutualisée, ni d'une personnalisation Website Builder — elle venait
de DEUX vues NATIVES du module website lui-même, actives par défaut
sur tout site Odoo :
  - website.footer_copyright_company_name (priority 16)
  - website.footer_custom (priority 16) — celle-ci fait précisément
    <xpath expr="//div[@id='footer']" position="replace">, la cible
    exacte de l'erreur.

Notre views/templates/layout.xml (theme_layout) ne déclarait aucune
priority explicite, donc valait 16 par défaut — À ÉGALITÉ avec ces
deux vues natives. À priorité égale, l'ordre d'application entre vues
n'est pas garanti dans notre sens : notre <xpath expr="//footer"
position="replace"> pouvait s'exécuter avant que ces vues natives
aient fini de patcher le footer natif d'origine, leur faisant perdre
leur cible (<div id="footer">) au moment de la validation.

Fix : ajout de priority="99" sur le template theme_layout
(views/templates/layout.xml). Odoo applique les vues héritées par
priorité croissante — 99 garantit que notre remplacement du footer
s'exécute en DERNIER, après que website.footer_copyright_company_name
et website.footer_custom aient patché le footer natif intact comme
prévu. Notre position="replace" jette ensuite tout ce contenu et le
remplace par theme_footer : le résultat visuel final est inchangé,
seul l'ORDRE d'application est désormais garanti et sans conflit.

Fichier modifié : views/templates/layout.xml (theme_layout,
priority="99" ajouté, aucun autre changement de contenu/xpath).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.93 — priority=99 "
        "ajouté sur theme_layout (views/templates/layout.xml) pour que "
        "notre remplacement du footer natif s'applique APRÈS les vues "
        "natives website.footer_copyright_company_name et "
        "website.footer_custom (priorité 16 par défaut, à égalité "
        "auparavant avec notre vue) — corrige la Validation Error "
        "'//div[@id=\\'footer\\'] cannot be located in parent view' qui "
        "bloquait toute mise à jour du module."
    )
    run_theme_maintenance(env)
