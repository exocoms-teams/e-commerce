import logging

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


def post_init_hook(env):
    website = env['website'].search([], limit=1)
    if not website or not website.menu_id:
        return
    for menu in website.menu_id.child_id:
        new_name = MENU_RENAMES.get(menu.name)
        if new_name:
            menu.name = new_name
        else:
            _logger.info("BlueSpa: menu '%s' laissé tel quel (déjà personnalisé ou déjà traduit)", menu.name)
