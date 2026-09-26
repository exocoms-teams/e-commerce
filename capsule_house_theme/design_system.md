# Capsule House — Design System de référence

Référence consolidée des couleurs (hex), polices et tailles de texte du module
`capsule_house_theme`, puis vérification de conformité page par page.

**État : conforme.** Audits des 8 CSS + templates XML — toutes les valeurs
en dur ont été corrigées pour passer par les tokens de `variables.css`.

**v19.0.1.0.106 — hiérarchie H1/H2/H3/paragraphe.** Les titres et les paragraphes
de contenu ne passent plus par des hauteurs propres à chaque page mais par
**4 tokens sémantiques uniques** (`--fs-h1`, `--fs-h2`, `--fs-h3`, `--fs-body`),
définis en `clamp()` pour que le titre principal reste bien visible en haut sur
mobile comme sur grand écran. Voir §3 et §4.1.

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

## 3. Tailles de texte — échelle sémantique (`--fs-h1` / `--fs-h2` / `--fs-h3` / `--fs-body`)

Toutes les déclarations `font-size` des 7 feuilles (base, homepage, layout, legal,
odoo-integration, pages, shop) utilisent un `var(--fs-*)` — **aucune valeur en dur
ne subsiste** (vérifié : `font-size:` suivi d'une valeur littérale = 0).

### 3.1 Échelle sémantique — SOURCE UNIQUE (v19.0.1.0.106)

Quatre tokens, jamais modifiés page par page. Tout titre ou paragraphe de
contenu passe par eux, quelle que soit la page.

| Rôle | Token | Valeur | Plancher / plafond | Graisse |
|---|---|---|---|---|
| **H1 — titre principal de page** | `--fs-h1` | `clamp(32px, 4.2vw, 46px)` | 32px mobile → 46px desktop | 800 |
| **H2 — titre de section** | `--fs-h2` | `clamp(23px, 2.8vw, 30px)` | 23px mobile → 30px desktop | 700–800 |
| **H3 — titre de carte / sous-bloc** | `--fs-h3` | `var(--fs-19)` = 19px | fixe | 700–800 |
| **Paragraphe** | `--fs-body` | `var(--fs-15)` = 15px | fixe | 400 |

Le `clamp()` sur H1/H2 est la clé du « titre principal toujours bien visible
en haut » : un H1 fixe à 46px déborde sur téléphone, un H1 fixe à 30px devient
discret sur grand écran. Le `clamp()` garantit les deux bornes **sans media
query** — d'où la suppression des 3 anciens media queries qui figeaient une
valeur différente de celle du reste du site.

`base.css` porte en plus les règles élément `h1`/`h2`/`h3`/`p` sur ces mêmes
tokens (filet de sécurité pour les pages Odoo natives et le template de devis),
`margin-top: 0` sur `h1`, et `text-wrap: balance` + `overflow-wrap: break-word`
sur les trois niveaux de titre.

### 3.2 Tokens `--fs-title-responsive*` — dépréciés

`--fs-title-responsive` (28→38), `-lg` (32→48) et `-md` (24→32) donnaient à
**chaque page une taille de titre différente**. Remplacés par `--fs-h1/h2/h3`
en v19.0.1.0.106. Conservés (backward-compat) mais **référencés par aucune
feuille ni aucun template**.

### 3.3 Échelle d'interface (`--fs-*` restants)

Réservée à l'interface et aux micro-typographies — **jamais** à un titre de
contenu ni à un paragraphe.

| Rôle | Token | Taille | Exemple sélecteur |
|---|---|---|---|
| Chiffre Avis | `--fs-72` | `72px` | `.ch-avis-score-big` |
| Bandeau garantie | `--fs-44` | `44px` | `.ch-aide-warranty-number` |
| Chiffres stats / étoiles picker | `--fs-28` / `--fs-20` | `28px` / `20px` | `.ch-entreprise-stat-num`, `.ch-avis-star-btn` |
| Prix produit | `--fs-17` | `17px` | `.ch-product-card-price` |
| Sous-titre | `--fs-16` | `16px` | `.ch-hero-subtitle`, `.ch-gamme-card-icon` |
| Corps (base) | `--fs-15` | `15px` | (aliasé par `--fs-body`) |
| Corps cartes / boutons / liens | `--fs-14` / `--fs-14-5` | `14px` / `14.5px` | `.ch-btn`, `.ch-aide-sidebar-link` |
| Navigation / footer | `--fs-13-5` | `13.5px` | header, liens footer |
| Texte secondaire | `--fs-13` | `13px` | libellés, badges texte |
| Meta | `--fs-12-5` | `12.5px` | dates, compteurs, réassurance |
| Meta petit | `--fs-12` / `--fs-11-5` / `--fs-11` | `12px` / `11.5px` / `11px` | colonnes footer, tableaux, étoiles |
| Micro / médailles | `--fs-10` / `--fs-10-5` | `10px` / `10.5px` | badges pager, badges gamme |

### 3.4 Tokens définis dans `variables.css`
`--fs-10` · `--fs-10-5` · `--fs-11` · `--fs-11-5` · `--fs-12` · `--fs-12-5` ·
`--fs-13` · `--fs-13-5` · `--fs-14` · `--fs-14-5` · `--fs-15` · `--fs-15-5` ·
`--fs-16` · `--fs-17` · `--fs-18` · `--fs-19` · `--fs-20` · `--fs-21` · `--fs-22` ·
`--fs-24` · `--fs-26` · `--fs-28` · `--fs-30` · `--fs-32` · `--fs-34` · `--fs-44` ·
`--fs-46` · `--fs-72` + les 4 tokens sémantiques `--fs-h1` / `--fs-h2` /
`--fs-h3` / `--fs-body` + les 3 tokens dépréciés `--fs-title-responsive*`.

---

## 4. Vérification de conformité — page par page

Légende : ✓ conforme. La colonne « H1 » indique le token appliqué au titre
principal de la page, « H2 » / « H3 » ceux des sections et sous-blocs.

| Page (template) | CSS chargé | H1 | H2 | H3 / corps | Résultat |
|---|---|---|---|---|---|
| **Accueil** (`home.xml` + partials) | `homepage.css` | `--fs-h1` | `--fs-h2` | `--fs-h3` / `--fs-body` | ✓ |
| **Boutique — listing** (`shop.xml`) | `shop.css` | `--fs-h1` | — | `--fs-body` | ✓ |
| **Header / Footer / Layout** (globaux) | `layout.css` | — | — | `--fs-h3` / `--fs-body` | ✓ tokens |
| **Nos gammes** — détail (`nos_gammes.xml`) | `pages.css` | `--fs-h1` | `--fs-h2` | `--fs-h3` / `--fs-body` | ✓ |
| **Entreprise — Concept** (`entreprise_concept.xml`) | `pages.css` | `--fs-h1` | `--fs-h2` | `--fs-h3` | ✓ |
| **Entreprise — À propos** (`entreprise_apropos.xml`) | `pages.css` | `--fs-h1` | `--fs-h2` | `--fs-h3` | ✓ |
| **Aide — Garantie / FAQ / Retours / Livraison** | `pages.css` | `--fs-h1` | `--fs-h2` | `--fs-h3` / `--fs-body` | ✓ |
| **Avis** (`avis.xml`) | `pages.css` | `--fs-h1` | `--fs-h2` | `--fs-h3` / `--fs-body` | ✓ `--fs-72` score, `--ch-amber` étoiles |
| **Pages légales** (`mentions_legales`, `cgv`, `confidentialite`) | `legal.css` | `--fs-h1` | `--fs-h2` | `--fs-body` | ✓ |
| **Intégration Odoo / formulaires / portail / checkout** | `odoo-integration.css` | inherited | inherited | `--fs-h3` | ✓ |
| **Devis** (`devis_template.xml`) | (base) | inherited | inherited | inherited | ✓ via `base.css` |

Les pages **Odoo natives** non couvertes par une page du thème (`/contactus`,
fiche produit, panier, checkout, `/my/*`) n'ont pas de template ici : elles
récupèrent l'échelle par les règles élément `h1`/`h2`/`h3`/`p` de `base.css`.

### 4.1 Écarts corrigés en 19.0.1.0.106 — hiérarchie des titres

Chaque page avait sa propre hauteur de titre. Écarts unifiés :

| Rôle | Avant (par page) | Après |
|---|---|---|
| **H1** | 46px accueil · 48px avis · 34px entreprise · 30px boutique · 38px aide/gammes/légales (plancher 28) | `--fs-h1` partout |
| **H2** | 32px avis · 24px section & usages · 24px/22px entreprise · 22px gammes · 19px légal · 18px sections gamme | `--fs-h2` partout |
| **H3** | 22px footer & succès avis · 16px nom de gamme · 15.5px aide · 14.5px performances | `--fs-h3` partout |
| **Paragraphe** | 15px / 16px / 14.5px selon la page | `--fs-body` partout |

Détail des changements :
- `.ch-shop-hero-title` 30px → `--fs-h1` (c'était le H1 le plus petit du site).
- `.ch-avis-hero-title` `clamp(32→48)` → `--fs-h1` (c'était le H1 le plus grand).
- `.ch-entreprise-hero .ch-aide-title` `--fs-34` → suppression de l'override.
- `.ch-gamme-section-title` 18px → `--fs-h2` (une section de page ne peut pas
  être plus petite que le H2 d'une page Aide).
- `.ch-legal-body h2` 19px → `--fs-h2` (liseré terracotta conservé).
- `.ch-aide-title-lg` (24px) / `.ch-aide-title-md` (22px) / `.ch-aide-h2` (17px) :
  les trois modificateurs ne sont plus que des alias de `--fs-h2` — ils
  subsistent dans les templates mais ne portent plus de hauteur propre.
- Titres de carte alignés sur `--fs-h3` : `.ch-aide-card-title`,
  `.ch-aide-timeline-title`, `.ch-aide-coverage-title`, `.ch-usage-name`,
  `.ch-gamme-card-name`, `.ch-gamme-format-name`, `.ch-gamme-perf-name`,
  `.ch-newsletter-title`, `.ch-avis-success-title`.
- 3 media queries de titre supprimées (`.ch-section-title` 992px,
  `.ch-hero-title` 768px, `.ch-legal-body h2` 640px) : le `clamp()` de
  `--fs-h1`/`--fs-h2` fait déjà ce travail, et ces valeurs divergeaient
  de celles appliquées sur le reste du site.
- `base.css` : `h1`/`h2`/`h3`/`p` câblés sur les 4 tokens, `margin-top: 0`
  sur `h1`, `text-wrap: balance` + `overflow-wrap: break-word` sur les titres.
- `.checkout_step_title` / `.card-title` (`odoo-integration.css`) : taille
  explicite en `--fs-h3` au lieu d'hériter du tag choisi par le template natif.
- `p { font-size: var(--fs-body) }` ajouté : un `<p>` sans classe (paragraphes
  du Website Builder) ne peut plus hériter d'une taille divergente.

### 4.2 Reste volontairement hors tokens (documenté)
- `rgba(255,255,255,…)` et `rgba(193,105,79,…)` : variantes alpha des tokens,
  non hex.
- SVG inline : valeurs = hex de la palette (conformes), liaison `var()` non
  appliquée (voir §6).
- `FontAwesome` : famille d'icônes, non typographique.
- `--fs-44` (bandeau garantie « 10 ans ») et `--fs-72` (score avis) : chiffres
  décoratifs, hors hiérarchie de titres.
- `.ch-aide-callout-title` (15.5px) : libellé d'encart d'alerte, pas un titre
  de section — le passer à 19px ferait déborder les phrases longues qui le
  composent.
- `--fs-30` / `--fs-34` / `--fs-26` / `--fs-21` : plus référencés par le thème,
  conservés dans `variables.css` pour compatibilité.

---

## 5. Conformité finale
Sur toutes les pages : polices = **Inter uniquement** ; couleurs texte/fond =
tokens `--ch-*` ; **titres et paragraphes = les 4 tokens sémantiques
`--fs-h1`/`--fs-h2`/`--fs-h3`/`--fs-body`** ; reste de la typo = tokens
`--fs-*` d'interface. **Aucune divergence sur ces critères** — le H1 est le même
sur les 11 pages du thème et sur les pages Odoo natives.

---

## 6. Recommandations optionnelles (non bloquantes)
1. Relier les SVG inline aux tokens via des classes CSS (`fill: var(--ch…)`,
   `stop-color: var(--ch…)`) — purement structurel, les valeurs sont déjà
   conformes.
2. Tokeniser les alphas (`--ch-terracotta-10`, `--ch-white-08`, …) si l'on veut
   100 % de la couleur (y compris alpha) dans les tokens.