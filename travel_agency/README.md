# e-commerce 2026
# Travel Agency - Module Odoo

Module Odoo de gestion d'agence de voyage. Il permet d'administrer des offres de voyage, des hôtels, des vols, des trains, des locations de voiture et des réservations clients depuis le back-office, avec des pages publiques intégrées au site web Odoo.

## Fonctionnalités

- Catalogue de produits voyage basé sur `product.template`
- Gestion des voyages, hôtels, vols, trains et voitures
- Pages website publiques avec listes, filtres et pages détail
- Formulaire de réservation en ligne
- Création de réservations avec passagers
- Référence automatique des réservations via séquence Odoo
- Calcul automatique de la durée, du nombre de voyageurs et du prix total
- Workflow de réservation: brouillon, en attente, confirmé, annulé
- Prestataires de paiement avec calcul de commission
- Transactions de paiement avec suivi de statut
- Email de confirmation de réservation
- Rapport PDF de réservation
- Données de démonstration

## Prérequis

- Odoo 19.0
- Modules Odoo requis:
  - `base`
  - `product`
  - `website`
  - `website_sale`

## Installation

1. Copier le dossier `travel_agency` dans le répertoire des addons Odoo.
2. Redémarrer le serveur Odoo.
3. Activer le mode développeur si nécessaire.
4. Mettre à jour la liste des applications.
5. Rechercher `Travel Agency` dans les Apps.
6. Installer le module.

Sur Odoo.sh, pousser le code sur la branche du projet, attendre la fin du build, puis installer le module depuis le menu Apps.

## Structure du module

```text
travel_agency/
├── controllers/
│   └── main.py
├── data/
│   ├── demo.xml
│   ├── email_template.xml
│   └── sequence.xml
├── models/
│   ├── car.py
│   ├── hotel.py
│   ├── product.py
│   ├── reservation.py
│   ├── reservation_passenger.py
│   ├── train.py
│   └── vol.py
├── payment/
│   └── payment_provider.py
├── payment_module/
│   └── models/
│       └── payment_transaction.py
├── report/
│   └── reservation_report.xml
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── travel_dashboard.xml
│   ├── travel_product_views.xml
│   ├── travel_reservation_views.xml
│   ├── travel_hotel_views.xml
│   ├── travel_vol_views.xml
│   ├── travel_train_views.xml
│   ├── travel_car_views.xml
│   ├── payment_provider_views.xml
│   ├── website_travel.xml
│   ├── website_hotel.xml
│   ├── website_vol.xml
│   ├── website_train.xml
│   ├── website_car.xml
│   └── website_menu.xml
├── __init__.py
└── __manifest__.py
```

## Modèles principaux

### Produits voyage

Le module étend `product.template` avec des champs dédiés au tourisme:

- type de voyage: aller simple, aller-retour, circuit, séjour
- catégorie: vol, hôtel, package, circuit
- pays et ville de départ
- pays et ville de destination
- durée du séjour
- capacité maximale
- classe de voyage
- nombre d'étoiles
- prix par personne
- disponibilité
- descriptions détaillées: situation, hôtel, logement, animations, restauration, excursions et formalités
- coordonnées géographiques

### Réservations

Le modèle `travel.reservation` centralise les réservations clients:

- référence automatique au format `RES/0001`
- informations client
- offre de voyage liée
- dates de départ et de retour
- durée calculée automatiquement
- nombre d'adultes, d'enfants et total voyageurs
- prix total calculé automatiquement
- prestataire de paiement
- commission calculée
- passagers associés
- notes internes
- statut de réservation

Les actions disponibles permettent de passer une réservation en attente, de la confirmer, de l'annuler ou de la remettre en brouillon.

### Passagers

Le modèle `travel.reservation.passenger` stocke les voyageurs liés à une réservation:

- prénom
- nom
- date de naissance
- type: adulte ou enfant

### Hôtels, vols, trains et voitures

Le module ajoute des modèles séparés pour gérer les offres spécifiques:

- `travel.hotel`: hôtels, chambres, pension, prix par nuit, étoiles
- `travel.vol`: vols, compagnie, numéro de vol, aéroports, classe, prix
- `travel.train`: trajets ferroviaires, gares, classe, durée, prix
- `travel.car`: locations de voiture, catégorie, transmission, lieux de prise en charge et restitution

## Pages website

Le contrôleur public expose plusieurs pages:

- `/travels`: liste des offres de voyage
- `/travels/<id>`: détail d'une offre
- `/travels/book/<id>`: formulaire de réservation
- `/travels/book/submit`: soumission de réservation
- `/hotels`: liste des hôtels
- `/hotels/<id>`: détail d'un hôtel
- `/vols`: liste des vols
- `/vols/<id>`: détail d'un vol
- `/trains`: liste des trains
- `/trains/<id>`: détail d'un trajet
- `/voitures`: liste des locations de voiture
- `/voitures/<id>`: détail d'une voiture
- `/a-propos`: page à propos
- `/faq`: foire aux questions
- `/conditions-utilisation`: conditions d'utilisation

Les listes publiques incluent des filtres selon le type d'offre: destination, prix maximum, étoiles, classe ou catégorie.

## Paiement

Le module contient une couche de paiement interne:

- `travel.payment.provider`: prestataires avec taux de commission, URL API et clé API
- `travel.payment.transaction`: transactions liées aux réservations

Les transactions peuvent passer par les états suivants:

- brouillon
- en attente
- terminé
- échoué
- annulé

## Rapport PDF

Un rapport QWeb PDF est disponible sur les réservations. Il récapitule:

- les informations client
- les informations du voyage
- les voyageurs
- le prix total
- le prestataire de paiement
- la commission
- le statut

## Sécurité

Le fichier `security/ir.model.access.csv` donne les droits d'accès aux utilisateurs internes pour gérer les réservations, prestataires, transactions, hôtels, vols, trains et voitures.

Des accès publics en lecture sont également prévus pour les modèles affichés sur le site web.

## Utilisation

1. Aller dans le menu Travel ou Agence de Voyage.
2. Créer les offres: voyages, hôtels, vols, trains ou voitures.
3. Publier les informations nécessaires au site web.
4. Depuis le site, consulter les pages publiques et réserver une offre.
5. Depuis le back-office, suivre la réservation, vérifier les passagers et mettre à jour le statut.
6. Générer le rapport PDF si nécessaire.

## Technologies

- Odoo 19.0
- Python
- XML / QWeb
- Website Odoo
- Website Sale
- Odoo.sh

## Auteur

 

## Licence

LGPL-3