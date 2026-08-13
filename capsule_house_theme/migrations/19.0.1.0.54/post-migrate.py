# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.54.

SUITE DU TEST DIAGNOSTIQUE cartes flottantes du hero (19.0.1.0.53).
Remarque du client, juste : avec `t-if="False"`, la balise `<t>` reste
malgré tout PRÉSENTE dans l'arch compilé par QWeb — seul son contenu
ne s'affiche pas au rendu. Si l'hypothèse à tester est bien "la simple
présence d'une balise `<t>` dans la `<section data-snippet>` empêche
Odoo de la traiter comme éditable" (même logique que la règle déjà
identifiée pour `oe_structure`), alors `t-if="False"` ne teste PAS
correctement cette hypothèse : il faut que la balise `<t>` disparaisse
réellement de l'arch, pas juste que son évaluation soit fausse.

Corrigé : le bloc des cartes flottantes (`t-if="featured_products"` /
`t-foreach="featured_products[:2]"`) est maintenant neutralisé par un
VRAI commentaire XML (`<!-- ... -->`) dans `partial_hero_fr` ET
`partial_hero_en`, au lieu de `t-if="False"`. Un commentaire XML est
supprimé par le parseur AVANT que QWeb ne compile le template — les
balises `<t>` à l'intérieur ne font donc plus structurellement partie
de l'arch tant qu'elles restent commentées. Toujours rien de supprimé :
le bloc complet (cartes, badges, prix, bouton "Ajouter au panier")
reste présent tel quel dans le fichier source, juste entre `<!--` et
`-->` ; il suffit de retirer ces deux marqueurs pour le restaurer à
l'identique.

Prochaine étape : le client reteste le panneau Style sur le hero après
ce déploiement. Si le panneau apparaît maintenant → confirmation que
la présence de balises `<t>` dynamiques dans une `<section
data-snippet>` bloque son édition, et il faudra restructurer (sortir
ce bloc de la section, ou trouver une autre approche) pour garder la
fonctionnalité sans bloquer l'éditeur. Si le panneau reste vide → même
avec les balises `<t>` complètement absentes de l'arch, cette piste
est définitivement écartée ; il faudra alors inspecter la console du
navigateur en mode Édition pour une erreur JS, plutôt que continuer à
deviner depuis le seul code source.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.54 — cartes "
        "flottantes du hero neutralisées par un vrai commentaire XML "
        "(plus t-if=False) pour que les balises <t> disparaissent "
        "réellement de l'arch compilé, test diagnostique plus strict."
    )
    run_theme_maintenance(env)
