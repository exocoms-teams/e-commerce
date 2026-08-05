# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.35.

Demande client : "va dans exocoms et crée donc cette page d'avis sur
capsule house" — après avoir constaté que le badge de note du hero
("★ 4.9 · 2 340 avis") ne s'affichait jamais sur le vrai site (chiffre
non renseigné, volontairement masqué pour ne rien fabriquer), le client
a demandé de reproduire le vrai système d'avis observé sur exocoms_theme
(models/avis.py, controllers/main.py, views/pages/avis.xml, etc.)
plutôt que de se contenter d'un chiffre statique à saisir à la main.

Ajouté ici, adapté à Capsule House (pods, pas terminaux de paiement) et
à nos propres conventions multi-site :

- `models/avis.py` : nouveau modèle `capsule.house.avis` (nom, note
  1-5, commentaire, modèle acheté, date, statut pending/published,
  website_id — scopé, obligatoire sur cette base à ~17 sites).
- `security/ir.model.access.csv` : droits base.group_user (modération
  backend).
- `views/avis_backend.xml` : liste/formulaire/action/menu pour modérer
  les avis (aucun avis n'est publié automatiquement).
- `views/partials/avis_hero.xml` + `avis_content.xml` +
  `views/pages/avis.xml` : page publique /avis (stats calculées,
  filtres par note, grille des avis PUBLIÉS uniquement, formulaire de
  dépôt). Pas de photo de fond (contrairement à exocoms_theme) : on
  n'en a pas, donc reprise du dégradé doux du thème plutôt que d'en
  fabriquer une.
- `controllers/main.py` : routes `/avis` (GET, liste+stats+formulaire)
  et `/avis/submit` (POST, crée un avis 'pending' — jamais publié
  directement). Routes neuves, pas de collision possible avec un autre
  site de la base mutualisée : pas besoin de garde `_is_our_website`,
  même logique que /boutique et /newsletter/subscribe.
- Badge de note du hero (`homepage()`) : calcule maintenant la vraie
  note moyenne / le vrai nombre d'avis à partir des avis PUBLIÉS de
  notre site s'il y en a (`_get_avis_stats`), et ne retombe sur
  l'ancien réglage manuel (ir.config_parameter) que si aucun avis n'est
  encore publié — jamais de chiffre fabriqué.
- Menu : nouvelle entrée "Avis clients" (/avis) dans _setup_menus.
- `static/src/css/pages.css` (jusque-là réservé/vide) : mis en
  service, classes .ch-avis-* avec notre palette (--ch-*), enregistré
  dans THEME_ASSETS.

Volontairement omis par rapport à exocoms_theme : la traduction
automatique des commentaires via l'API publique Google Translate
(models/avis.py côté exocoms) — hors scope de cette demande, pourrait
être ajouté plus tard si le site devient bilingue.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.35 — système "
        "d'avis clients réels ajouté (modèle capsule.house.avis, page "
        "/avis, badge de note du hero calculé sur les vrais avis "
        "publiés), réplique adaptée du mécanisme observé sur "
        "exocoms_theme."
    )
    run_theme_maintenance(env)
