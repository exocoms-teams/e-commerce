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
- **Écart connu, CORRIGÉ EN v19.0.1.0.64** : le footer (`footer.xml`)
  contenait des liens vers `/mentions-legales`, `/cgv`,
  `/confidentialite`, `/livraison`, `/retours`, `/garantie`, `/faq`,
  `/a-propos`, `/le-concept`, `/contact` sans que ces pages n'existent
  encore. `/livraison`, `/retours`, `/garantie`, `/faq`, `/a-propos`,
  `/le-concept` ont été livrées au fil des versions suivantes (voir
  sections dédiées plus bas) ; `/contact` reste volontairement la page
  NATIVE Odoo `/contactus`. Les 3 pages légales restantes
  (`/mentions-legales`, `/cgv`, `/confidentialite`) sont restées
  cassées jusqu'à ce que l'outil SEO natif d'Odoo les signale
  explicitement — voir section "Pages légales" plus bas.

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

Retour client sur cette v.29 : "comment l'autre occupe l'écran par
rapport au mien" — en recadrant la capture live exactement comme la
maquette (colonne visuelle seule), le halo du modèle lave quasiment
tout le fond de la carte (fondu ambiant très large, visible même dans
le coin opposé), alors que le nôtre retombait au blanc pur dès le
milieu du cadre. **Correctif v19.0.1.0.30** (testé en direct, capture
recadrée à l'identique du modèle pour comparaison directe) : inset
encore agrandi sur les 4 côtés (`top: -70%`, `right: -80%`, `left:
-60%`, `bottom: -60%`), fondu à 22%/78%, `blur(70px)`, `opacity: 0.4`.

Retour client sur cette v.30 (couverture correcte) : "il faut que ce
soit aussi visible que sur le modèle" — trop pâle. **Correctif
v19.0.1.0.31** (testé en direct, capture recadrée comme la maquette) :
`opacity` 0.4 → 0.65, `blur(70px)` → `blur(55px)`, fondu resserré à
30%/82% (au lieu de 22%/78%). Inset inchangé (la largeur de couverture
était déjà bonne).

Retour client sur cette v.31 : "non pas concentré comme ça, laisse
tomber" puis deux captures annotées à la main (traits tracés sur la
maquette ET sur notre rendu) pour clarifier : le halo du modèle a un
bord repérable, une limite qu'on peut suivre même en restant douce,
alors que le nôtre (trop flouté sur une zone trop large) n'avait plus
de forme du tout — juste un dégradé infini sans limite perceptible.
**Correctif v19.0.1.0.32** (testé en direct, capture recadrée comme la
maquette) : inset resserré (`top: -45%`, `right: -55%`, `left: -25%`,
`bottom: -30%`), fondu resserré à 42%/72%, `blur(38px)` (au lieu de
55px), `opacity: 0.6`. Objectif : contour net et traçable, sans
retomber sur un halo invisible comme les toutes premières versions.

Retour client sur cette v.32 : le contour était net mais le halo était
redevenu trop petit (visible seulement en haut) ET trop foncé — la
v.32 avait resserré la taille en même temps que le contour, ce qui
n'était pas demandé ; rappel que les traits tracés à la main montrent
une zone couvrant plus de la moitié du cadre. **Correctif
v19.0.1.0.33** (testé en direct) : inset rétabli large, proche de la
v.30 (`top: -65%`, `right: -75%`, `left: -50%`, `bottom: -50%`), fondu
gardé resserré (35%/70%) pour le contour, `opacity: 0.4` (couleur plus
claire), `blur(48px)`. Objectif : les 3 exigences réunies en même
temps (grande couverture + contour net + couleur claire), au lieu de
les corriger une par une en régressant sur les autres.

Retour client sur cette v.33 : capture annotée à la main avec un trait
rouge (étendue voulue) comparé à un trait gris (étendue actuelle) —
le rouge démarre bien plus à gauche en haut du cadre, alors que tout
le quart supérieur-gauche restait blanc en v.33. **Correctif
v19.0.1.0.34** (testé en direct, capture plein écran avec le texte du
hero visible) : `left: -90%` (au lieu de -50%), `bottom: -55%` (au
lieu de -50%), centre du dégradé recentré à `58% 32%` (au lieu de `64%
30%`) pour laisser le halo déborder visiblement au-dessus/à gauche du
bloc de texte, tout en gardant l'intensité concentrée en haut à droite.

## Système d'avis clients réels (v19.0.1.0.35)

Constat de départ : le badge de note du hero ("★ 4.9 · 2 340 avis" sur
la maquette) ne s'affichait jamais sur le vrai site, car ce chiffre
n'était qu'un paramètre système (`ir.config_parameter`) jamais
renseigné — volontairement, pour ne rien fabriquer. Demande client :
"va dans exocoms et crée donc cette page d'avis sur capsule house" —
reproduire le vrai système d'avis observé sur `exocoms_theme`
(`models/avis.py`, `controllers/main.py`, `views/pages/avis.xml`,
etc.) plutôt que de se contenter d'un chiffre à saisir à la main.

Adapté à Capsule House (pods, pas terminaux de paiement) et à nos
conventions multi-site :

- **`models/avis.py`** : nouveau modèle `capsule.house.avis` (nom,
  note 1-5, commentaire, modèle acheté, date, statut
  `pending`/`published`, `website_id` requis — scopé, obligatoire sur
  cette base à ~17 sites). Contrainte `@api.constrains` sur la note
  (1 à 5).
- **`security/ir.model.access.csv`** : droits `base.group_user`
  (modération backend, cohérent avec l'équipe centrale qui gère les
  17 sites).
- **`views/avis_backend.xml`** : liste (avec avis publiés grisés) +
  formulaire + action + menu "Avis clients (Capsule House)" pour
  modérer. Aucun avis n'est jamais publié automatiquement.
- **`views/partials/avis_hero.xml`** + **`avis_content.xml`** +
  **`views/pages/avis.xml`** : page publique `/avis` — note moyenne et
  répartition par étoile calculées dynamiquement (jamais fabriquées :
  "Aucun avis pour le moment" si `stats` est vide), filtres par note,
  grille des avis **publiés uniquement**, formulaire de dépôt avec
  sélecteur d'étoiles cliquable. Pas de photo de fond (contrairement à
  exocoms_theme qui utilise `heroavis.jpg`) : on n'a pas de vraie photo
  pour ce site, donc reprise du dégradé doux du thème plutôt que d'en
  fabriquer une ou de réutiliser celle d'exocoms.
- **`controllers/main.py`** :
  - `/avis` (GET) : liste + stats + formulaire.
  - `/avis/submit` (POST, CSRF) : crée un avis en statut `pending` —
    jamais publié directement, un admin doit le valider. Routes
    neuves (aucune collision possible avec un autre site de la base
    mutualisée) : pas besoin de garde `_is_our_website`, même logique
    que `/boutique` et `/newsletter/subscribe`.
  - `homepage()` : le badge de note du hero utilise maintenant
    `_get_avis_stats()` — note moyenne et nombre d'avis calculés sur
    les avis **publiés** de notre site s'il y en a ; ne retombe sur
    l'ancien réglage manuel (`ir.config_parameter`) que si aucun avis
    n'est encore publié (utile si le client a une note vérifiée
    ailleurs — Google, Trustpilot — mais pas encore de vrais avis sur
    le site lui-même).
- **`_setup_menus`** : nouvelle entrée "Avis clients" (`/avis`) dans
  la nav.
- **`static/src/css/pages.css`** : jusque-là réservé/vide pour les
  futures pages internes, mis en service ici (classes `.ch-avis-*`
  avec notre palette `--ch-*`), enregistré dans `THEME_ASSETS`.

**Volontairement omis** par rapport à `exocoms_theme` : la traduction
automatique des commentaires via l'API publique (non officielle) de
Google Translate (`models/avis.py` côté exocoms) — hors scope de cette
demande, notre site n'étant pas bilingue pour l'instant ; pourrait être
ajouté plus tard si besoin.

**Leçon technique** : un commentaire XML (`<!-- -->`) ne peut jamais
contenir un double tiret `--`, y compris dans des noms de variables
CSS comme `--ch-bg-soft` — ça casse le parsing XML de toute la vue.
Erreur commise puis corrigée dans `avis_hero.xml` pendant ce
développement (repérée par une validation XML systématique de tous
les fichiers avant livraison, pas seulement au moment du déploiement).

## Traduction des pages + Live Chat, comme sur exocoms_theme (v19.0.1.0.36)

Demande client : "gère la traduction de mes pages comme j'ai fait sur
exocoms ainsi que live chat" — recherche systématique du mécanisme
réel dans exocoms_theme avant d'écrire quoi que ce soit (même méthode
que pour le système d'avis en v.35), pas de reproduction à l'aveugle.

### Traduction (FR/EN)

