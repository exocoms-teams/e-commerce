# -*- coding: utf-8 -*-
from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.mandat_admin.models.res_partner import PUBLIC_ENTITY_TYPES


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
                'is_organisme_public': bool(post.get('is_organisme_public')),
                'chorus_engagement_required': bool(
                    post.get('chorus_engagement_required')),
                'structure_chorus': (post.get('chorus_siret') or '').strip()
                                or False,
                'service_chorus': (post.get('chorus_service_code')
                                        or '').strip() or False,
            }
            entity_type = post.get('public_entity_type')
            valid_types = [t[0] for t in PUBLIC_ENTITY_TYPES]
            values['public_entity_type'] = (
                entity_type if entity_type in valid_types else False
            )
            if values['is_organisme_public'] and not values['public_entity_type']:
                error_message = _(
                    "Veuillez sélectionner votre type de structure pour "
                    "déterminer le délai global de paiement applicable.")
            else:
                declaration_changed = (
                    values['is_organisme_public']
                    and (not partner.is_organisme_public
                         or partner.public_entity_type
                         != values['public_entity_type']
                         or (partner.structure_chorus or False)
                         != values['structure_chorus'])
                )
                try:
                    partner.sudo().write(values)
                    success = True
                except ValidationError as error:
                    error_message = str(error)

        return request.render(
            'mandat_admin.portal_mandat_form',
            {
                'partner': partner,
                'entity_types': PUBLIC_ENTITY_TYPES,
                'error_message': error_message,
                'success': success,
                'page_name': 'mandat_administratif',
            },
        )
