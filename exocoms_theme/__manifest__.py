{
    'name': 'Exocoms Theme',
    'version': '1.8',
    'summary': 'Custom website theme for Exocoms Group',
    'author': 'Exocoms Group',
    'license': 'LGPL-3',
    'category': 'Website',
    'depends': [
        'website',
        'website_sale',
        'im_livechat',
        'website_livechat',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/avis_backend.xml',
        'data/cron.xml',
        'data/website_data.xml',
        'views/pages/home.xml',
        'views/pages/services.xml',
        'views/pages/mentions_legales.xml',
        'views/pages/boutique.xml',
        'views/pages/avis.xml',
        'views/partials/hero.xml',
        'views/partials/dashbord.xml',
        'views/partials/dashbord_boutique.xml',
        'views/partials/services_hero.xml',
        'views/partials/services_content.xml',
        'views/partials/mentions_legales_content.xml',
        'views/partials/portal.xml',
        'views/partials/avis_hero.xml',
        'views/partials/avis_content.xml',
        'views/templates/header.xml',
        'views/templates/footer.xml',
        'views/templates/features.xml',
        'views/templates/layout.xml',
        'views/templates/services_features.xml',
        'data/seo_data.xml',
    ],
    # IMPORTANT : le bloc 'assets' a été retiré ICI volontairement.
    # Les CSS/JS étaient chargés via 'web.assets_frontend', un bundle
    # GLOBAL à toute la base Odoo (17 sites), jamais filtré par site.
    # Ils sont désormais enregistrés dynamiquement, scopés au site
    # Exocoms uniquement, via ir.asset + website_id — voir la fonction
    # _setup_theme_assets() dans __init__.py (post_init_hook /
    # post_migrate_hook). Ne PAS remettre de bloc 'assets' statique
    # ici, sous peine de recharger les CSS globalement sur les 16
    # autres sites de la base partagée.
    #
    # CORRECTIF STRUCTUREL : 'post_migrate' (ci-dessous) N'EST PAS une
    # clé reconnue par Odoo (seules pre_init_hook/post_init_hook/
    # uninstall_hook le sont). On la garde ici sans risque (Odoo
    # l'ignore silencieusement), mais le VRAI déclenchement de
    # post_migrate_hook() passe désormais par le script natif
    # migrations/1.2/post-migrate.py. À CHAQUE future mise à jour de
    # post_migrate_hook(), il faudra remonter ce numéro de version ET
    # créer un nouveau dossier migrations/<version>/ correspondant,
    # sinon Odoo ne rejouera jamais le script.
    #
    # FILET DE SÉCURITÉ (depuis 1.2) : un cron (data/cron.xml,
    # modèle exocoms.theme.maintenance) rejoue aussi post_migrate_hook()
    # toutes les heures, indépendamment de tout bump de version — si un
    # jour on oublie la démarche ci-dessus, la configuration se
    # rattrape quand même automatiquement dans l'heure. Le bump de
    # version reste utile pour un effet immédiat au déploiement, mais
    # n'est plus un point de défaillance unique.
    'post_init_hook': 'post_init_hook',
    'post_migrate': 'post_migrate_hook',
    'installable': True,
    'application': True,
}