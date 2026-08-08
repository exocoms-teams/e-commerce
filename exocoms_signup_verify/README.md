# exocoms_signup_verify — Validation email à l'inscription (Odoo 19)

## Le problème

Sur Odoo 19, `/web/signup` crée le compte, **connecte immédiatement** le
visiteur, puis envoie un simple mail de confirmation
(`auth_signup.mail_template_user_signup_account_created`). Aucune vérification
de l'adresse : n'importe quelle adresse inexistante passe.

## Le flux après installation

1. Le visiteur saisit **nom + email** (les champs mot de passe disparaissent).
2. L'adresse est normalisée, contrôlée syntaxiquement, comparée à la liste des
   domaines refusés, et son domaine est vérifié (MX) si `email_validator` est
   disponible.
3. Le compte portail est créé **sans mot de passe**, à l'état *Invité*
   (`state = new`) — donc inutilisable.
4. Odoo envoie le mail natif `auth_signup.portal_set_password_email` contenant
   le lien d'activation.
5. Le visiteur clique, définit son mot de passe, le compte devient *Confirmé*.

Le parcours **sur invitation** (lien avec jeton, `/web/signup?token=...`) n'est
pas modifié : les champs mot de passe restent affichés et le comportement natif
s'applique.

## Points d'implémentation

- Surcharge de `AuthSignupHome.web_auth_signup` : on ne délègue au natif que si
  un jeton est présent ou si la requête n'est pas un POST.
- Création via `res.users.signup(values)` **sans clé `password`**, puis
  `action_reset_password()` dans un contexte `create_user=1` pour obtenir le
  gabarit « bienvenue / définissez votre mot de passe » plutôt que
  « réinitialisation ».
- Si l'envoi du mail échoue (`UserError` remontée par
  `_action_reset_password`), la transaction est annulée : pas de compte
  orphelin, le visiteur peut réessayer.
- Aucune énumération de comptes : si l'adresse existe déjà, le même écran est
  affiché ; un compte jamais activé reçoit simplement un nouveau lien.

## Installation

```bash
git checkout -b feat/signup-verify
cp -r exocoms_signup_verify <repo_odoo_sh>/addons/
git add addons/exocoms_signup_verify && git commit -m "[ADD] exocoms_signup_verify 19.0.1.0.0"
git push
```

Sur Odoo.sh, ajouter au `requirements.txt` à la racine du dépôt (optionnel,
uniquement pour le contrôle MX) :

```
email_validator
```

Puis : Apps → *Mettre à jour la liste des applications* → installer
**EXOCOMS - Validation email à l'inscription**.

## Configuration

- Paramètres généraux → *Permissions* → **Compte client : Inscription libre**
  (sinon le module ne sert à rien, l'auto-inscription étant désactivée).
- Paramètres généraux → *Permissions* → **Validation de l'email à
  l'inscription** : activer/désactiver le contrôle MX, saisir les domaines
  refusés (séparés par des virgules).
- Site Web → Paramètres → *Intégrations* → **reCAPTCHA / Turnstile** :
  recommandé en complément contre les inscriptions automatisées.
- Vérifier le SPF/DKIM du domaine expéditeur, sinon les liens d'activation
  finissent en spam et plus personne ne peut créer de compte.

## Tests manuels

| Cas | Attendu |
|---|---|
| Inscription avec une adresse valide | Écran « Vérifiez votre boîte mail », mail reçu, compte à l'état *Invité* |
| Tentative de connexion avant le clic | Refus (aucun mot de passe défini) |
| Clic sur le lien | Définition du mot de passe, compte *Confirmé* |
| Adresse au domaine inexistant | Message d'erreur, aucun compte créé |
| Adresse déjà utilisée par un compte actif | Même écran de confirmation, aucun mail, aucune fuite d'information |
| Invitation par jeton (Gérer l'accès au portail) | Parcours natif inchangé |

## Limites connues

- Le lien d'activation généré en mode `signup` n'a pas de date d'expiration
  (comportement natif d'Odoo). Ajouter une expiration nécessiterait de forcer
  `signup_expiration` sur le partenaire.
- Le compte est créé avant validation : prévoir un filtre sur
  `state = new` pour purger périodiquement les inscriptions non confirmées.

---
EXOCOMS Group — v19.0.1.0.0 — LGPL-3
