from odoo import http
from odoo.http import request
from ..utils.ai_provider import AIProviderFactory

class ChatbotController(http.Controller):

    @http.route('/api/chat/message', type='jsonrpc', auth='public', website=True, csrf=False)
    def handle_message(self, **kw):
        user_message = kw.get('message', '').lower()
        
        # Use the configured AI provider
        ai_provider = AIProviderFactory.get_provider(request.env)
        
        system_prompt = request.env['ir.config_parameter'].sudo().get_param('oa_beauty_theme.ai_system_prompt', default="Tu es un assistant virtuel de beauté de luxe pour O&A Beauty. Sois élégant et concis.")
        
        full_prompt = f"{system_prompt}\n\nClient: {user_message}\nAssistant:"
        
        bot_reply = ai_provider.generate_response(full_prompt)

        return {
            'status': 'success',
            'reply': bot_reply
        }
