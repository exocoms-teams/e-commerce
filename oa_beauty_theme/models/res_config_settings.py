from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    oa_ai_api_key = fields.Char(string='AI API Key', config_parameter='oa_beauty_theme.ai_api_key', help='Enter your Gemini or OpenAI API Key here for future LLM integrations.')
    oa_ai_provider = fields.Selection([
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI')
    ], string='AI Provider', default='gemini', config_parameter='oa_beauty_theme.ai_provider')
    oa_ai_system_prompt = fields.Text(string='AI System Prompt', config_parameter='oa_beauty_theme.ai_system_prompt', default='You are an expert luxury beauty advisor for O&A Beauty.')
