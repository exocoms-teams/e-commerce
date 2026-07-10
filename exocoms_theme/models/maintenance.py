# -*- coding: utf-8 -*-
from odoo import api, models


class ExocomsThemeMaintenance(models.AbstractModel):
    """Point d'entrée appelé par le cron 'Exocoms Theme — Ré-application
    config' (voir data/cron.xml).

    POURQUOI CE MODÈLE EXISTE : post_migrate_hook() (dans __init__.py)
    ne se rejoue automatiquement QUE via un script de migration
    versionné (migrations/<version>/post-migrate.py), lui-même
    déclenché UNIQUEMENT si le numéro de 'version' du manifest a été
    remonté avant le push. Concrètement : chaque future modification de
    post_migrate_hook() oblige à penser à bumper la version ET créer le
    dossier migrations/ correspondant — sinon le correctif reste lettre
    morte sur un site déjà installé (c'est exactement ce qui s'est
    passé pour le rattachement des filtres Monétique).

    Ce cron sert de FILET DE SÉCURITÉ automatique : il rejoue
    périodiquement post_migrate_hook() SANS dépendre d'un bump de
    version. Toutes les fonctions qu'il appelle sont conçues pour être
    idempotentes (rien n'est dupliqué ni écrasé si c'est déjà à jour),
    donc l'exécuter toutes les heures ne présente aucun risque.

    Les enregistrements ir.cron sont chargés via 'data/' dans le
    manifest — ces fichiers sont eux TOUJOURS rejoués à chaque mise à
    jour du module (`-u exocoms_theme`), contrairement aux hooks. Donc
    même si on oublie de bumper la version, le cron continuera d'exister
    et de tourner, et rattrapera la configuration dans l'heure qui suit
    le déploiement — au lieu de rester cassé indéfiniment.
    """
    _name = 'exocoms.theme.maintenance'
    _description = "Exocoms Theme — Maintenance périodique (filet de sécurité)"

    @api.model
    def run(self):
        from odoo.addons.exocoms_theme import post_migrate_hook
        post_migrate_hook(self.env)
