# capsule_house_theme

Thème frontend Odoo pour le site **Capsule House** (société **Exocoms
Group**), déployé sur une base Odoo mutualisée multi-sites (~17 sites sur la
même instance). Cible **Odoo 19.0** (version du manifest : `19.0.1.0.0`) —
c'est la version réellement utilisée par cette instance, pas 16.0 comme
supposé au tout début du projet.

## Passer le domaine en production

Le site est créé SANS `domain` posé automatiquement (`_setup_domain()`
dans `__init__.py`) : un domaine posé avant que le DNS ne pointe vraiment
dessus casse le sélecteur de site et la preview dans le backend
(`DNS_PROBE_FINISHED_NXDOMAIN` en environnement de dev/staging). Une fois
`capsule-house.fr` réellement configuré en DNS vers cette instance,
activer :

```
ir.config_parameter: capsule_house_theme.domain_live = 1
```

Le prochain passage du hook (cron horaire, ou réinstallation) posera alors
`website.domain = 'capsule-house.fr'` automatiquement.

## Périmètre actuel

Pages livrées : **Accueil** (`/`) et **Boutique** (`/shop`, native
`website_sale`, personnalisée avec un bandeau d'en-tête).

Design reconstruit d'après une maquette de référence fournie par le client
(capture d'écran) : bandeau d'annonce, header avec nav "Tous les pods" +
catégories, hero avec recherche/pastilles/stats, section "Meilleures
ventes", footer newsletter + colonnes. Palette exacte (13 teintes,
`static/src/css/variables.css`) :

| Rôle | Couleur |
|---|---|
| Fond | `#FFFFFF` |
| Panneau / cartes | `#F6F1E9` |
| Encre / texte principal | `#1F2421` |
| Ambre (prix, étoiles) | `#F6B26B` |
| Terracotta (CTA) | `#C1694F` |
| Gris brume (texte secondaire) | `#7A7168` |
| Vert badge (promo/nouveauté) | `#2E7D5B` |
| Texte bas de footer | `#8A8177` |
| Texte secondaire footer (taupe) | `#B8AFA2` |
| Saumon (dégradé hublot) | `#E3A48A` |
| Beige/tan (dégradés logo/illustration) | `#EAD9C4` / `#EDE0D0` |
| Dégradé fond produit | `#FBF6EE` |
| Reflet hublot | `#FFF3E0` |

**Points à vérifier avec le client avant mise en ligne** (non fabriqués par
ce module, volontairement masqués/neutres par défaut) :
- La note "4.9 · X avis" en hero et les compteurs par produit ne
  s'affichent que si des vraies données existent (`ir.config_parameter`
  `capsule_house_theme.rating_value` / `.rating_count`, ou un module de
  reviews réel). La maquette affichait des chiffres fixes ("2 340 avis",
  "128", "204"...) qui n'étaient pas des données vérifiées.
- "X pods installés" : idem, via `capsule_house_theme.units_installed_count`.
- Le lien "Promotions" pointe sur `/shop?promotions=1` en attendant un vrai
  mécanisme de filtre (pricelist ou tag) côté catalogue.
- Les liens footer AIDE (Livraison/Retours/Garantie/FAQ) et ENTREPRISE (À
  propos/Le concept/Contact) pointent vers des pages pas encore livrées.
- L'inscription newsletter (`/newsletter/subscribe`) utilise `mailing.list`
  si `mass_mailing` est installé, sinon retombe sur un email de
  notification simple — pas de dépendance ajoutée au manifest pour ça.
- Le bandeau d'annonce ("Livraison & installation offertes...") est un
  texte figé de la maquette, à confirmer.

À venir, au fur et à mesure : Services, Contact, À propos (ajouter les
templates dans `views/pages/`, un CSS dédié le cas échéant dans
`static/src/css/pages.css` + son entrée dans `THEME_ASSETS`
`__init__.py`, et le menu correspondant dans `_setup_menus()`).

## Règles de sécurité multi-site (à respecter dans tout ajout futur)

1. **Jamais de recherche de site par nom.** Un site homonyme "Capsule
   House" peut déjà exister dans la base partagée. Notre site est retrouvé
   UNIQUEMENT via l'id mémorisé dans `ir.config_parameter`
   (`capsule_house_theme.website_id`, voir `_get_website()`). Si absent ou
   invalide, un site tout neuf est créé — jamais de réutilisation d'un site
   existant, même homonyme.
2. **Aucune donnée scopée site sans filtre `website_id` explicite.**
   `website.menu`, `website.page`, `ir.ui.view`, `product.template`,
   `product.public.category`... sont toujours filtrés sur notre
   `website_id`.
