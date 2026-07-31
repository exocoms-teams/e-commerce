# -*- coding: utf-8 -*-
{
    'name': 'Capsule House Theme',
    'version': '1.0',
    'category': 'Website/Theme',
    'summary': 'Thème officiel du site Capsule House — frontend complet',
    'description': """Thème frontend dédié au site Capsule House (société Exocoms Group), exécuté sur la base Odoo mutualisée multi-sites (environ 17 sites sur la même instance).

Ce module ne doit jamais impacter les autres sites de la base partagée : pas d'assets globaux (le CSS/JS est enregistré dynamiquement via ir.asset scopé website_id), et tous les hooks retrouvent notre site uniquement via son id mémorisé (ir.config_parameter), jamais par nom.

Pages actuellement livrées : Accueil, Boutique. Pages à venir au fur et à mesure : Services, Contact, À propos.
""",
    'author': 'Exocoms Group',
    'website': 'https://capsule-house.fr',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
        # Nécessaire pour que l'icône wishlist du header NATIF Odoo
        # (.o_wsale_my_wish) soit réellement fonctionnelle plutôt que
        # décorative — voir README "Header natif comme sur
        # exocoms_theme" : exocoms_theme lui-même style cette classe
        # dans son CSS sans déclarer cette dépendance dans son propre
        # manifest (donc potentiellement non fonctionnelle chez eux) ;
        # on choisit ici d'être explicite et correct plutôt que de
        # reproduire cette même lacune.
        'website_sale_wishlist',
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
