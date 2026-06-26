from . import controllers


def post_init_hook(env):
    _position_telecom_menu(env)


def post_migrate_hook(env):
    _position_telecom_menu(env)


def _position_telecom_menu(env):
    website = env['website'].search([], limit=1)
    if not website:
        return

    root_menu = env['website.menu'].search([
        ('website_id', '=', website.id),
        ('parent_id', '=', False),
    ], limit=1)
    if not root_menu:
        return

    shop_menu = env['website.menu'].search([
        ('url', '=', '/shop'),
        ('website_id', '=', website.id),
    ], limit=1)

    if shop_menu:
        shop_seq = shop_menu.sequence
    else:
        last_child = env['website.menu'].search([
            ('website_id', '=', website.id),
            ('parent_id', '=', root_menu.id),
        ], order='sequence desc', limit=1)
        shop_seq = last_child.sequence if last_child else 10

    telecom_menu = env.ref('telecom_services.menu_telecom', raise_if_not_found=False)
    if not telecom_menu:
        return

    # Décale vers le bas les menus après /shop pour faire de la place
    menus_after = env['website.menu'].search([
        ('website_id', '=', website.id),
        ('parent_id', '=', root_menu.id),
        ('sequence', '>', shop_seq),
        ('id', '!=', telecom_menu.id),
    ], order='sequence desc')
    for m in menus_after:
        m.sequence += 1

    telecom_menu.write({
        'website_id': website.id,
        'parent_id': root_menu.id,
        'sequence': shop_seq + 1,
    })
