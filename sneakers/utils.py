"""
Shared utilities for the sneakers e-commerce module.

Extracted from controllers/main.py to eliminate duplication.
Free functions — no mixin, no model inheritance.
"""

# ponytail: constants for template-side type checks where Python refs aren't available
PRODUCT_TYPE_DELIVERABLE = 'consu'


def _get_size_attribute(env):
    """Return the product.attribute record for 'Size', or None."""
    return env['product.attribute'].search([('name', '=', 'Size')], limit=1)


def _get_color_attribute(env):
    """Return the product.attribute record for 'Color', or None."""
    return env['product.attribute'].search([('name', '=', 'Color')], limit=1)


def _get_size_values(env, attribute_id):
    """Return attribute values for the given size attribute."""
    return env['product.attribute.value'].search([('attribute_id', '=', attribute_id)])


def _get_color_values(env, attribute_id):
    """Return attribute values for the given color attribute."""
    return env['product.attribute.value'].search([('attribute_id', '=', attribute_id)])


def _resolve_order_note(env, order_note):
    """
    Parse a partner note string and create crm.tag + res.partner.note if new.
    Returns (tag, note) or (None, None) if input is empty.
    """
    if not order_note:
        return None, None

    # ponytail: simple split, assumes '#tag' format from JS
    tag_name = order_note.strip().lstrip('#')
    if not tag_name:
        return None, None

    tag = env['crm.tag'].search([('name', '=', tag_name)], limit=1)
    if not tag:
        tag = env['crm.tag'].create({'name': tag_name})

    note = env['res.partner.note'].create({
        'name': tag_name,
        'tag_id': tag.id,
    })
    return tag, note


def _compute_website_price(product, pricelist):
    """
    Compute the website price for a product given a pricelist.
    Returns the price as a float.
    """
    if not pricelist:
        return product.list_price
    return pricelist.get_product_price(product, 1, False)


def _is_module_installed(env, module_name):
    """Check if a module is installed."""
    return bool(env['ir.module.module'].search([
        ('name', '=', module_name),
        ('state', '=', 'installed'),
    ], limit=1))
