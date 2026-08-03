from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _pre_dispatch(cls, rule, args):
        super()._pre_dispatch(rule, args)
        # Filet de sécurité EF-023 : sur ce déploiement, la résolution native
        # (URL > cookie frontend_lang > contexte > langue par défaut) faite par
        # http_routing ne retient pas toujours le cookie quand l'URL n'a pas de
        # préfixe de langue (constaté en test : le cookie revenait écrasé à la
        # langue par défaut). On revérifie ici explicitement le cookie brut de
        # la requête entrante et on corrige le contexte/cookie si besoin.
        if not getattr(request, 'is_frontend', False):
            return
        cookie_lang = request.cookies.get('frontend_lang')
        if not cookie_lang or cookie_lang == request.env.context.get('lang'):
            return
        lang = request.env['res.lang'].sudo().search([('code', '=', cookie_lang), ('active', '=', True)], limit=1)
        if lang:
            request.update_context(lang=lang.code)
            request.lang = request.env['res.lang']._get_data(code=lang.code)
            request.future_response.set_cookie('frontend_lang', lang.code)