3. **Pas d'adoption de données orphelines génériques.** Toute requête
   filtre aussi sur `company_id` exact (`Exocoms Group`), jamais de
   fallback `company_id=False`.
4. **Suppression de démo strictement conditionnée.** `_clean_demo_data()`
   ne supprime un site fantôme homonyme que s'il n'a aucun produit et au
   maximum 1 page — sinon il logue un avertissement et laisse le site
   intact.
5. **Idempotence obligatoire.** Chaque fonction de `__init__.py` peut être
   rejouée sans dupliquer ni casser l'existant (`post_init_hook`,
   `migrations/<version>/post-migrate.py`, cron horaire
   `capsule.house.theme.maintenance`).
6. **Pas d'assets globaux.** Le CSS/JS du thème n'est JAMAIS déclaré dans
   `web.assets_frontend` du manifest (bundle partagé par les 17 sites) : il
   est enregistré dynamiquement via `ir.asset` scopé à notre
   `website_id` uniquement (`_setup_theme_assets()`).
7. **Vues globales scopées après coup.** Les vues qui héritent d'un
   template partagé (`website.layout`, `website_sale.products`) sont créées
   génériques par le XML puis explicitement repassées sur notre
   `website_id` par `_scope_layout_views()` — sans quoi elles
   s'appliqueraient à tous les sites de la base.
8. **Attributs produit en filtres, pas en variantes.** Les
   `product.attribute` créés pour la boutique (`_setup_shop_filters()`)
   sont toujours en `create_variant='no_variant'`, avec un `try/except` qui
   logue plutôt que planter si l'attribut est déjà utilisé ailleurs en mode
   variante réelle.
9. **Catégories boutique scopées quand le champ existe.**
   `_setup_shop_categories()` feature-detecte si `product.public.category`
   a un champ `website_id` sur cette version d'Odoo avant de le poser ;
   sinon logue un avertissement (taxonomie alors partagée nativement).

## Structure

```
capsule_house_theme/
├── __init__.py              # hooks (post_init_hook, run_theme_maintenance, _get_website...)
├── __manifest__.py
├── controllers/main.py      # route '/', featured_products scopés website_id
├── models/maintenance.py    # modèle du cron horaire (filet de sécurité)
├── views/
│   ├── pages/                # home.xml, shop.xml
│   ├── partials/              # hero.xml, featured_products.xml
│   └── templates/             # header.xml, footer.xml, layout.xml
├── data/                      # website_data.xml (vide, cf. commentaire), seo_data.xml, cron.xml
├── security/ir.model.access.csv
├── static/src/{css,js,img}
├── i18n/en.po
└── migrations/19.0.1.0.0/post-migrate.py
```

## À chaque bump de version

Dupliquer `migrations/<ancienne_version>/post-migrate.py` sous
`migrations/<nouvelle_version>/post-migrate.py` (même contenu : appel à
`run_theme_maintenance`). Sans ce dossier, Odoo ne rejoue jamais le hook
lors d'une mise à jour (`-u capsule_house_theme`), seulement à l'install
initiale.

## Inspiré du module de référence exocoms_theme

Deux correctifs ajoutés directement grâce à l'historique de bugs déjà
documenté dans `exocoms_theme` (l'autre thème Exocoms Group sur cette
même base mutualisée) :

- **`_invalidate_frontend_assets()`** (v19.0.1.0.1) : supprime le/les
  `ir.attachment` du bundle `web.assets_frontend` compilé pour notre site
  s'il a été mis en cache de façon incomplète/corrompue (diagnostiqué en
  conditions réelles : le CSS du thème n'était pas du tout appliqué à
  l'écran alors qu'il était bien présent, complet, dans une requête brute
  sur l'URL du bundle). Une seule fois par garde-fou `ir.config_parameter`.
- **`_attach_shop_filters_to_products()`** (v19.0.1.0.2) : rattache
  l'attribut filtre 'Surface (m²)' aux produits publiés. Sans cette étape
  (absente de la première version de ce module), Odoo n'affiche jamais un
  filtre boutique pour un attribut qui n'est pas porté par au moins un
  `product.template.attribute_line_ids` — exactement le bug qu'
  `exocoms_theme` a dû corriger pour ses propres filtres Monétique
  (`_attach_monetique_attributes_to_products`).

### Bug CSS "le style ne s'applique pas" — cause racine réelle (v19.0.1.0.5)

