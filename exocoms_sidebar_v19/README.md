# EXOCOMS — Sidebar Filter
## Module Odoo **19** — Panneau latéral de filtrage 3 niveaux

---

## Structure du module

```
exocoms_sidebar_v19/
├── __init__.py
├── __manifest__.py                          ← version 19.0.1.0.0
├── controllers/
│   ├── __init__.py
│   └── main.py                              ← Contrôleur Python (Odoo 19 API)
├── static/src/
│   ├── css/
│   │   └── sidebar_filter.scss             ← Bootstrap 5.3 + variables EXOCOMS
│   └── js/
│       └── sidebar_filter.js               ← Module ES (@odoo-module)
└── views/
    └── sidebar_filter_templates.xml        ← QWeb + héritage website_sale v19
```

---

## Différences importantes vs Odoo 17

| Point                        | Odoo 17                          | Odoo 19                              |
|------------------------------|----------------------------------|--------------------------------------|
| Signature `shop()`           | `shop(page, category, ppg, ...)` | `shop(page, category, ...)` sans ppg |
| Publication catégories       | `website_published`              | Filtrage par `website_id`            |
| Publication produits         | `website_published`              | `is_published`                       |
| Modules JS                   | `odoo.define()` / `require()`    | `/** @odoo-module **/` ES natif      |
| Bootstrap                    | 4.x                              | 5.3 (`@include media-breakpoint-*`)  |
| Hook rechargement partiel    | n/a                              | `o_website_content_loaded`           |
| XPath page /shop             | `o_wsale_products_main_col`      | `o_wsale_products_grid_wrapper`      |
| Import contrôleur parent     | `website_sale.controllers.main`  | Idem ou `website_sale.controllers.website_sale` |

---

## Installation sur Odoo SH

```bash
# 1. Copie le dossier dans ton dépôt
cp -r exocoms_sidebar_v19/ /chemin/vers/ton-repo/custom_addons/

# 2. Déclare le dossier dans odoo.conf (si ce n'est pas déjà fait)
#    addons_path = ...,/chemin/vers/ton-repo/custom_addons

# 3. Push sur Odoo SH
git add custom_addons/exocoms_sidebar_v19/
git commit -m "feat: sidebar filter EXOCOMS v19"
git push
```

Puis dans Odoo :
- **Paramètres > Activer mode développeur**
- **Applications > Mettre à jour la liste**
- Installer **EXOCOMS — Sidebar Filter**

---

## Configuration des catégories

### Créer la hiérarchie dans Odoo

**Site Web > Configuration > Catégories de produits** (3 niveaux max) :

```
Monétique                          ← niveau 1 (parent_id = vide)
├── Terminaux de paiement          ← niveau 2
│   ├── Ingenico Desk 5000         ← niveau 3
│   └── Verifone T650p
└── TPE mobiles
    ├── SumUp Air
    └── Square Reader
```

### Ajouter les icônes Font Awesome par catégorie (optionnel)

Via **Studio** ou un module, ajoute un champ `x_sidebar_icon` (Char) sur
`product.public.category`. Renseigne des classes FA v4 : `fa-credit-card`,
`fa-shield`, `fa-wifi`, `fa-server`, etc.

Si le champ est absent, l'icône `fa-folder` est utilisée par défaut.

---

## Filtrage URL

Le bouton **Appliquer les filtres** génère :
```
/shop?cat_ids=12,34,56
```

Les IDs correspondent aux `product.public.category.id`.
Le contrôleur Python filtre automatiquement les produits avec :
```python
("public_categ_ids", "child_of", cat_ids)
```
ce qui inclut les produits des sous-catégories enfants.

---

## Route AJAX (optionnel)

Une route JSON est disponible pour du filtrage dynamique sans rechargement :

```javascript
const res = await fetch("/shop/sidebar/filter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        jsonrpc: "2.0", method: "call",
        params: { cat_ids: [12, 34], page: 0 }
    })
});
const { result } = await res.json();
// result.product_count, result.product_ids
```

---

## Personnalisation couleurs

Dans `static/src/css/sidebar_filter.scss` :

```scss
$exo-primary:    #1D9E75;   // couleur principale des cases à cocher et bouton
$exo-primary-dk: #0F6E56;   // hover du bouton
$exo-primary-lt: #E1F5EE;   // fond des tags actifs
$exo-purple:     #7F77DD;   // lien "Tout effacer"
```

---

## Dépannage

| Symptôme | Cause probable | Solution |
|----------|---------------|----------|
| Sidebar absent sur /shop | XPath ne correspond pas | Inspecter le DOM et ajuster le XPath dans `sidebar_filter_templates.xml` |
| Catégories vides | `website_id` ne correspond pas | Vérifier la configuration multi-site dans les catégories |
| JS ne se charge pas | Module non déclaré dans assets | Vérifier `__manifest__.py` > `web.assets_frontend` |
| SCSS non compilé | Fichier `.scss` au lieu de `.css` | Normal en Odoo SH — le SCSS est compilé automatiquement |
