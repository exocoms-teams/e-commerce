# -*- coding: utf-8 -*-
import logging

from . import controllers
from . import models
from . import wizards
from . import i18n_map

_logger = logging.getLogger(__name__)


def _assign_nouveaute_tag(env):
    """Pose automatiquement le tag "Nouveauté" sur quelques produits"""
    _ensure_french_is_default_language(env)
    _seed_matelas_caracteristiques(env)
    _fix_fr_translations(env)

    tag = env.ref('matelas.product_tag_nouveaute', raise_if_not_found=False)
    if not tag:
        return

    products = env['product.template'].search([
        ('is_published', '=', True),
    ], limit=4)

    for product in products:
        product.write({'product_tag_ids': [(4, tag.id)]})


def _seed_matelas_caracteristiques(env):
    """Pré-remplit des caractéristiques d'exemple"""
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


def _fix_fr_translations(env):
    """Réapplique explicitement les traductions françaises des vues du
    site, en lisant le texte source ACTUELLEMENT enregistré en base (via
    get_field_translations) plutôt qu'en se fiant à une correspondance
    exacte dans un fichier .po.

    Nécessaire à cause d'une particularité d'Odoo : le champ traduit
    arch_db utilise 'en_US' comme clé technique de référence, quelle que
    soit la langue du XML source. Importer les traductions anglaises
    (i18n/en_US.po) écrase donc cette référence avec du texte anglais, et
    le français (qui n'a pas de clé de référence à lui) affiche l'anglais
    par repli tant qu'une traduction fr_FR explicite n'est pas reposée sur
    le texte source du moment. Un fichier fr_FR.po statique doit
    correspondre EXACTEMENT (espaces, sauts de ligne...) au texte source
    réellement stocké en base pour que l'import fonctionne, ce qui s'est
    avéré peu fiable en pratique - d'où cette approche : on relit le texte
    source réel en base et on n'utilise i18n_map.EN_TO_FR que pour la
    valeur française à appliquer, sans dépendre d'une correspondance de
    fichier statique.
    """
    view_xmlids = [
        'home', 'avis_page', 'contact_page', 'mentions_legales',
        'cookie_policy_custom', 'fiche_technique', 'email_confirm_success',
        'email_confirm_invalid', 'website_footer',
        'view_matelas_newsletter_wizard_form', 'view_matelas_avis_form',
        'view_matelas_avis_list',
        'product_template_form_matelas_caracteristiques',
    ]
    for xmlid in view_xmlids:
        view = env.ref('matelas.%s' % xmlid, raise_if_not_found=False)
        if not view:
            continue
        translations, _info = view.get_field_translations('arch_db')
        update = {}
        for entry in translations:
            source = entry.get('source') or ''
            if not source:
                continue

            fr_value = (
                i18n_map.EN_TO_FR.get(source)
                or i18n_map.EN_TO_FR.get(source.strip())
            )
            if fr_value:
                update[source] = fr_value
            else:
                _logger.warning(
                    "No French translation mapping found for source %s "
                    "in view matelas.%s",
                    ascii(source),
                    xmlid,
                )

        if update:
            view.update_field_translations(
                'arch_db',
                {'fr_FR': update},
            )


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
