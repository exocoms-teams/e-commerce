# Mandat Administratif — Module Odoo 19

Module de paiement destiné aux administrations, collectivités territoriales et établissements publics français, conforme au cadre GBCP (Gestion Budgétaire et Comptable Publique).

---

## Fonctionnalités

### Paiement par mandat administratif
- Fournisseur de paiement **"Mandat Administratif"** intégré au checkout eCommerce
- Visible uniquement pour les contacts marqués **"Organisme public"**
- Transaction mise en attente (flux différé, comme un virement bancaire)

### Bon de Commande Administratif (BCA)
- Wizard complet de saisie du BCA depuis la commande de vente
- Validation SIRET avec algorithme de Luhn (exception La Poste — SIRET `356000000*`)
- Validation IBAN fournisseur
- Imputation budgétaire (section, chapitre, article, exercice)
- Gestion des pièces justificatives obligatoires
- **PDF BCA conforme GBCP** avec zones de signature (ordonnateur, comptable public)
- **Envoi automatique du BCA par email** au client après validation

### Workflow mandat
| Étape | Statut |
|---|---|
| BCA saisi | BCA en attente |
| BCA validé et envoyé | BCA émis |
| Service fait certifié | Service fait certifié |
| Prise en charge comptable | Prise en charge comptable |
| Mandat émis | Mandaté |
| Paiement reçu | Payé |
| Annulation | Annulé |

### Chorus Pro
- Champs Chorus Pro sur le contact (SIRET destinataire, code service, code tiers)
- Export **XML UBL 2.1 / Factur-X** depuis la commande de vente
- Boutons sur la facture : **"Déposée sur Chorus Pro"**, **"Annuler le dépôt"**, **"Ouvrir Chorus Pro"**
- Filtres dans la liste des factures : "À déposer sur Chorus Pro" / "Déposées sur Chorus Pro"
- Bloc réglementaire sur le **PDF de facture** (SIRET, code service, N° engagement, référence art. R. 2192-10 CCP)

### Autres
- Calcul automatique des **intérêts moratoires** (délai 30 jours, taux paramétrable)
- Gestion **TVA publique** (non assujetti, assujetti partiel, assujetti total, FCTVA)
- **Bordereau récapitulatif des mandats** signable par l'ordonnateur
- Badge **"Organisme public"** sur la fiche contact
- **Snippet Website Builder** glissable sur le site eCommerce
- Menus dédiés dans Ventes et Facturation

---

## Installation

1. Copier le dossier `mandat_admin/` dans le répertoire `addons/` de ton instance Odoo
2. Mettre à jour la liste des applications (`-u all` ou via l'interface)
3. Installer le module **"Mandat Administratif"**
4. Le fournisseur de paiement et la méthode de paiement sont créés automatiquement à l'installation

---

## Configuration

### Activer le fournisseur de paiement
1. Aller dans **Comptabilité → Configuration → Fournisseurs de paiement**
2. Ouvrir **"Mandat Administratif"** et passer en mode **"Activé"**

### Configurer un contact comme organisme public
1. Ouvrir la fiche du contact
2. Onglet **Vente et Achats** → section **"🏛 Organisme public – Mandat Administratif"**
3. Cocher **"Est un organisme public"**
4. Renseigner les champs Chorus Pro (SIRET, code service, code tiers)

### Configurer les coordonnées bancaires de la société
L'IBAN de la société (fournisseur) est pré-rempli automatiquement dans le wizard BCA depuis **Comptabilité → Configuration → Journaux → Compte bancaire**.

---

## Cadre réglementaire

| Référence | Objet |
|---|---|
| Décret n°2012-1246 du 7 novembre 2012 | GBCP |
| Décret n°2016-33 du 20 janvier 2016 | Pièces justificatives |
| Article L.1617-1 CGCT | Comptabilité publique |
| Article L.2192-10 / R.2192-10 CCP | Délai global de paiement 30 jours, intérêts moratoires |
| Ordonnance n°2014-697 / Décret n°2016-1478 | Facturation électronique obligatoire via Chorus Pro |
| Arrêté du 9 décembre 2016 | Chorus Pro |
| Nomenclatures M14 / M57 / M22 | Comptabilité des collectivités |

---

## Compatibilité

- **Odoo** : 19.0
- **Licence** : LGPL-3
- **Auteur** : Exocoms — [www.exocoms.fr](https://www.exocoms.fr)
