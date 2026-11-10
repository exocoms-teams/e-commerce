# exocoms_revolut_reconciliation

Importe les transactions **Revolut Business** dans les relevés bancaires Odoo 19,
via la Business API (`https://b2b.revolut.com/api/1.0`).

Module distinct de `exocoms_payment_revolut` : celui-ci encaisse (Merchant API),
celui-là rapproche (Business API). Deux API, deux jeux d'identifiants.

## Ce que fait le module

- Authentification OAuth 2.0 par JWT d'assertion signé RS256, renouvellement automatique
  du jeton d'accès (durée de vie : 40 minutes).
- Import des transactions d'un compte Revolut en `account.bank.statement.line`,
  déduplication sur l'identifiant de mouvement (`leg_id`).
- Conservation de la charge utile Revolut dans `transaction_details` pour audit.
- Gestion des montants en devise étrangère (`bill_amount` / `bill_currency`).
- Cron de synchronisation (désactivé par défaut) et bouton de synchronisation manuelle.

Le module signe le JWT avec `cryptography`, déjà dépendance d'Odoo : aucun paquet
supplémentaire à installer sur Odoo.sh.

## Configuration

**1. Générer le certificat**

```bash
openssl genrsa -out privatekey.pem 2048
openssl req -new -x509 -key privatekey.pem -out publiccert.cer -days 1825
```

**2. Déclarer le certificat dans Revolut Business**

`Paramètres → APIs → Business API → Add API certificate`
- coller le contenu de `publiccert.cer` dans *X509 public key*
- renseigner l'URI de redirection : `https://<votre-domaine>/revolut/business/callback`
- noter le **Client ID** affiché

**3. Créer la connexion dans Odoo**

`Comptabilité → Configuration → Revolut Business → Nouveau`
- Client ID, contenu de `privatekey.pem`, URI de redirection déclarée
- laisser *Production* décoché pour tester sur le bac à sable

**4. Autoriser**

Dans Revolut Business, cliquer sur **Enable API access**. Revolut redirige vers l'URI
déclarée avec un code d'autorisation ; le contrôleur Odoo l'échange contre un jeton de
rafraîchissement (valable 90 jours). Le bouton *Tester la connexion* liste alors vos comptes.

**5. Relier un journal**

Sur le journal de banque, onglet *Revolut* : choisir la connexion, cliquer sur
*Lister les comptes Revolut* pour récupérer l'UUID du compte, le coller, cocher
*Synchroniser avec Revolut* et fixer la date de départ. Activer ensuite le cron
`Revolut Business : synchronisation des transactions`.

## Limites assumées

- **Les frais ne sont pas comptabilisés.** Quand Revolut rapporte des frais sur un
  mouvement, ils sont stockés dans le champ `revolut_fee` à titre indicatif. Aucune
  écriture n'est générée : la ventilation des commissions reste à faire via un modèle
  de rapprochement Odoo, dont les règles dépendent de votre plan comptable.
- **Pas de lettrage automatique des versements marchands.** Un versement Revolut agrège
  plusieurs commandes en un seul virement net ; il n'existe pas de correspondance 1-à-1
  avec une `payment.transaction`. Le module ne devine un partenaire que lorsque la
  référence Revolut correspond exactement à une référence de transaction Odoo, ce qui
  vaut pour les virements unitaires, pas pour les versements agrégés.
- **Le type de transaction des versements marchands n'est pas garanti** par Revolut.
  `const.MERCHANT_SETTLEMENT_TYPES` documente les types attendus mais n'est pas utilisé
  comme filtre : toutes les transactions terminées du compte sont importées.
- Aucun jeton n'est chiffré au-delà de la protection par groupe `base.group_system`
  sur les champs. Traitez la base comme un support de secrets.

## Tests

```bash
odoo-bin -d <base> -i exocoms_revolut_reconciliation --test-enable \
  --test-tags /exocoms_revolut_reconciliation
```

## Licence

Odoo Proprietary License v1.0 (`OPL-1`) — Copyright 2026 EXOCOMS Group.
Le texte intégral doit être collé dans `LICENSE` avant toute distribution.

## Compatibilité

Odoo 19 uniquement.
