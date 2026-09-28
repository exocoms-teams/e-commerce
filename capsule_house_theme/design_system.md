# Capsule House — Design System de référence

Référence consolidée des couleurs (hex), polices et tailles de texte du module
`capsule_house_theme`, puis vérification de conformité page par page.

**État : conforme.** Audits des 8 CSS + templates XML — toutes les valeurs
en dur ont été corrigées pour passer par les tokens de `variables.css`.

---

## 1. Couleurs — palette officielle (hex)

Source : `static/src/css/variables.css`.

### 1.1 Couleurs principales (7)
| Token | Hex | Usage |
|---|---|---|
| `--ch-white` | `#FFFFFF` | fonds clairs, texte sur sombre |
| `--ch-panel` | `#F6F1E9` | fond panneaux / cartes produit |
| `--ch-ink` | `#1F2421` | texte principal, bandeaux sombres (header/footer) |
| `--ch-amber` | `#F6B26B` | accent : prix, étoiles |
| `--ch-terracotta` | `#C1694F` | accent secondaire : CTA, liens |
| `--ch-fog` | `#7A7168` | texte secondaire |
| `--ch-green` | `#2E7D5B` | badge promo / nouveauté |

### 1.2 Couleurs fonctionnelles (2)
| Token | Hex | Usage |
|---|---|---|
| `--ch-red` | `#B4553F` | alerte (distincte du terracotta CTA), pages Aide |

### 1.3 Dégradés, footer & illustrations (7)
| Token | Hex | Usage |
|---|---|---|
| `--ch-footer-text` | `#8A8177` | texte bas de footer |
| `--ch-footer-text-2` | `#B8AFA2` | texte secondaire footer (taupe) |
| `--ch-salmon` | `#E3A48A` | dégradé hublot produit |
| `--ch-tan-1` | `#EAD9C4` | dégradé logo / illustration (arche pod) |
| `--ch-tan-2` | `#EDE0D0` | dégradé logo / illustration |
| `--ch-bg-soft` | `#FBF6EE` | dégradé subtil fond produit |
| `--ch-highlight` | `#FFF3E0` | reflet clair du hublot |

### 1.4 Nuances dérivées (3)
| Token | Hex | Usage |
|---|---|---|
| `--ch-terracotta-mid` | `#A85640` | hover des liens terracotta |
| `--ch-gray-border` | `#E9E2D4` | bordures fines / séparateurs |
| `--ch-ink-soft` | `#34302A` | 2e teinte du dégradé hero boutique (dérivée de `--ch-ink`) |

### 1.5 Valeurs dérivées en alpha (non-hex, par construction)
`rgba(193, 105, 79, 0.08/0.10/…)` (terracotta) et `rgba(255,255,255,…)` (overlays
sur fond sombre) : dérivées des tokens — cohérentes, laissées telles quelles.

### 1.6 Couleurs restantes hors tokens (état après correctif)
- Aucun hex codé en dur dans les CSS hors `variables.css` (la seule référence
  `#875A7B` dans `shop.css` est un **commentaire** expliquant la couleur native
  Odoo).
- Les **SVG inline** des templates (hero.xml, entreprise_concept.xml,
  entreprise_apropos.xml) utilisent des valeurs **identiques à la palette**
  (`#FFFFFF`, `#EAD9C4`, `#FFF3E0`, `#E3A48A`, `#C1694F`, `#1F2421`) — conformes
  aux hex de référence, sans liaison `var()` (voir §6).

---

## 2. Polices (font-family)

| Famille | Poids chargés | Utilisation |
|---|---|---|
| **Inter** (`var(--font-head)` = `var(--font-body)`) | 400, 500, 600, 700, 800, 900 | tout le texte ; `--font-head` = titres, `--font-body` = corps |
| **FontAwesome** | — | icônes (header/footer, bullets, étoiles) — non typographique |

