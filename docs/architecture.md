# Architecture cible

## Modules

- auto_base : modeles metier, vues admin, securite, demo data
- auto_website : routes website, templates QWeb, assets SCSS/JS
- auto_sale : devis, liaison vente, transition de statut vehicule
- auto_booking : reservations, essais, creneaux, emails
- auto_compare : selection et comparaison de vehicules
- auto_reviews : avis client avec moderation
- auto_dashboard : KPI ventes / reservations / leads
- auto_financing : demandes de financement

## Principes de conception

- Aucun patch du core Odoo
- ORM Odoo privilegie, pas de SQL manuel
- ACL + record rules des l'introduction d'un modele
- Separation claire MVP vs post-MVP
- Pages publiques orientees conversion: Acheter / Devis / Reservation / Essai

## Parcours principaux

1. Achat direct: accueil -> catalogue -> fiche -> panier -> checkout
2. Demande de devis: fiche -> formulaire -> CRM lead + suivi
3. Reservation: fiche -> choix date/heure -> confirmation + back-office
4. Demande d'essai: fiche -> formulaire -> traitement commercial
