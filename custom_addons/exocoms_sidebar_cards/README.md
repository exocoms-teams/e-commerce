# EXOCOMS – Sidebar de filtres e-commerce (Odoo 19) — Modèle 1 (Cartes)

Module **complet et autonome** pour le e-commerce **Odoo 19**, mise en page
**Cartes**, snippet Website Builder (drag & drop) + module à rafraîchissement
automatique (AJAX).

## Fonctionnalités

- Catégories `product.public.category` repliables sur **3 niveaux** (icône
  niveau 1, cases à cocher niveaux 2-3, quantités disponibles).
- **Filtre par marques** (`product.brand`) repliable, cases à cocher, quantités.
- **Curseur de prix** double poignée.
- **Comparaison de produits** (max 4) avec, dans la modale :
  **Imprimer** (ouvre une page imprimable auto via `/exocoms/compare?...&print=1`)
  et **Partager** (lien encodant les produits comparés, API Web Share avec
  repli copie presse-papier).
- **Pagination réelle** : boutons « Précédent / Suivant » + numéros de page.
- **Rafraîchissement AJAX** sans rechargement.

## Options Website Builder

Produits par page (24/48/72), Filtre Marques (Affiché/Masqué), Comparaison
(Activée/Désactivée).

## Page de comparaison autonome

`/exocoms/compare?ids=ID1,ID2,...` (route `type="http"`, publique) rend un
tableau comparatif dans la mise en page du site ; le paramètre `&print=1`
déclenche l'impression automatique. C'est la cible des boutons Imprimer/Partager.

## APIs Odoo 19 (aucune fonctionnalité d'ancienne version)

`@web/public/interaction` (remplace `publicWidget`), `@web/core/network/rpc`,
routes `type="jsonrpc"` / `type="http"`, options `BaseOptionComponent` +
`BuilderAction` (bundle `website.website_builder_assets`), vues `<list>`.

## Installation

1. Copier `exocoms_sidebar_cards/` dans un répertoire d'addons.
2. *Apps → Mettre à jour la liste*, installer **« Modèle 1 - Cartes »**.
3. Renseigner les marques (*Ventes → Configuration → Marques*) et les affecter aux produits.
4. Éditer une page Website → glisser **« Filtres & catalogue »** (catégorie *Structure*).

> ⚠️ **Modules alternatifs et mutuellement exclusifs.** Les modules
> `exocoms_sidebar_cards`, `exocoms_sidebar_accordion` et
> `exocoms_sidebar_tree` partagent le modèle `product.brand` et les mêmes
> routes : **n'installez qu'un seul des trois à la fois**.

Section du snippet : `<section class="s_exocoms_sidebar o_exocoms_root">`.
