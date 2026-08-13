# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.67.

Nouvelle page /nos-modeles : vitrine des 4 gammes de pods (Studio, Duo,
Panorama, Accessoires), sur le modèle de "Nos services" d'exocoms_theme.

Historique de la demande : le client a montré la page "Application" de
guosegroup.com (fabricant chinois de maisons capsules,
fr.guosegroup.com/application) et demandé un équivalent pour Capsule
House. Un premier examen a montré que le contenu de Guose (photos
réelles de leurs installations en bureau/boutique/hôtel/salle
d'exposition) n'est pas transposable : Capsule House n'a jamais publié
de tel usage nulle part sur ce site, et rien ne permettait de le faire
sans inventer du contenu. Le client a alors précisé : "lorsque je
clique sur les elements de la page application c'est comme ma page
service sur exocoms indique juste leur domaine d'expertise", puis
confirmé vouloir cette page-là comme modèle : "la page service devrait
être la page application comme dans le site que je t'ai présenté".

Analyse de exocoms_theme/views/pages/services.xml et
partials/services_hero.xml : les cartes de cette page ne fabriquent
aucun contenu par domaine — elles décrivent chaque domaine en 2-3
phrases génériques, et ce sont les VRAIS tags du hero qui renvoient
vers les vrais filtres boutique (/shop/category/<id>). Reproduit ici à
l'identique pour Capsule House : chaque carte de /nos-modeles pointe
vers le vrai filtre boutique de sa catégorie (même URL que les entrées
de menu déjà créées par _setup_menus), et les 2-3 mots de description
par carte ne reprennent QUE des faits déjà publiés ailleurs sur ce
site :
- Studio (18 m²) et Panorama (jusqu'à 40 m²) : tailles déjà publiées
  sur /faq (aide_faq.xml).
- Trilogie "Studio, duo ou famille" : déjà publiée sur /shop
  (shop.xml, sous-titre du hero boutique).
- "Duo" : aucune surface publiée nulle part sur ce site pour ce
  modèle — la description se limite à ce que le nom affirme de
  lui-même (format pensé pour deux), rien d'inventé.

Nouvelle entrée de menu "Nos modèles" (séquence 15, entre Accueil et
Tous les pods) — même principe que "Nos services" chez exocoms, qui a
lui aussi sa propre entrée de menu dédiée (voir _setup_menus).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.67 — nouvelle page "
        "/nos-modeles (vitrine des 4 gammes, sur le modèle de \"Nos "
        "services\" d'exocoms_theme) + entrée de menu associée."
    )
    run_theme_maintenance(env)
