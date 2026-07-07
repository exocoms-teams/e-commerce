# -*- coding: utf-8 -*-
from . import controllers
from . import models


def _assign_nouveaute_tag(env):
    """Pose automatiquement le tag "Nouveauté" sur quelques produits
    publiés à l'installation du module, pour que la section "Nouveautés"
    de la page d'accueil ne soit pas vide par défaut. Le maître de stage
    peut ensuite ajouter/retirer ce tag sur n'importe quel produit
    (Ventes > Produits > champ "Tags produit") pour changer la sélection,
    sans toucher au code.
    """
    _ensure_french_is_default_language(env)

    tag = env.ref('Matelas.product_tag_nouveaute', raise_if_not_found=False)
    if not tag:
        return

    products = env['product.template'].search([
        ('is_published', '=', True),
    ], limit=4)

    for product in products:
        product.write({'product_tag_ids': [(4, tag.id)]})


def _ensure_french_is_default_language(env):
    """S'assure que le français reste la langue par défaut du site public,
    même après l'activation de l'anglais. On cherche la langue par son
    code ('fr_FR') plutôt que par un xmlid, car les langues autres que
    l'anglais n'ont pas toujours d'identifiant externe stable dans Odoo.
    """
    fr_lang = env['res.lang'].search([('code', '=', 'fr_FR')], limit=1)
    if not fr_lang:
        return
    if not fr_lang.active:
        fr_lang.active = True

    websites = env['website'].search([])
    for website in websites:
        vals = {}
        if fr_lang.id not in website.language_ids.ids:
            vals['language_ids'] = [(4, fr_lang.id)]
        if website.default_lang_id.id != fr_lang.id:
            vals['default_lang_id'] = fr_lang.id
        if vals:
            website.write(vals)
