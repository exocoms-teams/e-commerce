# Cam Surveillance — Bibliothèque de composants CSS

> Référence des classes CSS réutilisables du module `cam_surveillance`.
> Fichier CSS source : `cam_surveillance/static/src/css/cam_surveillance.css`
> Page bac à sable : `/cam-sandbox` (auth: user)

---

## 1. Boutons

### `.cam-btn-primary`
Bouton principal plein, couleur orange (`--color-primary`).

| État | Comportement |
|---|---|
| `:hover` | Fond plus foncé, translateY(-2px) |
| `:focus-visible` | Outline orange 3px + offset 3px |
| `:disabled` / `[aria-disabled]` | Opacité 50%, cursor not-allowed |

```html
<a href="/shop" class="cam-btn-primary">Voir nos produits</a>
<button class="cam-btn-primary" disabled>Indisponible</button>
```

### `.cam-btn-secondary`
Bouton secondaire contour orange, fond blanc.

| État | Comportement |
|---|---|
| `:hover` | Fond passe en orange, texte blanc |
| `:focus-visible` | Outline orange 3px + offset 3px |
| `:disabled` / `[aria-disabled]` | Opacité 50%, bordure grise |

```html
<a href="/shop" class="cam-btn-secondary">Voir tous les produits</a>
```

### `.cam-btn-sm`
Bouton compact (small), fond orange. Utilisé dans les cartes produit.

| État | Comportement |
|---|---|
| `:hover` | Fond plus foncé, translateY(-1px) |
| `:focus-visible` | Outline orange 3px + offset 2px |
| `:disabled` / `[aria-disabled]` | Opacité 50% |

```html
<span class="cam-btn-sm">Voir</span>
```

### `.cam-btn-audit`
Modificateur à combiner avec `.cam-btn-secondary` — supprime la bordure.

```html
<a href="/contact" class="cam-btn-secondary cam-btn-audit">Demander un audit</a>
```

---

## 2. Cartes produit

### `.cam-product-card`
Carte produit complète avec image, corps et footer.

**Structure HTML attendue :**
```html
<a href="/shop/1" class="cam-product-card">
    <div class="cam-product-img">
        <img src="..." alt="Nom du produit"/>
    </div>
    <div class="cam-product-body">
        <h3>Nom du produit</h3>
        <div class="cam-stock-status mt-1 mb-2">
            <span class="cam-badge-stock-in">
                <i class="fa fa-box me-1"/>5 en stock
            </span>
        </div>
        <div class="cam-product-footer">
            <span class="cam-product-price">450,00 € HT</span>
            <span class="cam-btn-sm">Voir</span>
        </div>
    </div>
</a>
```

**Sous-classes :**

| Classe | Rôle |
|---|---|
| `.cam-product-img` | Conteneur image (200px de haut) |
| `.cam-product-noimg` | Placeholder si pas d'image |
| `.cam-product-body` | Corps de la carte (padding 20px) |
| `.cam-product-footer` | Footer flex (prix + bouton) |
| `.cam-product-price` | Prix affiché en orange bold |

### `.cam-product-card--related`
Variante compacte pour les blocs "produits associés" et accessoires.
Image à 160px, titre à 1rem. Même structure que la carte standard.

```html
<a href="..." class="cam-product-card cam-product-card--related">
    <!-- même structure interne -->
</a>
```

### `.cam-products-grid`
Grille CSS 4 colonnes pour afficher les cartes. Passe en 1 colonne sous 768px.

```html
<div class="cam-products-grid">
    <!-- cam-product-card × N -->
</div>
```

---

## 3. Badges de stock

### `.cam-badge-stock-in`
Badge "en stock" — fond vert maison (#2ea043), texte blanc.

```html
<span class="cam-badge-stock-in">
    <i class="fa fa-box me-1"/>12 en stock
</span>
```

### `.cam-badge-stock-out`
Badge "rupture" — fond rouge maison (#e53e3e), texte blanc.

```html
<span class="cam-badge-stock-out">Rupture</span>
```

### Variantes

| Classe modificateur | Usage |
|---|---|
| `.cam-badge-stock-in--lg` | Fiche produit (taille plus grande) |
| `.cam-badge-stock-out--lg` | Fiche produit (taille plus grande) |

```html
<span class="cam-badge-stock-in cam-badge-stock-in--lg">
    <i class="fa fa-check-circle me-1"/>12 unités en stock
</span>
```

---

## 4. Badges généraux

### `.cam-badge`
Badge compact pour le footer (fond sombre, texte orange).

```html
<span class="cam-badge">Certifié AXIS</span>
```

### `.cam-hero-badge`
Badge en pilule pour le hero (fond clair, bordure orange).

```html
<div class="cam-hero-badge">Revendeur certifié AXIS</div>
```

---

## 5. Catégories

### `.cam-cat-card`
Carte de catégorie avec bordure-top animée au hover.

### `.cam-cat-featured`
Modificateur pour catégorie mise en avant (fond alt + bordure orange).

### `.cam-cat-grid`
Grille CSS 3 colonnes.

---

## 6. Sections

### `.cam-section-header`
En-tête de section centré (h2 + p). Utiliser systématiquement pour les titres de section.

```html
<div class="cam-section-header">
    <h2>Titre</h2>
    <p>Sous-titre</p>
</div>
```

### `.cam-container`
Conteneur centré max-width 1200px.

---

## 7. Bandeau promotionnel

### `.cam-promo-banner` + `.cam-promo-track`
Bandeau défilant horizontal orange. Se met en pause au hover.

---

## 8. Cartes "Pourquoi nous"

### `.cam-why-card`
Carte info centrée avec ombre. Utilisée dans la grille `.cam-why-grid` (4 colonnes).

---

## 9. Design Tokens

Toutes les variables CSS sont définies dans `:root` en haut de `cam_surveillance.css`.
Utiliser **toujours** les tokens plutôt que des valeurs en dur :

| Token | Valeur | Usage |
|---|---|---|
| `--color-primary` | `#FF6B00` | Couleur orange principale |
| `--color-primary-hover` | `#e55a00` | Hover des boutons |
| `--radius-md` | `8px` | Boutons, cartes secondaires |
| `--radius-lg` | `12px` | Cartes produit |
| `--radius-xl` | `30px` | Badges, pilules |
| `--shadow-md` | `0 4px 15px rgba(...)` | Cartes |
| `--shadow-primary` | `0 4px 15px rgba(255,107,0,0.3)` | Boutons primary |
| `--transition-standard` | `all 0.3s ease` | Toutes les transitions |
