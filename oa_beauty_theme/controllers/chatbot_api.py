from odoo import http
from odoo.http import request

class ChatbotController(http.Controller):

    @http.route('/api/chat/message', type='jsonrpc', auth='public', website=True)
    def handle_message(self, **kw):
        data = request.jsonrequest
        user_message = data.get('message', '').lower()
        
        # In the future, this is where we query Gemini or OpenAI
        # api_key = request.env['ir.config_parameter'].sudo().get_param('oa_beauty_theme.ai_api_key')
        # provider = request.env['ir.config_parameter'].sudo().get_param('oa_beauty_theme.ai_provider')
        # system_prompt = request.env['ir.config_parameter'].sudo().get_param('oa_beauty_theme.ai_system_prompt')

        # Dummy fallback logic matching keywords against product catalog or FAQ
        if 'shipping' in user_message or 'delivery' in user_message:
            bot_reply = "We offer free shipping on all orders over €150. Standard delivery takes 3-5 business days."
        elif 'return' in user_message:
            bot_reply = "O&A Beauty offers a 30-day satisfaction guarantee. If you are not completely satisfied, you can return your items for a full refund."
        elif 'dry skin' in user_message or 'hydration' in user_message:
            # Dynamic product query example
            serum = request.env['product.template'].sudo().search([('name', 'ilike', 'hydrating')], limit=1)
            if serum:
                bot_reply = f"For dry skin, I highly recommend our {serum.name}. It is formulated to deeply hydrate and restore your skin's barrier."
            else:
                bot_reply = "For dry skin, focus on deep hydration. I recommend exploring our Skincare collection."
        else:
            bot_reply = "Welcome to O&A Beauty! I am your AI Beauty Assistant. How can I help you discover your perfect routine today?"

        return {
            'status': 'success',
            'reply': bot_reply
        }
