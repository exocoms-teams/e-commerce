# exocoms_debranding

Debranding complet d'Odoo **19** (Community / Enterprise). Le module refuse de
s'installer sur toute autre version (`pre_init_hook`).

## Ce qui est couvert

| Zone | Mécanisme |
|---|---|
| Titre de l'onglet backend | patch OWL de `WebClient` (partie `zopenerp`) |
| `<title>` des pages `web.layout` / `web.frontend_layout` | héritage QWeb dynamique |
| Tous les liens `odoo.com` des templates QWeb (login, portail, site, emails de notification, « Powered by Odoo ») | scan + héritages QWeb générés à l'installation |
| Menu utilisateur : Documentation, Support, Mon compte Odoo | retrait ou re-ciblage via le registre `user_menuitems` |
| Titres des dialogues d'erreur (« Odoo Server Error »…) | surcharge des statiques `error_dialogs` |
| Nom de l'application PWA (`manifest.webmanifest`) | paramètre système `web.web_app_name` |
| Icônes PWA + couleur de thème | override défensif du contrôleur `WebManifest` |
| Visuels Odoo (`<img>`, `<link rel="icon">` pointant sur `/web/static/img/odoo*`) | héritages QWeb dynamiques, `position="attributes"` |
| Version du serveur dans `session_info` | masquée pour les non-administrateurs (optionnel) |
| Cron « Publisher: Update Notification » | désactivé **uniquement sur base Community** ; réactivé à la désinstallation |
| Favicon | champ `res.company.favicon` exposé dans l'écran de configuration |

## Multi-société

Interrupteur **Marque par société** (`debranding.multi_company`), désactivé par
défaut.

| | Mono-société (défaut) | Multi-société |
|---|---|---|
| Marque dans les templates | écrite en dur à l'installation | expression QWeb résolue au rendu |
| Logo / favicon | `res.company`, déjà par société | idem |
| Nom, URL, doc, support, logo, couleur | globaux (`ir.config_parameter`) | champs `res.company.debranding_*`, repli sur les paramètres système |
| Dépendance au contexte de rendu | aucune | `ir.qweb._prepare_values` |

En mode multi-société les patchs émettent `t-out="debranding['name']"`,
`t-att-href="debranding['url']"`, `t-att-src="debranding['logo']"`. Le
dictionnaire `debranding` est injecté par une surcharge de
`ir.qweb._prepare_values`, traversée par tous les rendus serveur : backend,
écran de connexion, portail, site web, layouts de courriels, rapports.

Résolution de la société, dans l'ordre : `company` / `res_company` du contexte
(rapports, courriels) → `website.company_id` → `company_id` de
l'enregistrement rendu → `request.env.company` → `self.env.company`. La
surcharge est enveloppée dans un `try` : une erreur de résolution est
journalisée, jamais fatale pour le rendu.

Les templates OWL ne sont pas concernés : depuis Odoo 15 ils vivent dans les
bundles d'assets et non en base, donc hors du périmètre du scan.

**Limite assumée** : dans un contexte de rendu qui ne passerait pas par
`_prepare_values`, les expressions échoueraient. Le mode mono-société n'a aucune
dépendance de ce type — c'est le repli, réversible par un décochage suivi d'un
**Ré-appliquer le debranding**.

## Approche technique

Aucun héritage QWeb statique n'est livré. À l'installation (et à chaque
enregistrement de la configuration), le module :

1. supprime ses anciens patchs ;
2. recherche les vues `qweb` contenant `odoo.com`, remonte à leur vue racine ;
3. calcule l'arch combinée, compte les ancres, génère une vue d'extension
   `priority=99` avec autant de specs `xpath ... position="replace"` ;
4. crée chaque vue dans un `savepoint` — si le xpath ne s'applique pas, le patch
   est abandonné et journalisé en `warning`, sans faire échouer l'installation.

Conséquence : le module survit aux évolutions de structure des templates Odoo.

## Configuration

**Paramètres → Technique → Debranding** (`base.group_system`). L'écran édite la
société sélectionnée dans le sélecteur en haut à droite ; les champs laissés
vides retombent sur les valeurs par défaut de la base.

