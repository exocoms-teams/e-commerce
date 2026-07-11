# Mandat administratif (Chorus Pro) — Odoo 19 uniquement

Module de paiement pour les entités publiques françaises (administrations, collectivités territoriales, établissements publics) réglant par **mandat administratif**, avec dépôt des factures sur **Chorus Pro**.

## Installation sur Odoo.sh

1. Copier le dossier `mandat_administratif` à la racine de votre dépôt Git (ou dans votre dossier d'addons personnalisés).
2. Commit + push sur la branche cible : Odoo.sh reconstruit l'environnement.
3. Apps → Mettre à jour la liste des applications → installer **Mandat administratif (Chorus Pro)**.

## Configuration

### 1. Activer le fournisseur de paiement
Site Web / Facturation → Configuration → **Fournisseurs de paiement** → « Mandat administratif » :
- passer l'état sur **Activé** ;
- cocher **Publié** pour l'afficher au checkout eCommerce ;
- ajuster le délai global de paiement (30 jours par défaut, 50 pour les EPS).

### 2. Marquer les clients publics
Sur la fiche contact, onglet *Ventes & Achats*, bloc **Mandat administratif — Chorus Pro** :
- cocher **Entité publique (mandat administratif)** ;
- renseigner le **SIRET destinataire** (14 chiffres, clé de Luhn contrôlée), le **code service** et, si besoin, **Engagement juridique obligatoire**.

> Le mode de paiement « Mandat administratif » n'apparaît au checkout **que** pour les clients marqués « Entité publique ».

### 3. Envoi automatique via l'API PISTE/AIFE (optionnel)
Comptabilité → Configuration → Paramètres → bloc **Chorus Pro — Mandat administratif** :
1. Créer un compte et une application sur **piste.gouv.fr**, activer l'API « Factures » (CGU), récupérer Client ID / Client Secret (Sandbox puis Production).
2. Sur **Chorus Pro** (portail de qualification pour la Sandbox) : Raccordement API → déclarer le raccordement PISTE → créer le **compte technique** (TECH_1_xxxx@cpro.fr) et noter son mot de passe.
3. Renseigner les 4 identifiants dans Odoo, choisir l'environnement (**commencer en Sandbox**) et la syntaxe de flux (**Factur-X recommandé** : c'est le PDF natif d'Odoo), puis **Tester la connexion**.
4. Sur la facture comptabilisée d'une entité publique : générer le PDF (« Imprimer et envoyer ») puis bouton **Envoyer sur Chorus Pro** → le n° de flux (numeroFluxDepot) est stocké ; **Vérifier le statut Chorus** interroge le compte rendu de traitement. Le marquage manuel reste disponible si l'API n'est pas activée.

> Odoo.sh n'a pas d'IP sortante statique : aucun problème ici, PISTE authentifie par OAuth2 + compte technique, sans liste blanche d'IP.

### 4. Auto-déclaration par le client (délai 30/50/60 jours)
Le client public déclare lui-même sa structure sur son portail : **Mon compte → Mandat administratif** (`/my/mandat-administratif`), aussi accessible via le bouton du snippet. Il coche « entité publique », choisit son type de structure — État/collectivité/EPA (30 j), établissement public de santé (50 j), entreprise publique (60 j) — et renseigne SIRET, code service et exigence d'engagement juridique. Le module active alors le mode de paiement, calcule le délai global de paiement et affecte automatiquement le terme de paiement Odoo correspondant (« Mandat administratif — 30/50/60 jours », créés à l'installation) : les échéances de factures suivent sans intervention d'EXOCOMS. Tout reste modifiable côté backend sur la fiche contact (champ « Type de structure publique »).

### 5. Snippet website
Éditer une page → panneau des blocs → catégorie *Contenu* → glisser-déposer **Mandat administratif** (mot-clés : chorus, mandat, collectivité).

## Flux de travail

1. L'entité publique commande (en ligne ou par bon de commande) et choisit « Mandat administratif » → la transaction est mise **en attente**, la commande est confirmée (comme un virement bancaire).
2. Le n° d'engagement juridique et le code service sont saisis sur la commande (onglet *Autres informations*) et **propagés automatiquement à la facture**.
3. La facture PDF comporte un bloc « Règlement par mandat administratif — Chorus Pro » (SIRET, code service, engagement juridique, référence réglementaire).
4. Depuis la facture : bouton **Ouvrir Chorus Pro** (portail) puis **Déposée sur Chorus Pro** (horodatage + note au chatter). Filtres dédiés : *À déposer sur Chorus Pro* / *Déposées sur Chorus Pro*.
5. Le comptable public règle par virement ; enregistrer le paiement rapproche la facture, la transaction en attente peut être confirmée manuellement.

## Cadre réglementaire

- Ordonnance n° 2014-697 et décret n° 2016-1478 : facturation électronique obligatoire vers le secteur public via Chorus Pro.
- Code de la commande publique (art. R. 2192-10) : délai global de paiement de 30 jours (50 jours pour les établissements publics de santé).

## Notes techniques

- Fournisseur de paiement à flux différé calqué sur `payment_custom` (virement bancaire) : `redirect_form` → `POST /payment/mandat_administratif/process` → `_set_pending()`.
- API de paiement Odoo 19 exclusivement (`_process`, `_extract_reference`, `_apply_updates`). Non compatible avec les versions antérieures d'Odoo.
- Hooks `post_init_hook` / `uninstall_hook` via `odoo.addons.payment.setup_provider / reset_payment_provider`.
- Aucun nouveau modèle (uniquement des champs hérités) : pas de règles d'accès supplémentaires nécessaires.
- Envoi automatique via l'API PISTE/AIFE : OAuth2 client_credentials sur oauth.piste.gouv.fr (jeton 1 h), en-tête `cpro-account` (compte technique base64), service `POST /cpro/factures/v1/deposer/flux` (deposerFluxFacture), suivi via `POST /cpro/transverses/v1/consulterCR`. Syntaxes gérées : Factur-X `IN_DP_E2_FACTURX` (PDF Odoo natif, recommandé), `IN_DP_E1_CII_16B`, `IN_DP_E1_UBL_INVOICE`.

## Robustesse et supervision

- **Engagement juridique dans les fichiers (BT-13)** : le n° d'engagement est injecté automatiquement dans le XML CII (y compris celui embarqué dans les PDF Factur-X, généré par le même builder) et UBL — `ram:BuyerOrderReferencedDocument` / `cac:OrderReference` — pour éviter les rejets Chorus Pro des structures exigeant l'EJ. Injection défensive : en cas d'imprévu, le fichier d'origine est conservé et un avertissement est journalisé.
- **Validation humaine des auto-déclarations** : chaque déclaration portail (nouvelle ou modifiée) trace un message au chatter du contact et crée une activité « Vérifier l'auto-déclaration d'entité publique » pour le commercial du compte (à défaut l'administrateur).
- **Noms de flux uniques** : horodatage systématique du nom de fichier — un nouveau dépôt est possible après rejet (via « Annuler le dépôt Chorus Pro »).
- **Cron quotidien** « Chorus Pro : suivi des flux déposés » : rafraîchit le statut des flux non finalisés et crée une activité sur la facture en cas de rejet.
- **Tests automatisés** (`tests/`) : contrainte SIRET (Luhn + exception La Poste), délais 30/50/60 par type de structure, affectation des termes de paiement, réservation du mode de paiement aux entités publiques, horodatage des noms de flux. Lancement : `odoo --test-tags /mandat_administratif`.

Licence : LGPL-3 — © EXOCOMS Group
