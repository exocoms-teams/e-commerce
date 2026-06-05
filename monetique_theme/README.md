# monetique_theme — Guide de déploiement Odoo.sh

## Récapitulatif du module

| Fichier / Dossier | Rôle |
|---|---|
| `__manifest__.py` | Déclaration du module, dépendances (`website`, `website_sale`, `mail`) |
| `__init__.py` | Import controllers + models |
| `controllers/main.py` | Routes : `/`, `/solutions`, `/a-propos`, `/contact`, `/rappel` |
| `views/layout_templates.xml` | Header global (topbar + nav + footer) via `inherit_id="website.layout"` |
| `views/homepage_templates.xml` | Page d'accueil reconstruite |
| `views/pages_templates.xml` | Contact, À propos, Solutions, page succès |
| `views/shop_templates.xml` | Intégration `/shop` (breadcrumb uniquement, e-commerce intact) |
| `data/website_data.xml` | Menus Odoo (Solutions, Terminaux, Tarifs, À propos, Contact) |
| `static/src/css/variables.css` | Design system : couleurs `#0D47A1`, Poppins/Roboto, tokens |
| `static/src/css/layout.css` | Topbar fixe, header, nav dropdowns, footer 5 colonnes |
| `static/src/css/base.css` | Reset, boutons, utilitaires globaux |
| `static/src/css/homepage.css` | Hero, solutions grid, produits, stats, trust logos |
| `static/src/css/pages.css` | Contact, À propos, Tarifs, Garanties |
| `static/src/css/shop.css` | Harmonisation visuelle website_sale |
| `static/src/js/main.js` | Menu burger mobile, nav active, modal rappel, scroll reveal |
| `static/src/img/` | Dossier vide — y déposer vos images |

---

## ÉTAPE 1 — Placer le module dans le repo Git Odoo.sh

### Structure attendue du repo

```
votre-repo-odoosh/
├── monetique_theme/          ← module à placer ici
│   ├── __manifest__.py
│   ├── __init__.py
│   ├── controllers/
│   ├── models/
│   ├── views/
│   ├── static/
│   ├── data/
│   └── security/
└── README.md
```

### Commandes

```bash
# 1. Cloner votre repo Odoo.sh
git clone git@github.com:VOTRE-ORG/VOTRE-REPO.git
cd VOTRE-REPO

# 2. Extraire le ZIP et copier le module
unzip monetique_theme_v2.zip
cp -r monetique_theme/ ./

# 3. Vérifier la structure
ls -la monetique_theme/

# 4. Ajouter au repo
git add monetique_theme/
git status   # vérifier que tous les fichiers sont trackés
```

---

## ÉTAPE 2 — Push sur Odoo.sh

```bash
# Commit
git commit -m "feat: add monetique_theme — frontend complet monetiques.fr"

# Push sur la branche de staging
git push origin staging
# ou production
git push origin main
```

Odoo.sh détecte automatiquement le push et redémarre le serveur. Attendez que le build soit vert dans le dashboard Odoo.sh avant de continuer.

---

## ÉTAPE 3 — Installer le module dans Odoo

### Via l'interface (recommandé)

1. Ouvrir votre instance Odoo
2. **Paramètres** → activer le **Mode développeur** (debug)
3. Aller dans **Applications** (menu principal)
4. Cliquer **Mettre à jour la liste des applications**
5. Rechercher `monétique` ou `monetique_theme`
6. Cliquer **Installer**

### Via le shell Odoo.sh

```bash
# Dans le shell de votre branche Odoo.sh
python odoo-bin -d NOM_DE_VOTRE_DB --install=monetique_theme --stop-after-init

# Mise à jour (après modification)
python odoo-bin -d NOM_DE_VOTRE_DB -u monetique_theme --stop-after-init
```

---

## ÉTAPE 4 — Vérifications post-installation

### Pages à tester obligatoirement

| URL | Ce qu'on doit voir |
|---|---|
| `/` | Homepage reconstruite : hero, solutions, produits, stats |
| `/shop` | Boutique Odoo **inchangée**, avec header bleu ajouté en haut |
| `/shop/cart` | Panier Odoo fonctionnel |
| `/shop/checkout` | Checkout Odoo fonctionnel |
| `/my/orders` | Commandes client Odoo |
| `/solutions` | Page solutions |
| `/a-propos` | Page à propos |
| `/contact` | Formulaire de contact |
| `/web/login` | Login Odoo standard |

### Checklist e-commerce

- [ ] `/shop` affiche les produits existants
- [ ] Les catégories de produits sont visibles
- [ ] Le bouton "Ajouter au panier" fonctionne
- [ ] Le badge panier dans le header affiche la quantité
- [ ] Le checkout complet fonctionne (livraison, paiement)
- [ ] Les commandes apparaissent dans `/my/orders`
- [ ] Les produits sont bien dans l'admin Odoo

### Checklist navigation

- [ ] Topbar bleue visible avec téléphone et email
- [ ] Logo MONÉTIQUES cliquable → redirige vers `/`
- [ ] Menu horizontal avec dropdowns au survol
- [ ] Bouton "Être rappelé" ouvre la modale
- [ ] Menu burger sur mobile
- [ ] Footer 5 colonnes avec liens et réseaux sociaux

---

## ÉTAPE 5 — Ajouter vos images

Le module est livré sans images pour que vous puissiez intégrer les vôtres.

