import requests
import json
import logging
import os
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AIProviderFactory:
    """
    Factory class to instantiate the correct AI provider based on Odoo config.
    Supports Gemini, OpenAI, Claude, and local FastAPI endpoints.
    """
    @staticmethod
    def get_provider(env):
        config = env['ir.config_parameter'].sudo()
        provider_name = (config.get_param('oa_beauty_theme.ai_provider', default='gemini') or 'gemini').lower()
        api_key = config.get_param('oa_beauty_theme.ai_api_key') or AIProviderFactory._get_env_api_key(provider_name)
        
        if provider_name in ('local', 'fastapi'):
            return LocalFastAPIProvider(os.getenv('OA_BEAUTY_AI_LOCAL_URL', 'http://localhost:8000'))

        if not api_key:
            _logger.warning(f"No API key configured for AI provider: {provider_name}")
            return MockAIProvider()

        if provider_name == 'gemini':
            model = config.get_param('oa_beauty_theme.gemini_model', default='gemini-3.5-flash')
            return GeminiProvider(api_key, model=model)
        elif provider_name == 'openai':
            return OpenAIProvider(api_key)
        elif provider_name == 'claude':
            return ClaudeProvider(api_key)
        else:
            return MockAIProvider()

    @staticmethod
    def _get_env_api_key(provider_name):
        env_names = {
            'gemini': ('GEMINI_API_KEY', 'GOOGLE_API_KEY'),
            'openai': ('OPENAI_API_KEY',),
            'claude': ('ANTHROPIC_API_KEY',),
        }
        for name in env_names.get(provider_name, ()):
            value = os.getenv(name)
            if value:
                return value
        return None

class BaseAIProvider:
    def generate_response(self, prompt, context=None):
        raise NotImplementedError("Subclasses must implement generate_response")

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key, model='gemini-3.5-flash'):
        self.api_key = api_key
        self.model = model
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate_response(self, prompt, context=None):
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': self.api_key,
        }
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
            return "Désolé, je n'ai pas pu formuler de réponse."
        except requests.exceptions.HTTPError as e:
            response = e.response
            status_code = response.status_code if response is not None else 'unknown'
            error_text = ''
            if response is not None:
                try:
                    error_data = response.json()
                    error_text = error_data.get('error', {}).get('message') or str(error_data)[:500]
                except ValueError:
                    error_text = response.text[:500]
            _logger.error("Gemini API HTTP error: status=%s model=%s message=%s", status_code, self.model, error_text)
            return "Une erreur de communication avec l'assistant est survenue."
        except Exception as e:
            _logger.error("Gemini API error: type=%s model=%s message=%s", type(e).__name__, self.model, str(e))
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