`_invalidate_frontend_assets()` (ci-dessus) partait d'un diagnostic
incomplet. La vraie cause, confirmée en conditions réelles en comparant
le bundle compilé de notre site à celui d'un autre site de la base
mutualisée : `variables.css` chargeait Google Fonts via `@import
url('...css2?family=Inter:wght@400;500;600;700;800;900...')` — la
syntaxe "poids variable" de l'API css2 utilise des **points-virgules à
l'intérieur même de l'URL**. Le minifieur CSS d'Odoo scanne le fichier
de façon naïve et coupe la règle `@import` au premier `;` rencontré, y
compris ceux dans l'URL, produisant un `@import` tronqué (sans guillemet
ni parenthèse fermante) qui cassait le parsing de TOUT ce qui suit dans
le bundle partagé — pas seulement nos règles `.ch-*`, mais aussi
Bootstrap et le CSS natif Odoo pour ce site entier.

Corrigé à la source : `variables.css` utilise désormais la syntaxe
historique (virgules, sans point-virgule dans l'URL), qui se compile et
se parse correctement. Le contournement `<link>` direct dans
`views/templates/layout.xml` (ajouté en 19.0.1.0.3, avant que la vraie
cause soit identifiée) reste en place par sécurité, en plus de l'`ir.asset`
normal.

**Leçon pour tout futur `@import` ajouté à ce thème** : ne jamais utiliser
la syntaxe css2 à poids variable avec point-virgule dans l'URL
(`wght@400;700`) — toujours la syntaxe historique par virgules
(`family=Police:400,700`), plus sûre vis-à-vis du minifieur d'Odoo.

### Boutique "native Odoo" comme exocoms_theme (v19.0.1.0.11)

Sur demande client ("la boutique est native à Odoo comme j'ai fait sur
exocoms"), `shop.xml` pose désormais explicitement `hasLeftColumn=True`
sur `website_sale.products` via un xpath sur le `t-set` natif — même
technique que `boutique_sidebar` dans `exocoms_theme`.

Différence assumée avec exocoms_theme : leur sidebar native est ensuite
entièrement masquée par CSS (`.o_wsale_products_categories { display:
none }`) au profit d'un méga-menu catégories statique custom
(`dashboard_menu_boutiques_sidebar`, jamais réellement appelé dans leur
code — template orphelin). Capsule House n'a pas ce méga-menu : la
sidebar native reste donc VISIBLE et stylée (nouvelle section dans
`odoo-integration.css` pour `.o_wsale_products_categories` et
`.o_wsale_products_attributes`), car c'est elle qui porte le filtre
"Surface (m²)" déjà attaché aux produits via
`_attach_shop_filters_to_products()`.

### Header natif comme sur exocoms_theme (v19.0.1.0.12)

Correctif d'architecture demandé explicitement par le client : "regarde
comment j'ai procédé pour faire mon header sur exocoms theme, je n'ai
pas du tout créé de xml pour ça".

Vérification faite dans `exocoms_theme` (recherche exhaustive de
`custom_header` dans tout le module) : leur `views/templates/header.xml`
définit bien un template `custom_header`, mais il n'est **jamais
t-call-é nulle part** — un reste abandonné, du même type que leurs
anciens SVG de logo Capsule House qu'on nous a dit de ne pas réutiliser,
ou que leur `dashboard_menu_boutiques_sidebar` (voir section boutique
ci-dessus). Leur VRAI header en production est le header **natif** Odoo
(`header#top`), simplement restylé par CSS
(`static/src/css/header.css` : sélecteurs `header#top`,
`.navbar-brand.logo`, `#top_menu`, `.o_wsale_my_cart`, `.o_wsale_my_wish`,
`.o_header_language_selector`, `li.dropdown.o_no_autohide_item`) — le
menu vient de `website.menu`, le logo du champ natif `website.logo`,
panier/wishlist/recherche/langue/compte des widgets natifs des modules
`website` / `website_sale` / `website_sale_wishlist`.

Notre module faisait l'inverse : `theme_layout` (`layout.xml`)
remplaçait entièrement `<header id="top">` par un template maison
(`theme_header`) recodant à la main logo (SVG inline), nav (boucle sur
`website.menu_id.child_id`), panier, wishlist décorative, sélecteur de
langue et dropdown compte. Corrigé :

- **`layout.xml`** : suppression du xpath `position="replace"` sur
  `header#top`. Le header natif reste intact ; seule une fine bannière
  d'annonce est encore insérée `position="before"` (élément de maquette
  sans équivalent natif Odoo — ne touche à aucun moment à la structure
  du header).
- **`header.xml`** : ne contient plus que ce bandeau d'annonce
  (`theme_announce_bar`) ; tout le reste de l'ancien `theme_header` a
  été retiré.
- **`layout.css`** : nouvelles règles ciblant les classes natives
  (`header#top`, `.navbar-brand.logo`, `#top_menu .nav-link`,
  `.o_wsale_my_cart`, `.o_wsale_my_wish`,
  `a[data-bs-target="#o_search_modal"]`, `.o_header_language_selector`,
  `li.dropdown.o_no_autohide_item`, navbar mobile), mêmes cibles que
  `exocoms_theme/header.css`, adaptées à nos variables `--ch-*`. Le lien
  "Tous les pods" (`/shop`) est mis en pastille pleine via un sélecteur
  d'attribut (`.nav-link[href="/shop"]`), jamais par ordre/position.
- **`base.css`** : suppression du `padding-top` qui compensait l'ancien
  header fixe — le header natif est en flux normal (`#wrapwrap { padding:
  0 !important; margin: 0 !important; }`, comme chez exocoms_theme).
  `--topbar-h`/`--header-h` retirées de `variables.css` (plus utilisées).
- **`__init__.py`** : `_set_logo()` pointait vers `logo.png`, jamais
  livré (no-op silencieux permanent). Pointe maintenant vers
  `static/src/img/capsule-house-logo.png`, généré à partir du badge SVG
  validé par le client + du wordmark "capsule house" (aplatis en un
  seul PNG) — le logo natif s'applique donc réellement au site
  maintenant.
- **`main.js`** : suppression de `initBurger()`/`initNavActive()`, du JS
  qui pilotait l'ancien menu mobile custom (`#chBurger`/`#chNav`) —
  le menu mobile (offcanvas) et l'état actif sont gérés nativement par
  Odoo.
- **`__manifest__.py`** : ajout de la dépendance `website_sale_wishlist`
  pour que l'icône wishlist native soit réellement fonctionnelle (note :
  `exocoms_theme` style `.o_wsale_my_wish` dans son CSS sans déclarer
  cette dépendance dans son propre manifest — potentiellement non
  fonctionnel chez eux ; on choisit d'être explicite/correct plutôt que
  de reproduire cette lacune).

