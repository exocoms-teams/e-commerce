# -*- coding: utf-8 -*-
"""Migration 19.0.1.6.1

payment_method_data.xml est chargé avec noupdate="1", donc une simple
mise à jour du module ne réapplique jamais les changements sur le champ
`image` de payment.method une fois l'enregistrement déjà créé. On force
donc ici le rechargement du fichier icône depuis le module, une bonne
fois pour toutes, peu importe ce qui était déjà en base.
"""
import base64
import logging
import os

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    method = env.ref(
        'mandat_administratif.payment_method_mandat_administratif',
        raise_if_not_found=False,
    )
    if not method:
        _logger.warning(
            "Migration 19.0.1.6.1 : payment.method "
            "'mandat_administratif' introuvable, rien à faire."
        )
        return

    module_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    icon_path = os.path.join(
        module_root, 'static', 'src', 'img', 'payment_method_icon.png',
    )
    if not os.path.exists(icon_path):
        _logger.warning(
            "Migration 19.0.1.6.1 : fichier icône introuvable (%s), "
            "rien à faire.", icon_path,
        )
        return

    with open(icon_path, 'rb') as f:
        method.image = base64.b64encode(f.read())

    _logger.info(
        "Migration 19.0.1.6.1 : icône de 'Mandat administratif' "
        "rechargée avec succès."
    )
