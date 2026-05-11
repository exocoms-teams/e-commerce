# PayCore Website — Module Odoo 19

Module website custom pour PayCore. Conçu pour Odoo 19 / Odoo.sh.  
Design premium inspiré Stripe, Revolut Business, Linear.

---

## Architecture

```
paycore_website/
├── __manifest__.py              # Déclaration du module
├── __init__.py                  # Imports Python
│
├── controllers/
│   ├── __init__.py
│   └── main.py                  # Routes: /, /services, /contact, etc.
│
├── models/
│   └── __init__.py              # Extensible (pas de modèles custom en v1)
│
├── data/
│   └── website_data.xml         # Config website Odoo
│
├── security/
│   └── ir.model.access.csv      # ACL (vide en v1)
│
├── i18n/
│   └── fr.po                    # Traductions françaises
│
├── views/
│   ├── menus.xml                # Menus website
│   ├── templates/
│   │   ├── layout.xml           # Override navbar + footer
│   │   └── components.xml       # Composants réutilisables
│   └── pages/
│       ├── home.xml             # Page d'accueil
│       ├── services.xml         # Page services
│       ├── tpe.xml              # Solutions TPE
│       ├── encaissement.xml     # Logiciels encaissement
│       ├── omnicanal.xml        # Paiement omnicanal + support + about
│       └── contact.xml          # Formulaire contact
│
└── static/
    └── src/
        ├── js/
        │   ├── main.js          # Point d'entrée, init de tous les modules
        │   ├── navbar.js        # Sticky scroll, burger mobile, dropdowns
        │   ├── animations.js    # IntersectionObserver → .is-visible
        │   └── counters.js      # Compteurs animés requestAnimationFrame
        ├── scss/
        │   ├── utils/
        │   │   ├── _variables.scss   # Design tokens
        │   │   ├── _mixins.scss      # Utilitaires SCSS
        │   │   └── _animations.scss  # Keyframes + classes animate
        │   ├── layout/
        │   │   ├── _reset.scss       # Reset scopé .pc-site
        │   │   ├── _base.scss        # Typographie, containers, grilles
        │   │   ├── _navbar.scss      # Navbar glassmorphism sticky
        │   │   ├── _footer.scss      # Footer 4 colonnes dark
        │   │   └── _grid.scss        # Layout helpers
        │   ├── components/
        │   │   ├── _buttons.scss
        │   │   ├── _cards.scss
        │   │   ├── _badges.scss
        │   │   ├── _forms.scss
        │   │   └── _sections.scss
        │   └── pages/
        │       ├── _home.scss
        │       ├── _services.scss
        │       └── _contact.scss
        └── img/
            └── favicon.svg
```

---

## Installation locale (développement)

### Prérequis
- Odoo 19 installé localement (Community ou Enterprise)
- Python 3.10+
- Git

### 1. Cloner / placer le module

```bash
# Dans votre addons path Odoo
cd /path/to/your/odoo/addons
git clone git@github.com:VOTRE_ORG/paycore_website.git
```

Ou si vous avez un repo Odoo.sh dédié :

```bash
cd /path/to/odoo-sh-repo
# Le module doit être à la racine ou dans un sous-dossier déclaré
cp -r paycore_website ./
```

### 2. Redémarrer Odoo avec le module

```bash
python odoo-bin -c odoo.conf -u paycore_website --dev=xml
```

Flag `--dev=xml` → rechargement automatique des templates XML sans restart.

### 3. Activer dans l'interface

1. **Paramètres → Mode développeur** (activer)
2. **Applications → Rechercher** `paycore_website`
3. Cliquer **Installer**

---

## Déploiement Odoo.sh + GitHub

### Structure du repo GitHub

Odoo.sh attend **un repo par projet**. Deux structures possibles :

#### Option A — Repo = projet complet (recommandé Odoo.sh)
```
mon-projet-odoo/          ← racine du repo GitHub
├── paycore_website/      ← votre module custom
├── autre_module/         ← autres modules custom si besoin
└── requirements.txt      ← dépendances Python tierces (si besoin)
```

