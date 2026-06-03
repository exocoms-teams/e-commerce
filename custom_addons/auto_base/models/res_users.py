from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auto_base_assign_admin_group(self):
        """Assign the automobile admin group across supported Odoo versions."""
        admin = self.env.ref("base.user_admin", raise_if_not_found=False)
        group = self.env.ref("auto_base.group_auto_admin", raise_if_not_found=False)
        if not admin or not group:
            return True

        group_field = "group_ids" if "group_ids" in admin._fields else "groups_id"
        admin.sudo().write({group_field: [(4, group.id)]})
        return True
