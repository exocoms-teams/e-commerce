# EXOCOMS — Demande d'inscription portail

Odoo 19. **Aucun utilisateur, aucun contact n'est créé tant que l'adresse email
n'a pas été confirmée.**

## Pourquoi cette architecture

Les tentatives précédentes créaient le compte immédiatement puis l'archivaient
en attendant la confirmation. Cela obligeait à manipuler le cycle de vie de
`res.users` — archiver, débloquer, purger, empêcher la connexion — et à
réécrire la validation du formulaire d'Odoo. Chaque interaction avec le code
natif était une source de régression.

Ici, le POST de `/web/signup` avec jeton reste **intégralement natif**. Le
module n'ajoute qu'une table à lui et un aiguillage.

## Déroulé

1. Le visiteur saisit **nom + adresse email**. Rien d'autre.
2. L'adresse est contrôlée : format, domaine jetable, DNS, liste blanche
   facultative. Un refus s'affiche sur le formulaire.
3. Une ligne est écrite dans `exocoms.signup.request` et un lien à usage unique
   est envoyé. **Aucun `res.users`, aucun `res.partner` n'existe encore.**
4. Le clic sur le lien crée le contact, appelle `signup_prepare()` dessus et
   redirige vers `/web/signup?token=…`.
5. Odoo affiche **sa propre page**, le visiteur choisit son mot de passe, Odoo
   crée l'utilisateur et ouvre la session.

C'est le parcours d'invitation standard d'Odoo, déclenché après vérification de
l'adresse.

## Ce que l'architecture supprime

* Plus d'archivage / désarchivage de `res.users`.
* Plus de blocage de connexion à écrire : un compte inexistant ne se connecte
  pas.
* Plus de mot de passe conservé en attente.
* Plus d'adresse non vérifiée dans la base contacts.
* Le cron ne touche **que** `exocoms.signup.request`.

## Nettoyage de la table

Cron quotidien « EXOCOMS : purge des demandes d'inscription ». Il commence par
basculer en *expirée* toute demande dont le lien a dépassé sa validité — elles
restent visibles en back-office — puis supprime selon trois durées distinctes :

| Catégorie | Défaut | Effet de la valeur 0 |
|---|---|---|
| Demandes expirées | 7 jours | conservation indéfinie |
| Demandes confirmées | 30 jours | conservation indéfinie |
| Demandes refusées | 3 jours | conservation indéfinie |

Supprimer une demande confirmée n'a **aucun effet sur le compte créé** : seule
la trace de la demande disparaît. Chaque suppression tourne dans son propre
savepoint, une ligne qui résiste ne bloque pas le lot.

Une adresse n'est jamais « occupée » par un compte fantôme : un visiteur qui
recommence son inscription le lendemain n'est pas bloqué.

## Protection contre les dépôts automatisés

Deux garde-fous complémentaires, en plus du plafond d'emails par adresse.

**Plafond par origine** — 5 demandes par heure et par connexion, réglable, 0
pour désactiver. Le contrôle s'applique **avant** la validation de l'adresse,
pour qu'un robot ne puisse pas sonder les règles de filtrage sans limite. Le
message renvoyé est neutre et ne révèle pas le seuil.

L'adresse IP n'est **jamais stockée** : seul un HMAC-SHA256 tronqué, calculé
avec le secret de la base, est conservé dans le champ `ip_hash`. Le sel étant
propre à l'instance, l'empreinte est inexploitable ailleurs, et elle disparaît
avec la demande lors de la purge.

Derrière le proxy d'Odoo.sh, l'IP réelle n'est correcte que si le serveur
tourne en mode proxy — c'est le cas par défaut sur la plateforme.

**Piège à robots** — un champ masqué, retiré de la navigation clavier et de la
lecture d'écran, qu'un formulaire rempli automatiquement renseignera. S'il est
rempli, la demande est silencieusement ignorée et la page de confirmation
habituelle s'affiche : le robot n'apprend pas qu'il a été repéré.

Ces deux mesures n'ajoutent aucune friction pour un visiteur légitime. Si le
site subit une attaque soutenue, il faudra passer à un captcha.

## Réglages

Paramètres généraux → bloc « Inscription portail (EXOCOMS) » : les trois durées
de conservation ci-dessus, la validité du lien (24 h), le délai entre deux
envois (120 s), le plafond d'emails (5), et les trois contrôles d'adresse.

Ces réglages sont dans `ir.config_parameter` : ils sont **globaux, pas par
société**. C'est le comportement de tout champ `config_parameter=` dans Odoo.

Suivi des demandes : Paramètres → Utilisateurs et sociétés → **Demandes
d'inscription**. Liste des domaines : Paramètres → Technique → Email →
**Domaines d'inscription** (53 domaines jetables fournis).

