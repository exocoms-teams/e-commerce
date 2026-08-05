# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.43.

Suite du diagnostic "où ça m'envoie lorsque je me déconnecte" :
`/web/login` et `/web/session/logout` atterrissaient sur le site Odoo
générique par défaut ("My Website") au lieu de Capsule House, alors
que `/` résolvait correctement.

Le client a explicitement demandé de rester sur une analyse DU CODE
local d'exocoms_theme (pas de manipulation sur l'instance Odoo.sh) —
recherche exhaustive faite en ce sens dans exocoms_theme/__init__.py
(aucune occurrence de `sequence` sur le modèle website, aucune classe
ir.http/website custom, aucune route de login/logout personnalisée) :
rien dans LEUR code ne gère spécifiquement ce cas. Ce n'est donc pas
une technique qu'on aurait ratée chez eux — c'est un réglage qu'il
faut poser nous-mêmes.

Nouvelle fonction `_setup_website_priority(env, website)` : sans
`website.domain` posé (notre cas tant que le DNS n'est pas confirmé,
voir `_setup_domain()`), Odoo départage les sites candidats pour les
routes natives (dont /web/login, /web/session/logout) via
`website.sequence` — plus bas = prioritaire. Tous les sites non
configurés partagent la même valeur par défaut (10), y compris le
site générique "My Website". Fix : `website.sequence` posé à 1 sur
NOTRE site uniquement (jamais touché ailleurs), pour qu'il gagne
systématiquement ce départage.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.43 — website.sequence "
        "abaissée à 1 sur notre site pour gagner le départage natif Odoo "
        "sur les routes /web/login et /web/session/logout."
    )
    run_theme_maintenance(env)
