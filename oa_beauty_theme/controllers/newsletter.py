# -*- coding: utf-8 -*-
# Part of O&A Beauty Theme. Newsletter → Brevo (ex-Sendinblue) integration.

import json
import logging
import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

# ⚠️ Ne jamais mettre les clés API en dur dans le code.
# Configurez-les dans Odoo : Paramètres → Technique → Paramètres système
# Clés à créer :
#   brevo.api_key     → votre clé API Brevo (xkeysib-...)
#   brevo.list_id     → ID numérique de votre liste Brevo (ex: 3)


class NewsletterController(http.Controller):

    @http.route('/newsletter/subscribe', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def subscribe(self, **kwargs):
        """
        Point d'entrée appelé par le formulaire newsletter du footer.
        Ajoute l'email dans la liste Brevo et renvoie un statut JSON.
        """
        email = (kwargs.get('email') or '').strip()

        if not email or '@' not in email:
            return {'success': False, 'message': 'Adresse e-mail invalide.'}

        params = request.env['ir.config_parameter'].sudo()
        api_key = params.get_param('brevo.api_key', default='')
        list_id = params.get_param('brevo.list_id', default='')

        if not api_key:
            _logger.error("[Newsletter] Brevo API Key non configurée !")
            return {'success': False, 'message': 'Configuration manquante. Contactez l\'administrateur.'}

        if not list_id:
            _logger.error("[Newsletter] Brevo List ID non configuré !")
            return {'success': False, 'message': 'Configuration manquante. Contactez l\'administrateur.'}

        try:
            # API Brevo : créer/mettre à jour un contact
            url = "https://api.brevo.com/v3/contacts"
            headers = {
                "Content-Type": "application/json",
                "api-key": api_key,
            }
            payload = {
                "email": email,
                "listIds": [int(list_id)],
                "updateEnabled": True,   # si le contact existe déjà → mise à jour
                "attributes": {
                    "SOURCE": "O&A Beauty Newsletter Footer",
                },
            }

            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)

            if resp.status_code in (200, 201):
                _logger.info(f"[Newsletter] ✅ {email} abonné avec succès à Brevo.")
                self._trigger_n8n_webhook(email)
                return {'success': True, 'message': 'Merci ! Vérifiez votre boîte mail pour votre code –10 %.'}

            elif resp.status_code == 204:
                # Contact existant mis à jour
                _logger.info(f"[Newsletter] 🔄 {email} déjà existant, mis à jour dans Brevo.")
                self._trigger_n8n_webhook(email)
                return {'success': True, 'message': 'Votre inscription a été mise à jour !'}

            elif resp.status_code == 400:
                data = resp.json()
                code = data.get('code', '')
                if code == 'duplicate_parameter':
                    return {'success': False, 'message': 'Cette adresse est déjà abonnée.'}
                _logger.warning(f"[Newsletter] Brevo 400: {data}")
                return {'success': False, 'message': 'Erreur lors de l\'inscription. Réessayez.'}

            else:
                _logger.error(f"[Newsletter] Brevo erreur {resp.status_code}: {resp.text}")
                return {'success': False, 'message': 'Une erreur est survenue. Réessayez plus tard.'}

        except requests.exceptions.Timeout:
            _logger.error("[Newsletter] Timeout lors de l'appel Brevo.")
            return {'success': False, 'message': 'Délai dépassé. Réessayez plus tard.'}
        except Exception as e:
            _logger.exception(f"[Newsletter] Erreur inattendue: {e}")
            return {'success': False, 'message': 'Une erreur est survenue.'}

    def _trigger_n8n_webhook(self, email):
        """
        Envoie aussi l'email au webhook n8n (optionnel).
        Configurable dans Paramètres Odoo → Paramètres Techniques.
        """
        n8n_url = request.env['ir.config_parameter'].sudo().get_param(
            'n8n.newsletter_webhook_url', default=''
        )
        if not n8n_url:
            return  # pas de webhook configuré, on passe

        try:
            requests.post(
                n8n_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps({"email": email, "source": "newsletter_footer"}),
                timeout=5,
            )
            _logger.info(f"[Newsletter] n8n webhook déclenché pour {email}.")
        except Exception as e:
            _logger.warning(f"[Newsletter] n8n webhook échoué (non bloquant): {e}")
