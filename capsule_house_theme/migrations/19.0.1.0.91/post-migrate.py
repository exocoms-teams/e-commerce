# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.91.

Retour client après la 19.0.1.0.90 : "maintenant plus de block qui
s'affiche comme au début, même le grand block promis" — régression :
plus AUCUN bloc sélectionnable sur les sections Gammes/Usages de
l'accueil, alors qu'avant même le bloc de titre (plus petit) marchait.

Cause identifiée : depuis la 19.0.1.0.89, la zone oe_structure vivait
dans home.xml (page_home) et enveloppait un <t t-call="..."/> vers une
AUTRE vue (partial_home_gammes / partial_home_usages, déjà scopée
séparément). Un oe_structure et le contenu qu'il est censé rendre
éditable doivent vivre dans LA MÊME vue — les relier via un t-call
casse la détection de bloc par le Website Builder (aucune section, ni
la grande englobante ni les anciennes imbriquées, n'était plus
sélectionnable).

Fix (retour au schéma déjà confirmé fonctionnel sur les pages Aide/
Entreprise/légales) : l'oe_structure est redescendu DANS
home_gammes.xml et home_usages.xml, directement autour de leur
<section> racine. home.xml t-call de nouveau ces deux templates sans
aucun wrapper.

Filet de sécurité ajouté (__init__.py, _reset_customized_views(),
appelée dans run_theme_maintenance juste après _scope_layout_views) :
si le client a ouvert/sauvegardé le mode édition pendant qu'une des
versions intermédiaires cassées (19.0.1.0.89 notamment) était en
ligne, Odoo peut avoir figé cet état dans l'arch_db de la vue
(personnalisation native à Odoo, indépendante des mises à jour de
module suivantes). reset_arch('hard') sur
capsule_house_theme.partial_home_gammes et .partial_home_usages force
un retour strict à l'arch définie dans le module — idempotent, sans
effet si la vue n'a jamais été personnalisée.

Fichiers modifiés : views/pages/home.xml, views/partials/
home_gammes.xml, views/partials/home_usages.xml, __init__.py
(_reset_customized_views, RESETTABLE_VIEW_XML_IDS).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.91 — oe_structure "
        "redescendu dans la même vue que le contenu qu'il rend éditable "
        "(home_gammes.xml/home_usages.xml, plus de wrapper dans "
        "home.xml relié par t-call) ; reset_arch hard appliqué en filet "
        "de sécurité sur ces deux vues au cas où une version cassée "
        "aurait été sauvegardée entre-temps."
    )
    run_theme_maintenance(env)
