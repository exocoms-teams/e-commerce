# -*- coding: utf-8 -*-
"""Helpers Firebase partagés (PWA + API)."""


def firebase_params(env):
    icp = env['ir.config_parameter'].sudo()
    return {
        'apiKey':            (icp.get_param('sinistre.firebase_api_key') or '').strip(),
        'authDomain':        (icp.get_param('sinistre.firebase_auth_domain') or '').strip(),
        'projectId':         (icp.get_param('sinistre.firebase_project_id') or '').strip(),
        'storageBucket':     (icp.get_param('sinistre.firebase_storage_bucket') or '').strip(),
        'messagingSenderId': (icp.get_param('sinistre.firebase_messaging_sender_id') or '').strip(),
        'appId':             (icp.get_param('sinistre.firebase_app_id') or '').strip(),
        'vapidKey':          (icp.get_param('sinistre.firebase_vapid_key') or '').strip(),
    }


def firebase_configured(params):
    return bool(
        params.get('apiKey')
        and params.get('projectId')
        and params.get('vapidKey')
        and not str(params['apiKey']).startswith('__')
    )


def inject_firebase_sw(content, params):
    mapping = {
        '__FIREBASE_API_KEY__':             params.get('apiKey', ''),
        '__FIREBASE_AUTH_DOMAIN__':         params.get('authDomain', ''),
        '__FIREBASE_PROJECT_ID__':          params.get('projectId', ''),
        '__FIREBASE_STORAGE_BUCKET__':      params.get('storageBucket', ''),
        '__FIREBASE_MESSAGING_SENDER_ID__': params.get('messagingSenderId', ''),
        '__FIREBASE_APP_ID__':              params.get('appId', ''),
    }
    for placeholder, value in mapping.items():
        content = content.replace(placeholder, value or placeholder)
    return content
