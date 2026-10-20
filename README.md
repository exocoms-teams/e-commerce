# Capsule House

Site e-commerce de **Capsule House** (maisons modulaires / pods design), réalisé comme un **module thème Odoo 19** (`capsule_house_theme`) et déployé sur **Odoo.sh**.

| | |
|---|---|
| Module | `capsule_house_theme` (« Capsule House Theme ») |
| Version | 19.0.1.0.106 |
| Plateforme | Odoo 19 (Community/Enterprise), hébergement Odoo.sh |
| Éditeur | Exocoms Group |
| Licence | LGPL-3 |
| Langues | Français (par défaut) et anglais |
| Branche principale | `capsule_house` |

---

## Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Pages et routes](#pages-et-routes)
3. [Architecture](#architecture)
4. [Structure du dépôt](#structure-du-dépôt)
5. [Installation et déploiement](#installation-et-déploiement)
6. [Environnement de développement](#environnement-de-développement)
7. [Configuration](#configuration)
8. [Internationalisation](#internationalisation)
9. [Conventions de travail](#conventions-de-travail)
10. [Points d'attention et évolutions](#points-dattention-et-évolutions)

---

## Fonctionnalités

- **Vitrine** : page d'accueil (hero, produits vedettes, gammes, usages, témoignages, moyens de paiement), boutique, header et footer personnalisés.
- **Catalogue** : 24 produits préchargés, catégories (Capsule, Cabine, Dôme, Modulaire, Pliable, Accessoires), filtres et affichage de la boutique configurés automatiquement.
- **Gammes** : une page de détail par gamme (`capsule`, `cabine`, `dome`, `modulaire`, `pliable`) alimentée par des données statiques, avec **catalogue PDF** téléchargeable (généré avec `reportlab`).
- **Devis sur mesure** : formulaire public qui crée une demande commerciale.
- **Avis clients** : dépôt public, **modération** dans le back-office, note moyenne et nombre d'avis calculés à partir des avis publiés.
- **Centre d'aide** : livraison, retours, garantie, FAQ.
- **Pages Entreprise** : À propos, Le concept.
- **Pages légales** : mentions légales, CGV, confidentialité.
- **Services Odoo** : wishlist, newsletter, live chat, blog, panier latéral (mini-panier).
- **Provisioning automatique** : société, site web, liste de prix, langues, menus, catégories, filtres, logo et publication des produits sont créés et maintenus par le module.

## Pages et routes

| Route | Description |
|---|---|
| `/` | Accueil |
| `/shop`, `/boutique` | Boutique (`/boutique` est un alias de `/shop`) |
| `/nos-gammes`, `/nos-gammes/<slug>` | Liste et détail des gammes |
| `/nos-gammes/<slug>/catalogue.pdf` | Catalogue PDF d'une gamme |
| `/devis-sur-mesure` (+ `/submit`) | Devis sur mesure |
| `/avis` (+ `/submit`) | Avis clients |
| `/aide` | Centre d'aide (onglets livraison, retours, garantie, FAQ) |
| `/a-propos`, `/le-concept` | Pages Entreprise |
| `/mentions-legales`, `/cgv`, `/confidentialite` | Pages légales |
| `/newsletter/subscribe` | Inscription newsletter |
| `/capsule-house/*.json` | Données dynamiques du front (hero, panier, témoignages, moyens de paiement) |

Redirections conservées pour les anciens liens : `/livraison`, `/retours`, `/garantie`, `/faq` (vers `/aide#…`), `/nos-modeles` et `/capsule-house/home`.

## Architecture

### Base mutualisée, multi-sites

Le module tourne sur une **base Odoo partagée par une quinzaine de sites**. Toute la logique est donc **scopée à notre site** :

- le site est retrouvé par l'**identifiant mémorisé** dans `ir.config_parameter` (`capsule_house_theme.website_id`), jamais par son nom ;
- les contrôleurs qui surchargent des routes natives (comme `/`) sont protégés par `_is_our_website` ;
- les modèles propres au module portent un `website_id` posé explicitement ;
- le CSS/JS est enregistré via des `ir.asset` limités au site.

### Maintenance idempotente

`run_theme_maintenance()` (dans `setup_utils.py`) orchestre toute la configuration. Elle est rejouée :

- à l'installation (`post_init_hook`) ;
- à chaque mise à jour (scripts dans `migrations/`) ;
- toutes les heures par un **cron** (`Capsule House Theme: maintenance horaire`).

Chaque étape doit rester **idempotente** : la rejouer ne doit jamais changer le résultat ni écraser un réglage fait ensuite par le client.

### Données statiques

Les gammes et les usages sont définis dans `data_definition/__init__.py` (`GAMMES_DATA`, `USAGES_DATA`, `DEVIS_SUR_MESURE_DATA`) et injectés dans les templates par les contrôleurs. Les valeurs des gammes autres que « Capsule » sont des **données provisoires** à compléter.

## Structure du dépôt

```text
.
├── README.md                     # Ce fichier
├── SETUP_DEV.md                  # Installation de l'environnement dev (Windows)
├── setup-dev.ps1                 # Script d'installation dev
└── capsule_house_theme/
    ├── __manifest__.py
    ├── __init__.py               # run_theme_maintenance() et hooks
    ├── constants.py              # Clés de config, assets, constantes du site
    ├── setup_utils.py            # Étapes de provisioning (idempotentes)
    ├── controllers/
    │   ├── main.py               # Pages, JSON, formulaires publics
    │   └── catalogue_pdf.py      # Génération du catalogue PDF
    ├── models/
    │   ├── avis.py               # capsule.house.avis (avis modérés)
    │   └── maintenance.py        # Point d'entrée du cron
    ├── data/                     # cron, produits, SEO, données du site
    ├── data_definition/          # Gammes, usages, devis (données statiques)
    ├── security/                 # Droits d'accès
    ├── views/
    │   ├── templates/            # header, footer, layout
    │   ├── partials/             # blocs réutilisables (hero, gammes, avis…)
    │   └── pages/                # pages complètes
    ├── static/src/
    │   ├── css/                  # variables, base, layout, pages, shop…
    │   ├── js/                   # main.js, reveal.js
    │   └── img/                  # logo, visuels
    ├── i18n/en.po                # Traductions anglaises
    ├── migrations/               # Un dossier par version
    └── README.md                 # Journal détaillé des choix et correctifs
```

## Installation et déploiement

Le site n'est pas lancé en local : il tourne sur **Odoo.sh**.

1. Pousser les modifications sur la branche `capsule_house` (ou sur une branche de dev/staging Odoo.sh).
2. Odoo.sh construit l'environnement et met à jour le module : les scripts de `migrations/` et `run_theme_maintenance()` s'exécutent.
3. Tester sur le build (navigation privée, FR et EN) avant de passer en production.

### Dépendances Odoo

`website`, `website_sale`, `website_sale_wishlist`, `mail`, `im_livechat`, `website_livechat`, `website_blog`.

### Dépendance Python

`reportlab` (génération du catalogue PDF).

### Publier une nouvelle version

À **chaque** évolution :

1. incrémenter `version` dans `__manifest__.py` ;
2. ajouter un dossier `migrations/<nouvelle-version>/post-migrate.py` qui rejoue `run_theme_maintenance()` ;
3. documenter le changement dans `capsule_house_theme/README.md`.

## Environnement de développement

Un script installe l'autocomplétion Odoo dans VS Code, un `venv` et les dépendances (voir [SETUP_DEV.md](SETUP_DEV.md)) :

```bash
git clone --recurse-submodules --branch capsule_house https://github.com/exocoms-teams/e-commerce.git
cd e-commerce
powershell -ExecutionPolicy Bypass -File setup-dev.ps1
```

Prérequis : Git, Python 3.10 minimum (3.11 recommandé), VS Code avec Python et Pylance. Le script ne lance pas Odoo ; il fournit seulement l'autocomplétion et le `venv`.

## Configuration

| Paramètre (`ir.config_parameter`) | Rôle |
|---|---|
| `capsule_house_theme.website_id` | Identifiant du site Capsule House (posé par le module) |
| `capsule_house_theme.domain_live` | Mettre à `1` **uniquement** quand le DNS `capsule-house.fr` pointe réellement sur le site. Sinon le domaine est retiré pour permettre la prévisualisation sur les environnements Odoo.sh |

Réglages côté back-office :

- **Avis** : modération dans le menu dédié (état *publié* pour afficher un avis).
- **Produits, prix, catégories** : gérés comme dans n'importe quel site Odoo (eCommerce).

## Internationalisation

- Langue par défaut : `fr_FR`. L'anglais (`en_US`) est activé automatiquement.
- Les textes des pages sont fournis en FR et EN ; les traductions complémentaires sont dans `i18n/en.po`.
- Pour les menus et enregistrements créés par script, écrire explicitement les deux langues (sans contexte de langue, le français atterrirait dans la colonne anglaise).

## Conventions de travail

- **Jamais de contenu inventé** : textes, coordonnées légales et chiffres proviennent de contenus validés par le client.
- **Toujours scoper au site** (`website_id`) tout ce que le module crée ou lit.
- **Étapes de maintenance idempotentes** et sans écrasement des réglages faits par le client.
- Les réglages à appliquer **une seule fois** utilisent une clé de garde dans `ir.config_parameter`.

## Points d'attention et évolutions

Constats issus de la revue du code, à traiter en priorité :

- **Devis sur mesure** : la route est déclarée deux fois, `crm` n'est pas dans les dépendances alors que le formulaire crée un `crm.lead`, et il n'y a ni validation ni anti-spam.
- **Cron horaire** : il réinitialise des vues personnalisées et republie les produits, ce qui annule des modifications faites à la main dans l'éditeur ou le back-office.
- **Migrations** : une centaine de dossiers quasi identiques ; un seul mécanisme suffirait.
- **Droits sur les avis** : tout utilisateur interne a tous les droits ; restreindre à un groupe éditeur du site.
- **Formulaires publics** (avis, newsletter) : ajouter validation des entrées et protection anti-flood.
- **Tests** : aucun test automatisé pour l'instant.
- **Contenu** : gammes autres que « Capsule » à compléter ; mentions légales, CGV et garanties à faire valider.

Évolutions envisagées :

- **Mode de livraison au checkout** : classique, spécialisée, installation incluse (méthodes de livraison natives Odoo).
