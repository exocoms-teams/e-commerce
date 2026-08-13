# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.69.

Correction de la réponse FAQ "Ai-je besoin d'un permis de construire ?"
(views/pages/aide_faq.xml, chFaq1/chFaq1en).

Origine : discussion avec le client sur l'opportunité d'expliquer les
démarches administratives (permis de construire / déclaration
préalable) sur le site, les tailles réelles des pods (Studio 18 m²,
Panorama jusqu'à 40 m²) tombant justement dans la zone où ces seuils
s'appliquent. Le client a d'abord proposé d'en faire un vrai service
("le service doit prendre ça en compte"), mais a explicitement dit ne
pas savoir quel niveau d'engagement Capsule House peut tenir
("j'en sais rien en fait").

Décision : commencer par le niveau le plus sûr — informer, pas
promettre. Or la réponse EXISTANTE de cette FAQ (déjà présente dans le
module, reprise de la maquette d'origine du client) affirmait "Nous
vous accompagnons dans les démarches" — exactement l'engagement de
service que le client vient de dire ne pas pouvoir confirmer.

Corrigé :
- Retrait de la promesse d'accompagnement non confirmée.
- Seuils réels vérifiés par recherche (sources : Code de l'urbanisme
  art. R.421-14 b, formulaires CERFA 16702/16703) : moins de 5 m²,
  aucune formalité ; 5 à 20 m², déclaration préalable ; plus de 20 m²,
  permis de construire ; seuil porté à 40 m² en zone urbaine PLU si la
  surface de plancher déjà bâtie sur le terrain ne dépasse pas 150 m².
- Application honnête à nos tailles réelles : Studio (18 m², dans la
  zone déclaration préalable), Panorama (jusqu'à 40 m², qui peut
  basculer en permis de construire selon la zone).
- Renvoi vers la mairie du client pour la décision finale (les règles
  dépendent de sa commune, pas de nous) plutôt qu'une promesse de
  service.

Contenu FR et EN corrigés en parallèle.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.69 — correction de la "
        "réponse FAQ \"permis de construire\" : retrait d'une promesse "
        "d'accompagnement non confirmée par le client, remplacée par des "
        "seuils réels vérifiés (CERFA 16702/16703, art. R.421-14 b) "
        "appliqués aux tailles Studio/Panorama."
    )
    run_theme_maintenance(env)
