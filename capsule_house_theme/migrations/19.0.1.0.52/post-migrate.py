# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.52.

ROOT CAUSE CONFIRMÉE (rapport transmis par le client) — le Website
Builder ne pouvait déposer aucun bloc car Odoo se base sur l'attribut
`data-oe-model` pour détecter les zones éditables. Quand `oe_structure
oe_empty` est posé sur un élément contenant des balises `<t>` (t-call,
t-if, t-foreach, t-set), Odoo considère cet élément comme un
conteneur de template et supprime `data-oe-model` au rendu : aucune
zone de dépôt n'est créée.

Règles retenues pour ce module, désormais la référence pour tout
futur développement (voir README) :
1. Ne jamais poser `oe_structure oe_empty` sur un élément qui contient
   des `<t>` descendants — toujours un `<div>` enfant à part, sans
   aucune balise `<t>` dedans ni autour.
2. Ne jamais imbriquer un `<section>` dans un `<section>`, ni un
   `<aside>` dans un `<aside>` — un `<div>` pour les conteneurs
   internes.
3. Ne jamais imbriquer plusieurs `<div class="oe_structure oe_empty">`
   l'un dans l'autre au sein d'une même zone éditable (des divs
   `oe_structure oe_empty` SŒURS/successives restent autorisées,
   comme le fait exocoms_theme lui-même sur ses pages : plusieurs
   placeholders à différents endroits d'une même page).
4. Chaque `<section>` destinée à accepter des blocs doit avoir sa
   propre zone `oe_structure oe_empty` interne, juste avant sa
   fermeture.
5. Images produit : toujours via la route `/web/image/product.template
   /<id>/image_<taille>`, jamais via le champ binaire `.image_256`
   directement dans un template.
6. Après chaque modification XML : vérifier que le mode Édition
   permet bien d'insérer/déplacer des blocs ; si non, vérifier en
   premier le placement de `oe_structure`.

Audit complet du module contre ces règles :
- Règle 1 : déjà respectée depuis la 19.0.1.0.48 (suppression du
  `<div id="wrap" class="oe_structure">` qui enveloppait tout le
  contenu réel, `<t t-call>` compris, sur les 8 pages du module).
- Règle 2 : aucune violation trouvée (aucun `<aside>` dans ce module,
  aucun `<section>` imbriqué dans un autre).
- Règle 3 : aucune violation (les placeholders `oe_structure oe_empty`
  de ce module sont tous des divs sœurs, jamais imbriqués les uns
  dans les autres).
- Règle 4 : MANQUANTE avant cette version. `views/partials/hero.xml`
  (partial_hero_fr/en) et `views/partials/avis_hero.xml`
  (avis_hero_fr/en) n'avaient pas leur propre zone interne, alors que
  les hero_section_fr/en et avis_hero_fr/en réels d'exocoms_theme en
  ont bien une (`oe_structure_hero_extra` / `oe_structure_avis_
  hero_extra`, juste avant `</section>`). Corrigé ici :
  `oe_structure_ch_hero_extra` ajouté dans les deux <section> de
  hero.xml, `oe_structure_ch_avis_hero_extra` ajouté dans les deux
  <section> de avis_hero.xml.
- Règle 5 : aucune violation (toutes les images produit de ce module
  passent déjà par `/web/image/product.template/<id>/image_<taille>`).

Profitant de cette même passe, `avis_hero.xml` a aussi été mis au même
niveau que le hero d'accueil (déjà corrigé en 19.0.1.0.49/50/51) : sa
<section> ne portait NI data-snippet, NI data-name, NI o_colored_level,
et son texte marketing n'était pas oe_editable — alors que l'avis_hero
réel d'exocoms_theme a bien tout cela. Corrigé pour cohérence.
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.52 — ajout des "
        "zones oe_structure internes manquantes (hero, avis_hero) + "
        "avis_hero mis au niveau du hero d'accueil (data-snippet, "
        "o_colored_level, oe_editable)."
    )
    run_theme_maintenance(env)
