from odoo import models


class Website(models.Model):
    _inherit = 'website'

    def get_supplement_categories(self):
        self.ensure_one()
        return self.env['product.public.category'].sudo().search(
            [('parent_id', '=', False)], order='sequence, name'
        )

    def get_supplement_category_children(self, category):
        return category.child_id.sorted(key=lambda child: (child.sequence, child.name))

    def get_supplement_attribute_values(self, label):
        attribute = self.env['product.attribute'].sudo().search(
            [('name', 'ilike', label)], limit=1
        )
        return attribute.value_ids if attribute else self.env['product.attribute.value']
