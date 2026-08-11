# exocoms_signup_activation

Activation du compte portail par email (double opt-in) — Odoo 19.

## Ce que fait le module

| Étape | Comportement natif Odoo 19 | Avec le module |
|---|---|---|
| Le visiteur remplit `/web/signup` | Compte créé + connexion immédiate | Compte créé puis **archivé**, email envoyé, redirection vers `/signup/pending` |
| Le visiteur tente de se connecter | — | Message « compte non activé » + bouton de renvoi |
| Le visiteur clique sur le lien | — | Compte réactivé, page de succès, connexion pré-remplie |
| Lien expiré | — | Page dédiée avec demande d'un nouveau lien |
| Inscription jamais activée | Compte fantôme conservé | Purge automatique par cron |

Les invitations émises depuis le back-office (lien avec `token`) conservent le
comportement natif : l'adresse est déjà connue de l'entreprise.

## Routes ajoutées

| Route | Rôle |
|---|---|
| `/signup/pending` | Page « vérifiez votre boîte mail » |
| `/signup/activate/<token>` | Consommation du lien d'activation |
| `/signup/resend` (POST) | Renvoi de l'email, avec limitation |

## Paramètres

Réglages → Paramètres généraux → bloc **Activation des comptes portail (EXOCOMS)**

| Clé `ir.config_parameter` | Défaut |
|---|---|
| `exocoms_signup_activation.token_ttl_hours` | 24 |
| `exocoms_signup_activation.purge_days` | 7 |
| `exocoms_signup_activation.resend_interval` | 120 |
| `exocoms_signup_activation.max_resend` | 5 |
| `exocoms_signup_activation.reveal_pending` | True |

## Déploiement

Le module contient du Python : déploiement par **Git / Odoo.sh** uniquement.

```bash
git add addons/exocoms_signup_activation
git commit -m "feat: activation du compte portail par email (double opt-in)"
git push origin <branche>
```

Puis, sur la branche Odoo.sh : Apps → Mettre à jour la liste → installer
**EXOCOMS - Activation du compte par email**.

## Pré-requis fonctionnels

1. Réglages → Paramètres généraux → **Création de compte client : libre**
   (`auth_signup_uninvited = b2c`), sinon le formulaire d'inscription est désactivé.
2. Un serveur de messagerie sortant valide (`ir.mail_server`) — l'email est envoyé
   en `force_send`, une panne SMTP n'annule pas l'inscription mais empêche
   l'activation tant que le visiteur ne demande pas un renvoi.
3. `web.base.url` correctement renseigné (et `web.base.url.freeze = True` en
   production) : c'est cette valeur qui construit le lien d'activation.

## Recette rapide

1. Se déconnecter, aller sur `/web/signup`, créer un compte de test.
2. Vérifier la redirection vers `/signup/pending` et **l'absence de connexion**.
3. Vérifier l'email reçu (ou Réglages → Technique → Emails).
4. Tenter `/web/login` avec ce compte → message « compte non activé ».
5. Cliquer sur le lien → page de succès → connexion possible.
6. Recliquer sur le même lien → « lien invalide » (usage unique).
7. Back-office : Utilisateurs → filtre **Activation en attente** → onglet
   *Activation du compte* → boutons de renvoi / activation manuelle.

## Compatibilité

Cumulable avec `exocoms_signup_verify` : ce dernier valide la *forme* de
l'adresse (MX, domaines jetables) au moment de la soumission, celui-ci valide la
*possession* de la boîte mail. Aucun conflit de route (`exocoms_signup_verify`
agit en amont dans la validation du formulaire).

## Points d'attention

* Le compte est bloqué via `active = False`. Un compte archivé n'apparaît pas
  dans les listes standards : utiliser le filtre *Activation en attente*.
* La purge supprime l'utilisateur puis, si possible, le partenaire associé.
  Un partenaire référencé ailleurs (devis, message…) est conservé.
* `reveal_pending` : à décocher si la non-divulgation de l'existence d'un compte
  prime sur le confort utilisateur (énumération d'adresses email).
