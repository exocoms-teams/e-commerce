models/extension_data.py from odoo import models, fields, api
from datetime import datetime 

class ExtensionTracking(models.Model):
    _name = 'extension.tracking'
    _description = 'Extension Tracking Data'
    _order = 'create_date desc'

    product_name = fields.Char(string='Product Name', required=True)
    website = fields.Selection([
        ('amazon', 'Amazon'),
        ('ebay', 'eBay'),
        ('etsy', 'Etsy'),
        ('walmart', 'Walmart'),
        ('other', 'Other'),
    ], string='Website', required=True)
    product_url = fields.Char(string='Product URL')
    price = fields.Float(string='Price', digits=(10, 2))
    currency = fields.Char(string='Currency', default='USD')
    trend_score = fields.Float(string='Trend Score', digits=(3, 2))
    user_id = fields.Many2one('res.users', string='User')
    tracking_date = fields.Datetime(string='Tracking Date', default=fields.Datetime.now)
    notes = fields.Text(string='Notes')

    @api.model
    def get_dashboard_stats(self):
        """Get stats for dashboard"""
        total_products = self.search_count([])
        active_users = self.search_read([], ['user_id']).mapped('user_id')
        active_users_count = len(set(active_users))
        total_trackings = self.search_count([])
        
        # Calculate average trend score
        trend_scores = self.search_read([], ['trend_score'])
        avg_trend = 0
        if trend_scores:
            avg_trend = sum(t.get('trend_score', 0) for t in trend_scores) / len(trend_scores)
        
        return {
            'total_products': total_products,
            'active_users': active_users_count,
            'total_trackings': total_trackings,
            'avg_trend': round(avg_trend, 2),
        }