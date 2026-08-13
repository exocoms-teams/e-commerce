# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.64.

L'outil SEO natif d'Odoo ("Optimize SEO", panneau Promote) a détecté
plusieurs liens cassés sur le site : /mentions-legales, /cgv,
/confidentialite. Ce n'est pas une régression — c'est un écart connu et
documenté dans le README depuis le tout début du projet ("Écart connu,
non corrigé pour l'instant" : le footer contient ces liens depuis le
départ, mais les pages n'avaient jamais été construites, au même titre
que Services/Contact/À propos qui, eux, ont depuis été livrés).

Corrigé : trois nouvelles pages légales, requises pour une boutique en
ligne française :
- /mentions-legales (mentions_legales.xml)
- /cgv (cgv.xml)
- /confidentialite (confidentialite.xml)

Contenu — rien n'est inventé :
- Mentions légales : coordonnées légales RÉELLES d'Exocoms Group,
  reprises à l'identique de exocoms_theme (même société gérant les deux
  sites, confirmé explicitement par le client : "c'est la même
  entreprise qui gère les deux"). Seule l'activité déclarée est adaptée
  au contexte réel (vente de maisons modulaires), et l'email de contact
  reprend la convention déjà utilisée ailleurs dans ce module
  (contact@capsule-house.fr).
- CGV : chaque clause reprend un fait déjà publié ailleurs sur ce même
  site (acompte 20%, délais de fabrication/livraison, garantie 10 ans,
  paiement 3x sans frais — voir aide_livraison.xml, aide_retours.xml,
  aide_garantie.xml, hero.xml), formalisé juridiquement, y compris le
  fondement légal réel de l'absence de rétractation pour un bien
  personnalisé (art. L221-28 3° du Code de la consommation).
- Confidentialité : décrit les traitements de données RÉELLEMENT en
  place (avis, newsletter, commandes, live chat) — vérifié qu'aucun
  outil d'analytics/pixel tiers n'est configuré dans ce module avant
  d'écrire la section cookies.

Hébergement (IONOS, mentions légales) repris tel quel d'exocoms_theme,
à confirmer/corriger par le client si l'hébergement réel diffère.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.64 — pages légales "
        "créées (/mentions-legales, /cgv, /confidentialite), corrigeant "
        "des liens cassés présents dans le footer depuis le début du "
        "projet (détecté par l'outil SEO natif d'Odoo)."
    )
    run_theme_maintenance(env)
