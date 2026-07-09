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
    _seed_matelas_caracteristiques(env)

    tag = env.ref('Matelas.product_tag_nouveaute', raise_if_not_found=False)
    if not tag:
        return

    products = env['product.template'].search([
        ('is_published', '=', True),
    ], limit=4)

    for product in products:
        product.write({'product_tag_ids': [(4, tag.id)]})


def _seed_matelas_caracteristiques(env):
    """Pré-remplit des caractéristiques d'exemple (dimensions, matière,
    épaisseur, fermeté, garantie) sur les premiers produits publiés, pour
    que la fiche technique ne soit pas vide dès l'installation. Le maître
    de stage peut ensuite modifier ces valeurs produit par produit (Ventes
    > Produits > onglet "Caractéristiques matelas"), sans toucher au code.
    """
    exemples = [
        {
            'matelas_dimensions': '140 x 190 cm',
            'matelas_matiere': 'Mousse à mémoire de forme',
            'matelas_epaisseur': '25 cm',
            'matelas_fermete': 'medium',
            'matelas_garantie': '10 ans',
        },
        {
            'matelas_dimensions': '160 x 200 cm',
            'matelas_matiere': 'Latex naturel',
            'matelas_epaisseur': '22 cm',
            'matelas_fermete': 'ferme',
            'matelas_garantie': '15 ans',
        },
        {
            'matelas_dimensions': '90 x 190 cm',
            'matelas_matiere': 'Mousse polyuréthane',
            'matelas_epaisseur': '18 cm',
            'matelas_fermete': 'souple',
            'matelas_garantie': '5 ans',
        },
        {
            'matelas_dimensions': '180 x 200 cm',
            'matelas_matiere': 'Ressorts ensachés + mousse',
            'matelas_epaisseur': '28 cm',
            'matelas_fermete': 'medium',
            'matelas_garantie': '10 ans',
        },
    ]

    products = env['product.template'].search([
        ('is_published', '=', True),
    ], limit=len(exemples))

    for product, valeurs in zip(products, exemples):
        if not product.matelas_dimensions:
            product.write(valeurs)


def _ensure_french_is_default_language(env):
    """Installe (si besoin) et active la langue française, puis la remet
    comme langue par défaut du site public.

   
    """
    fr_lang = env['res.lang']._activate_and_install_lang('fr_FR')
    if not fr_lang:
        return

    websites = env['website'].search([])
    for website in websites:
        vals = {}
        if fr_lang.id not in website.language_ids.ids:
            vals['language_ids'] = [(4, fr_lang.id)]
        if website.default_lang_id.id != fr_lang.id:
            vals['default_lang_id'] = fr_lang.id
        if vals:
            website.write(vals)
