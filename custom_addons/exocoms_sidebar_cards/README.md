# EXOCOMS – Sidebar de filtres e-commerce (Odoo 19) — Modèle 1 (Cartes)

Module **complet et autonome** pour le e-commerce **Odoo 19**, mise en page
**Cartes**, avec snippet Website Builder (drag & drop) :

- Catégories `product.public.category` repliables sur **3 niveaux** (icône au
  niveau 1, cases à cocher aux niveaux 2 et 3, quantités disponibles).
- **Filtre par marques** (`product.brand`) repliable, cases à cocher, quantités.
- **Curseur de prix** à double poignée.
- **Comparaison de produits** autonome (tableau comparatif en modale, max 4).
- **Pagination réelle** : boutons « Précédent / Suivant » + numéros de page.
- **Rafraîchissement AJAX** sans rechargement.

## Options Website Builder (panneau de droite)

- **Produits par page** : 24 / 48 / 72 (action custom `BuilderAction`).
- **Filtre Marques** : Affiché / Masqué (`classAction`).
- **Comparaison de produits** : Activée / Désactivée (`classAction`).

## APIs Odoo 19 (aucune fonctionnalité d'ancienne version)

- Front : `@web/public/interaction` (remplace `publicWidget`), `@web/core/network/rpc`.
- Contrôleur : routes `type="jsonrpc"`.
- Options éditeur : `BaseOptionComponent` / `BuilderAction`, plugin
  `website-plugins`, bundle `website.website_builder_assets`.
- Vues back-office : balise `<list>`.

## Installation

1. Copier `exocoms_sidebar_cards/` dans un répertoire d'addons.
2. *Apps → Mettre à jour la liste des applications*, puis installer
   **« EXOCOMS - Sidebar de filtres (Modèle 1 - Cartes) »**.
3. Renseigner les marques (*Ventes → Configuration → Marques*) et les affecter
   aux produits.
4. Éditer une page Website → glisser le bloc **« Filtres & catalogue »**
   (catégorie *Structure*).

> ⚠️ **Modules alternatifs.** `exocoms_sidebar_cards` (Modèle 1) et
> `exocoms_sidebar_accordion` (Modèle 2) définissent le même modèle
> `product.brand` et les mêmes routes : **n'installez qu'un seul des deux à la
> fois** (ils sont mutuellement exclusifs).

Section du snippet : `<section class="s_exocoms_sidebar o_exocoms_root">`.
