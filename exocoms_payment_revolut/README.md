# exocoms_payment_revolut

Fournisseur de paiement **Revolut Business** pour Odoo 19 (Merchant API `2026-08-17`).

## Fonctionnalités

- Encaissement en ligne par redirection vers la page de paiement hébergée Revolut
  (carte, Revolut Pay, Apple Pay / Google Pay, SEPA Direct Debit selon la configuration
  de votre compte marchand).
- Capture manuelle (totale et partielle) et annulation d'autorisation.
- Remboursements totaux et partiels depuis Odoo, avec clé d'idempotence.
- Webhooks signés (HMAC-SHA256, tolérance de rejeu de 5 minutes, rotation de secret gérée).
- Bascule automatique Sandbox / Production selon l'état du fournisseur (`Test` / `Activé`).

## Installation

```bash
git add addons/exocoms_payment_revolut
git commit -m "feat: fournisseur de paiement Revolut Business"
git push odoo <branche>
```

Puis `Applications` → mettre à jour la liste → installer **Paiement : Revolut Business**.

## Configuration

1. Dans Revolut Business : `Merchant` → `API` → générer les clés.
   Récupérer la clé secrète (`sk_...`) — Sandbox ou Production selon le cas.
2. Dans Odoo : `Comptabilité` → `Configuration` → `Fournisseurs de paiement` → **Revolut Business**.
3. Renseigner la clé secrète, choisir l'état (`Test` pour le Sandbox, `Activé` pour la production).
4. Cliquer sur **Créer le webhook Revolut**. Le secret de signature (`wsk_...`) est
   enregistré automatiquement. L'URL doit être joignable en HTTPS depuis Internet
   (`https://<domaine>/payment/revolut/webhook`).
5. Optionnel : cocher `Capture manuelle` pour autoriser puis capturer plus tard.
6. Publier le fournisseur.

## Endpoints exposés

| Route | Usage |
| --- | --- |
| `/payment/revolut/return` | Retour client après paiement (relit la commande via l'API). |
| `/payment/revolut/webhook` | Notifications signées Revolut. |

## Notes d'exploitation

- La commande Revolut est la source de vérité : le retour client et le webhook
  relisent systématiquement `GET /api/orders/{id}` avant de mettre à jour la transaction.
- Une commande capturée ou remboursée passe par l'état `processing` avant règlement.
  Les transactions filles de capture / remboursement sont marquées « terminé » dès cet état,
  l'opération étant déjà irréversible côté Revolut.
- Sans capture manuelle, une autorisation non capturée expire au bout de 7 jours.
- Revolut n'accepte pas les URL de webhook en HTTP : le bouton refuse de créer
  le webhook si `web.base.url` n'est pas en HTTPS.

## Tests

```bash
odoo-bin -d <base> -i exocoms_payment_revolut --test-enable --test-tags /exocoms_payment_revolut
```

Couvre la vérification de signature webhook (signature valide, corps altéré, rejeu,
mauvais secret, rotation de secret), la construction du payload de commande,
la conversion des montants, le mapping des états de commande et le traitement
particulier des transactions filles de capture.

## Licence

Odoo Proprietary License v1.0 (`OPL-1`) — Copyright 2026 EXOCOMS Group.
Le texte intégral de la licence doit être collé dans le fichier `LICENSE`
avant toute distribution (voir https://www.odoo.com/documentation/19.0/legal/licenses.html).

## Compatibilité

Odoo 19 uniquement. Utilise les points d'extension `_process` / `_search_by_reference` /
`_apply_updates` / `_extract_amount_data` et l'assistant `_send_api_request` du module `payment`.