| Paramètre système | Rôle |
|---|---|
| `debranding.name` | Nom de marque de substitution |
| `debranding.url` | Cible des liens rebrandés (vide → texte simple) |
| `debranding.documentation_url` | Vide → entrée retirée du menu utilisateur |
| `debranding.support_url` | Vide → entrée retirée du menu utilisateur |
| `debranding.hide_version` | Masque la version serveur aux non-admins |
| `debranding.excluded_modules` | Modules dont les liens `odoo.com` sont fonctionnels |
| `debranding.multi_company` | Rendu de la marque par société (défaut `False`) |
| `debranding.logo_url` | Source par défaut des icônes PWA et des visuels remplacés |
| `debranding.theme_color` | Couleur de thème PWA (hex) |
| `web.web_app_name` | Nom PWA |

⚠️ Les liens `odoo.com` de `iap*`, `partner_autocomplete`, `google_*`,
`microsoft_*`, `payment` et `web_editor` sont **exclus par défaut** : les
réécrire casserait l'achat de crédits IAP et les flux OAuth.

## Logo

Trois niveaux, du plus natif au plus spécifique :

0. **Interrupteur multi-société** — en mode par société, chaque `res.company`
   porte son `debranding_logo_url` ; sinon la valeur par défaut s'applique.
1. **`res.company.logo`** — couvre nativement l'écran de connexion, la barre de
   navigation, les rapports PDF (`web.external_layout_*`) et l'en-tête des
   courriels de notification. Exposé dans l'écran de configuration du module.
2. **`res.company.favicon`** — onglet navigateur, backend et portail. Idem.
3. **Reste du branding visuel** — icônes PWA, `apple-touch-icon`, page hors
   ligne, visuels `/web/static/img/odoo-*` encore présents dans certains
   templates : réécrits vers `debranding.logo_url` (défaut `/logo.png`, qui sert
   le logo de la société courante).

Format conseillé : PNG carré 512×512 sur fond transparent pour `logo_url` si
l'installation PWA est utilisée — la route `/logo.png` redimensionne mais ne
recadre pas.

Non couvert : le logo du gestionnaire de bases (`/web/database/manager`), rendu
hors base de données.

## Exploitation

- **Après installation d'un nouveau module** (website, sale, helpdesk…), cliquer
  sur **Ré-appliquer le debranding**. Le scan ne se relance pas tout seul sur un
  `-u`.
- **Multi-website** : les patchs sont créés sur la vue racine, hors mécanisme
  COW. Relancer le scan après toute duplication de site.
- **Gestionnaire de bases** (`/web/database/manager`) : rendu hors base de
  données, non patchable depuis un module. Le neutraliser côté serveur :
  `list_db = False` dans `odoo.conf` (sur Odoo.sh : non exposé en production).
- **Licence** : voir la section dédiée ci-dessous.

## Licence et cadre juridique

Le module lui-même est publié en **LGPL-3** (champ `license` du manifeste).

- **Odoo Community** — LGPLv3 : modification et redistribution autorisées, y
  compris le retrait des mentions de marque.
- **Odoo Enterprise / Odoo.sh** — Odoo Enterprise Edition License v1.0 : le
  logiciel ne peut être utilisé, modifié ou exécuté après modification qu'avec
  un abonnement valide pour le nombre correct d'utilisateurs. La modification
  est donc permise, mais l'abonnement reste la condition de l'usage.
- **Marque** — « Odoo » est une marque déposée d'Odoo S.A. La retirer est une
  chose, s'en servir pour nommer une offre en est une autre : ne pas
  commercialiser le résultat comme étant « de l'Odoo » ni comme un produit
  propriétaire distinct sans vérification juridique.
- **Cron de notification éditeur** — sur Enterprise, il alimente le décompte
  d'utilisateurs de l'abonnement. Le module ne le désactive donc que si aucun
  module sous licence `OEEL-1` n'est installé.
- **Accord de partenariat** — si EXOCOMS est partenaire Odoo, l'accord de
  partenariat peut contenir des clauses supplémentaires sur l'usage de la
  marque. À vérifier avec le contrat signé.

## Déploiement Odoo.sh

Dépôt Git uniquement — l'import ZIP n'exécute pas les hooks Python.

```bash
cp -r exocoms_debranding /chemin/vers/repo/
cd /chemin/vers/repo
git add exocoms_debranding && git commit -m "feat: exocoms_debranding (Odoo 19)"
git push origin <branche>
```

## Désinstallation

Les vues générées portent un `ir.model.data` du module : elles sont supprimées
automatiquement. Le cron de notification éditeur est réactivé par
l'`uninstall_hook`. Les `ir.config_parameter` (`noupdate`) restent en base et
peuvent être purgés manuellement.
