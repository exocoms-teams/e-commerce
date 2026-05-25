# Plan de test MVP

## 1) Accueil
- ouvrir `/cars/home`
- verifier hero, marques, vehicules mis en avant
- verifier responsive mobile

## 2) Catalogue
- ouvrir `/cars`
- tester filtres: marque, categorie, motorisation, disponibilite, prix
- tester tri et pagination

## 3) Fiche vehicule
- ouvrir une fiche depuis le catalogue
- verifier galerie, specs, options et CTA
- tester `Buy now`, `Request quote`, `Reserve vehicle`, `Request test drive`

## 4) Devis
- soumettre formulaire devis
- verifier creation `auto.quote.request`
- verifier creation opportunite CRM

## 5) Reservation / essai
- soumettre reservation et essai
- verifier references auto.booking / auto.test.drive
- verifier affichage portail `/my/bookings` et `/my/test-drives`

## 6) Comparateur
- ajouter 2+ vehicules au comparateur
- verifier tableau `/cars/compare`

## 7) Avis
- soumettre un avis en compte connecte
- verifier moderation back-office
- approuver puis verifier affichage sur fiche

## 8) Dashboard
- creer snapshot `auto.dashboard.snapshot`
- verifier KPI ventes/devis/reservations/essais/avis

## 9) Securite
- utilisateur portail: acces uniquement a ses donnees
- conseiller: gestion demandes/devis
- admin auto: droits complets
