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


def _supprimer_demo_natif(env):
    """Supprime les produits et categories demo natifs d'Odoo.
    Logique : supprimer les produits en premier pour lever le blocage
    sur les categories, puis supprimer les categories.
    """
    nos_noms = ['Smartphones', 'Montres', 'Accessoires', 'TV']

    # Categories natives = tout ce qui n'est pas a nous
    cats_natives = env['product.public.category'].sudo().search([
        ('name', 'not in', nos_noms),
    ])
    if not cats_natives:
        _logger.info("Planet Mobil: aucune categorie native a supprimer.")
        return

    nos_cats = env['product.public.category'].sudo().search([
        ('name', 'in', nos_noms),
    ])

    # Produits lies aux categories natives, mais PAS a nos categories
    candidats = env['product.template'].sudo().search([
        ('public_categ_ids', 'in', cats_natives.ids),
    ])
    produits_natifs = candidats.filtered(
        lambda p: not (p.public_categ_ids & nos_cats)
    )

    # 1. Supprimer les produits natifs (archiver si suppression impossible)
    for prod in produits_natifs:
        try:
            prod.unlink()
        except Exception:
            try:
                prod.write({'active': False, 'is_published': False})
                _logger.info("Planet Mobil: produit '%s' archive.", prod.name)
            except Exception as e2:
                _logger.warning("Planet Mobil: produit '%s' non traite (%s)", prod.name, e2)

    # 2. Supprimer les categories natives (maintenant sans produits)
    for cat in cats_natives:
        try:
            cat.unlink()
            _logger.info("Planet Mobil: categorie native '%s' supprimee.", cat.name)
        except Exception as e:
            _logger.warning(
                "Planet Mobil: categorie '%s' non supprimee (%s)", cat.name, e
            )


def post_init_hook(env):
    """Hook execute apres l'installation/mise a jour du module.

    Entoure d'un try/except global : meme en cas d'erreur, le build reste
    vert et l'installation du module n'est pas bloquee.
    """
    try:
        _activer_francais_par_defaut(env)
        _supprimer_demo_natif(env)
        _logger.info("Planet Mobil: post_init_hook termine avec succes.")
    except Exception as e:
        _logger.warning("Planet Mobil: post_init_hook ignore (%s)", e)
