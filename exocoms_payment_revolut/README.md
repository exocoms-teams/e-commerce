# exocoms_payment_revolut

Fournisseur de paiement **Revolut Business** pour Odoo 20 (Merchant API `2026-08-17`).

> **Branche de pré-production.** Odoo 20.0 n'est pas encore en version finale.
> Ce portage suit l'API `payment` telle qu'elle existe aujourd'hui sur la branche `20.0` ;
> une revérification est nécessaire à la sortie officielle.

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

## Licence

Odoo Proprietary License v1.0 (`OPL-1`) — Copyright 2026 EXOCOMS Group.
Le texte intégral de la licence doit être collé dans le fichier `LICENSE`
avant toute distribution (voir https://www.odoo.com/documentation/19.0/legal/licenses.html).

## Compatibilité

Odoo 20 uniquement. Différences par rapport à la version 19.0 du module :

| Sujet | 19.0 | 20.0 |
| --- | --- | --- |
| Réception des données | `tx._process('revolut', data)` | `tx._record(data)` — enregistrement en base puis traitement asynchrone par le cron `payment.processing_cron` |
| Bascule Sandbox / Production | champ `state` (`test` / `enabled`) | champ booléen `is_live` |
| Désactivation d'un fournisseur | `state = 'disabled'` | archivage (`active`) |
| Moyen de paiement depuis un code | `payment.method._get_from_code()` | `payment.provider._get_pm_from_code()` |
| Formulaire de redirection | gabarit dédié dans le module | gabarit générique `payment.generic_redirect_form` (`http_method` + `url_params`) |

Conséquence de l'asynchronisme : après un encaissement, la transaction n'est plus mise à jour
dans la requête HTTP mais au déclenchement du cron. Vérifiez que `payment.processing_cron`
est actif sur la base.