#### Retour terrain (v19.0.1.0.13)

Après déploiement de la 19.0.1.0.12, capture d'écran du site en ligne :
la nav natif s'affichait bien restylée (pastille "Tous les pods", icônes
rondes), mais deux problèmes visibles :

- Numéro de téléphone factice (`+1 555-555-5556`) et bouton "Contact Us"
  encore affichés — pré-remplis par défaut par Odoo sur tout nouveau
  site, aucune donnée business réelle de Capsule House. Masqués par CSS
  (`layout.css`) via sélecteur structurel
  (`li:has(a[href^="tel:"])`, `li:has(a.btn_cta)`), même technique que
  `exocoms_theme/header.css` (les règles `data-oe-id` d'exocoms sont
  spécifiques à leur propre base et volontairement pas reprises ici).
- Logo affichant le placeholder générique Odoo "Your Logo" au lieu du
  nôtre. Cause : `_set_logo()` utilisait `if website.logo: return` en
  supposant ce champ vide par défaut sur un site neuf — en réalité Odoo
  y pose lui-même un placeholder à la création du site, donc cette
  condition bloquait TOUJOURS la pose de notre logo, dès le tout premier
  passage du hook. Remplacé par un garde-fou `ir.config_parameter`
  classique (`capsule_house_theme.logo_applied_v1`, même idiome que
  `CONFIG_ASSETS_FIX_KEY`) qui force la pose une seule fois.

### 403 sur /shop — pricelist manquante pour notre société (v19.0.1.0.14)

Une fois le header natif propre (logo + nav OK, confirmé par capture
d'écran), clic sur "Tous les pods" (`/shop`) → 403 :

```
Failed to read field res.country.group.pricelist_ids
Access to unauthorized or invalid companies.
```

Cause : `_get_company()` crée la société "Exocoms Group" via un simple
`res.company.create({'name': ...})`. Contrairement à la création d'une
société via l'assistant standard d'Odoo (Paramètres > Sociétés), un
`create()` direct ne seed AUCUNE pricelist par défaut pour cette
société. Sans pricelist scopée à notre `company_id`, `website_sale`
élargit sa recherche de pricelist applicable via les groupes de pays
partagés (`res.country.group.pricelist_ids`) — une liste qui traverse
TOUTES les pricelists de la base mutualisée, y compris celles des ~16
autres sociétés/sites que la nôtre n'est pas autorisée à lire (règle
d'accès multi-société native d'Odoo) : d'où le 403.

