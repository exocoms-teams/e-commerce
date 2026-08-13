# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.55.

RÉSULTAT DU TEST DIAGNOSTIQUE cartes flottantes du hero (19.0.1.0.53/
54) : NÉGATIF. Le client a confirmé qu'avec le bloc des cartes
flottantes entièrement absent de l'arch compilé (vrai commentaire XML,
pas juste t-if="False"), le panneau Style restait toujours vide sur le
hero. Cette hypothèse est donc définitivement écartée : la présence de
balises `<t t-if>`/`<t t-foreach>` dynamiques dans la `<section
data-snippet>` n'est PAS la cause du problème.

Le bloc est restauré à l'identique dans `partial_hero_fr` et
`partial_hero_en` (rien n'avait été supprimé, juste commenté).

État des lieux après 6 versions de correctifs successifs sur le hero
(49 à 55), tous sans effet confirmé sur le panneau Style :
- data-snippet + data-name (49)
- + o_colored_level (50)
- scission en templates FR/EN indépendants comme exocoms_theme (51)
- zone oe_structure interne comme exocoms_theme (52)
- retrait du contenu dynamique, d'abord par t-if=False puis par
  commentaire XML réel (53/54) — résultat négatif (55)

Tous ces changements reproduisent fidèlement ce qui est vérifié dans
le code réel d'exocoms_theme, et restent corrects/légitimes à
conserver indépendamment de ce diagnostic (ils rapprochent réellement
le comportement de ce module de celui d'exocoms_theme). Mais aucun
n'a résolu le symptôme observé par le client.

Prochaine étape recommandée, faute de pouvoir tester en direct sur
l'instance Odoo.sh du client : inspecter la console du navigateur
(F12 > Console) en mode Édition au moment du clic sur le hero, à la
recherche d'une erreur JavaScript. Si le panneau Style est vide sur
TOUT le site (pas seulement le hero), la cause est probablement plus
générale (bundle JS du Website Builder qui ne charge pas correctement
pour ce site, conflit d'assets, etc.) plutôt que spécifique au code de
ce module.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.55 — test "
        "diagnostique cartes flottantes du hero NEGATIF (confirmé par "
        "le client), bloc restauré à l'identique. Cause du panneau "
        "Style vide toujours non identifiée après 6 versions de "
        "correctifs sur hero.xml/avis_hero.xml."
    )
    run_theme_maintenance(env)
