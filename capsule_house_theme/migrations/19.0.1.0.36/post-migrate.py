# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.36.

Demande client : "gère la traduction de mes pages comme j'ai fait sur
exocoms ainsi que live chat" — deux fonctionnalités répliquées depuis
exocoms_theme (recherche systématique du mécanisme réel dans ce module
de référence avant d'écrire quoi que ce soit, comme toujours sur ce
projet).

1) TRADUCTION DES PAGES (FR/EN)

_setup_languages() (déjà en place depuis une version antérieure)
activait fr_FR/en_US et posait le sélecteur natif, mais le CONTENU des
pages restait français uniquement — aucune page ne changeait vraiment
de texte selon la langue. Même mécanisme que exocoms_theme (pas de
traduction .po native pour le corps de page, mais du texte statique
dupliqué dans des blocs `t-if/t-else` sur `request.env.lang`, exactement
la convention documentée dans leurs propres commentaires) :

- `views/partials/hero.xml` : bloc `.ch-hero-content` dupliqué FR/EN,
  + badges "Nouveau"/"Promo" et bouton "Ajouter au panier" des cartes
  flottantes.
- `views/templates/footer.xml` : newsletter, colonnes Boutique/Aide/
  Entreprise, bandeau bas, dupliqués FR/EN.
- `views/partials/avis_hero.xml` : scindé en `avis_hero_fr` /
  `avis_hero_en` + aiguilleur `avis_hero` (mêmes noms de templates que
  exocoms_theme, même principe).
- `views/partials/avis_content.xml` : libellés statiques (stats,
  filtres, formulaire, messages) dupliqués FR/EN ; les boucles
  dynamiques (stats/avis_list) restent PARTAGÉES entre les deux
  langues pour éviter de dupliquer la logique elle-même.

Le header (nav) reste volontairement français uniquement, comme sur
exocoms_theme (jamais bilingue dans le module de référence non plus).

2) LIVE CHAT

Nouveau : dépendances `im_livechat` + `website_livechat` ajoutées au
manifest. Fonctions `_get_default_operator(env)` et
`_setup_livechat(env, website)` dans `__init__.py`, réplique du
mécanisme exocoms_theme._setup_livechat() :
- Canal `im_livechat.channel` dédié, rattaché via `website.channel_id`
  (champ nativement scopé par site).
- Différence délibérée : canal nommé "Capsule House - Live Chat" (pas
  d'après COMPANY_NAME 'Exocoms Group', partagé par les ~17 sites —
  éviterait sinon de retrouver/réutiliser le canal d'un AUTRE site,
  dont exocoms_theme lui-même).
- Couleurs du widget alignées sur notre palette (--ch-terracotta /
  --ch-ink), pas celles d'exocoms.
- Règle d'affichage (`im_livechat.channel.rule`, regex_url='/') créée
  si absente : un canal créé par code n'en a aucune par défaut.
- Opérateur réel assigné automatiquement (jamais OdooBot/uid=1) si le
  canal n'en a aucun, à chaque exécution (install et update).

Appelé dans run_theme_maintenance() juste après _scope_layout_views(),
même position relative que dans exocoms_theme.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.36 — pages "
        "traduites FR/EN (hero, footer, avis) + Live Chat natif "
        "configuré (canal dédié, opérateur réel), réplique adaptée du "
        "mécanisme observé sur exocoms_theme."
    )
    run_theme_maintenance(env)
