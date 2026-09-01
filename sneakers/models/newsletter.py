from odoo import models, fields


class NewsletterSubscriber(models.Model):
    _name = 'newsletter.subscriber'
    _description = 'Newsletter Subscriber'
    _order = 'create_date desc'

    email = fields.Char(required=True, index=True)
    name = fields.Char()
    state = fields.Selection([
        ('subscribed', 'Subscribed'),
        ('unsubscribed', 'Unsubscribed'),
    ], default='subscribed', required=True, index=True)
    subscribed_date = fields.Datetime(default=fields.Datetime.now)
    unsubscribed_date = fields.Datetime()

    _email_unique = models.Constraint(
        'UNIQUE(email)',
        'This email is already subscribed.'
    )

    def action_unsubscribe(self):
        self.write({
            'state': 'unsubscribed',
            'unsubscribed_date': fields.Datetime.now,
        })


class NewsletterCampaign(models.Model):
    _name = 'newsletter.campaign'
    _description = 'Newsletter Campaign'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    subject = fields.Char(required=True)
    body_html = fields.Html()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ], default='draft', required=True)
    sent_date = fields.Datetime()
    recipient_count = fields.Integer(default=0)

    def action_mark_sent(self):
        self.write({
            'state': 'sent',
            'sent_date': fields.Datetime.now,
        })