`_setup_languages()` (en place depuis une version antérieure) activait
déjà `fr_FR`/`en_US` et posait le sélecteur de langue natif dans le
header — mais aucune page ne changeait réellement de texte selon la
langue choisie. Confirmé sur exocoms_theme : **pas de traduction .po
native pour le corps des pages**, mais une convention systématique de
texte statique dupliqué dans des blocs `t-if/t-else` sur
`request.env.lang` (leur propre commentaire : *"Texte statique dupliqué
t-if/t-else fr_FR, comme partout ailleurs dans ce thème"*). Un seul
champ modèle traduisible (`translate=True`) chez eux, et une traduction
automatique optionnelle des avis via l'API publique Google Translate —
**volontairement non reprise ici** (hors scope, site pas bilingue au
niveau du contenu généré par les utilisateurs pour l'instant).

Appliqué avec la même convention :
- `views/partials/hero.xml` : bloc `.ch-hero-content` dupliqué FR/EN,
  badges "Nouveau"/"Promo" et bouton panier des cartes flottantes.
- `views/templates/footer.xml` : newsletter, colonnes, bandeau bas.
- `views/partials/avis_hero.xml` : scindé en `avis_hero_fr` /
  `avis_hero_en` + aiguilleur, mêmes noms que exocoms_theme.
- `views/partials/avis_content.xml` : libellés dupliqués FR/EN,
  boucles dynamiques (stats/avis_list) partagées entre les langues
  pour ne pas dupliquer la logique elle-même.
- Header (nav) volontairement français uniquement, comme sur
  exocoms_theme (jamais bilingue chez eux non plus).

### Live Chat

Natif Odoo (`im_livechat` + `website_livechat`), pas de widget tiers —
confirmé en lisant le manifest d'exocoms_theme. Ajouté aux dépendances
du module. Fonctions `_get_default_operator(env)` /
`_setup_livechat(env, website)` dans `__init__.py`, réplique du
mécanisme `exocoms_theme._setup_livechat()` :
- Canal `im_livechat.channel` dédié, rattaché via `website.channel_id`
  (déjà nativement scopé par site).
- **Différence délibérée** : canal nommé "Capsule House - Live Chat",
  pas d'après `COMPANY_NAME` ('Exocoms Group', partagé par les ~17
  sites de la base) — sinon risque de retrouver/réutiliser le canal
  d'un AUTRE site déjà installé avec ce nom de société, dont
  exocoms_theme lui-même.
- Couleurs du widget sur notre palette (`--ch-terracotta` /
  `--ch-ink`), pas celles d'exocoms.
- Règle d'affichage (`im_livechat.channel.rule`, `regex_url='/'`)
  créée si absente (un canal créé par code n'en a aucune par défaut,
  contrairement à un canal créé depuis l'interface).
- Opérateur réel assigné automatiquement si le canal n'en a aucun, à
  chaque exécution — jamais OdooBot/uid=1 (bug identique corrigé chez
  exocoms : `env.uid` pointe vers OdooBot quand le code tourne via un
  hook/cron plutôt qu'une vraie session).

Appelé dans `run_theme_maintenance()` juste après
`_scope_layout_views()`, même position relative que chez exocoms.

## Traduction — oublis corrigés (v19.0.1.0.37)

Retour client sur la v.36, captures FR vs EN à l'appui : "le header en
anglais n'est pas traduit, la partie meilleures ventes non plus, et le
live chat ne s'affiche pas — je t'ai demandé de tout gérer". Trouvé et
corrigé :

- **Menu du haut** : `website.menu.name` est traduisible nativement
  dans Odoo, mais `_setup_menus()` n'avait jamais posé de valeur pour
  `en_US` — corrigé via `record.with_context(lang='en_US').write(...)`
  pour Accueil/Tous les pods/Promotions/Avis clients/Accessoires.
  Studio/Duo/Panorama restent inchangés (noms de gamme, pas du texte
  d'UI).
- **`views/partials/featured_products.xml`** ("Meilleures ventes") :
  entièrement oubliée en v.36, traduite ici.
- **`views/templates/header.xml`** (bandeau d'annonce) et
  **`views/pages/shop.xml`** (titre au-dessus de la grille boutique) :
  également oubliés, traduits.
- **Live Chat invisible** : diagnostic en cours au moment de ce commit
  — nécessite une inspection live du site réel (URL à jour du client),
  pas encore fait. Ancienne URL de test vérifiée entre-temps : encore
  sur v.34, donc pas représentative de l'environnement actuellement
  observé par le client.

## Live Chat invisible + menu FR en anglais — root cause trouvé et corrigé (v19.0.1.0.38)

Client : "tu ne vois pas qu'il y a trois autres sites, le live chat
s'applique sur le premier website" — hypothèse initiale (résolution de
domaine ambiguë sur l'URL de preview). Inspection live sur une page
confirmée Capsule House (`document.title` == "Capsule House — Maisons
modulaires") a montré que ce n'était PAS un problème de domaine :

- **Live Chat** : `.o-livechat-root` bien présent dans le DOM, visible,
  z-index correct (donc `website.channel_id` / règle d'affichage /
  opérateur posés par `_setup_livechat()` sont corrects côté backend),
  mais **vide** (0 enfant). La console montrait :
  `ReferenceError: initBurger is not defined` levée par
  `@capsule_house_theme/js/main`, qui casse le chargement du bundle JS
  de la page. En cascade, plusieurs templates Owl natifs échouaient à
  s'enregistrer (`web.PagerIndicator`, `web.OverlayContainer`,
  `web.BlockUI`, `html_editor.UploadProgressToast`, et surtout
  **`mail.ChatHub`** — le composant qui affiche la fenêtre du chat).
  Cause exacte : `static/src/js/main.js` appelait encore `initBurger()`
  et `initNavActive()` dans `init()`, deux fonctions supprimées lors du
  passage au header natif Odoo (le commentaire en tête de fichier avait
  été mis à jour à l'époque, mais pas le nettoyage de `init()`). Fix :
  suppression des deux appels orphelins — le Live Chat se monte
  maintenant normalement, sur toutes les pages.
- **Menu FR affiché en anglais** : sur la même capture (page confirmée
  en français), le menu du haut affichait "Home, All pods, Accessories,
  Deals, Reviews" au lieu des libellés français. Cause dans
  `_setup_menus()` : l'écriture du libellé français ne posait aucun
  contexte de langue, donc héritait de la langue ambiante de
  l'environnement du hook/cron (superuser, `en_US` par défaut) — le
  texte français atterrissait dans la case de traduction `en_US`, que
  l'écriture EN explicite juste après écrasait avec "Home" etc. La case
  `fr_FR` n'était en réalité jamais remplie ; un visiteur FR se
  rabattait donc sur la valeur `en_US`. Fix : `fr_FR` est maintenant
  posé explicitement (`with_context(lang='fr_FR')`) à la création ET à
  la mise à jour, avant l'écriture `en_US`.

Conclusion sur l'hypothèse "3 sites / résolution de domaine" : cette
piste n'est pas exclue en général sur une instance mutualisée sans
domaine propre par site (voir "Passer le domaine en production"
ci-dessus), mais elle n'était PAS la cause du problème observé ici —
les deux bugs ci-dessus suffisaient à eux seuls à expliquer les deux
symptômes rapportés, et ont été confirmés par inspection DOM/console
live sur une page dont le contexte Capsule House était certain.

## Décalage horizontal de la page — root cause trouvé et corrigé (v19.0.1.0.39)

Client : capture du backend (vue "Edit") montrant la page décalée
horizontalement — menu coupé à gauche, titre du hero tronqué, scrollbar
horizontale visible. "Regarde qu'est-ce qui cause ce décalage."

Diagnostic en direct (mesuré, pas deviné) :
- `document.documentElement.scrollWidth` = 1786 vs `clientWidth` = 1521
  → 265px de débordement horizontal réel sur toute la page.
- Masquer temporairement `.ch-hero-visual` fait tomber ce débordement à
  0 (diff exact : 265px) → confirme que c'est le halo décoratif
  (`.ch-hero-visual::before`, ajusté sur ~12 itérations en v.22-.34
  pour matcher la maquette) le responsable, pas le menu ni un autre
  composant.

Cause exacte : le halo a des insets très généreux (`left: -90%`,
`right: -75%`) et `.ch-hero-visual` a `overflow: visible` posé exprès
pour le laisser déborder de sa carte — mais rien plus haut dans
l'arbre (`.ch-hero-grid`, `.ch-hero`, `body`) ne contenait ce
débordement au niveau de la SECTION. Le halo débordait donc de la page
entière, ajoutant 265px de largeur scrollable au document.

Fix : `overflow: hidden` ajouté sur `.ch-hero` (la section pleine
largeur, pas la carte). Le halo continue de déborder librement à
l'intérieur de la section (rendu visuel inchangé, vérifié par capture
avant/après), sans plus jamais dépasser les bords réels de la page.

## Pastille "Tous les pods"/"All pods" absente en anglais (v19.0.1.0.40)

Client, sur deux captures EN vs FR de la home : "je parle au niveau de
all pods" — la pastille noire pleine (reprise de la maquette) était
présente sur "Tous les pods" en français mais absente sur "All pods"
en anglais.

Cause (confirmée en inspectant `#top_menu li` en direct sur les deux
URLs) : le style vient de `layout.css`, ciblé par
`.nav-link[href="/shop"]` — correspondance EXACTE. Odoo préfixe
automatiquement les liens internes avec le code langue hors langue par
défaut : le lien devient `/en/shop` en anglais, qui ne matche plus
`"/shop"`. Fix : sélecteur de suffixe `[href$="/shop"]`, qui matche
quel que soit le préfixe de langue, sans faux positif possible (aucune
autre URL du menu ne se termine par `/shop`). Vérifié en direct par
injection CSS avant d'être reporté dans le fichier.

## Design boutique "Chips" — classes corrigées d'après exocoms_theme (v19.0.1.0.41)

Client (capture du panneau "Products Design: Chips" dans l'éditeur de
site) : "je t'ai dit que je voulais ce style comme design sur mes
produits du shop, essaye de voir comment ça a été fait sur
exocoms_theme pour bien le faire sur Capsule House."

Le mécanisme (poser le design "en code" via le champ natif
`website.shop_opt_products_design_classes`, demande explicite du
client plutôt qu'un clic dans l'éditeur) était déjà en place
(`_setup_shop_display()`), mais la liste de classes CSS
(`SHOP_DESIGN_CLASSES`) avait été **devinée** lors d'une session
précédente, jamais vérifiée contre une implémentation réelle. Corrigée
en comparant au code réel d'exocoms_theme (écrit deux fois chez eux —
post_init_hook et le hook de maintenance principal — donc confirmé
fonctionnel en production) :

- `o_wsale_products_opt_design_thumbs` → `_design_chips` (la vraie
  classe "Chips" — celle qu'on devinait n'existe même pas sous ce nom
  dans leur config) ;
- `_rounded_2` → `_rounded_4` ;
- `_actions_onhover` → `_actions_inline` + `_actions_promote` ;
- `_wishlist_fixed` → `_wishlist_inline` ;
- `_has_description` et `_actions_subtle` retirées (absentes chez
  exocoms) ;
- `_has_comparison`, `_cc` et `_thumb_6_5` ajoutées (présentes chez
  exocoms, manquantes chez nous).

Ajout de `_setup_shop_grid_design()`, filet de sécurité repris tel
quel (même prudence de scoping) de la fonction du même nom chez
exocoms : si une vue `website_sale.products` spécifique à NOTRE site
existe déjà, on s'assure que sa classe grid porte bien
`o_wsale_products_opt_design_chips` — jamais de vue créée, jamais la
vue générique partagée par les 17 sites touchée.

## Menu compte en anglais + couleurs pages de connexion, d'après exocoms_theme (v19.0.1.0.42)

Client, capture du menu déroulant du compte natif : "tu vois ça ne suit
pas la langue [My Account / Logout en anglais malgré le site en
français], va regarder sur exocoms_theme, j'ai aussi géré l'affichage
du header lorsqu'on se déconnecte, mais les couleurs des pages de
connexion et déconnexion sur exocoms_theme, sur le init, regarde bien,
gère bien."

Recherche menée dans le code réel d'exocoms_theme (pas deviné) :

1. **Menu compte natif en anglais** : ce dropdown "My Account"/"Logout"
   n'est pas un template à nous, c'est le menu natif du module
   `portal`. exocoms_theme force le rechargement des traductions
   françaises officielles d'Odoo pour les modules natifs concernés
   (`mods._update_translations('fr_FR')` sur base/web/website/
   website_sale/portal/auth_signup/mail/sale) — sans quoi ces chaînes
   natives peuvent rester en anglais sur une base mutualisée où le
   français a été activé après coup. Repris à l'identique dans une
   nouvelle fonction `_reload_native_translations(env)`, appelée après
   `_setup_languages()`.
2. **Couleurs des pages /web/login, /web/signup, etc.** : exocoms_theme
   n'a PAS de règle dédiée à ces pages — ils ont un `.btn-primary`
   GLOBAL non scopé à un conteneur (layout.css), sans `!important`, qui
   retombe donc naturellement sur toute page native non déjà couverte
   par une règle plus spécifique. Chez nous, toutes les règles
   `.btn-primary` existantes étaient scopées (`.oe_website_sale`,
   `.o_wsale_product_btn`, `#products_grid`, `.o_portal_wrap`) :
   aucune ne couvrait `/web/login`, resté sur le bleu/violet par défaut
   d'Odoo. Ajout d'une règle globale équivalente dans
   `odoo-integration.css` avec `--ch-terracotta` — sa spécificité plus
   faible que les règles existantes garantit qu'elle ne s'applique que
   là où rien de plus spécifique n'est déjà défini, sans régression
   ailleurs sur le site.

## Déconnexion envoyait sur le mauvais site (v19.0.1.0.43)

Suite du diagnostic "où ça m'envoie lorsque je me déconnecte" : `/web/
login` et `/web/session/logout` atterrissaient sur le site générique
par défaut ("My Website") au lieu de Capsule House, alors que `/`
résolvait correctement.

Le client a demandé de rester sur une analyse du CODE local
d'exocoms_theme, pas de manipulation sur l'instance Odoo.sh —
recherche exhaustive faite dans ce sens (`__init__.py` complet :
aucune occurrence de `sequence` sur le modèle `website`, aucune classe
`ir.http`/`website` personnalisée, aucune route de login/logout ;
`controllers/main.py`, `models/`, `data/website_data.xml` : rien non
plus). Rien dans leur code ne gère spécifiquement ce cas — ce n'est
donc pas une technique qu'on aurait ratée chez eux, c'est un réglage à
poser nous-mêmes.

Sans `website.domain` posé (notre cas tant que le DNS n'est pas
confirmé), Odoo départage les sites candidats pour les routes natives
comme `/web/login` via `website.sequence` (plus bas = prioritaire).
Tous les sites non configurés partagent la même valeur par défaut
(10), y compris le site générique. Fix : nouvelle fonction
`_setup_website_priority()`, qui pose `website.sequence = 1` sur
NOTRE site uniquement (jamais touché ailleurs), pour qu'il gagne
systématiquement ce départage.

## Pagination boutique restée violette (v19.0.1.0.44)

Client : "tu as oublié la couleur ici comme on a fait dans
exocoms_theme" (capture du pager, rond de page active en violet). Le
pager natif Odoo (`#o_wsale_pager`) garde sa couleur primaire par
défaut (#875A7B) tant qu'aucune règle ne le recolore — jamais fait
côté Capsule House. Vérifié dans exocoms_theme
(`static/src/css/layout.css`) : ils ont exactement cette règle, scopée
à `#o_wsale_pager`. Reprise à l'identique dans `shop.css` avec
`--ch-terracotta`/`--ch-white`.

## Pages Aide — Livraison, Retours, Garantie, FAQ (v19.0.1.0.46)

Les 4 liens de la colonne "Aide" du footer (jusque-là en 404) mènent
maintenant à de vraies pages, livrées d'après une maquette fournie par
le client :

- `/livraison` : encart "livraison offerte dès 25 000 €", timeline 4
  étapes, tableau des délais/frais par zone (France métro/Corse/DOM-TOM).
- `/retours` : encart d'alerte sur le droit de rétractation (non
  applicable après lancement fabrication, produit sur mesure), 3
  cartes (avant fabrication / après livraison / procédure), bouton
  vers `/contactus` (page de contact NATIVE d'Odoo — lien mis à jour en
  v19.0.1.0.47, voir section "Pages Entreprise" ci-dessous ; pointait
  vers `/contact` avant que la décision de ne jamais reconstruire de
  page contact ne soit prise).
- `/garantie` : bandeau "10 ans", colonnes Couvert (vert)/Non couvert
  (rouge), étapes pour déclarer un sinistre.
- `/faq` : questions groupées par catégorie, accordéon Bootstrap natif
  (markup du snippet Accordéon du Website Builder, pas de JS custom).

Menu latéral "Aide" partagé par les 4 pages (`aide_sidebar.xml`),
état actif calculé dynamiquement depuis l'URL réelle (jamais codé en
dur par page). Contenu bilingue FR/EN, même convention que le reste du
thème. Responsive : le menu latéral passe en barre horizontale
scrollable sous 900px.

Deux écarts avec le brief fourni, choisis pour rester cohérent avec le
reste du site déjà en place (le brief ne correspondait pas exactement
à ce qui est réellement déployé) :
- **Police** : Inter, pas Manrope — Inter est la police utilisée
  partout ailleurs sur le site (variables.css) ; changer de police
  seulement sur ces 4 pages aurait cassé la cohérence visuelle.
- **Icônes** : FontAwesome (`<i class="fa fa-*">`), pas de SVG en
  ligne dédiées — même bibliothèque d'icônes que le hero et les avis.

Couleur ajoutée : `--ch-red` (#B4553F, rouge alerte/non-couvert),
absente jusqu'ici de `variables.css` — le reste de la palette
(`--ch-panel`, `--ch-ink`, `--ch-terracotta`, `--ch-amber`, `--ch-fog`,
`--ch-green`) existait déjà et correspond exactement aux couleurs
demandées, réutilisée telle quelle.

## Pages Entreprise — À propos, Le concept, Contact natif (v19.0.1.0.47)

Les liens de la colonne "Entreprise" du footer mènent maintenant à de
vraies pages, livrées d'après une maquette fournie par le client :

- `/a-propos` : hero (texte + illustration SVG reprise à l'identique
  du hero d'accueil), bandeau 4 statistiques (année de fondation, pods
  installés, taille d'équipe, ateliers), 3 cartes "Nos valeurs" (design
  intemporel / fabrication responsable / installation rapide),
  historique en timeline verticale (4 jalons 2022→2026).
- `/le-concept` : intro "Qu'est-ce qu'un pod Capsule House ?", tableau
  comparatif Pod vs construction traditionnelle (délai, permis,
  empreinte carbone, mobilité, budget), 4 étapes "De l'atelier à votre
  terrain" (matériaux/fabrication/contrôle qualité/transport & pose),
  schéma "Coupe technique" (même illustration SVG que le hero,
  stylisée en contour pointillé avec libellés superposés).
- **Contact : décision explicite du client — "tout les contact de mes
  pages doive etre dirigé vers la pages contacts native odoo"**. Ce
  module ne construit AUCUNE page de contact. Tous les liens "Contact"
  du site (nav en pills `entreprise_nav.xml`, colonne "Entreprise" du
  footer, bouton "Contacter le service client" de `/retours`) pointent
  vers `/contactus`, la page de contact native du module `website`
  (déjà dans les dépendances de ce thème) — confirmée par le code local
  d'`exocoms_theme` qui l'utilise aussi tel quel (`footer.xml`).

Nav en onglets "pills" partagée par les 2 pages (`entreprise_nav.xml`),
même principe que `aide_sidebar.xml` : état actif calculé dynamiquement
depuis l'URL réelle, jamais codé en dur par page. L'onglet "Contact" de
cette nav n'est jamais marqué actif (il ne pointe pas vers une page à
nous). Contenu bilingue FR/EN, même convention que le reste du thème.
CSS (`.ch-entreprise-*` dans `pages.css`) réutilise volontairement les
classes `.ch-aide-*` existantes (titre, sous-titre, cartes, tableau)
plutôt que dupliquer un système parallèle.

Mêmes deux écarts que les pages Aide (v19.0.1.0.46), pour rester
cohérent avec le reste du site déjà en place : police Inter (pas
Manrope) et icônes FontAwesome (pas de SVG en ligne dédiées). Aucune
nouvelle couleur : la palette existante (`--ch-panel`, `--ch-ink`,
`--ch-terracotta`, `--ch-fog`, `--ch-tan-1`) couvre entièrement le
brief — ce brief-ci ne demandait d'ailleurs pas de rouge (contrairement
aux pages Aide).

## Blocs non éditables comme sur exocoms_theme (v19.0.1.0.48)

Question posée par le client, capture d'écran à l'appui (Website
Builder ouvert sur la page d'accueil) : comment le hero d'accueil, et
plus largement le contenu de la page d'accueil, sont-ils protégés pour
ne pas être éditables nativement via le panneau "Blocks" d'Odoo — comme
c'est le cas sur exocoms_theme ?

Réponse honnête après relecture du code local d'exocoms_theme : ce
n'était **pas** le cas jusqu'à cette version. Les 8 templates de page
de ce module enveloppaient tout leur contenu réel (hero compris) dans
un même `<div id="wrap" class="oe_structure">`. Deux problèmes :

1. `website.layout` pose déjà lui-même un `#wrap` natif — on créait
   donc un second `id="wrap"` dupliqué (HTML invalide) à l'intérieur.
2. `oe_structure` marque toute la zone comme un conteneur de blocs
   éditable par le Website Builder (glisser-déposer, édition inline).
   En l'appliquant à tout le contenu, celui-ci restait exposé à
   l'édition ou à la suppression accidentelle depuis "Edit" — ce n'est
   pas ainsi qu'exocoms_theme fonctionne réellement.

Vérification directe du code d'exocoms_theme (`views/pages/home.xml`,
`avis.xml`, `services.xml`) : aucun de ces templates n'enveloppe son
contenu réel dans `oe_structure`. Les sections (hero, contenu) sont
`t-call`-ées directement ; seuls des `<div class="oe_structure
oe_empty">` séparés et **réellement vides** sont insérés entre les
sections, comme simples points d'ancrage pour ajouter de nouveaux blocs
— sans jamais rendre éditable le contenu déjà codé en dur.

Corrigé en reproduisant exactement ce principe sur les 8 pages du
module (`page_home`, `avis_page`, les 4 pages Aide, les 2 pages
Entreprise) : suppression du `<div id="wrap" class="oe_structure">`
englobant, remplacé par des placeholders vides
(`oe_structure_ch_<page>_after_hero` / `_bottom`) aux mêmes endroits
qu'exocoms_theme — après le hero sur Accueil et Avis, en bas de page
partout. Aucun changement
visuel : les classes CSS posées sur le div supprimé (`.ch-home`,
`.ch-aide-page`, `.ch-avis-page`, `.ch-entreprise-page`) n'étaient
ciblées par aucune règle CSS (vérifié dans `static/src/css/`).

**Correctif de ce correctif (v19.0.1.0.49)** : l'affirmation ci-dessus
("le hero et tout le reste du contenu ne sont donc plus éditables")
était en partie fausse — erreur repérée par le client (capture
d'écran : panneau Style vide en cliquant sur le hero) et confirmée en
relisant cette fois le contenu réel de
`exocoms_theme/views/partials/hero.xml`, pas seulement `home.xml`. Le
hero d'exocoms N'EST PAS verrouillé : sa `<section>` porte
`data-snippet="s_exocoms_hero"` + `data-name="Exocoms Hero"` (donc
sélectionnable, panneau Style actif), et le texte marketing statique
(badge, titre, sous-titre, boutons, bandeau de confiance) porte la
classe `oe_editable` (donc éditable en ligne). Seul leur SVG décoratif
est explicitement `o_not_editable`. Le correctif 19.0.1.0.48
(suppression de l'`oe_structure` englobant) restait juste — c'est bien
ainsi qu'exocoms structure ses pages — mais il manquait ce second
niveau : sans `data-snippet`/`oe_editable` sur le hero lui-même, celui-
ci se retrouvait totalement verrouillé au lieu de reproduire le
comportement réel d'exocoms.

Corrigé sur `views/partials/hero.xml` : `data-snippet="s_ch_hero"` +
`data-name="Capsule House Hero"` sur la `<section class="ch-hero">`,
`oe_editable` sur le titre, le sous-titre, le bloc des 3 pastilles et
le bandeau de confiance (même granularité par bloc qu'exocoms, pas
span par span), `o_not_editable` sur le SVG de l'illustration.
Restent volontairement NON éditables — déviation assumée, propre à
Capsule House puisque ce contenu n'existe pas chez exocoms — les 3
statistiques (nombres ET libellés) et le formulaire de recherche : ces
zones affichent des valeurs calculées dynamiquement à chaque rendu
(`t-esc published_products_count` / `units_installed_count`) ; les
rendre éditables aurait risqué de figer un chiffre en dur au premier
Save et de casser le comptage automatique aux rendus suivants. Même
raisonnement pour le bouton "Ajouter au panier" et les cartes produits
flottantes (contenu 100 % dynamique).

**Suite (v19.0.1.0.50)** : après déploiement de la 19.0.1.0.49, le
panneau Style restait toujours vide en cliquant sur le hero
(nouvelle capture d'écran du client) — `data-snippet`/`data-name`
seuls n'ont pas suffi. En recomparant précisément les classes de la
`<section>` hero d'exocoms (`o_colored_level pt32 pb32 oe_img_bg
o_bg_img_center`, en plus de `data-snippet`) à la nôtre, `o_colored_level`
est ajoutée par hypothèse — c'est une classe cœur d'Odoo qui enregistre
un `<section>` auprès du panneau d'options générique Background/
Layout/Visibility, exactement ce qu'affiche la capture d'écran sur
exocoms. **Non vérifié à 100 %** faute d'accès au JS cœur d'Odoo en
local (seuls les modules thème sont montés) — à confirmer par un
nouveau test après déploiement. Si ça ne suffit toujours pas, prochaine
piste : `oe_img_bg`/`o_bg_img_center` (liées à une image de fond, que
notre hero n'a pas — fond en dégradé CSS, pas image).

**Suite (v19.0.1.0.51)** : module bien mis à niveau à chaque test
(confirmé par le client), donc pas un problème de déploiement — le
panneau Style restait quand même vide après la 19.0.1.0.50. Piste
suivante, proposée par le client : l'**organisation** du template, pas
seulement ses classes. Avant cette version, `partial_hero` était un
seul template contenant le FR ET le EN à l'intérieur (t-if/t-else
internes) — la `<section data-snippet>` n'était donc pas le résultat
direct d'un `t-call` vers un template dédié à une seule langue.

Vérification du vrai code d'exocoms_theme : leur `hero_section` n'est
qu'un aiguilleur (2 lignes, un `t-if` par langue) qui `t-call` soit
`hero_section_fr` soit `hero_section_en` — deux templates complets et
indépendants, chacun avec sa propre `<section data-snippet="...">`
entière (rien de partagé, tout dupliqué y compris l'illustration). Par
comparaison, leur `features_section` (pas de `data-snippet`, section
"normale") utilise lui un simple `t-if/t-else` interne à un seul
template — donc CE N'EST QUE pour le hero (élément formellement
"snippet") qu'exocoms scinde en deux templates par langue.

Reproduit à l'identique (v19.0.1.0.51) : `hero.xml` scindé en
`partial_hero_fr` / `partial_hero_en` (templates complets et
indépendants), `partial_hero` devenu un simple aiguilleur. Les deux
nouveaux ids ajoutés à `SCOPED_VIEW_XML_IDS`.
`partial_featured_products` ("Meilleures ventes", pas de
`data-snippet`) n'est pas concerné, comme son équivalent
`features_section` chez exocoms.

**Root cause confirmée (v19.0.1.0.52)**, rapport transmis par le
client : le Website Builder ne pouvait déposer aucun bloc car Odoo se
base sur l'attribut `data-oe-model` pour détecter les zones éditables.
Quand `oe_structure oe_empty` est posé sur un élément qui contient des
balises `<t>` (`t-call`, `t-if`, `t-foreach`, `t-set`), Odoo considère
cet élément comme un conteneur de template et supprime `data-oe-model`
au rendu — aucune zone de dépôt n'est créée. C'est exactement le bug
de la structure d'AVANT la 19.0.1.0.48 (`<div id="wrap"
class="oe_structure">` contenant directement des `<t t-call>`).

**Règles retenues pour tout futur développement sur ce module :**
1. Ne jamais poser `oe_structure oe_empty` sur un élément contenant
   des `<t>` descendants — toujours un `<div>` enfant à part, sans
   aucune balise `<t>` dedans ni autour.
2. Ne jamais imbriquer un `<section>` dans un `<section>`, ni un
   `<aside>` dans un `<aside>` — un `<div>` pour les conteneurs
   internes.
3. Ne jamais imbriquer plusieurs `<div class="oe_structure oe_empty">`
   l'un dans l'autre au sein d'une même zone éditable (des divs sœurs/
   successives à différents endroits d'une page restent autorisées —
   c'est ce que fait ce module et exocoms_theme lui-même).
4. Chaque `<section>` destinée à accepter des blocs doit avoir sa
   propre zone `oe_structure oe_empty` interne, juste avant sa
   fermeture.
5. Images produit : toujours via `/web/image/product.template/<id>/
   image_<taille>`, jamais via le champ binaire directement dans un
   template.
6. Après chaque modification XML : vérifier que le mode Édition
   permet bien d'insérer/déplacer des blocs ; si non, vérifier en
   premier le placement de `oe_structure`.

**Audit du module contre ces règles** : règles 1, 2, 3, 5 déjà
respectées (rien à corriger). Règle 4 manquante sur `hero.xml`
(`partial_hero_fr`/`_en`) et `avis_hero.xml` (`avis_hero_fr`/`_en`) —
corrigé : `oe_structure_ch_hero_extra` / `oe_structure_ch_avis_hero_
extra` ajoutés juste avant `</section>` dans chacun, comme
`oe_structure_hero_extra` / `oe_structure_avis_hero_extra` chez
exocoms. Au passage, `avis_hero.xml` a aussi été mis au même niveau
que le hero d'accueil : `data-snippet`, `data-name`, `o_colored_level`
sur la `<section>`, `oe_editable` sur l'eyebrow/titre/sous-titre/
bouton — il en était complètement dépourvu jusqu'ici malgré son
schéma FR/EN déjà correct.

## Test diagnostique cartes flottantes du hero (v19.0.1.0.53)

Malgré tous les correctifs précédents (data-snippet, data-name,
o_colored_level, oe_editable, zone `oe_structure` interne, scission
FR/EN), le panneau Style restait toujours vide sur le hero. Hypothèse
du client à tester : le bloc des 2 cartes flottantes de produits dans
`hero.xml` (`<t t-if="featured_products">` /
`<t t-foreach="featured_products[:2]" t-as="hero_product">`, contenu
100 % dynamique) pourrait empêcher Odoo de traiter la `<section
data-snippet>` comme éditable — même logique que la règle
"`oe_structure` ne doit jamais être posé sur un élément contenant des
`<t>`" déjà identifiée.

**Rien n'est supprimé.** Changement strictement réversible et
temporaire : la condition est passée de `t-if="featured_products"` à
`t-if="False"` dans `partial_hero_fr` ET `partial_hero_en` — le bloc
entier (cartes, badges, prix, bouton "Ajouter au panier") reste
intact dans le code, juste désactivé à l'affichage.

**Résultat attendu par le client** : retester le panneau Style sur le
hero après déploiement.
- Panneau Style apparaît maintenant → le bloc dynamique était bien la
  cause ; prochaine étape : trouver comment le garder (ex : le sortir
  de la `<section data-snippet>`, le repositionner en CSS) sans
  bloquer l'éditeur.
- Panneau Style toujours vide → piste écartée, remettre
  `t-if="featured_products"` aux deux endroits et chercher ailleurs
  (piste suggérée : inspecter la console du navigateur en mode Édition
  pour une éventuelle erreur JS, plutôt que continuer à deviner à
  partir du seul code source).

**Suite (v19.0.1.0.54)** : remarque juste du client — avec
`t-if="False"`, la balise `<t>` reste malgré tout présente dans l'arch
compilé par QWeb, seul son contenu ne s'affiche pas. Ça ne teste donc
pas correctement l'hypothèse "la simple présence d'une balise `<t>`
dans la section bloque l'édition". Corrigé : le bloc est maintenant
neutralisé par un **vrai commentaire XML** (`<!-- ... -->`) au lieu de
`t-if="False"` — un commentaire XML est éliminé par le parseur avant
que QWeb ne compile le template, donc les balises `<t>` à l'intérieur
disparaissent réellement de l'arch tant qu'elles restent commentées.
Toujours rien de supprimé : décommenter restaure le bloc à
l'identique.

**Résultat du test (v19.0.1.0.55) : NÉGATIF**, confirmé par le client.
Même avec le bloc entièrement absent de l'arch compilé, le panneau
Style restait vide sur le hero. Cette hypothèse est écartée. Le bloc
est restauré à l'identique (rien n'avait été supprimé).

**Bilan après 6 versions de correctifs sur le hero (49 à 55)**, aucun
n'a résolu le symptôme, bien que chacun reproduise fidèlement le vrai
code d'exocoms_theme et reste légitime à conserver : data-snippet +
data-name (49), + o_colored_level (50), scission FR/EN (51), zone
oe_structure interne (52), retrait du contenu dynamique par
t-if=False puis par commentaire XML réel (53/54) — négatif (55).

**Prochaine étape recommandée** : la cause n'est probablement plus à
chercher dans le code de `hero.xml` lui-même. Sans accès direct à
l'instance Odoo.sh du client pour tester en direct, la piste la plus
fiable est d'inspecter la console du navigateur (F12 > Console) en
mode Édition au moment du clic sur le hero, à la recherche d'une
erreur JavaScript. Si le panneau Style reste vide sur TOUT le site
(pas seulement le hero), la cause est probablement plus générale
(chargement du bundle JS du Website Builder pour ce site, conflit
d'assets) plutôt que spécifique au code de ce module.

## Cause trouvée — hero et Style panel (v19.0.1.0.56)

Le client a fourni deux captures DevTools (onglet Elements) montrant
le DOM rendu réel du hero sur exocoms_theme face à celui de Capsule
House — comparaison du rendu final, pas seulement du code source.

Différence identifiée : la `<section>` hero d'exocoms porte, en plus
de `data-snippet`/`data-name`/`o_colored_level`, les classes
`oe_img_bg o_bg_img_center o_bg_img_origin_border_box` (gestion
d'image de fond). Conséquence visible directement dans le DOM rendu :
Odoo ajoute alors automatiquement, sur la `<section>` elle-même, la
classe `o_editable` et les attributs `data-oe-model="ir.ui.view"`
`data-oe-id` `data-oe-field="arch"` `data-oe-xpath="/t[1]/section[1]"`.

Sur le hero de Capsule House (jusqu'à la 19.0.1.0.55), ces attributs
n'apparaissaient que sur les enfants `oe_editable` (titre, sous-titre),
jamais sur la `<section>` — Odoo ne la reconnaissait donc que comme un
conteneur de texte, pas comme un bloc sélectionnable pour le panneau
Style. `o_colored_level` seul était insuffisant ; il fallait la
combinaison avec `oe_img_bg`/`o_bg_img_center`.

Corrigé : ces classes ajoutées à la `<section>` de `hero.xml`
(`partial_hero_fr`/`_en`) et `avis_hero.xml`
(`avis_hero_fr`/`_en`, même diagnostic probable). Aucune image de
fond en `style` inline : rien ne change visuellement, les fonds CSS
existants restent inchangés. Effet secondaire positif possible : le
panneau Background qui doit apparaître permettra au client de
remplacer ce fond par une vraie photo directement depuis le Website
Builder.

Ce diagnostic est basé sur une comparaison directe du DOM rendu réel
des deux sites (pas du code source), plus fiable que les tentatives
précédentes (49 à 55).

**Correctif de ce correctif** : la v56 seule n'a pas suffi — voir
"Cause réelle trouvée — routing de l'accueil" ci-dessous (v19.0.1.0.57).
Le hero de `/avis` fonctionnait déjà avant même la v56 (aucune classe
`oe_img_bg` nécessaire côté avis), ce qui aurait dû alerter plus tôt
que la différence n'était pas dans le balisage du hero lui-même.

## Cause réelle trouvée — routing de l'accueil (v19.0.1.0.57)

À la demande explicite du client (« regarde bien les deux projets,
fais une analyse complète des deux projets ») après l'échec de la
v56 à résoudre le problème sur l'accueil (alors que `/avis`
fonctionnait avec un balisage désormais identique), analyse
comparative complète de `capsule_house_theme` et `exocoms_theme` :
contrôleurs, `__init__.py`, manifestes, pages.

Une seule différence structurelle restait entre les deux thèmes une
fois le balisage des heros aligné : **comment chaque site sert sa
page d'accueil.**

- `exocoms_theme` sert `/` directement : `ExocomsWebsite` hérite du
  contrôleur natif `Website` et surcharge `index()` via
  `@http.route()` **sans argument** (réutilise la route native
  existante, n'en crée aucune nouvelle), avec une garde
  `_is_our_site()` et un `super().index(**kw)` pour les 16 autres
  sites. Un seul rendu, aucun redirect.
- `capsule_house_theme` (jusqu'à la 19.0.1.0.56) servait l'accueil
  sur une route dédiée `/capsule-house/home`, atteinte depuis `/`
  via le champ natif `website.homepage_url` (posé par
  `_setup_homepage()`) — un **vrai redirect HTTP côté navigateur**,
  confirmé par le propre commentaire du module dans `_setup_menus()`
  (écrit bien avant ce diagnostic, pour un bug de surlignage de menu
  sans rapport avec l'éditeur à l'époque). Deux hops : `/` → 302 →
  `/capsule-house/home`.

La page `/avis`, elle, était déjà servie en un seul rendu direct
(comme `/` chez exocoms) — et fonctionnait. C'est la variable qui
manquait : le redirect empêchait apparemment le Website Builder de
garder le fil de « quelle page suis-je en train d'éditer » pendant
ce second hop, laissant la `<section>` hero sans `data-oe-model`/
`data-oe-id`/`data-oe-xpath` propres, alors que ses enfants
`oe_editable` (rendus dans la page finale) les récupéraient bien.

**Corrigé** : `CapsuleHouseWebsite.index()` surcharge maintenant `/`
directement, exactement comme `exocoms_theme` — même garde stricte
(`_is_our_website` + `super().index(**kw)` pour tous les autres
sites), même sécurité multi-site (aucune nouvelle route sur `/`,
seulement une surcharge héritée). C'est le pattern déjà éprouvé sans
incident en production sur `exocoms_theme` depuis longtemps.

- `_setup_homepage()` vide désormais `website.homepage_url` au lieu
  de le pointer vers `/capsule-house/home` (plus nécessaire, et
  cohérent avec exocoms_theme qui ne pose jamais ce champ).
- L'ancienne route `/capsule-house/home` est conservée en simple
  redirect 301 permanent vers `/` (`homepage_legacy_redirect`), pour
  ne pas casser d'éventuels favoris/liens déjà partagés.
- Le menu "Accueil" et les breadcrumbs des pages Aide/Entreprise
  pointent de nouveau vers `/` (`_setup_menus()`, `aide_*.xml`,
  `entreprise_*.xml`) — cohérent avec l'URL réellement affichée
  maintenant que le redirect n'existe plus.

Sécurité : ce changement reprend un pattern déjà validé en
production sur 17 sites (`exocoms_theme`), pas une nouvelle
tentative de surcharge de `'/'` — la garde `_is_our_website` +
fallback `super()` systématique protège les 16 autres sites de la
base mutualisée exactement comme chez exocoms.

Ce correctif seul n'a **pas** résolu le problème (confirmé par le
client après déploiement) — voir la section suivante pour la cause
réelle, trouvée juste après.

## Cause réelle #2 — ancêtre `o_editable` manquant (v19.0.1.0.58)

Le correctif de routing (v57) était bien fondé mais insuffisant : le
panneau Style restait vide sur le hero même en servant `/`
directement. Test décisif proposé pour trancher entre "problème
spécifique au hero" et "problème de l'éditeur sur cette page" : le
client a glissé un bloc **natif** Odoo ("Masonry") depuis le panneau
Blocks juste après le hero, sur la même page, dans la même session
d'édition. Résultat : le panneau Style s'affiche normalement pour ce
bloc natif — donc l'éditeur fonctionne très bien sur cette page ;
seul le hero pose problème.

Capture du code du bloc natif fournie par le client :

```html
<section class="s_masonry_block pt48 pb48 o_colored_level"
         data-snippet="s_masonry_block" data-name="Masonry"
         contenteditable="false">
```

**Aucun `data-oe-model`/`data-oe-id`/`data-oe-xpath` sur cette
`<section>` non plus.** Toute la piste suivie depuis la v56 (faire
apparaître ces attributs sur la section du hero via `oe_img_bg` etc.)
reposait donc sur une fausse corrélation : ce n'est pas cet attribut
qui déclenche le panneau Style.

La vraie différence, visible dans le même DOM (fourni par le
client) : le bloc Masonry est un **enfant** de :

```html
<div id="oe_structure_ch_home_after_hero"
     class="oe_structure oe_empty o_editable" contenteditable="true">
```

— alors que notre `<section class="ch-hero">` n'avait **aucun
ancêtre** portant `o_editable` ni `contenteditable="true"`, jusqu'à
`<main>` inclus. Le SnippetsMenu d'Odoo cherche, au clic, le plus
proche ancêtre marqué comme zone éditable pour savoir si l'élément
cliqué (ou son ancêtre `[data-snippet]`) est sélectionnable — sans
cet ancêtre, aucun clic ne peut jamais activer la sélection de bloc,
quel que soit le balisage du hero lui-même. Ça explique pourquoi 8
tentatives successives sur le balisage du hero (v49 à v56) n'ont rien
changé : le problème était un niveau au-dessus, dans
`home.xml`/`avis.xml`, pas dans `hero.xml`/`avis_hero.xml`.

**Corrigé (tentative v58, REVERT EN v59)** : le `<t
t-call="capsule_house_theme.partial_hero"/>` (et `avis_hero`) a été
enveloppé dans un `<div class="o_editable" contenteditable="true">`.
**Erreur** : `contenteditable="true"` écrit en dur dans le code source
est un attribut HTML natif du navigateur, appliqué à TOUS les
visiteurs en permanence — pas une classe Odoo activée seulement en
mode édition. Résultat en conditions réelles : le hero devenait
éditable pour n'importe quel visiteur, sans jamais cliquer sur
"Edit". Signalé immédiatement par le client ("ça rendait le hero
éditable sans que je ne clique sur edit") et reverté en v59. Ce que
montrait la capture DevTools (le `contenteditable="true"` sur le div
`oe_structure` généré automatiquement) était injecté dynamiquement
par Odoo, côté serveur, UNIQUEMENT pour la session de l'éditeur
connecté — jamais présent dans le code source, jamais statique.
Leçon : ne plus jamais coder `contenteditable` en dur dans un
template.

## Cause réelle #3 — contenu dynamique dans le hero (v19.0.1.0.60)

Après le revert de la v58/59, retour à l'analyse : comparaison
directe, dans la même session d'édition, entre le hero (toujours pas
sélectionnable) et un bloc natif Odoo ("Masonry") glissé juste après
lui. Le bloc natif s'est révélé parfaitement fonctionnel (panneau
Style complet), et surtout **sa propre `<section>` n'avait elle non
plus AUCUN `data-oe-model`** — ce qui invalide rétroactivement toute
la piste suivie depuis la v56 (cet attribut n'a jamais été le
déclencheur du panneau Style, la corrélation observée était fausse).

Comparaison précise du DOM complet fourni par le client : tout ce qui
est purement statique dans le hero est marqué `o_editable`/
`data-oe-*` par Odoo — y compris des conteneurs entiers comme
`.ch-hero-visual` (toute la colonne illustration). Mais
`.ch-hero-content`, `.ch-hero-grid` et la `<section>` elle-même ne le
sont jamais. La seule chose commune à ces trois-là, absente de
`.ch-hero-visual` : ils contiennent quelque part `.ch-hero-stats`, qui
affichait de VRAIES valeurs dynamiques via `t-esc`
(`published_products_count`, `units_installed_count`), ainsi que le
badge de note (`rating_value`/`rating_count`) et les cartes flottantes
de produits vedettes (`t-foreach` sur `featured_products`).

Vérification croisée, deux sources indépendantes :
- Lecture directe du code source complet d'exocoms_theme
  (`views/partials/hero.xml`) : **aucune** expression dynamique nulle
  part dans leur hero, uniquement du texte fixe. `avis_hero.xml` (qui
  fonctionne chez nous aussi) n'en a pas non plus.
- Doc officielle Odoo 19 ("Building blocks > Dynamic Content
  templates") : les snippets dynamiques natifs d'Odoo (ex: Articles de
  blog) gardent leur `<section>` 100% statique dans l'arch source, et
  injectent le contenu réel via **JavaScript après le chargement de la
  page** — jamais via `t-esc`/`t-foreach` directement dans l'arch.

**Corrigé**, à la demande du client ("avoir tout ce qu'on veut en
pensant par le JS") : `hero.xml` (`partial_hero_fr`/`_en`) ne contient
plus aucune expression dynamique. Les 4 zones concernées (badge de
note, comptage produits publiés, comptage unités installées, cartes
flottantes + raccourci panier) sont désormais des placeholders
statiques (masqués par défaut via `d-none` quand la donnée peut être
absente), peuplés côté client par `static/src/js/main.js`
(`initHeroDynamicContent`) à partir d'une nouvelle route JSON dédiée,
`/capsule-house/hero-data.json` (`CapsuleHouseWebsite.hero_data()`,
`controllers/main.py`) — mêmes calculs qu'avant, aucune donnée
fabriquée, juste injectés après coup au lieu d'être rendus côté
serveur dans l'arch. Dégradation gracieuse : en cas d'échec du fetch,
le hero reste utilisable, les placeholders restent simplement masqués.

Effet attendu : la `<section>` du hero redevient 100% statique dans
l'arch source — condition nécessaire, confirmée par comparaison
directe avec exocoms_theme et le bloc natif Masonry, pour qu'Odoo la
marque comme un bloc sélectionnable avec panneau Style complet.

## SEO — même principe que exocoms_theme (v19.0.1.0.63)

Jusqu'ici, `data/seo_data.xml` était vide (juste un commentaire
"réservé pour plus tard") : aucune meta description, robots, Open
Graph, Twitter Card ni schema.org n'existait nulle part dans le
module — contrairement à `exocoms_theme`, dont `layout.xml` pose un
bloc SEO global et dont plusieurs pages (`avis.xml`, `boutique.xml`,
`services.xml`, `mentions_legales.xml`) surchargent ce bloc avec leur
propre contenu.

Reproduit à l'identique :
- **Bloc global** (`views/templates/layout.xml`, xpath `//head`) :
  meta description, `robots`, Open Graph, Twitter Card, schema.org
  `Organization` en JSON-LD. Image de partage : le logo du site
  (`capsule-house-logo.png`), même logique que `EXOCOMS.png` chez
  exocoms.
- **Surcharges page par page** (`t-set="head"`) : `home.xml`,
  `avis.xml`, les 4 pages Aide, les 2 pages Entreprise — description et
  `canonical` propres à chaque page.

Tout le texte est réutilisé depuis du contenu déjà validé sur le site
(sous-titres, h1 existants) — jamais de texte SEO inventé. Coordonnées
schema.org (téléphone, adresse) : reprises à l'identique de celles
d'exocoms_theme, à la demande explicite du client ("c'est la même
entreprise qui gère les deux") — Exocoms Group gère les deux sites. À
ajuster si Capsule House obtient ses propres coordonnées dédiées.

**Non couvert** : `views/pages/shop.xml` (page boutique native
`website_sale.products`) — structure de vue héritée moins prévisible
pour un xpath `//head` fiable, laissé de côté plutôt que de risquer un
xpath qui casse à l'installation. À traiter dans une prochaine version
si besoin.

## Pages légales — Mentions légales, CGV, Confidentialité (v19.0.1.0.64)

En ouvrant le panneau SEO natif d'Odoo (Promote > Optimize SEO), le
client a découvert des liens cassés : `/mentions-legales`, `/cgv`,
`/confidentialite`. Pas une régression — ces liens sont dans le footer
depuis le tout début du projet, documentés comme "écart connu, non
corrigé pour l'instant" (voir plus haut), jamais construits.

`/shop/category/4` (Accessoires) apparaissait aussi cassé dans le même
panneau : pas un bug de routing (la catégorie est bien créée par
`_setup_shop_categories()`), simplement une conséquence du catalogue
actuellement vide (0 produit publié) — devrait se résoudre de
lui-même une fois de vrais produits publiés.

**Corrigé** : trois nouvelles pages (`views/pages/mentions_legales.xml`,
`cgv.xml`, `confidentialite.xml`), routes dédiées dans
`controllers/main.py`. Contenu — rien d'inventé :
- **Mentions légales** : coordonnées légales réelles d'Exocoms Group
  (SIRET, adresse, forme juridique, hébergeur), reprises à l'identique
  de `exocoms_theme` — même société gérant les deux sites, confirmé
  explicitement par le client ("c'est la même entreprise qui gère les
  deux"). Seule l'activité déclarée est adaptée (vente de maisons
  modulaires) et l'email de contact reprend la convention déjà en
  place ailleurs dans ce module (`contact@capsule-house.fr`).
  Hébergement (IONOS) repris tel quel — à confirmer/corriger si
  l'hébergement réel diffère.
- **CGV** : chaque clause reprend un fait déjà publié ailleurs sur le
  site (acompte 20 %, délais de fabrication/livraison, garantie 10 ans,
  paiement 3x sans frais), formalisé juridiquement — y compris le
  fondement légal réel de l'absence de rétractation pour un bien
  personnalisé (art. L221-28 3° du Code de la consommation).
- **Confidentialité** : décrit les traitements de données réellement en
  place (avis, newsletter, commandes, live chat) ; vérifié qu'aucun
  outil d'analytics/pixel tiers n'est configuré dans le module avant
  d'écrire la section cookies (uniquement des cookies fonctionnels).

### CSS dédié — `legal.css` (v19.0.1.0.65)

À la livraison (v19.0.1.0.64), les trois pages légales réutilisaient les
classes `.ch-aide-*` des pages Aide (`pages.css`), faute de style qui
leur soit propre. À la demande du client ("crée un css qui leur est
propre et bien propre"), elles ont désormais leur propre feuille :
`static/src/css/legal.css`, avec un namespace dédié `.ch-legal-*`
(`ch-legal-breadcrumb`, `ch-legal-wrap`, `ch-legal-title`,
`ch-legal-lead`, `ch-legal-body`) :
- Largeur de lecture plus étroite (760px) que le reste du site, adaptée
  à un format "document" plutôt qu'aux pages marketing.
- Titres `<h2>` avec liseré terracotta (`border-left`) au lieu du style
  inline `margin-top:32px;` retiré des 3 templates.
- Ne dépend plus des pages Aide/Entreprise : les deux familles de pages
  peuvent évoluer indépendamment sans se marcher dessus.

Enregistré dans `THEME_ASSETS` (`__init__.py`) comme les autres feuilles
du thème, via `ir.asset` scopé `website_id` (jamais dans
`web.assets_frontend` global). Aucun contenu juridique modifié.

## Audit exocoms_theme — témoignages & réassurance sur la home (v19.0.1.0.66, RETIRÉ EN v19.0.1.0.68)

Demande client : "regarde exocoms et ajoute ce qui est nécessaire pour
capsule house et si tu peux l'améliorer tu le fais". Comparaison complète
des deux modules (tous les fichiers `.py`/`.xml`/`.css`/`.js`).

**Éléments d'exocoms_theme identifiés mais volontairement NON repris :**
- `views/pages/contact.xml` (page contact custom) — Capsule House utilise
  délibérément la page NATIVE Odoo `/contactus`, décision déjà actée
  (voir manifest, "jamais reconstruite par ce module").
- `views/pages/services.xml` + `informatique.xml`/`telecom.xml`/
  `monéthique.xml` (hub "Services" avec 3 pages de domaines d'expertise)
  — spécifique à l'activité d'Exocoms (IT/Télécom/Monétique), pas
  transposable à Capsule House sans inventer des domaines d'expertise
  qui n'existent pas. C'est le même blocage identifié plus tôt en
  réponse à "la page application ne peut-elle pas être faite" (site
  Guose) : pas de vrai contenu disponible.
- `views/pages/emplois.xml` (carrières) — nécessiterait de vraies offres
  d'emploi, non disponibles.
- `views/partials/dashbord.xml`/`dashbord_boutique.xml` (carousels
  Nouveautés/Meilleures ventes/Vus récemment) — Capsule House a déjà son
  équivalent minimal (`partial_featured_products`, grille "Meilleures
  ventes") ; passer à 3 carousels distincts n'apporte rien tant que le
  catalogue est à 0 produit publié.
- Bande "moyens de paiement" (logos Visa/Mastercard/PayPal/Amex...) —
  affirmerait des moyens de paiement dont ce module n'a aucune
  confirmation qu'ils sont réellement configurés côté `website_sale`
  pour ce site.

**Éléments réellement portables, ajoutés** (`views/partials/home_trust.xml`,
t-appelé depuis `home.xml` après `partial_featured_products`) :
1. **Témoignages** (`.ch-testimonials`) : carousel alimenté par les VRAIS
   avis publiés (`capsule.house.avis`), via une nouvelle méthode
   `_get_home_avis_context()` dans `controllers/main.py` (réplique fidèle
   de `_get_home_avis_context` côté exocoms). Volontairement indépendante
   de `_get_avis_stats()` (utilisée pour le badge du hero, qui peut
   retomber sur un réglage manuel `ir.config_parameter`) : la section
   témoignages n'affiche jamais autre chose que de vrais avis — état vide
   explicite ("Soyez le premier à partager votre expérience") sinon.
2. **Réassurance** (`.ch-why-us`) : 4 items, mais contrairement aux 4
   promesses génériques d'exocoms (non vérifiées pour notre activité :
   "retours faciles", "qualité garantie"...), chaque item ici reformate un
   fait déjà publié et validé ailleurs sur CE site — rien de nouveau
   n'est affirmé : annulation 48h/remboursement intégral
   (`aide_retours.xml`), livraison 6 semaines France métropolitaine
   (`aide_livraison.xml`), garantie constructeur 10 ans
   (`aide_garantie.xml`), paiement 3x sans frais dès 1000€ (`hero.xml`,
   `aide_faq.xml`). Chaque item pointe vers sa page source respective.

**Amélioration apportée** (au-delà de la simple reprise) : chez exocoms,
le script de défilement automatique du carousel témoignages est un
`<script>` inline dans le template QWeb (`features.xml`). Ici, déplacé
dans `static/src/js/main.js` (`initTestimonialsCarousel`) — cohérent avec
le reste de ce module, où tout le JS du thème vit dans `main.js`, jamais
dans les vues.

**RETIRÉ EN v19.0.1.0.68** : retour client — "j'ai pas aimé tes ajout sur
la page acceuil trouve tu ca necessaire sur capsule ?", puis "retire
ca". Question posée honnêtement en retour : ni les témoignages ni la
réassurance n'étaient réellement NÉCESSAIRES pour Capsule House (contrairement
à la demande initiale du 19.0.1.0.66) — les deux avaient été ajoutés sous
couvert de "si tu peux l'améliorer, fais-le", pas d'un besoin identifié.
Les témoignages arrivaient prématurément (peu/pas d'avis publiés encore,
`/avis` existe déjà en page dédiée) et la réassurance était redondante
avec le hero et les pages Aide. Tout le code de cette section a été
retiré (`home_trust.xml` supprimé, `_get_home_avis_context()` retiré du
contrôleur, CSS/JS associés retirés) — voir migration 19.0.1.0.68. La
page `/nos-modeles` (section suivante) n'est PAS concernée par ce
retrait : demande distincte, confirmée séparément par le client.

## Page /nos-modeles — sur le modèle de "Nos services" (v19.0.1.0.67)

Historique de la demande, en trois temps :
1. Le client a montré `fr.guosegroup.com/application` (fabricant chinois
   de maisons capsules) et demandé si ce site pouvait servir à voir ce
   qui manque au nôtre. Leur page "Application" montre le pod utilisé
   comme logement/bureau/boutique/salle d'exposition/abribus, avec de
   VRAIES photos de leurs propres installations.
2. Analyse : ce contenu n'est pas transposable. Rien sur le site Capsule
   House ne mentionne d'usage bureau/boutique/exposition ; les
   catégories boutique (Studio/Duo/Panorama/Accessoires) sont des
   tailles de pods, pas des cas d'usage. Construire une page équivalente
   aurait nécessité d'inventer des usages — refusé, cohérent avec le
   principe "jamais de contenu fabriqué" de ce module.
3. Le client a clarifié : "lorsque je clique sur les elements de la page
   application c'est comme ma page service sur exocoms indique juste
   leur domaine d'expertise", puis confirmé vouloir cette page comme
   modèle plutôt que celle de Guose.

Analyse de `exocoms_theme/views/pages/services.xml` +
`partials/services_hero.xml` : leurs cartes ne fabriquent aucun contenu
par domaine — 2-3 phrases génériques par carte, et ce sont les VRAIS
tags du hero qui renvoient vers les vrais filtres boutique
(`/shop/category/<id>`). exocoms a même sa propre entrée de menu dédiée
("Nos services").

**Reproduit à l'identique pour Capsule House** (`views/pages/nos_modeles.xml`,
route `/nos-modeles`, contrôleur `nos_modeles()`) :
- Chaque carte pointe vers le VRAI filtre boutique de sa catégorie
  (même URL que les entrées de menu créées par `_setup_menus`) — aucune
  sous-page de contenu inventée par catégorie.
- Description de 1 ligne par carte, strictement réelle : tailles Studio
  (18 m²) et Panorama (jusqu'à 40 m²) déjà publiées sur `/faq`
  (`aide_faq.xml`) ; trilogie "Studio, duo ou famille" déjà publiée sur
  `/shop` (`shop.xml`) ; "Duo" se limite à ce que le nom affirme de
  lui-même (aucune surface publiée nulle part pour ce modèle — pas
  d'invention).
- Image de carte = vraie photo du premier produit publié de la
  catégorie (`image_id`), sinon icône générique — jamais de photo
  fabriquée. Compteur "X modèle(s) en ligne" = vrai `search_count`,
  affiché seulement si `> 0`.
- Nouvelle entrée de menu "Nos modèles" (séquence 15, entre Accueil et
  Tous les pods) — même principe que "Nos services" chez exocoms.

## FAQ "Permis de construire" — retrait d'un engagement non confirmé (v19.0.1.0.69)

En creusant l'idée de la page Application (usages Logement/Bureau/etc.,
voir section précédente), la discussion a dérivé vers une vraie question
client : est-ce que le site doit informer sur les démarches
administratives (permis de construire / déclaration préalable) ? Les
tailles réelles des pods (Studio 18 m², Panorama jusqu'à 40 m²) tombent
justement dans la zone où ces seuils s'appliquent — une vraie question
que se pose un acheteur, absente ailleurs sur le site.

Le client a d'abord envisagé d'en faire un vrai service
("le service doit prendre ça en compte"), puis a dit explicitement ne
pas savoir quel niveau d'engagement Capsule House peut tenir
("j'en sais rien en fait"). Décision : rester au niveau le plus sûr —
informer, pas promettre.

En vérifiant la FAQ existante (`aide_faq.xml`, chFaq1/chFaq1en,
présente depuis l'origine du module, reprise de la maquette client),
sa réponse affirmait déjà "Nous vous accompagnons dans les démarches"
— exactement l'engagement de service que le client venait de dire ne
pas pouvoir confirmer. Corrigé :
- Retrait de la promesse d'accompagnement.
- Seuils réels vérifiés par recherche (Code de l'urbanisme
  art. R.421-14 b, formulaires CERFA 16702/16703) : moins de 5 m²,
  aucune formalité ; 5 à 20 m², déclaration préalable ; plus de 20 m²,
  permis de construire ; seuil porté à 40 m² en zone urbaine PLU si la
  surface de plancher déjà bâtie sur le terrain ne dépasse pas 150 m².
- Application honnête aux tailles réelles : Studio (18 m², typiquement
  déclaration préalable), Panorama (jusqu'à 40 m², qui peut basculer en
  permis de construire selon la zone).
- Renvoi vers la mairie du client pour la décision finale, plutôt
  qu'une promesse de service non confirmée.

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