Chargement : `@import` Google Fonts dans `variables.css` (syntaxe historique sans
`;` dans l'URL — voir correctif commenté en tête du fichier).

Remarques :
- Aucune autre famille utilisée → ✓ une seule famille à 6 graisses.
- `--font-head` et `--font-body` pointent tous deux vers Inter.

---

## 3. Tailles de texte — échelle tokenisée (`--fs-*`)

Toutes les déclarations `font-size` des 7 feuilles (base, homepage, layout, legal,
odoo-integration, pages, shop) utilisent désormais `var(--fs-*)` — **aucune valeur
en dur ne subsiste** (vérifié par grep : `font-size:` non accompagné de `var(` = 0).

### 3.1 Échelle par rôle
| Rôle | Token | Taille | Graisse | Exemple sélecteur |
|---|---|---|---|---|
| Chiffre Avis | `--fs-72` | `72px` | 800 | `.ch-avis-score-big` |
| Hero H1 | `--fs-46` | `46px` (mobile `--fs-32`) | 800 | `.ch-hero-title` |
| Bandeau garantie | `--fs-44` | `44px` | 800 | `.ch-aide-warranty-number` |
| H1 page responsif | `--fs-title-responsive` / `-lg` | `clamp(28→38)` / `clamp(32→48)` | 800 | `.ch-aide-title`, `.ch-avis-hero-title` |
| Hero Entreprise | `--fs-34` | `34px` | 800 | `.ch-entreprise-hero .ch-aide-title` |
| Hero boutique | `--fs-30` | `30px` | 800 | `.ch-shop-hero-title` |
| Chiffres stats / étoiles picker | `--fs-28` / `--fs-20` | `28px` / `20px` | 800 | `.ch-entreprise-stat-num`, `.ch-avis-star-btn` |
| H2 section | `--fs-26` | `26px` (mobile `--fs-21`) | 800 | `.ch-section-title` |
| H2 bloc | `--fs-24` / `--fs-22` | `24px` / `22px` | 700–800 | `.ch-usage-title`, `.ch-newsletter-title` |
| H3 carte / chef de colonne | `--fs-19` / `--fs-17` | `19px` / `17px` | 700 | `.ch-legal-body h2`, `.ch-product-card-price` |
| Titre de carte courante | `--fs-15-5` / `--fs-18` | `15.5px` / `18px` | 700 | `.ch-aide-card-title`, `.ch-gamme-section-title` |
| Sous-titre | `--fs-16` | `16px` | 600 | hero sous-titre, `.ch-usage-name` |
| Corps (base) | `--fs-15` | `15px` | 400 | `body` |
| Corps cartes / boutons / liens | `--fs-14` / `--fs-14-5` | `14px` / `14.5px` | 400–700 | `.ch-btn`, `.ch-aide-sidebar-link` |
| Navigation / footer | `--fs-13-5` | `13.5px` | 500–600 | header, liens footer |
| Texte secondaire | `--fs-13` | `13px` | 400–600 | libellés, badges texte |
| Meta | `--fs-12-5` | `12.5px` | 400–600 | dates, compteurs, réassurance |
| Meta petit | `--fs-12` / `--fs-11-5` / `--fs-11` | `12px` / `11.5px` / `11px` | 400–700 | colonnes footer, tableaux, étoiles |
| Micro / médailles | `--fs-10` / `--fs-10-5` | `10px` / `10.5px` | 700 | badges pager, badges gamme |

### 3.2 Tokens définis dans `variables.css`
`--fs-10` · `--fs-10-5` · `--fs-11` · `--fs-11-5` · `--fs-12` · `--fs-12-5` ·
`--fs-13` · `--fs-13-5` · `--fs-14` · `--fs-14-5` · `--fs-15` · `--fs-15-5` ·
`--fs-16` · `--fs-17` · `--fs-18` · `--fs-19` · `--fs-20` · `--fs-21` · `--fs-22` ·
`--fs-24` · `--fs-26` · `--fs-28` · `--fs-30` · `--fs-32` · `--fs-34` · `--fs-44` ·
`--fs-46` · `--fs-72` + `--fs-title-responsive` · `--fs-title-responsive-lg` ·
`--fs-title-responsive-md` (clamp).

---

## 4. Vérification de conformité — page par page

Légende : ✓ conforme.

| Page (template) | CSS chargé | Résultat |
|---|---|---|
| **Accueil** (`home.xml` + partials) | `homepage.css` | ✓ couleurs = tokens · ✓ tailles = `var(--fs-*)` |
| **Header / Footer / Layout** (globaux) | `layout.css` | ✓ tokens (`#000000` → `--ch-ink`) · ✓ tailles tokenisées (overlays footer : rgba blanc, dérivés) |
| **Boutique — listing / produit** (`shop.xml`) | `shop.css` | ✓ dégradé hero = `--ch-ink`/`--ch-ink-soft` · ✓ tailles tokenisées |
| **Nos gammes** (`nos_gammes.xml`) | `pages.css` | ✓ badges = rgba terracotta/vert à 10 % · ✓ tailles tokenisées |
| **Entreprise — Concept** (`entreprise_concept.xml`) | `pages.css` | ✓ inline `font-size:22px` supprimé → classe `.ch-aide-title-md` · ✓ tailles tokenisées |
| **Entreprise — À propos** (`entreprise_apropos.xml`) | `pages.css` | ✓ inline `font-size:24px` supprimé → classe `.ch-aide-title-lg` · ✓ tailles tokenisées |
| **Aide — Garantie** (`aide_garantie.xml`) | `pages.css` | ✓ inline `font-size:17px` supprimé → classe `.ch-aide-h2` · ✓ alertes `--ch-red` |
| **Aide — FAQ / Retours / Livraison** | `pages.css` | ✓ tokens + alertes |
| **Avis** (`avis.xml`) | `pages.css` | ✓ `--ch-amber` étoiles · ✓ `--fs-72` score |
| **Pages légales** (`mentions_legales`, `confidentialite`, `cgv`) | `legal.css` | ✓ 100 % tokens |
| **Intégration Odoo / formulaires** | `odoo-integration.css` | ✓ alert-info = `--ch-fog` · ✓ tailles tokenisées |

### 4.1 Écarts corrigés (récapitulatif)
1. **Couleurs en dur (8)** : 5× `#000000` skeleton → `--ch-ink` ; `#34302A` →
   `--ch-ink-soft` ; `#3B82F6` alert-info → `--ch-fog` ; `#E1F0E8` / `#F7E9E3`
   badges gamme → `rgba(…)` des tokens vert/terracotta.
2. **Tailles en dur (~180 occurrences)** : toutes remplacées par `var(--fs-*)`,
   et échelle complète (dont display 72/44/34/28 px et demi-points 10.5/11.5/
   14.5/15.5) consignée dans `variables.css`.
3. **Inline styles (10)** : `font-size` 22/24/17px supprimés des templates,
   reportés dans des classes CSS `.ch-aide-title-md` / `-lg` / `.ch-aide-h2`.

### 4.2 Reste volontairement hors tokens (documenté)
- `rgba(255,255,255,…)` et `rgba(193,105,79,…)` : variantes alpha des tokens,
  non hex.
- SVG inline : valeurs = hex de la palette (conformes), liaison `var()` non
  appliquée (voir §6).
- `FontAwesome` : famille d'icônes, non typographique.

---

## 5. Conformité finale
Sur toutes les pages : polices = **Inter uniquement** ; couleurs texte/fond =
tokens `--ch-*` ; tailles = tokens `--fs-*`. **Aucune divergence de la liste de
référence** sur ces trois critères.

---

## 6. Recommandations optionnelles (non bloquantes)
1. Relier les SVG inline aux tokens via des classes CSS (`fill: var(--ch…)`,
   `stop-color: var(--ch…)`) — purement structurel, les valeurs sont déjà
   conformes.
2. Tokeniser les alphas (`--ch-terracotta-10`, `--ch-white-08`, …) si l'on veut
   100 % de la couleur (y compris alpha) dans les tokens.