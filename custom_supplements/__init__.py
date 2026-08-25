from . import models
from . import controllers
from .hooks import demo_purge

def post_init_hook(env):
    top_menu = env['website.menu'].search([
        ('parent_id', '=', False),
        ('website_id', '!=', False),
    ], limit=1)

    if not top_menu:
        return

    for xmlid in ['custom_supplements.menu_home', 'custom_supplements.menu_shop']:
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            record.write({
                'parent_id': top_menu.id,
                'website_id': top_menu.website_id.id,
            })
    
    # Propager website_id aux enfants de menu_shop
    menu_shop = env.ref('custom_supplements.menu_shop', raise_if_not_found=False)
    if menu_shop:
        menu_shop.child_id.write({'website_id': top_menu.website_id.id})