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
