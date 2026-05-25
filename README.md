# Ecommerce Voitures Chinoises (Odoo)

Plateforme e-commerce automobile basee sur Odoo avec modules custom pour:
- gestion metier des vehicules,
- catalogue public,
- devis et vente,
- reservations et essais,
- comparateur,
- avis,
- dashboard,
- demandes de financement.

## Prerequis

- Docker + Docker Compose
- (Optionnel) Odoo local + PostgreSQL si execution hors Docker

## Demarrage rapide

```bash
docker compose up -d
```

Odoo sera disponible sur `http://localhost:8069`.

## Installation des modules

1. Creer une base dans Odoo.
2. Activer le mode developpeur.
3. Mettre a jour la liste des applications.
4. Installer les modules dans cet ordre:
   - `auto_base`
   - `auto_website`
   - `auto_sale`
   - `auto_booking`
   - `auto_compare`
   - `auto_reviews`
   - `auto_dashboard`
   - `auto_financing`

## Structure du projet

- `custom_addons/auto_base` : socle metier automobile
- `custom_addons/auto_website` : pages publiques et UX e-commerce
- `custom_addons/auto_sale` : devis et integration vente
- `custom_addons/auto_booking` : reservation et demande d'essai
- `custom_addons/auto_compare` : comparateur de vehicules
- `custom_addons/auto_reviews` : avis clients et moderation
- `custom_addons/auto_dashboard` : indicateurs commerciaux
- `custom_addons/auto_financing` : demandes de financement (phase 2)

## Comptes et roles

Groupes metier crees:
- Automobile Administrator
- Automobile Sales Advisor
- Automobile Content Manager

## Donnees de demo

Le module `auto_base` inclut des marques, motorisations, categories et vehicules de demonstration.

## Tests manuels recommandes

- Parcours catalogue > fiche > panier > checkout
- Demande de devis depuis fiche vehicule
- Reservation et essai depuis fiche vehicule
- Verification des droits portail vs back-office

## Documentation

Voir `docs/` pour l'architecture, la roadmap 8 semaines et les choix techniques.

- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/test_plan.md`
- `docs/git_workflow.md`
- `docs/delivery_checklist.md`
