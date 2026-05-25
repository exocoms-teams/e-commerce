def post_init_hook(env):
    website = env['website'].search([], limit=1)
    if website:
        website.shop_opt_products_design_classes = 'o_wsale_products_opt_design_chips'