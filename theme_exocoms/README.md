# theme_exocoms — thème Odoo 19

Portage du prototype statique EXOCOMS en thème Odoo 19. Généré depuis les fichiers HTML du
dossier parent : `index.html`, `pages/*.html` et `partials/*.html`.

## Installation

1. Copier `theme_exocoms/` à la racine du dépôt odoo.sh, sur une **branche de développement**.
2. odoo.sh construit et installe automatiquement.
3. Activer le thème dans **Site web → Configuration → Thème**.
4. **Définir `/accueil` comme page d'accueil** dans les paramètres du site web. Le module
   `website` occupe déjà l'URL `/` ; publier un doublon ferait échouer l'installation.

En local :

```bash
odoo-bin -d exocoms -i theme_exocoms --addons-path=addons,/chemin/vers/ce/depot
```

## Contenu

| Fichier | Rôle |
|---|---|
| `__manifest__.py` | dépendances `website` + `website_crm`, bundle `web.assets_frontend` |
| `views/layout.xml` | sidebar, topbar, footer, et surcharge de `website.layout` |
| `views/pages.xml` | 8 templates de page + 8 enregistrements `website.page` |
| `static/src/scss/main.scss` | design system et styles, repris du prototype |
| `static/src/img/` | sprite d'icônes, illustrations, logos partenaires |




