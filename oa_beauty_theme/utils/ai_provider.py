import requests
import json
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AIProviderFactory:
    """
    Factory class to instantiate the correct AI provider based on Odoo config.
    Supports Gemini, OpenAI, Claude, and local FastAPI endpoints.
    """
    @staticmethod
    def get_provider(env):
        provider_name = env['ir.config_parameter'].sudo().get_param('oa_beauty_theme.ai_provider', default='gemini')
        api_key = env['ir.config_parameter'].sudo().get_param('oa_beauty_theme.ai_api_key')
        
        if not api_key and provider_name != 'local':
            _logger.warning(f"No API key configured for AI provider: {provider_name}")
            return MockAIProvider()

        if provider_name == 'gemini':
            return GeminiProvider(api_key)
        elif provider_name == 'openai':
            return OpenAIProvider(api_key)
        elif provider_name == 'claude':
            return ClaudeProvider(api_key)
        elif provider_name == 'local':
            # Local endpoint config would be needed here, hardcoded for demo
            return LocalFastAPIProvider("http://localhost:8000")
        else:
            return MockAIProvider()

class BaseAIProvider:
    def generate_response(self, prompt, context=None):
        raise NotImplementedError("Subclasses must implement generate_response")

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"

    def generate_response(self, prompt, context=None):
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            response = requests.post(self.endpoint, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
            return "Désolé, je n'ai pas pu formuler de réponse."
        except Exception as e:
            _logger.error(f"Gemini API Error: {str(e)}")
            return "Une erreur de communication avec l'assistant est survenue."

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def generate_response(self, prompt, context=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            _logger.error(f"OpenAI API Error: {str(e)}")
            return "Une erreur de communication avec l'assistant est survenue."

class ClaudeProvider(BaseAIProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = "https://api.anthropic.com/v1/messages"

    def generate_response(self, prompt, context=None):
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['content'][0]['text']
        except Exception as e:
            _logger.error(f"Claude API Error: {str(e)}")
            return "Une erreur de communication avec l'assistant est survenue."

class LocalFastAPIProvider(BaseAIProvider):
    def __init__(self, base_url):
        self.endpoint = f"{base_url}/generate"

    def generate_response(self, prompt, context=None):
        try:
            response = requests.post(self.endpoint, json={"prompt": prompt}, timeout=10)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            _logger.error(f"Local API Error: {str(e)}")
            return "Le service d'intelligence artificielle local est indisponible."

class MockAIProvider(BaseAIProvider):
    """Fallback provider when no API key is configured."""
    def generate_response(self, prompt, context=None):
        return "Je suis l'assistant virtuel O&A Beauty (Mode Simulation). Je serai bientôt connecté à une intelligence artificielle puissante pour mieux vous servir."