Fix : nouvelle fonction `_setup_pricelist(env, website, company)`
(appelée en tout début de `run_theme_maintenance`, juste après
`_get_website`) qui crée une `product.pricelist` scopée strictement à
notre `company_id` (idempotent, ne touche jamais une pricelist d'une
autre société) et la pose comme pricelist par défaut du site si le
champ existe sur cette version (feature-detect, comme ailleurs dans ce
module).

#### Cause EXACTE confirmée en conditions réelles (v19.0.1.0.15)

Le correctif 19.0.1.0.14 (pricelist) était une bonne pratique mais pas
la vraie cause du blocage. Diagnostic confirmé en inspectant directement
la session live du site (`/web/session/get_session_info`) :

```
uid=2 "Mitchell Admin", allowed_companies = {1: "YourCompany"} SEULEMENT
```

L'administrateur qui navigue sur le site Capsule House n'a jamais eu
"Exocoms Group" (la société de ce site) dans ses sociétés autorisées
(`res.users.company_ids`). Dès qu'un code a besoin de lire un modèle à
règle multi-société pendant la navigation (ici :
`website_sale.get_pricelist_available()` lisant
`res.country.group.pricelist_ids`), `env.companies` lève
`AccessError("Access to unauthorized or invalid companies.")` — le 403
observé.

Fix : nouvelle fonction `_grant_company_access(env, company)` (appelée
en tout début de `run_theme_maintenance`, juste après `_get_company`)
qui ajoute notre société aux sociétés autorisées de tout utilisateur
membre du groupe Administration/Paramètres (`base.group_system`).
Cohérent avec le fait que cette base mutualisée (~17 sites) est gérée
par une seule équipe centrale administrant tous les sites clients.
Idempotent, ne touche jamais un utilisateur non-administrateur ni les
sociétés des autres sites.

**Attention version du manifeste** : à un moment, `__manifest__.py`
`'version'` est repassé localement à `'1.0'` (format court). Un retour à
ce format fait sauter silencieusement TOUTES les migrations
(`migrations/19.0.1.0.1/` à `.15/`) au prochain upgrade, car Odoo ne les
rejoue que s'il reconnaît une progression cohérente avec le schéma
`19.0.1.0.x`. Remis à `19.0.1.0.15` — ne plus revenir à un format court
sur ce module.

### Audit systématique complet vs exocoms_theme (v19.0.1.0.16 → .17)

Jusqu'ici, les écarts avec exocoms_theme (module de référence) étaient
corrigés au coup par coup, à chaque fois que le client en pointait un
lui-même. Sur sa demande explicite, comparaison complète fichier par
fichier (contrôleurs, `__init__.py`, vues, CSS) plutôt que réactive.

- **`/boutique`** (v19.0.1.0.16) : route manquante, ajoutée dans
  `controllers/main.py` (alias de `/shop`, identique à exocoms_theme).
- **Sélecteur de langue invisible** (v19.0.1.0.17) : le header
  (`header.xml`/`layout.css`) affiche déjà un sélecteur de langue natif,
  mais seulement si le site a plus d'une langue active — et rien dans ce
  module n'en activait jamais une deuxième. Le sélecteur de langue
  demandé par le client restait donc construit mais invisible en
  pratique. Nouvelle fonction `_setup_languages(env, website)` (même
  pattern que `exocoms_theme._setup_languages`) : active fr_FR + en_US,
  fr_FR par défaut.
- **Écarts volontairement NON repris**, car hors périmètre demandé pour
  Capsule House ou propres à l'activité d'exocoms (monétique/TPE) :
  système d'avis clients (`models/avis.py`, `/avis`), live chat
  (`_setup_livechat`, dépendances `im_livechat`/`website_livechat`),
  widget "vus récemment" (`ExocomsWebsiteSale.product()`), pages
  Services/Contact/À propos (déjà actées "au fur et à mesure" par le
  client).
- **Écart connu, non corrigé pour l'instant** : le footer
  (`footer.xml`) contient des liens vers `/mentions-legales`, `/cgv`,
  `/confidentialite`, `/livraison`, `/retours`, `/garantie`, `/faq`,
  `/a-propos`, `/le-concept`, `/contact` — aucune de ces pages n'existe
  encore dans ce module (elles mèneront à un 404 tant qu'elles ne sont
  pas créées), cohérent avec le calendrier "au fur et à mesure" déjà
  acté pour Services/Contact/À propos.

### CRITIQUE — panne totale de chargement du module (v19.0.1.0.18)

La 19.0.1.0.17 a fait planter le chargement du module lors du
déploiement réel (traceback confirmé) :

