import base64
import logging
import os

_logger = logging.getLogger(__name__)

# Libellés observés sur le site BlueSpa original (démo du 25/06/2026). Odoo crée
# par défaut des entrées de menu "Home" / "Shop" / "Contact Us" à l'installation
# du module website : on les renomme si on les trouve encore sous leur nom par
# défaut, sans rien casser si elles ont déjà été traduites ou renommées.
MENU_RENAMES = {
    'Home': 'Accueil',
    'Shop': 'Boutique',
    'Contact Us': 'Contactez-nous',
    'Contact us': 'Contactez-nous',
}

LOGO_PATH = os.path.join(os.path.dirname(__file__), 'static', 'src', 'img', 'logo.png')


def post_init_hook(env):
    _rename_default_menus(env)
    _set_website_logo(env)


def _rename_default_menus(env):
    website = env['website'].search([], limit=1)
    if not website or not website.menu_id:
        return
    for menu in website.menu_id.child_id:
        new_name = MENU_RENAMES.get(menu.name)
        if new_name:
            menu.name = new_name
        else:
            _logger.info("BlueSpa: menu '%s' laissé tel quel (déjà personnalisé ou déjà traduit)", menu.name)


def _set_website_logo(env):
    """Pose le logo BlueSpa (haut à gauche du header) depuis l'image livrée avec
    le module, plutôt que de compter sur un import manuel via Réglages > Site Web
    qui serait reperdu au prochain rebuild d'une base de développement."""
    if not os.path.isfile(LOGO_PATH):
        _logger.warning("BlueSpa: logo introuvable à %s", LOGO_PATH)
        return
    website = env['website'].search([], limit=1)
    if not website:
        return
    with open(LOGO_PATH, 'rb') as f:
        logo_data = base64.b64encode(f.read())
    try:
        if 'logo' in website._fields:
            website.write({'logo': logo_data})
        elif website.company_id and 'logo' in website.company_id._fields:
            website.company_id.write({'logo': logo_data})
        else:
            _logger.warning("BlueSpa: aucun champ logo trouvé sur website/company_id")
    except Exception:
        _logger.exception("BlueSpa: échec de l'écriture du logo du site")
