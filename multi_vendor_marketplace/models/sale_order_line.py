# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
# 
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>. 
#
#############################################################################
# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    """ Added seller information""" 
    _inherit = 'sale.order.line'

    seller_id = fields.Many2one('res.partner', readonly=True,
                                string="Seller",
                                help="For getting seller information",
                                related='product_id.seller_id')
    partner_id = fields.Many2one('res.partner',
                                 related='order_id.partner_id',
                                 string="Customer",
                                 help="Get the partner information")
    marketplace_state = fields.Selection(
        selection=[('pending', 'Pending'),
                   ('approved', 'Approved'),
                   ('shipped', 'Shipped'),
                   ('cancel', 'Cancel')],
        string="Marketplace State",
        help="Get the approval states",
        default='pending')

    def cancel_order(self):
        self.marketplace_state = 'cancel'

    def approve_order(self):
        data_stock_pick = self.env['stock.picking'].sudo().search(
            [('origin', '=', self.order_id.name)])
        partner_id = data_stock_pick.partner_id
        opr_type = data_stock_pick.picking_type_id
        location_id = data_stock_pick.location_id
        location_dst_id = data_stock_pick.location_dest_id
        name = data_stock_pick.name
        vals = []
        qty_info = self.env['stock.quant'].search(
            [('product_id', '=', self.product_id.id), ('location_id', '=', 8)])
        if qty_info.quantity <= self.product_uom_qty:
            qty_reserved = self.product_uom_qty
        else:
            qty_reserved = qty_info.quantity
        vals.append({'product_id': self.product_id,
                     'product_uom_qty': self.product_uom_qty,
                     'forecast_availability': qty_reserved,
                     'location_id': location_id,
                     'location_dest_id': location_dst_id,
                     'name': name})
        if data_stock_pick.state != 'cancel':
            data_stock_pick.state = 'cancel'
            new_rec = self.env['stock.picking'].create({
                'partner_id': partner_id.id,
                'picking_type_id': opr_type.id,
                'seller_id': self.seller_id.id,
                'move_ids_without_package': vals,
                'origin': ' ' + self.order_id.name,
            })
            new_rec.update({'ref_id': self.id})
            new_rec.state = 'assigned'
            self.marketplace_state = 'approved'
        else:
            new_rec = self.env['stock.picking'].create({
                'partner_id': partner_id.id,
                'picking_type_id': opr_type.id,
                'move_ids_without_package': vals,
                'origin': ' ' + self.order_id.name,
            })
            new_rec.update({'ref_id': self.id})
            new_rec.state = 'assigned'
            self.marketplace_state = 'approved'

    def shipped(self):
        stock_picking_record = self.env['stock.picking'].search(
            [('ref_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Picking',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': stock_picking_record.id,
        }