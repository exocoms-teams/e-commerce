# -*- coding: utf-8 -*-
from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.mandat_administratif.models.res_partner import (
    PUBLIC_ENTITY_TYPES,
)


class MandatAdministratifPortal(http.Controller):

    @http.route(['/my/mandat-administratif'], type='http', auth='user',
                methods=['GET', 'POST'], website=True)
    def portal_mandat_administratif(self, **post):
        """Page « Mon compte » permettant à l'entité publique de déclarer
        elle-même son type de structure (délai 30/50/60 jours), son SIRET,
        son code service Chorus Pro et l'exigence d'engagement juridique."""
        partner = request.env.user.partner_id.commercial_partner_id
        error_message = False
        success = False

        if request.httprequest.method == 'POST':
            values = {
                'is_public_entity': bool(post.get('is_public_entity')),
                'chorus_engagement_required': bool(
                    post.get('chorus_engagement_required')),
                'chorus_siret': (post.get('chorus_siret') or '').strip()
                                or False,
                'chorus_service_code': (post.get('chorus_service_code')
                                        or '').strip() or False,
            }
            entity_type = post.get('public_entity_type')
            valid_types = [t[0] for t in PUBLIC_ENTITY_TYPES]
            values['public_entity_type'] = (
                entity_type if entity_type in valid_types else False
            )
            if values['is_public_entity'] and not values['public_entity_type']:
                error_message = _(
                    "Veuillez sélectionner votre type de structure pour "
                    "déterminer le délai global de paiement applicable.")
            else:
                declaration_changed = (
                    values['is_public_entity']
                    and (not partner.is_public_entity
                         or partner.public_entity_type
                         != values['public_entity_type']
                         or (partner.chorus_siret or False)
                         != values['chorus_siret'])
                )
                try:
                    partner.sudo().write(values)
                    partner.sudo()._apply_public_payment_term()
                    if declaration_changed:
                        partner.sudo()._notify_public_entity_declaration()
                    success = True
                except ValidationError as error:
                    error_message = str(error)

        return request.render(
            'mandat_administratif.portal_mandat_form',
            {
                'partner': partner,
                'entity_types': PUBLIC_ENTITY_TYPES,
                'error_message': error_message,
                'success': success,
                'page_name': 'mandat_administratif',
            },
        )