```
ValueError: Invalid field res.users.groups_id in condition
('groups_id', 'in', 4)
```

Cause : `_grant_company_access()` (v19.0.1.0.15) utilisait
`Users.search([('groups_id', 'in', admin_group.id)])` — le champ
many2many `groups_id` sur `res.users` a été renommé dans Odoo 19.
Corrigé en remplaçant ce domaine par `user.has_group('base.group_system')`,
la méthode stable et publique d'Odoo pour tester l'appartenance à un
groupe, indépendante du nom interne du champ m2m — plus robuste aussi
aux futurs changements de version.

**Leçon** : ne jamais écrire de domaine de recherche sur un champ m2m
"système" (`groups_id`, et probablement d'autres équivalents) sans
d'abord vérifier son nom exact sur la version cible via
`Model._fields`, ou préférer une méthode publique stable
(`has_group()`, `_is_admin()`, etc.) quand une existe — exactement le
même principe de prudence déjà appliqué ailleurs dans ce module pour
`product.public.category.website_id` ou `website.pricelist_id`
(feature-detect avant utilisation).

### Indicateur "page active" absent sur Accueil (v19.0.1.0.19)

Constaté en conditions réelles (capture d'écran) : sur la catégorie
"Studio", le lien "Studio" du header s'affiche bien en pastille claire
(indicateur natif de page active) ; sur l'accueil, "Accueil" ne
s'allume jamais.

Cause : le menu "Accueil" pointait vers `/`, qui fait un redirect natif
Odoo vers `website.homepage_url` (= `/capsule-house/home`, posé par
`_setup_homepage()`). L'URL réellement affichée dans le navigateur une
fois sur l'accueil est donc `/capsule-house/home`, jamais `/` — et le
surlignage natif du header (`#top_menu`) compare l'URL du menu à l'URL
réelle de la page, donc ne correspondait jamais pour Accueil.

Fix : `_setup_menus()` pointe désormais le menu "Accueil" directement
vers `HOMEPAGE_ROUTE` au lieu de `/` — l'ancien menu (url `/`) est
automatiquement nettoyé par la logique `stray_menus` déjà existante.
Bénéfice secondaire : un aller-retour de redirect en moins au clic sur
"Accueil".

### Titre "All products" mal placé sur /shop (v19.0.1.0.20)

Constaté en conditions réelles, confirmé en inspectant le DOM live
(pas une supposition cette fois) : `#o_wsale_products_header` est
nativement en `d-flex flex-column gap-2` — titre "All products", puis
rangée catégories (`.o_wsale_filmstrip_container`), puis barre
recherche/tri (`.products_header.btn-toolbar`), empilés verticalement,
alignés à gauche par défaut.

Notre CSS (`odoo-integration.css`) forçait `align-items: center` et
`justify-content: space-between` sur ce même conteneur en colonne : sur
un flex en colonne, `align-items` agit sur l'axe horizontal (recentre
chaque ligne au lieu de les garder alignées à gauche) et
`justify-content` sur l'axe vertical (perturbe l'espacement entre les
lignes) — d'où le titre décalé au lieu de rester en haut à gauche comme
sur le rendu natif par défaut.

Fix : `#o_wsale_products_header` ne reçoit plus qu'un padding
cosmétique ; plus aucune règle display/flex-direction/align-items/
justify-content — les classes natives (`d-flex flex-column gap-2`)
suffisent telles quelles.

### Cartes produit "chip" sur /shop (v19.0.1.0.21)

Demande client : reprendre le style de carte produit d'exocoms_theme
("en chips" — coins arrondis, ombre douce, effet de soulèvement au
survol).

