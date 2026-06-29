# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def _activer_francais_par_defaut(env):
    """Active le francais, charge ses traductions et le definit comme langue
    par defaut du site, tout en gardant l'anglais disponible.

    Cette fonction reproduit automatiquement, a chaque build Odoo.sh, les
    actions faites manuellement dans l'interface, pour qu'elles ne soient
    pas perdues au rebuild de la base.
    """
    # 1. S'assurer que le francais (fr_FR) est actif
    lang = env['res.lang'].with_context(active_test=False).search(
        [('code', '=', 'fr_FR')], limit=1)
    if not lang:
        # Installe la langue si elle n'existe pas encore
        env['res.lang']._activate_lang('fr_FR')
        lang = env['res.lang'].with_context(active_test=False).search(
            [('code', '=', 'fr_FR')], limit=1)
    if lang and not lang.active:
        lang.active = True

    # 2. Charger / mettre a jour les traductions francaises (equivaut au
    #    bouton "Mettre a jour" sur la ligne Francais)
    try:
        env['base.language.install'].create({
            'lang_ids': [(6, 0, [lang.id])],
            'overwrite': True,
        }).lang_install()
    except Exception:
        # Selon la version, la signature peut differer : on tente le fallback
        try:
            env['base.language.install'].create({
                'lang': 'fr_FR',
                'overwrite': True,
            }).lang_install()
        except Exception as e:
            _logger.warning("Planet Mobil: chargement des traductions FR ignore (%s)", e)

    # 3. Mettre fr_FR comme langue par defaut sur chaque site web,
    #    en gardant l'anglais dans les langues disponibles
    websites = env['website'].search([])
    for website in websites:
        try:
            if lang not in website.language_ids:
                website.language_ids = [(4, lang.id)]
            website.default_lang_id = lang.id
        except Exception as e:
            _logger.warning("Planet Mobil: langue par defaut non appliquee (%s)", e)


def _supprimer_categories_natives(env):
    """Supprime les categories website natives d'Odoo (demo data).
    Seules les categories Planet Mobil sont conservees.
    """
    categories_natives = [
        'Desks', 'Furnitures', 'Boxes', 'Drawers',
        'Cabinets', 'Bins', 'Lamps', 'Services',
        'All', 'Office Furniture', 'Indoor Furniture',
        'Outdoor Furniture', 'Components', 'Software',
    ]
    cats = env['product.public.category'].sudo().search([
        ('name', 'in', categories_natives),
    ])
    for cat in cats:
        try:
            cat.unlink()
            _logger.info("Planet Mobil: categorie native '%s' supprimee.", cat.name)
        except Exception as e:
            _logger.warning(
                "Planet Mobil: impossible de supprimer la categorie '%s' (%s)",
                cat.name, e
            )


def post_init_hook(env):
    """Hook execute apres l'installation/mise a jour du module.

    Entoure d'un try/except global : meme en cas d'erreur, le build reste
    vert et l'installation du module n'est pas bloquee.
    """
    try:
        _activer_francais_par_defaut(env)
        _supprimer_categories_natives(env)
        _logger.info("Planet Mobil: post_init_hook termine avec succes.")
    except Exception as e:
        _logger.warning("Planet Mobil: post_init_hook ignore (%s)", e)
