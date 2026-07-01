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
    """Depublie les produits qui n'appartiennent a aucune categorie Planet Mobil.
    Logique : on recupere nos categories via leur xmlid (module=website_planet_mobil),
    puis on depublie tous les produits publiés qui n'en font pas partie.
    On ne supprime pas (contraintes FK Odoo), on depublie seulement.
    """
    pm_cat_ids = env['ir.model.data'].sudo().search([
        ('model', '=', 'product.public.category'),
        ('module', '=', 'website_planet_mobil'),
    ]).mapped('res_id')

    if not pm_cat_ids:
        _logger.info("Planet Mobil: categories PM non trouvees, nettoyage ignore.")
        return

    # Produits publiés qui ne sont dans AUCUNE de nos categories
    produits_natifs = env['product.template'].sudo().search([
        ('is_published', '=', True),
        '!', ('public_categ_ids', 'in', pm_cat_ids),
    ])

    if not produits_natifs:
        _logger.info("Planet Mobil: aucun produit natif publie a depublier.")
        return

    for prod in produits_natifs:
        try:
            prod.write({'is_published': False})
            _logger.info("Planet Mobil: produit '%s' depublie.", prod.name)
        except Exception as e:
            _logger.warning(
                "Planet Mobil: produit '%s' non depublie (%s)", prod.name, e
            )


def _configurer_shop(env):
    """Force 4 produits par ligne sur la page shop."""
    websites = env['website'].search([])
    for website in websites:
        try:
            website.write({'shop_ppr': 4})
            _logger.info("Planet Mobil: shop_ppr=4 applique sur '%s'.", website.name)
        except Exception as e:
            _logger.warning("Planet Mobil: shop_ppr non applique (%s)", e)


def _run_hooks(env):
    _activer_francais_par_defaut(env)
    _supprimer_demo_natif(env)
    _configurer_shop(env)


def post_init_hook(env):
    """Apres installation initiale."""
    try:
        _run_hooks(env)
        _logger.info("Planet Mobil: post_init_hook termine avec succes.")
    except Exception as e:
        _logger.warning("Planet Mobil: post_init_hook ignore (%s)", e)


def post_migrate_hook(env):
    """Apres chaque upgrade du module (--update)."""
    try:
        _run_hooks(env)
        _logger.info("Planet Mobil: post_migrate_hook termine avec succes.")
    except Exception as e:
        _logger.warning("Planet Mobil: post_migrate_hook ignore (%s)", e)
