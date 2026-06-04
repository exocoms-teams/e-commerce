# Mandat Administratif Français — Module Odoo 19

## Table des matières

1. [Présentation](#présentation)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Configuration initiale](#configuration-initiale)
5. [Utilisation](#utilisation)
6. [Workflow complet](#workflow-complet)
7. [Export Hélios](#export-hélios)
8. [Sécurité et rôles](#sécurité-et-rôles)
9. [Architecture technique](#architecture-technique)
10. [Dépannage](#dépannage)

---

## Présentation

Ce module gère les **mandats administratifs** conformément à la réglementation
française applicable aux collectivités territoriales et établissements publics.

### Conformité réglementaire

| Instruction | Périmètre |
|---|---|
| **M14** | Communes et groupements de communes |
| **M52** | Départements |
| **M57** | Régions, métropoles, autres collectivités |
| **M4** | Services publics industriels et commerciaux |
| **M22** | Établissements publics de santé |

### Fonctionnalités principales

- ✅ Création et suivi des mandats de paiement
- ✅ Numérotation automatique (`MAN/AAAA/MM/NNNNN`)
- ✅ Gestion des imputations budgétaires (Chapitre/Article/Rubrique)
- ✅ Contrôle de disponibilité des crédits
- ✅ Workflow ordonné : Brouillon → Validation → Mandaté → Payé
- ✅ Bordereaux de mandats avec totaux
- ✅ Impression PDF conforme (mandat + bordereau)
- ✅ Export CSV compatible **Hélios / Indigo** (DGFiP)
- ✅ Validation groupée avec création automatique de bordereau
- ✅ Gestion des retenues de garantie
- ✅ Suivi des marchés publics
- ✅ Pièces justificatives attachées
- ✅ Chatter et historique complet
- ✅ Contrôle d'accès par rôles (Lecteur / Gestionnaire / Ordonnateur / Admin)

---

## Prérequis

- **Odoo 19.0** (Community ou Enterprise)
- Python ≥ 3.10
- Modules Odoo requis : `base`, `account`, `mail`, `base_setup`
- Accès shell au serveur Odoo (pour l'installation manuelle)

---

## Installation

### Méthode 1 — Installation manuelle (recommandée en production)

#### Étape 1 : Copier le module

```bash
# Se placer dans le répertoire des addons personnalisés
# (adapter le chemin selon votre installation)
cd /opt/odoo/custom-addons/

# Copier le dossier du module
cp -r /chemin/vers/mandat_administratif_fr .

# Vérifier les permissions
chown -R odoo:odoo mandat_administratif_fr/
chmod -R 755 mandat_administratif_fr/
```

#### Étape 2 : Vérifier le chemin dans odoo.conf

```bash
sudo nano /etc/odoo/odoo.conf
```

Assurez-vous que `addons_path` contient votre répertoire personnalisé :

```ini
[options]
addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom-addons
# Ajouter /opt/odoo/custom-addons si absent
```

#### Étape 3 : Redémarrer Odoo avec mise à jour de la liste des modules

```bash
# Redémarrer le service
sudo systemctl restart odoo

# OU si vous utilisez un fichier de service manuel
sudo -u odoo /opt/odoo/odoo-bin --config /etc/odoo/odoo.conf &
```

#### Étape 4 : Activer le mode développeur (si nécessaire)

Dans Odoo :
1. Aller dans **Paramètres → Général**
2. En bas de page : **Activer le mode développeur**
   - ou ajouter `?debug=1` à l'URL

#### Étape 5 : Mettre à jour la liste des modules

```
Paramètres → Technique → Modules → Mettre à jour la liste des modules
```

#### Étape 6 : Installer le module

```
Paramètres → Modules → Modules installés
→ Rechercher "Mandat Administratif"
→ Cliquer "Installer"
```

---

### Méthode 2 — Installation via ligne de commande

```bash
# Arrêter Odoo
sudo systemctl stop odoo

# Installer le module directement
sudo -u odoo /opt/odoo/odoo-bin \
  --config /etc/odoo/odoo.conf \
  --database NOM_DE_VOTRE_BASE \
  --update mandat_administratif_fr \
  --stop-after-init

# Redémarrer
sudo systemctl start odoo
```

---

### Méthode 3 — Docker / Docker Compose

```yaml
# docker-compose.yml — extrait
services:
  odoo:
    image: odoo:19.0
    volumes:
      - ./custom-addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
```

```bash
# Copier le module
cp -r mandat_administratif_fr ./custom-addons/

# Mettre à jour
docker-compose run --rm odoo \
  odoo --database mydb \
  --update mandat_administratif_fr \
  --stop-after-init
```

---

## Configuration initiale

### 1. Paramétrer la collectivité

```
Paramètres → Sociétés → Votre collectivité
```
Renseignez :
- Nom officiel de la collectivité
- Adresse complète
- SIRET (utilisé sur les documents)
- Logo (apparaîtra sur les mandats imprimés)

### 2. Configurer les séquences (optionnel)

```
Paramètres → Technique → Séquences et identifiants → Séquences
```
Rechercher `Mandat Administratif` pour personnaliser le préfixe ou le padding.

Exemple de format : `MAN/2025/01/00001`

### 3. Créer les utilisateurs et leur affecter les rôles

```
Paramètres → Utilisateurs → Utilisateurs
→ Ouvrir un utilisateur
→ Onglet "Accès" → Section "Mandat Administratif"
```

| Rôle | Droits |
|---|---|
| **Lecteur** | Consultation uniquement |
| **Gestionnaire** | Création, modification, saisie |
| **Ordonnateur** | + Validation, mandatement, paiement |
| **Administrateur** | Accès complet, annulations, configuration |

### 4. Paramétrer les informations bancaires des créanciers

```
Contacts → Ouvrir un contact
→ Onglet "Informations privées" → Compte bancaire
→ Ajouter l'IBAN
```

---

## Utilisation

### Créer un mandat

1. Menu **Mandats Administratifs → Mandats → Tous les mandats**
2. Cliquer **Nouveau**
3. Renseigner :
   - **Objet** du mandat
   - **Type** (dépense ordinaire, investissement…)
   - **Instruction comptable** (M14, M52, M57…)
   - **Créancier** (bénéficiaire)
   - **Montant HT** et **Taux TVA**
   - **Imputation budgétaire** (chapitre/article)
   - **Pièce justificative** (facture, mémoire…)
4. Enregistrer

### Soumettre à validation

Bouton **"Soumettre à validation"** → Le mandat passe en état *En attente*.

### Valider (Ordonnateur)

L'ordonnateur voit les mandats en attente dans le menu dédié.
Bouton **"Valider (Ordonnancer)"** → Le numéro de mandat est attribué automatiquement.

### Créer un bordereau

Option 1 — **Automatique** via le wizard de validation groupée :
- Cocher plusieurs mandats dans la liste
- Action → "Valider les mandats sélectionnés"
- Cocher "Créer un bordereau automatiquement"

Option 2 — **Manuel** :
- Menu **Bordereaux → Nouveau bordereau**
- Les mandats validés lui seront associés

### Mandater et payer

```
Mandat validé → "Mandater" → "Marquer comme payé"
```

---

## Workflow complet

```
BROUILLON
    │
    ▼ [Soumettre à validation]
EN ATTENTE DE VALIDATION
    │
    ├─ [Rejeter] ──→ REJETÉ ──→ [Remettre en brouillon] ──┐
    │                                                       │
    ▼ [Valider - Ordonnateur]                              │
VALIDÉ (ordonnancé) ◄──────────────────────────────────────┘
    │
    ▼ [Mandater]
MANDATÉ (transmis au comptable)
    │
    ▼ [Marquer comme payé]
PAYÉ ✓
    │
    ├─ À tout moment (sauf Payé) : [Annuler] → ANNULÉ
```

---

## Export Hélios

L'export génère un fichier **CSV encodé UTF-8 BOM** (compatible Excel français)
à importer dans la plateforme **Hélios / Indigo** de la DGFiP.

```
Analyse → Export Hélios (DGFiP)
→ Choisir la période et les états
→ Cliquer "Générer l'export"
→ Télécharger le fichier CSV
```

> ⚠️ **Note** : Le format exact peut varier selon la version de votre trésorerie
> de rattachement. Vérifier avec votre comptable public assignataire la
> conformité du format avant la première utilisation en production.

---

## Sécurité et rôles

### Règles multi-société

Chaque utilisateur ne voit que les mandats de sa/ses collectivité(s) assignées.
Configurable dans **Paramètres → Utilisateurs → Sociétés autorisées**.

### Séparation ordonnateur / comptable

Conformément au principe de **séparation ordonnateur-comptable** du droit
budgétaire français, les rôles sont distincts :
- L'**ordonnateur** crée, valide et ordonnance
- Le **comptable** (DGFiP externe) prend en charge et paie

---

## Architecture technique

```
mandat_administratif_fr/
├── __manifest__.py              # Déclaration du module
├── __init__.py
├── models/
│   ├── mandat_administratif.py  # Modèle principal + workflow
│   ├── bordereau_mandat.py      # Regroupement de mandats
│   └── imputation_budgetaire.py # Lignes budgétaires
├── views/
│   ├── mandat_administratif_views.xml
│   ├── bordereau_mandat_views.xml
│   ├── imputation_budgetaire_views.xml
│   └── mandat_menu.xml
├── wizard/
│   ├── validation_mandat_wizard.py       # Validation groupée
│   ├── validation_mandat_wizard_views.xml
│   ├── export_helios_wizard.py           # Export DGFiP
│   └── export_helios_wizard_views.xml
├── report/
│   ├── mandat_report.xml    # PDF mandat de paiement
│   └── bordereau_report.xml # PDF bordereau
├── security/
│   ├── mandat_security.xml  # Groupes et règles
│   └── ir.model.access.csv  # Droits CRUD
├── data/
│   ├── mandat_sequence.xml  # Numérotation automatique
│   └── mandat_type_data.xml
└── static/
    └── src/css/mandat_style.css
```

---

## Dépannage

### Le module n'apparaît pas dans la liste

```bash
# Vérifier que le dossier est dans addons_path
grep addons_path /etc/odoo/odoo.conf

# Vérifier la syntaxe du __manifest__.py
python3 -c "import ast; ast.literal_eval(open('__manifest__.py').read())"
```

### Erreur "Access Denied" lors de la validation

→ Vérifier que l'utilisateur a le rôle **Ordonnateur** ou **Administrateur**.

### Séquence dupliquée après import

```sql
-- En psql, réinitialiser si besoin
UPDATE ir_sequence SET number_next = 1
WHERE code = 'mandat.administratif';
```

### Le PDF ne s'affiche pas correctement

→ Vérifier que **wkhtmltopdf** est installé et dans le PATH :
```bash
wkhtmltopdf --version
# Doit retourner wkhtmltopdf 0.12.x ou supérieur
```

---

## Licence

LGPL-3 — Ce module est distribué sous licence libre.
Compatible avec Odoo Community (OCA) et Odoo Enterprise.

---

*Développé pour les collectivités territoriales françaises — Odoo 19.0*
