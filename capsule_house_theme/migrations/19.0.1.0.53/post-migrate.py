# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.53.

TEST DIAGNOSTIQUE TEMPORAIRE, demandé par le client, pour isoler la
cause du panneau Style toujours vide sur le hero malgré tous les
correctifs précédents (data-snippet, data-name, o_colored_level,
oe_editable, zone oe_structure interne, scission FR/EN).

Hypothèse à tester : le bloc des 2 "cartes flottantes" produits dans
`views/partials/hero.xml` utilise `<t t-if="featured_products">` et
`<t t-foreach="featured_products[:2]" t-as="hero_product">` — du
contenu dynamique data-driven. Si ce genre de balise empêche Odoo de
traiter proprement une <section data-snippet> comme éditable (même
logique que la règle "oe_structure ne doit jamais être sur un élément
contenant des <t>", transmise par le client), ce bloc pourrait être la
cause.

Le client a explicitement demandé de NE RIEN SUPPRIMER. Changement
strictement réversible : la condition est passée de
`t-if="featured_products"` à `t-if="False"` dans partial_hero_fr ET
partial_hero_en — le bloc entier (t-foreach, badges, image, prix,
formulaire "Ajouter au panier") reste intact dans le code source, il
est juste désactivé à l'affichage le temps du test. Pour réactiver :
remettre `t-if="featured_products"` aux deux endroits.

Prochaine étape après ce déploiement : le client doit retester le
panneau Style sur le hero. Si le panneau apparaît maintenant → le
bloc dynamique était bien la cause, on cherchera une façon de le
garder sans bloquer l'éditeur (ex: le sortir de la <section
data-snippet> et le repositionner autrement en CSS). Si le panneau
reste vide → cette piste est écartée, remettre
`t-if="featured_products"` et chercher ailleurs (voir suggestion
précédente : inspecter la console navigateur pour une erreur JS).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.53 — cartes "
        "flottantes du hero désactivées temporairement (t-if=False, "
        "code intact) pour tester si elles bloquent le panneau Style."
    )
    run_theme_maintenance(env)
