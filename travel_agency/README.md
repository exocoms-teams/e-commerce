# travel_agency

## Structure du projet
 # Module Travel Agency — ODOO 19.0

## Description

Module custom ODOO de gestion d'une agence de voyage, développé dans le cadre du projet **Exocoms e-commerce**.
Il permet de gérer les voyages (vols, hôtels, packages, circuits) et les réservations clients directement depuis ODOO.

---

## Structure du module

```
travel_agency/
├── models/
│   ├── __init__.py
│   ├── product.py          → Extension du produit ODOO avec les champs voyage
│   └── reservation.py      → Gestion complète des réservations
├── views/
│   ├── travel_product_views.xml       → Formulaire produit voyage
│   └── travel_reservation_views.xml   → Formulaire et liste des réservations
├── data/
│   └── email_template.xml  → Template email de confirmation automatique
├── security/
│   └── ir.model.access.csv → Droits d'accès au modèle
├── __init__.py
└── __manifest__.py
```

---

## Fonctionnalités développées

### 1. Produit Voyage (`models/product.py`)
Extension du modèle `product.template` avec les champs suivants :
- **Type de voyage** : Aller simple, Aller-retour, Circuit, Séjour
- **Catégorie** : Vol, Hôtel, Package Vol+Hôtel, Circuit
- **Destination** : Pays et ville de départ / destination
- **Classe** : Économique, Affaires, Première classe
- **Durée** : Nombre de jours
- **Capacité** : Nombre de personnes maximum
- **Prix par personne** (en €)
- **Disponibilité** : Booléen activé/désactivé
- **Vérification de disponibilité** sur une plage de dates (`is_available_for_dates`)

### 2. Réservation Voyage (`models/reservation.py`)
Modèle `travel.reservation` avec :
- Référence automatique (séquence ODOO)
- Liaison au produit voyage
- Informations client (nom, email, téléphone, adresse, pays)
- Dates de départ et retour
- Calcul automatique du nombre de jours
- Gestion des voyageurs (adultes + enfants)
- Calcul automatique du prix total (nb voyageurs × prix par personne)
- Workflow de statuts : **Draft → En attente → Confirmée → Annulée**
- Validations : dates cohérentes, capacité maximale respectée, pas de chevauchement de réservations
- Envoi automatique d'un email de confirmation au client

### 3. Email de confirmation (`data/email_template.xml`)
Email automatique envoyé au client lors de la confirmation d'une réservation, contenant :
- Référence de la réservation
- Nom du voyage
- Dates de départ et retour
- Nombre de voyageurs
- Prix total

### 4. Vues ODOO (`views/`)
- Formulaire produit voyage intégré dans la fiche produit ODOO
- Formulaire de réservation avec boutons d'action (Envoyer, Confirmer, Annuler)
- Liste des réservations avec statut
- Menu **"Agence de Voyage"** accessible depuis ODOO

---
 

 
 

## Installation

1. Pousser le code sur la branche `travel_agency` via GitHub
2. Attendre que le build ODOO.sh soit **vert ✅**
3. Aller dans ODOO → **Apps** → chercher **"Travel Agency"** → **Installer**

---

## Technologies utilisées

- **ODOO 19.0**
- **Python** (models, logique métier)
- **XML** (vues, templates email)
- **ODOO.sh** (déploiement et CI/CD)
- **GitHub** (gestion du code source)

---

## Équipe
 

---
 