Avant d'écrire la moindre règle, vérification en direct des vraies
classes natives sur `/shop` (leçon tirée des bugs précédents — ne plus
copier une classe d'exocoms sans la confirmer) : leur propre règle
`.o_product` ne correspond à RIEN sur cette instance Odoo 19 (classe
absente du DOM réel, probablement écrite pour une version antérieure
d'Odoo). Les vraies classes confirmées par inspection :
`.o_wsale_product_grid_wrapper` (la carte elle-même), `.oe_product_image`
/ `.oe_product_image_img` (image), `.o_wsale_products_item_title`
(titre), `.o_add_wishlist` (bouton wishlist — pas
`.o_add_wishlist_dyn`/`.o_wish_add` comme précédemment supposé).

Nouvelle section dans `odoo-integration.css` stylant ces classes
vérifiées : carte blanche à coins arrondis (`--r-lg`), ombre légère au
repos, soulèvement + ombre plus marquée + léger zoom sur l'image au
survol, titre en police d'accroche, bouton wishlist en cercle discret
superposé sur l'image.

### Design "Chips" posé par le code, pas par l'éditeur (v19.0.1.0.22)

Demande client explicite : "je veux ça [le design Chips] mais je veux
que ça soit en local" — c'est-à-dire posé par le module, pas par un
clic dans Style > Products Design > Chips de l'éditeur de site (pas
versionné, pas reproductible sur une autre instance).

Diagnostic fait en conditions réelles (lecture directe des champs via
JSON-RPC, pas deviné) : ce réglage n'est PAS une vue à hériter mais des
champs natifs du modèle `website` — `shop_opt_products_design_classes`
(la chaîne de classes CSS qui pilote le design ; "Chips" correspond en
interne à `o_wsale_products_opt_design_thumbs`, le nom affiché dans
l'éditeur diffère du nom technique), `shop_ppg`/`shop_ppr`/`shop_gap`
(taille de grille), `shop_page_container`, `shop_default_sort`. Valeurs
reprises telles quelles depuis l'état actuellement appliqué sur le site
(lu en direct) : 21 produits/page, 3 colonnes, écart 16px, conteneur
"regular", tri "En vedette".

Nouvelle fonction `_setup_shop_display(env, website)`, idempotente
(write uniquement si une valeur diffère de celle voulue).

### Halo orange derrière l'illustration hero (v19.0.1.0.23)

Retour client, à partir d'une comparaison capture maquette / capture
site réel : "et cla couleur orange en background" — sur la maquette,
un halo orangé/pêche flouté déborde derrière la carte de
l'illustration du hero. Absent du rendu réel non pas à cause d'une
donnée manquante (contrairement aux badges/cartes flottantes traités
juste avant, qui dépendent de vrais produits), mais parce que cet
effet purement visuel n'avait tout simplement jamais été codé.

Correctif 100% CSS (`static/src/css/homepage.css`), aucun template ni
donnée touchés :
- `.ch-hero-visual` passé en `overflow: visible` (le halo doit pouvoir
  déborder du cadre).
- `.ch-hero-visual::before` : `radial-gradient` flouté (`filter:
  blur(60px)`, `opacity: 0.32`), couleurs reprises de la palette
  existante (`--ch-terracotta` / `--ch-salmon`), `z-index: 0`.
- `.ch-hero-illustration` (`z-index: 1`) et `.ch-hero-float-card`
  (`z-index: 2`) remontés pour rester visibles au-dessus du halo.

Retour client sur cette v.23 : "il y a pas toujours cette couleur
derrière comme sur le modèle" — le halo était trop pâle/délavé.
**Ajustement en v19.0.1.0.24** : `opacity` 0.32 → 0.55, `blur(60px)` →
`blur(40px)`, fondu du gradient resserré (salmon 40%/transparent 68%
au lieu de 45%/72%), inset resserré à `-14% -8%`. Toujours du CSS pur,
aucune donnée ni template touchés.

Retour client sur cette v.24 (halo bien visible, "l'effet est plutôt
cool" mais décentré vers un coin) : "je veux que ça soit comme sur le
modèle". Cause : inset asymétrique (-14% haut/bas, -8% gauche/droite)
+ `radial-gradient(closest-side, ...)` sans mot-clé `circle` = ellipse
calée sur la forme rectangulaire de la carte plutôt qu'un cercle
homogène. **Correctif v19.0.1.0.25** : inset uniforme `-20%` sur les 4
côtés + `radial-gradient(circle closest-side, ...)` pour un halo
rond, centré, symétrique dans toutes les directions.

Malgré ça, retour client persistant : "toujours rien" / halo quasi
invisible sur le site réel. Plutôt que de retoucher une 4e fois les
réglages à l'aveugle, **inspection live du DOM réel** (Claude in
Chrome : `getComputedStyle`, lecture du fichier CSS réellement servi,
capture d'écran) sur
`https://exocoms-e-commerce-capsule-house-35749213.dev.odoo.com/` :
- Le CSS déployé correspondait bien à la v.25 (`?v=19.0.1.0.25`
  confirmé, contenu du fichier confirmé) — ce n'était donc PAS un
  problème de cache/déploiement comme suspecté.
- `getComputedStyle` confirmait `opacity: 0.55`, `filter: blur(40px)`,
  couleurs correctes, aucun ancêtre avec `overflow: hidden` — le CSS
  s'appliquait bien.
- Mais rendu visuel (capture d'écran) : halo quasiment invisible.
- **Cause réelle trouvée par le calcul** : avec `closest-side` (cercle
  ou ellipse) et un fondu vers transparent à 68% du rayon, le rayon
  "coloré" du dégradé (avant transparence) était plus petit que le
  demi-côté de la carte elle-même. Tout le halo coloré se retrouvait
  donc caché DERRIÈRE la carte ; seul un infime liseré flouté (quelques
  px) dépassait — exactement ce qui était visible sur chaque capture,
  et pourquoi aucun réglage d'opacité/flou n'avait d'effet visible : le
  problème n'a jamais été la couleur, mais la géométrie.
- **Correctif validé EN DIRECT** (override CSS injecté dans la page
  live + capture d'écran de confirmation avant de committer quoi que
  ce soit) : `radial-gradient(ellipse closest-side, --ch-terracotta 0%,
  --ch-salmon 55%, transparent 88%)` (fondu repoussé beaucoup plus
  loin), `opacity: 0.6`, `blur(35px)`. **v19.0.1.0.26.**

⚠️ Au passage, `__manifest__.py` était repassé à `'version': '1.0'`
localement (probablement lors d'un test) — remis à `19.0.1.0.26` avant
tout déploiement. Rappel : ce format casse le mécanisme de replay des
migrations (voir avertissement en tête du fichier).

Retour client sur cette v.26 (halo enfin visible) : "mais il doit être
placé comme sur le modèle" — sur la maquette, le halo est concentré en
haut à droite (effet "source de lumière"), pas centré/symétrique.
**Correctif v19.0.1.0.27** (testé en direct sur le site réel avant
d'être écrit dans le code, capture à l'appui) : inset asymétrique
(`top: -18%`, `right: -22%`, `bottom: -6%`, `left: -6%`) + centre du
radial-gradient décalé (`at 68% 32%` au lieu de centré), fondu à
50%/85%.

Retour client sur cette v.27 (position correcte cette fois) : "tu vois
la diff avec les deux ?" — capture montrant que le halo réel restait
trop compact et trop saturé (bord visible, presque une tache nette),
alors que sur la maquette il est beaucoup plus étalé et progressif.
**Correctif v19.0.1.0.28** (testé en direct, capture à l'appui) : inset
encore agrandi (`top: -30%`, `right: -35%`, `bottom: -12%`, `left:
-10%`), fondu repoussé à 30%/90% (dégradé long, pas de bord dur),
`blur(55px)` (au lieu de 35px), `opacity: 0.42` (au lieu de 0.6, pour
une texture plus douce/pastel).

Retour client sur cette v.28, avec 2 captures comparatives : "ne
vois-tu pas la grandeur du halo du modèle par rapport au mien, je veux
que ce soit exactement pareil" — le halo du modèle occupe une zone
nettement plus grande. **Correctif v19.0.1.0.29** : inset quasi doublé
(`top: -55%`, `right: -65%`, `bottom: -20%`, `left: -15%`), fondu à
28%/88%, `blur(60px)`, `opacity: 0.45`.

⚠️ **Cette itération n'a PAS pu être vérifiée en direct** avant d'être
committée : Odoo.sh renvoyait une erreur de plateforme ("Odoo.sh |
Platform Error") sur toutes les tentatives d'accès au site au moment
du fix. Valeurs estimées par comparaison visuelle des 2 captures
client, à confirmer une fois le site de nouveau accessible.

## Point de vérification connu

Le xpath de `views/pages/shop.xml`
(`//div[hasclass('o_wsale_products_page')]`) a été écrit d'après la
structure `website_sale.products` telle que connue à la rédaction de ce
module ; il n'a pas été vérifié contre le DOM réel généré par cette
instance Odoo 19. À contrôler à la première installation (inspecter la
page `/shop` rendue) et ajuster le xpath si la classe a changé entre
versions.

## Compatibilité de version

Ce module cible **Odoo 19.0**. Deux points à surveiller si l'instance
change de version majeure un jour :
- `__manifest__.py` → `version` doit toujours commencer par le numéro de
  série exact du serveur (`19.0.x.y.z`) : Odoo désactive
  silencieusement (`installable=False`, sans erreur bloquante) tout module
  dont le préfixe de version ne correspond pas à la série en cours — c'est
  ce qui s'est produit une première fois ici avec un manifest resté à
  `16.0.x`.
- `post_init_hook` utilise la signature `(env)` (Odoo 17+). Sur une
  instance antérieure à 17, il faudrait repasser à `(cr, registry)` et
  reconstruire l'environnement soi-même via `api.Environment(cr,
  SUPERUSER_ID, {})`.
