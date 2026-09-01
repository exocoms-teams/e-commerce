from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    oa_ai_api_key = fields.Char(string='AI API Key', config_parameter='oa_beauty_theme.ai_api_key', help='Enter your API Key here for future LLM integrations.')
    oa_ai_provider = fields.Selection([
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI'),
        ('claude', 'Anthropic Claude'),
        ('fastapi', 'Custom FastAPI')
    ], string='AI Provider', default='gemini', config_parameter='oa_beauty_theme.ai_provider')
    oa_ai_system_prompt = fields.Char(string='AI System Prompt', config_parameter='oa_beauty_theme.ai_system_prompt', default='You are an expert luxury beauty advisor for O&A Beauty.')

    # Packlink Pro Settings
    oa_packlink_api_key = fields.Char(string='Packlink API Key', config_parameter='oa_beauty_theme.packlink_api_key', help='Your Packlink PRO API Key.')
    oa_packlink_sandbox = fields.Boolean(string='Packlink Sandbox Mode', config_parameter='oa_beauty_theme.packlink_sandbox', default=True, help='Enable for testing.')

    # Analytics Settings
    oa_ga4_id = fields.Char(string='Google Analytics 4 ID (G-XXXXX)', config_parameter='oa_beauty_theme.ga4_id')
    oa_gtm_id = fields.Char(string='Google Tag Manager ID (GTM-XXXXX)', config_parameter='oa_beauty_theme.gtm_id')
    oa_meta_pixel_id = fields.Char(string='Meta Pixel ID', config_parameter='oa_beauty_theme.meta_pixel_id')
    oa_tiktok_pixel_id = fields.Char(string='TikTok Pixel ID', config_parameter='oa_beauty_theme.tiktok_pixel_id')
    oa_pinterest_tag_id = fields.Char(string='Pinterest Tag ID', config_parameter='oa_beauty_theme.pinterest_tag_id')
    oa_consent_mode_enabled = fields.Boolean(string='Enable Consent Mode v2', config_parameter='oa_beauty_theme.consent_mode_enabled', default=False)