#### Option B — Repo = module seul
```
paycore_website/          ← racine du repo GitHub = le module
├── __manifest__.py
├── ...
```

> **Odoo.sh détecte automatiquement** les modules par la présence de `__manifest__.py`.

### Étapes de connexion GitHub → Odoo.sh

#### 1. Créer le repo GitHub

```bash
# Depuis la racine de votre projet
git init
git add .
git commit -m "feat: initial paycore_website module"
git branch -M main
git remote add origin git@github.com:VOTRE_ORG/paycore-odoo.git
git push -u origin main
```

#### 2. Connecter sur Odoo.sh

1. Se connecter sur **https://odoo.sh**
2. **Nouveau projet** → choisir **GitHub**
3. Autoriser l'accès OAuth GitHub si pas encore fait
4. Sélectionner votre repo `paycore-odoo`
5. Choisir la branche : `main` → **Production**
6. Odoo.sh clone le repo, détecte les modules et lance un build

#### 3. Workflow CI/CD quotidien

```bash
# Développement normal
git checkout -b feat/nouvelle-section
# ... modifications ...
git add .
git commit -m "feat(home): ajouter section témoignages"
git push origin feat/nouvelle-section
```

→ Odoo.sh crée automatiquement une **branche staging** avec un rebuild  
→ Tester sur l'URL staging fournie par Odoo.sh  
→ Merger sur `main` → rebuild **production** automatique

#### 4. Mise à jour module après push

Odoo.sh exécute automatiquement :
```
odoo --update paycore_website
```

Si besoin de forcer depuis l'interface Odoo.sh :  
**Builds → votre build → Restart with module update**

---

## Variables d'environnement utiles (Odoo.sh)

Dans **Odoo.sh → Paramètres → Variables** :

| Variable | Usage |
|----------|-------|
| `ADMIN_PASSWD` | Mot de passe master Odoo |
| `SMTP_HOST` | Serveur mail pour envoi formulaire contact |
| `SMTP_PORT` | Port SMTP (587 pour TLS) |
| `SMTP_USER` | Compte SMTP |
| `SMTP_PASSWORD` | Mot de passe SMTP |

---

## Développement SCSS

Le SCSS est compilé par Odoo lui-même via son pipeline assets.  
**Pas besoin de Webpack, Vite ou node_modules.**

Pour voir les changements SCSS instantanément :
1. Activer le **mode développeur** dans Odoo
2. **Paramètres → Technique → Assets** → Désactiver le cache
3. Ou : ajouter `?debug=assets` à l'URL

En production, Odoo compile et minifie automatiquement.

---

## Conventions de code

### SCSS
- Tout est scopé sous `.pc-site` pour éviter les conflits Bootstrap/Odoo
- Nommage BEM : `.pc-block__element--modifier`
- Variables dans `_variables.scss`, jamais en dur dans les composants
- Ordre d'import : utils → layout → components → pages

### JavaScript
- Modules ES natifs avec `/** @odoo-module **/`
- Exports nommés (pas de `default`)
- Pas de jQuery (même si disponible via Odoo)
- Chaque fichier = une responsabilité

### XML Odoo
- `t-call` pour les composants réutilisables
- `inherit_id` pour les overrides (jamais écraser les templates core)
- `groups` sur les menus admin uniquement

---

## Checklist avant mise en production

- [ ] Remplacer les textes placeholder par le contenu client final
- [ ] Ajouter les vraies images (og-paycore.png, apple-touch-icon.png)
- [ ] Configurer SMTP dans Odoo.sh pour le formulaire contact
- [ ] Vérifier SEO : meta title/description sur chaque page
- [ ] Tester responsive sur mobile réel (pas seulement DevTools)
- [ ] Activer le cache assets en production
- [ ] Configurer Google Analytics / Matomo via Odoo Website
- [ ] Vérifier les redirections si remplacement d'un site existant

---

## License

Propriétaire — © PayCore. Tous droits réservés.
