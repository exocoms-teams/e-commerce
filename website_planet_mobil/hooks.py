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
    """Force 5 produits par ligne sur la page shop."""
    websites = env['website'].search([])
    for website in websites:
        try:
            website.write({'shop_ppr': 5})
            _logger.info("Planet Mobil: shop_ppr=5 applique sur '%s'.", website.name)
        except Exception as e:
            _logger.warning("Planet Mobil: shop_ppr non applique (%s)", e)


def _activer_cookies_bar(env):
    """Active la barre de consentement cookies sur chaque site web.
    Equivaut a cocher 'Barre de cookies' dans Site Web > Configuration >
    Parametres, reglage perdu a chaque rebuild de la base."""
    websites = env['website'].search([])
    for website in websites:
        try:
            website.write({'cookies_bar': True})
            _logger.info("Planet Mobil: cookies_bar active sur '%s'.", website.name)
        except Exception as e:
            _logger.warning("Planet Mobil: cookies_bar non applique (%s)", e)


def _archiver_carriers_demo(env):
    """Archive les methodes de livraison demo d'Odoo (Standard delivery,
    The Poste, Local Delivery) pour ne garder que les notres.
    Logique : tous les carriers qui n'ont PAS un xmlid du module
    website_planet_mobil sont archives.
    """
    pm_carrier_ids = env['ir.model.data'].sudo().search([
        ('model', '=', 'delivery.carrier'),
        ('module', '=', 'website_planet_mobil'),
    ]).mapped('res_id')

    carriers_demo = env['delivery.carrier'].with_context(active_test=False).sudo().search([
        ('id', 'not in', pm_carrier_ids),
        ('active', '=', True),
    ])

    for carrier in carriers_demo:
        try:
            carrier.write({'active': False})
            _logger.info("Planet Mobil: carrier demo '%s' archive.", carrier.name)
        except Exception as e:
            _logger.warning("Planet Mobil: carrier '%s' non archive (%s)", carrier.name, e)


def _archiver_attributs_brand_doubles(env):
    """Archive les attributs 'Brand'/'brand' natifs Odoo pour ne garder que le notre.
    Sans ca, le filtre /shop (limit:1) tombe sur le natif (ID inferieur) et ignore
    notre attr_brand qui a les vraies valeurs Apple/Samsung/LG.
    """
    our_brand = env.ref('website_planet_mobil.attr_brand', raise_if_not_found=False)
    if not our_brand:
        _logger.warning("Planet Mobil: attr_brand introuvable, nettoyage Brand ignore.")
        return

    doublons = env['product.attribute'].with_context(active_test=False).sudo().search([
        ('name', 'in', ['Brand', 'brand', 'Marque', 'marque']),
        ('id', '!=', our_brand.id),
    ])
    for attr in doublons:
        try:
            attr.write({'active': False})
            _logger.info("Planet Mobil: attribut doublon '%s' (id=%s) archive.", attr.name, attr.id)
        except Exception as e:
            _logger.warning("Planet Mobil: attribut '%s' non archive (%s)", attr.name, e)


def _activer_virement_bancaire(env):
    """Active le virement bancaire (Wire Transfer) comme moyen de paiement.
    Odoo.sh recrée une base fraiche a chaque push → le provider repasse en
    'disabled'. Ce hook le remet en 'enabled' automatiquement.
    """
    try:
        provider = env.ref('payment.payment_provider_transfer', raise_if_not_found=False)
        if provider:
            provider.sudo().write({'state': 'enabled'})
            _logger.info("Planet Mobil: Wire Transfer active.")
        else:
            _logger.warning("Planet Mobil: Wire Transfer introuvable (xmlid payment.payment_provider_transfer).")
    except Exception as e:
        _logger.warning("Planet Mobil: Wire Transfer non active (%s)", e)


def _run_hooks(env):
    _activer_francais_par_defaut(env)
    _supprimer_demo_natif(env)
    _configurer_shop(env)
    _activer_cookies_bar(env)
    _archiver_carriers_demo(env)
    _archiver_attributs_brand_doubles(env)
    _activer_virement_bancaire(env)


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
