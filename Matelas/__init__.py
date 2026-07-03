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
    tag = env.ref('Matelas.product_tag_nouveaute', raise_if_not_found=False)
    if not tag:
        return

    products = env['product.template'].search([
        ('is_published', '=', True),
    ], limit=4)

    for product in products:
        product.write({'product_tag_ids': [(4, tag.id)]})
