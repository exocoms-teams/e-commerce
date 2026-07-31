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
