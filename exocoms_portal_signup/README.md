# EXOCOMS — Inscription portail sécurisée

Module unique pour Odoo 19 regroupant la **vérification de l'adresse email** et
l'**activation du compte par lien** (double opt-in).

## Il remplace deux modules

Désinstaller `exocoms_signup_verify` **et** `exocoms_signup_activation` avant
d'installer celui-ci. Deux modules qui surchargent `/web/signup` ne peuvent pas
cohabiter de façon fiable : selon l'ordre de chargement, l'un annule l'autre.

## Parcours client

1. Le visiteur remplit le formulaire d'inscription.
2. L'adresse est vérifiée **avant** toute création : format, domaine jetable,
   enregistrement DNS, liste blanche éventuelle. Un refus s'affiche directement
   sur le formulaire.
3. Le compte est créé puis **archivé** (`active = False`). Aucune connexion
   n'est possible — c'est Odoo lui-même qui refuse l'authentification.
4. Un email contenant un lien à usage unique est envoyé. Le visiteur est
   redirigé vers `/signup/pending`.
5. Le clic sur le lien consomme le jeton, réactive le compte et propose la page
   de connexion avec l'identifiant pré-rempli.
6. Sans clic, un cron quotidien supprime l'inscription après le délai configuré,
   ainsi que le partenaire s'il n'est rattaché à aucun autre utilisateur.

Une tentative de connexion avant activation renvoie vers une page explicite
avec un bouton de renvoi, plutôt que vers l'erreur générique d'Odoo.

## Architecture

Le contrôleur se greffe sur `_signup_with_values()`, point d'extension natif
appelé par `do_signup()` **après** la validation Odoo du formulaire. Cette
validation n'est jamais réécrite, ce qui élimine toute une classe de
régressions lors des montées de version.

`web_auth_signup()` est repris pour l'orchestration seule : suppression de
l'email « compte créé » d'Odoo et de la connexion automatique, remplacés par la
redirection vers la page d'attente. Les invitations émises depuis le
back-office (jeton de signup) conservent intégralement le comportement natif.

## Réglages

Paramètres généraux → bloc « Inscription portail (EXOCOMS) ».

| Réglage | Défaut |
|---|---|
| Refuser les adresses jetables | activé |
| Vérifier le domaine (DNS) | activé |
| Limiter aux domaines autorisés | désactivé |
| Validité du lien | 24 heures |
| Purge des inscriptions non activées | 7 jours (0 = jamais) |
| Délai entre deux envois | 120 secondes |
| Nombre maximum d'emails | 5 (0 = illimité) |
| Signaler « compte non activé » | activé |

Ces réglages sont stockés dans `ir.config_parameter` : ils sont **globaux**, pas
propres à une société. C'est le comportement de tout champ `config_parameter=`
dans Odoo. Pour des valeurs distinctes par société, il faut les porter en champs
sur `res.company`.

La liste des domaines se gère dans Réglages → Technique → Email →
Domaines d'inscription. 53 domaines jetables courants sont fournis au départ.

## Dépendance optionnelle

Le contrôle DNS utilise `dnspython`. Si la bibliothèque est absente, le contrôle
est ignoré et journalisé : l'inscription n'est **jamais** bloquée pour cette
raison. Pour l'activer sur Odoo.sh, ajouter à `requirements.txt` :

```
dnspython
```

Le contrôle ne refuse que sur une réponse DNS explicitement négative. Un
timeout ou une panne réseau laisse passer l'inscription — un problème
d'infrastructure ne doit pas bloquer les ventes.

## Multi-société / multi-site

Le compte hérite de la société du site d'inscription, et l'email reprend ses
coordonnées. Le lien d'activation est construit à partir du domaine réel
d'inscription (`website.domain`, repli `url_root`), et non du `web.base.url`
global : un client inscrit sur le site de la société B reçoit bien un lien vers
le domaine de la société B.

Vérifier que le champ `domain` de chaque site web est renseigné.

## Déploiement

Le module contient du Python : déploiement par Git sur Odoo.sh, pas par import
de zip.

```bash
git add exocoms_portal_signup
git commit -m "feat: inscription portail sécurisée (vérification + activation)"
git push origin staging
```

Puis Apps → *Update Apps List* → installer `exocoms_portal_signup`.

## Recette avant mise en production

1. Inscription avec une adresse valide → réception de l'email.
2. Tentative de connexion **avant** le clic → page « compte non activé ».
3. Clic sur le lien → activation, puis connexion effective.
4. Inscription avec `test@yopmail.com` → refus sur le formulaire.
5. Inscription avec un domaine inexistant → refus si `dnspython` est installé.
6. Deux demandes de renvoi consécutives → la seconde est refusée avec le délai
   restant.
7. Clic sur un lien déjà utilisé → page « lien invalide ».
8. Déclenchement manuel du cron (Paramètres → Technique → Actions planifiées)
   après avoir antidaté un `create_date` → purge effective.
9. Invitation depuis le back-office → parcours natif inchangé.

## Points de vigilance en montée de version

* `//notebook` sur `base.view_users_form` et `//app[@name='base_setup']` sur la
  vue des réglages : xpaths dépendants de la structure des vues natives.
* `_signup_with_values()` et `do_signup()` : API interne d'`auth_signup`, à
  recomparer avec le code natif lors d'un passage en 20.
