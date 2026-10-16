# Plan: Modernisation de la barre de recherche et du tri sur /shop

## Context
Le design actuel des éléments de contrôle de la page /shop (barre de recherche et menu de tri) est jugé trop basique. L'objectif est de les moderniser pour les aligner avec l'identité visuelle épurée du thème monetique_theme.

## Proposed Changes
1. **Barre de recherche**: 
   - Cible: .o_wsale_products_searchbar_form
   - Design: Container arrondi (24px-30px), fond blanc, bordure #e2e8f0, effet focus (halo bleu).
   - Intégrer l'icône loupe.
2. **Menu de tri**: 
   - Cible: .dropdown_sorty_by (ou équivalent)
   - Style: Coins arrondis (20px), ombre portée douce sur dropdown-menu.

## Files to Modify
- monetique_theme/static/src/css/shop_categories.css : Ajout des règles CSS.
- monetique_theme/views/templates/shop.xml : (Si nécessaire) Surcharge via XPath pour injection de classes ou modification de structure.

## Validation
- Vérifier la fluidité et le comportement responsive.
- Confirmer que l'interaction avec filter_sidebar.js reste fonctionnelle.
