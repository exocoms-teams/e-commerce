from odoo import models, fields


class SocialPost(models.Model):
    _name = 'social.post'
    _description = 'Social Media Post'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    content = fields.Text(required=True)
    platform = fields.Selection([
        ('twitter', 'Twitter/X'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
        ('instagram', 'Instagram'),
    ], required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ], default='draft', required=True, index=True)
    post_url = fields.Char(readonly=True)
    published_date = fields.Datetime()
    image_ids = fields.Many2many('ir.attachment', relation='social_post_attachment_rel', string='Images')

    def action_mark_published(self, url=False):
        self.write({
            'state': 'published',
            'published_date': fields.Datetime.now,
            'post_url': url,
        })

    def action_mark_failed(self):
        self.write({'state': 'failed'})