## Prérequis

L'inscription libre doit être activée : Paramètres → Autoriser les utilisateurs
externes à s'inscrire (`auth_signup.invitation_scope = b2c`). Sinon
`/web/signup` redirige vers la page de connexion.

Le contrôle DNS utilise `dnspython` — à ajouter dans `requirements.txt` sur
Odoo.sh. Absent, le contrôle est ignoré et journalisé, jamais bloquant. Il ne
refuse que sur une réponse DNS explicitement négative : un timeout ou une panne
réseau laisse passer.

## Adresse déjà rattachée à un compte

Le formulaire répond la même page dans tous les cas, sans révéler si l'adresse
est connue. Après confirmation, le jeton natif s'applique à un contact qui
possède déjà un utilisateur : Odoo propose alors la définition d'un nouveau mot
de passe. La sécurité est équivalente à une réinitialisation classique, puisque
le lien n'est accessible qu'au titulaire de la boîte mail.

## Multi-société / multi-site

Le `login` étant unique sur toute la base, un client qui s'inscrit sur le site
de la société A puis sur celui de la société B possède **un seul compte**.
C'est une contrainte d'Odoo, pas un choix du module : la contourner impose des
bases séparées.

**Rattachement automatique.** Chaque demande enregistre sa société d'origine. À
la création du compte, les sociétés de toutes les demandes confirmées pour
cette adresse sont ajoutées à `company_ids`. Sans cela, le client ne verrait
dans son portail que les documents de la première société, et ses commandes
chez l'autre entité lui resteraient invisibles. Le rattachement n'ajoute
jamais que des sociétés — aucun retrait, et la société principale n'est pas
modifiée. Il ne s'applique qu'aux comptes portail : les droits d'un utilisateur
interne ne sont jamais touchés.

**Demandes cloisonnées.** Une demande en attente sur le site A n'empêche pas
d'en déposer une pour le site B : la recherche est portée par société.

**Politiques par société.** Une société peut déroger aux réglages généraux
depuis sa fiche (onglet « Inscription portail ») : validité du lien, plafond
par origine, adresses jetables, contrôle DNS, liste blanche. Tant que la case
« Politique d'inscription propre » reste décochée, les réglages généraux
s'appliquent intégralement.

**Domaines par société.** Une règle de domaine sans société vaut partout ; une
règle rattachée à une société ne s'applique qu'aux inscriptions déposées sur
son site.

**Contacts non rattachés.** Les contacts créés le sont avec
`company_id = False`. C'est indispensable : un contact rattaché à une société
devient invisible depuis l'autre, et le client perd la vue sur une partie de
ses documents.

**Lien de confirmation.** Construit à partir du domaine réel d'inscription
(`website.domain`, repli `url_root`), pas du `web.base.url` global. Vérifier
que le champ `domain` de chaque site est renseigné.

## Déploiement

Contient du Python : déploiement par Git sur Odoo.sh.

```bash
git add exocoms_signup_request
git commit -m "feat: demande d'inscription portail avec confirmation d'adresse"
git push origin staging
```

Désinstaller au préalable `exocoms_signup_verify`, `exocoms_signup_activation`
et `exocoms_portal_signup` : un seul module doit toucher à `/web/signup`.

## Recette

1. `/web/signup` affiche le formulaire nom + email.
2. Dépôt d'une demande → page « vérifiez votre boîte mail » + email reçu.
3. Vérifier qu'**aucun** utilisateur ni contact n'a été créé à ce stade.
4. Clic sur le lien → page Odoo de choix du mot de passe → compte créé et
   connecté.
5. `test@yopmail.com` → refus affiché sur le formulaire.
6. Domaine inexistant → refus si `dnspython` est installé.
7. Deux renvois consécutifs → le second refusé avec le délai restant.
8. Clic sur un lien déjà utilisé → page « lien invalide ».
9. Antidater un `create_date`, lancer le cron à la main → purge effective.
10. Invitation depuis le back-office → parcours natif inchangé.
11. Multi-société : inscription sur le site A, confirmation, puis inscription
    sur le site B avec la même adresse → une seule et même connexion, et
    `company_ids` contient bien les deux sociétés.
12. Cocher « Politique d'inscription propre » sur une société avec une validité
    de lien différente → le délai appliqué est bien celui de la société.

## Points de vigilance en montée de version

* `//app[@name='base_setup']` sur la vue des réglages et `//sheet` sur la
  fiche société.
* `res.users.signup()` est surchargé pour le rattachement multi-société.
* `signup_prepare()` sur `res.partner` et la route `/web/signup?token=` :
  API d'`auth_signup`, à recomparer lors d'un passage en Odoo 20.
