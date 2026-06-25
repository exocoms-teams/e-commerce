# -*- coding: utf-8 -*-
from . import controllers


def _get_website(env):
    """Retourne le website Exocoms Group — par nom ; fallback sur le premier."""
    website = env['website'].search([('name', '=', 'Exocoms Group')], limit=1)
    if not website:
        website = env['website'].search([], limit=1)
    return website


def _position_telecom_menu(env):
    """
    Positionne le méga-menu Télécom juste après Boutique (/shop).

    Logique :
      1. Lit la séquence du menu /shop du site.
      2. Assigne sequence = shop_seq + 1 au menu Télécom.
      3. Décale les autres menus de premier niveau (sequence >= shop_seq + 1)
         pour éviter les collisions.
      4. Défensif : si /shop est introuvable, on place Télécom à sequence=20.

    ⚠️ Risque d'ordre d'exécution : si le post_migrate_hook de exocoms_theme
    tourne APRÈS celui-ci, les séquences seront réinitialisées à 1-7 et
    Événements (seq=3) entrera en collision avec Télécom (seq=3). Pour garantir
    la stabilité, lancer `-u telecom_services` après `-u exocoms_theme`.
    Solution durable : passer les séquences de exocoms_theme de 1-7 à 10-70.
    """
    website = _get_website(env)
    if not website:
        return

    telecom_menu = env.ref('telecom_services.menu_telecom', raise_if_not_found=False)
    if not telecom_menu:
        return

    # Associer au website et au menu racine si pas encore fait
    if not telecom_menu.website_id:
        root_menu = env['website.menu'].search([
            ('parent_id', '=', False),
            ('website_id', '=', website.id),
        ], limit=1)
        vals = {'website_id': website.id}
        if root_menu:
            vals['parent_id'] = root_menu.id
        telecom_menu.write(vals)

    # Lire la séquence du menu Boutique
    shop_menu = env['website.menu'].search([
        ('url', '=', '/shop'),
        ('website_id', '=', website.id),
    ], limit=1)
    shop_seq = shop_menu.sequence if shop_menu else 20

    target_seq = shop_seq + 1
    telecom_menu.write({'sequence': target_seq})

    # Décaler tous les autres menus de premier niveau après Boutique
    parent_id = telecom_menu.parent_id.id or False
    menus_to_shift = env['website.menu'].search([
        ('website_id', '=', website.id),
        ('parent_id', '=', parent_id),
        ('sequence', '>=', target_seq),
        ('id', '!=', telecom_menu.id),
    ], order='sequence asc')
    for i, m in enumerate(menus_to_shift):
        m.write({'sequence': target_seq + 1 + i})


def post_init_hook(env):
    _position_telecom_menu(env)


def post_migrate_hook(env):
    _position_telecom_menu(env)
