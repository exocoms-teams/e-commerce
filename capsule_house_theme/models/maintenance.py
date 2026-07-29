# -*- coding: utf-8 -*-
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class CapsuleHouseThemeMaintenance(models.Model):
    """Filet de sécurité horaire, indépendant du versioning des migrations.

    `post_init_hook` ne se rejoue qu'à l'install ou si une nouvelle version
    du manifest ajoute un `migrations/<version>/post-migrate.py`. Ce cron
    rejoue la même logique (`run_theme_maintenance`) toutes les heures, pour
    rattraper : un site fantôme réapparu, des vues qui auraient perdu leur
    website_id suite à une manip manuelle, des produits de notre société pas
    encore publiés sur notre site, etc. Toute la logique appelée est
    idempotente (voir __init__.py), donc ce rejeu horaire est sans risque.
    """
    _name = 'capsule.house.theme.maintenance'
    _description = 'Capsule House Theme — Maintenance horaire (filet de sécurité multi-site)'

    def run(self):
        """Rejoue run_theme_maintenance(env). Appelé par data/cron.xml.

        Import différé (au moment de l'appel, pas au chargement du module)
        pour éviter tout import circulaire avec le package racine, qui
        importe lui-même `models` dans son __init__.py.
        """
        from odoo.addons.capsule_house_theme import run_theme_maintenance
        try:
            run_theme_maintenance(self.env)
        except Exception:
            _logger.exception(
                "capsule_house_theme: échec du cron de maintenance horaire, "
                "sera retenté à la prochaine exécution."
            )
        return True
