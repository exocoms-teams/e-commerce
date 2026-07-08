from . import models
from . import controllers


def _setup_helpdesk(env):
    """Crée l'équipe support et les SLAs (post_init_hook = registre chargé)"""
    team = env['helpdesk.team'].search([('name', '=', 'Support Infogérance')], limit=1)
    if team:
        return team

    team = env['helpdesk.team'].create({
        'name': 'Support Infogérance',
        'description': 'Équipe dédiée aux clients infogérance Exocoms',
        'assign_method': 'randomly',
    })
    # Note: flags use_* activés manuellement dans UI (évite _check_modules_to_install)

    env['ir.model.data'].create({
        'module': 'exocoms_infogerance',
        'name': 'helpdesk_team_infogerance',
        'model': 'helpdesk.team',
        'res_id': team.id,
    })

    new_stage = env.ref('helpdesk.helpdesk_ticket_stage_new')
    for sla_name, priority, time_val in [
        ('SLA Critique - 4h', '3', 4),
        ('SLA Normal - 24h', '1', 24),
    ]:
        if not env['helpdesk.sla'].search([('name', '=', sla_name)], limit=1):
            env['helpdesk.sla'].create({
                'name': sla_name,
                'team_id': team.id,
                'stage_id': new_stage.id,
                'priority': priority,
                'time': time_val,
                'time_unit': 'hour',
            })
    return team


def post_init_hook(env):
    """Ajoute le menu infogerance détaillée + équipe helpdesk + SLAs"""
    from odoo.addons.website.models.website import Menu

    _setup_helpdesk(env)

    website = env['website'].search([('name', '=', 'Exocoms Group')], limit=1)
    if not website:
        website = env['website'].search([], limit=1)

    if not website:
        return

    parent_menu = env['website.menu'].search([
        ('url', '=', '/infogerance'),
        ('website_id', '=', website.id),
    ], limit=1)

    if parent_menu:
        existing = env['website.menu'].search([
            ('url', '=', '/infogerance/detail'),
            ('website_id', '=', website.id),
        ], limit=1)
        if not existing:
            env['website.menu'].create({
                'name': 'Détail & tarifs',
                'url': '/infogerance/detail',
                'website_id': website.id,
                'parent_id': parent_menu.id,
                'sequence': 20,
            })


def post_migrate_hook(env):
    post_init_hook(env)
