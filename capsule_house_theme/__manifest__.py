# -*- coding: utf-8 -*-
{
    'name': 'Capsule House Theme',
    # NB : ne JAMAIS revenir à un format court ("1.0") — Odoo ne rejoue les
    # scripts de migrations/<version>/ que s'il reconnaît une progression de
    # version cohérente avec le schéma utilisé par ce module (19.0.1.0.x).
    # Un retour à "1.0" fait sauter silencieusement TOUTES les migrations
    # (.1 à .14 à ce jour) au prochain upgrade, ce qui a probablement causé
    # les régressions observées (pricelist, accès société, logo, CSS non
    # appliqués malgré le code correctement poussé).
    'version': '19.0.1.0.70',
    'category': 'Website/Theme',
    'summary': 'Thème officiel du site Capsule House — frontend complet',
    'description': """Thème frontend dédié au site Capsule House (société Exocoms Group), exécuté sur la base Odoo mutualisée multi-sites (environ 17 sites sur la même instance).

Ce module ne doit jamais impacter les autres sites de la base partagée : pas d'assets globaux (le CSS/JS est enregistré dynamiquement via ir.asset scopé website_id), et tous les hooks retrouvent notre site uniquement via son id mémorisé (ir.config_parameter), jamais par nom.

Pages actuellement livrées : Accueil, Nos modèles (/nos-modeles), Boutique, Avis clients (/avis), Aide (Livraison /livraison, Retours /retours, Garantie /garantie, FAQ /faq), Entreprise (À propos /a-propos, Le concept /le-concept), pages légales (Mentions légales /mentions-legales, CGV /cgv, Confidentialité /confidentialite). Le contact passe par la page NATIVE Odoo /contactus, jamais reconstruite par ce module.
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
        # Live chat natif Odoo (v19.0.1.0.36, réplique du mécanisme
        # observé sur exocoms_theme) — voir _setup_livechat() dans
        # __init__.py. Pas de widget tiers (Crisp/Tawk/Intercom).
        'im_livechat',
        'website_livechat',
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
        # Ajouté en 19.0.1.0.67 : page /nos-modeles, sur le modèle de
        # "Nos services" d'exocoms_theme (voir nos_modeles.xml).
        'views/pages/nos_modeles.xml',
        # Avis clients (19.0.1.0.35, voir models/avis.py) : vrais avis
        # soumis par les clients, modérés avant publication. Vues backend
        # de modération d'abord, puis partiels/page frontend.
        'views/avis_backend.xml',
        'views/partials/avis_hero.xml',
        'views/partials/avis_content.xml',
        'views/pages/avis.xml',
        # Pages Aide (19.0.1.0.46) : Livraison, Retours, Garantie, FAQ —
        # liens du footer colonne "Aide", jusque-là en 404. Menu latéral
        # partagé (aide_sidebar.xml) chargé avant les 4 pages qui le
        # t-call-ent.
        'views/partials/aide_sidebar.xml',
        'views/pages/aide_livraison.xml',
        'views/pages/aide_retours.xml',
        'views/pages/aide_garantie.xml',
        'views/pages/aide_faq.xml',
        # Pages Entreprise (19.0.1.0.47) : À propos, Le concept — liens du
        # footer colonne "Entreprise". "Contact" reste la page NATIVE
        # Odoo /contactus (module website, déjà dans les dépendances),
        # aucun fichier de page contact n'est livré par ce module.
        'views/partials/entreprise_nav.xml',
        'views/pages/entreprise_apropos.xml',
        'views/pages/entreprise_concept.xml',
        # Pages légales (19.0.1.0.64) : Mentions légales, CGV,
        # Confidentialité — liens du footer présents depuis le début du
        # projet mais jamais construits jusqu'ici (liens cassés détectés
        # par l'outil SEO natif d'Odoo).
        'views/pages/mentions_legales.xml',
        'views/pages/cgv.xml',
        'views/pages/confidentialite.xml',
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