### Emplacement

Toutes les images vont dans :
```
monetique_theme/static/src/img/
```

### Fichiers recommandés

| Nom suggéré | Utilisation | Dimensions recommandées |
|---|---|---|
| `hero-tpe.png` | Image du terminal dans le hero homepage | 800×600 px |
| `sol-terminaux.jpg` | Card "Terminaux de paiement" | 600×338 px (16:9) |
| `sol-mobile.jpg` | Card "Paiement mobile" | 600×338 px |
| `sol-enligne.jpg` | Card "Paiement en ligne" | 600×338 px |
| `sol-support.jpg` | Card "Services & support" | 600×338 px |
| `about-team.jpg` | Photo équipe page À propos | 800×600 px |
| `logo-*.png` | Logos clients (section "Ils nous font confiance") | hauteur 40px |

### Comment activer une image

Dans `views/homepage_templates.xml`, chaque zone image contient un commentaire :

```xml
<!-- INSTRUCTION : Remplacez ce bloc par votre image.
     <img src="/monetique_theme/static/src/img/hero-tpe.png"
          alt="Terminal de paiement professionnel"/>
-->
<div class="mq-hero-img-placeholder">...</div>
```

**Pour activer :**
1. Déposez votre image dans `static/src/img/`
2. Supprimez le `<div class="mq-...-placeholder">...</div>`
3. Décommentez la balise `<img>` correspondante
4. Faites un `git commit` + `git push`
5. Mettez à jour le module dans Odoo : **Applications** → **Mettre à jour**

---

## ÉTAPE 6 — Personnalisation

### Changer le numéro de téléphone

Dans `views/layout_templates.xml`, cherchez et remplacez :
```xml
href="tel:+33184800222">01 84 80 02 22
```

Et dans `views/pages_templates.xml` (page contact), même chose.

### Changer l'email de contact

Dans `controllers/main.py` :
```python
'email_to': request.website.email or 'contact@monetiques.fr',
```
→ Remplacez `contact@monetiques.fr` par votre email.

Ou directement dans Odoo : **Paramètres** → **Site web** → **Email**.

### Changer l'adresse

Dans `views/pages_templates.xml`, cherchez :
```xml
12 rue de la Paix<br/>75002 Paris
```

### Modifier les couleurs

Dans `static/src/css/variables.css` :
```css
:root {
    --mq-blue:       #0D47A1;   /* Bleu principal */
    --mq-blue-light: #1976D2;   /* Bleu clair */
    --mq-blue-pale:  #E3F2FD;   /* Fond bleu très clair */
}
```

---

## ÉTAPE 7 — Mise à jour du module après modifications

```bash
# 1. Modifier les fichiers localement
# 2. Commit + push
git add -A
git commit -m "fix: mise à jour du thème"
git push origin staging

# 3. Dans Odoo (mode développeur) :
# Paramètres → Applications → monetique_theme → Mettre à jour
# OU via shell :
python odoo-bin -d NOM_DB -u monetique_theme --stop-after-init
```

---

## Dépannage fréquent

### La homepage affiche encore l'ancienne page cassée

Le controller `/` de `website.layout` prend priorité. Pour forcer le vôtre :
1. Aller dans **Site web** (backend) → **Pages**
2. Trouver la page `/` ou `Home`
3. La **dépublier** ou la **supprimer**
4. Votre controller `monetique_theme.homepage` prend alors le relais

### Le module n'apparaît pas dans la liste des applications

```bash
# Vérifier que le dossier est bien dans le path addons
# Dans odoo.conf, chercher : addons_path
# Votre repo doit être dans ce path
```

### Erreur XML au démarrage

```bash
# Vérifier la syntaxe :
python3 -c "import xml.etree.ElementTree as ET; ET.parse('views/layout_templates.xml')"
```

### Le `/shop` ne charge plus après installation

C'est que `shop_templates.xml` a un conflit d'héritage. Solution rapide :
1. Retirer `'views/shop_templates.xml'` du `data` dans `__manifest__.py`
2. Mettre à jour le module
3. Le `/shop` Odoo sera entièrement intact, sans header custom

### La police Poppins ne se charge pas

Vérifier la connexion Internet de votre serveur Odoo.sh. Si le serveur est derrière un proxy, ajouter les polices en local dans `static/src/css/variables.css` :
```css
/* Remplacer le @import Google Fonts par des fonts locales */
/* Télécharger Poppins sur fonts.google.com et les mettre dans static/src/fonts/ */
```

---

## Architecture technique résumée

```
Requête /          → controller MonetiqueWebsite.homepage()
                   → template monetique_theme.homepage
                   → hérite website.layout (topbar + header + footer)

Requête /shop      → controller Odoo website_sale (inchangé)
                   → template website_sale.products
                   → hérite website.layout (même topbar + header + footer)
                   → + injection breadcrumb via shop_templates.xml

Requête /contact   → controller MonetiqueWebsite.contact()
                   → template monetique_theme.page_contact

POST /contact/send → controller MonetiqueWebsite.contact_send()
                   → envoi mail.mail Odoo
                   → redirect vers page_contact_success
```

Le e-commerce Odoo (`website_sale`) est **entièrement préservé**. Le module `monetique_theme` n'en remplace aucune fonctionnalité — il ajoute seulement le thème visuel par-dessus via l'héritage de `website.layout`.
