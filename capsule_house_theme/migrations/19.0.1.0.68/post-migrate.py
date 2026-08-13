# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.68.

RETRAIT complet de l'ajout "témoignages + réassurance" sur la home
(livré en 19.0.1.0.66). Retour client explicite : "j'ai pas aimé tes
ajout sur la page acceuil trouve tu ca necessaire sur capsule ?", puis
"retire ca". Question posée honnêtement en retour : ni les témoignages
(carousel .ch-testimonials) ni la bande de réassurance (.ch-why-us)
n'étaient réellement NÉCESSAIRES pour Capsule House — les deux avaient
été ajoutés sous couvert de "si tu peux l'améliorer, fais-le" (demande
du 19.0.1.0.66), pas d'un besoin identifié. Le client a confirmé vouloir
les retirer.

Retiré :
- views/partials/home_trust.xml (fichier supprimé).
- t-call vers ce partiel dans views/pages/home.xml.
- Méthode `_get_home_avis_context()` et son appel dans `index()`
  (controllers/main.py) — le rendu de la home revient exactement à son
  état d'avant 19.0.1.0.66.
- Règles CSS .ch-testimonials*/.ch-why-us* (et leurs media queries)
  dans static/src/css/homepage.css.
- Fonction JS `initTestimonialsCarousel()` et son appel dans `init()`
  (static/src/js/main.js).
- Entrée `capsule_house_theme.partial_home_trust` dans
  SCOPED_VIEW_XML_IDS (__init__.py).
- Entrée `views/partials/home_trust.xml` dans la liste `data` du
  manifest.

NON affecté par ce retrait : la page /nos-modeles (19.0.1.0.67, "Nos
modèles") reste en place — demande distincte et explicitement confirmée
par le client, contrairement à cet ajout home qui n'avait pas été
demandé aussi précisément.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.68 — retrait complet "
        "de l'ajout \"témoignages + réassurance\" sur la home (livré en "
        "19.0.1.0.66), à la demande explicite du client. La page "
        "/nos-modeles (19.0.1.0.67) n'est PAS affectée."
    )
    run_theme_maintenance(env)
