# -*- coding: utf-8 -*-
{
    'name': 'Capsule House Theme',
    'version': '19.0.1.0.0',
    'category': 'Website/Theme',
    'summary': 'Thème officiel du site Capsule House — frontend complet',
    'description': """
Capsule House Theme
====================
Thème frontend dédié au site Capsule House (société Exocoms Group), exécuté
sur la base Odoo mutualisée multi-sites (~17 sites sur la même instance).

Ce module ne doit JAMAIS impacter les autres sites de la base partagée :
- Pas d'assets globaux (`web.assets_frontend`) : le CSS/JS est enregistré
  dynamiquement via `ir.asset` scopé à notre `website_id` uniquement
  (voir `_setup_theme_assets` dans `__init__.py`).
- Tous les hooks retrouvent NOTRE site uniquement via son id, mémorisé dans
  `ir.config_parameter` (clé `capsule_house_theme.website_id`), jamais par
  nom (un site homonyme peut déjà exister dans la base partagée).
- Toute requête sur un modèle scopé site est filtrée explicitement sur
  `website_id` (et `company_id` exact, jamais de fallback `company_id=False`).

Pages actuellement livrées : Accueil, Boutique.
Pages à venir (au fur et à mesure) : Services, Contact, À propos.
""",
    'author': 'Exocoms Group',
    'website': 'https://capsule-house.fr',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/website_data.xml',
        'data/seo_data.xml',
        'data/cron.xml',
        'views/templates/header.xml',
        'views/templates/footer.xml',
        'views/templates/layout.xml',
        'views/partials/hero.xml',
        'views/partials/featured_products.xml',
        'views/pages/home.xml',
        'views/pages/shop.xml',
    ],
    # NB: pas de clé 'assets' ici. Les CSS/JS de ce thème sont enregistrés
    # dynamiquement à l'installation via `_setup_theme_assets()` (ir.asset
    # avec website_id posé), jamais via web.assets_frontend (bundle global
    # partagé par tous les sites de la base).
    'post_init_hook': 'post_init_hook',
    # 'post_migrate': documenté ici pour mémoire. Le vrai déclenchement passe
    # par migrations/<version>/post-migrate.py, à dupliquer à CHAQUE bump de
    # version, sinon Odoo ne rejoue jamais le hook après une mise à jour.
    'installable': True,
    'auto_install': False,
    'application': False,
}
