/** @odoo-module **/
/**
 * EXOCOMS — Sidebar Filter AJAX
 * Odoo 19 · Filtrage dynamique sans rechargement de page
 *
 * Architecture :
 *   ExoSidebar          — objet singleton, point d'entrée public
 *   ExoSidebarFilter    — classe principale (état, events, AJAX)
 *   ExoAccordion        — gestion des accordéons
 *   ExoCheckboxSync     — synchronisation cases parent ↔ enfants
 *   ExoTags             — affichage des tags actifs
 *   ExoAjax             — appels réseau vers /shop/sidebar/filter
 *   ExoPagination       — rendu et navigation de la pagination
 */

// ─── Constantes ───────────────────────────────────────────────────────────────
const ROUTE      = "/shop/sidebar/filter";
const DEBOUNCE   = 380;   // ms — délai après frappe dans le champ recherche
const PRICE_WAIT = 600;   // ms — délai après saisie de prix

// ─── Utilitaires ──────────────────────────────────────────────────────────────
const qs  = (sel, ctx = document) => ctx.querySelector(sel);
const qsa = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
const stopProp = e => e.stopPropagation();

function debounce(fn, delay) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

function escHtml(str) {
    return String(str).replace(/[&<>"']/g, c =>
        ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
}

// ─── AJAX ─────────────────────────────────────────────────────────────────────
class ExoAjax {
    /**
     * Appelle /shop/sidebar/filter via JSON-RPC (format Odoo).
     * Retourne la Promise de la réponse.
     */
    static async call(params) {
        const resp = await fetch(ROUTE, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({
                jsonrpc: "2.0",
                method:  "call",
                id:      Date.now(),
                params,
            }),
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const json = await resp.json();
        if (json.error) throw new Error(json.error.data?.message || json.error.message);
        return json.result;
    }
}

// ─── Accordéon ────────────────────────────────────────────────────────────────
class ExoAccordion {
    constructor(sidebar) {
        this.sidebar = sidebar;
        this._bindCats();
        this._bindSubcats();
        this._bindKeyboard();
    }

    _bindCats() {
        qsa(".exo-cat-head", this.sidebar).forEach(head => {
            head.addEventListener("click", e => {
                if (e.target.type === "checkbox") return;
                this._toggle(head, qs(`#${head.dataset.subcatsId}`, this.sidebar));
            });
        });
    }

    _bindSubcats() {
        qsa(".exo-subcat-head[data-has-children]", this.sidebar).forEach(head => {
            head.addEventListener("click", e => {
                if (e.target.type === "checkbox") return;
                const children = head.nextElementSibling;
                if (children?.classList.contains("exo-children")) {
                    this._toggle(head, children);
                }
            });
        });
    }

    _toggle(head, panel) {
        const open = head.classList.toggle("open");
        head.setAttribute("aria-expanded", String(open));
        panel?.classList.toggle("open", open);
    }

    _bindKeyboard() {
        qsa(".exo-cat-head, .exo-subcat-head", this.sidebar).forEach(head => {
            head.addEventListener("keydown", e => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    head.click();
                }
            });
        });
    }

    openParentsOf(cb) {
        const subBlock = cb.closest(".exo-subcat-block");
        if (subBlock) {
            const head     = qs(".exo-subcat-head", subBlock);
            const children = qs(".exo-children", subBlock);
            head?.classList.add("open");
            head?.setAttribute("aria-expanded", "true");
            children?.classList.add("open");
        }
        const catBlock = cb.closest(".exo-cat-block");
        if (catBlock) {
            const head   = qs(".exo-cat-head", catBlock);
            const subcats = catBlock.dataset.subcatsId
                ? qs(`#${head?.dataset.subcatsId}`, this.sidebar)
                : null;
            head?.classList.add("open");
            head?.setAttribute("aria-expanded", "true");
            subcats?.classList.add("open");
        }
    }
}

// ─── Synchronisation cases à cocher ──────────────────────────────────────────
class ExoCheckboxSync {
    /**
     * Après un changement sur une case, remonte l'état (coché/indéterminé)
     * vers les ancêtres et redescend vers les enfants si nécessaire.
     */
    static syncDown(cb, checked) {
        const block = cb.closest(".exo-cat-block, .exo-subcat-block");
        if (!block) return;
        qsa("input[type='checkbox']", block).forEach(c => {
            c.checked = checked;
            c.indeterminate = false;
        });
    }

    static syncAncestors(cb) {
        // Niveau 2 → sous-catégorie parente
        const subBlock = cb.closest(".exo-subcat-block");
        if (subBlock) {
            const subCb   = qs(":scope > .exo-subcat-head input[type='checkbox']", subBlock);
            const children = qsa(".exo-child-item input[type='checkbox']", subBlock);
            if (subCb && children.length) {
                const all  = children.every(c => c.checked);
                const some = children.some(c => c.checked);
                subCb.checked      = all;
                subCb.indeterminate = some && !all;
                qs(".exo-subcat-label", subBlock)
                    ?.classList.toggle("checked", some);
            }
        }
        // Niveau 1 → catégorie racine
        const catBlock = cb.closest(".exo-cat-block");
        if (catBlock) {
            const catCb = qs(":scope > .exo-cat-head input[type='checkbox']", catBlock);
            const subs  = qsa(".exo-subcat-head input, .exo-child-item input", catBlock);
            if (catCb && subs.length) {
                const all  = subs.every(c => c.checked);
                const some = subs.some(c => c.checked);
                catCb.checked      = all;
                catCb.indeterminate = some && !all;
            }
        }
    }

    static clearAll(sidebar) {
        qsa("input[type='checkbox']", sidebar).forEach(cb => {
            cb.checked = false;
            cb.indeterminate = false;
        });
        qsa(".exo-subcat-label", sidebar).forEach(l => l.classList.remove("checked"));
    }
}

// ─── Tags actifs ──────────────────────────────────────────────────────────────
class ExoTags {
    constructor(container, onRemove) {
        this.container = container;
        this.onRemove  = onRemove;
    }

    update(sidebar) {
        this.container.innerHTML = "";
        const checked = qsa("input[type='checkbox']:checked", sidebar);
        if (!checked.length) {
            this.container.classList.remove("visible");
            return;
        }
        this.container.classList.add("visible");
        checked.forEach(cb => {
            const label = cb.dataset.label || this._findLabel(cb);
            if (!label) return;
            const btn = document.createElement("button");
            btn.type      = "button";
            btn.className = "exo-tag";
            btn.setAttribute("aria-label", `Supprimer : ${label}`);
            btn.innerHTML = `${escHtml(label)} <i class="fa fa-times" aria-hidden="true"></i>`;
            btn.addEventListener("click", () => this.onRemove(cb));
            this.container.appendChild(btn);
        });
    }

    _findLabel(cb) {
        const parent = cb.closest(".exo-cat-head, .exo-subcat-head, .exo-child-item");
        return (
            qs(".exo-cat-label",    parent)?.textContent.trim() ||
            qs(".exo-subcat-label", parent)?.textContent.trim() ||
            qs("label",             parent)?.textContent.trim() ||
            null
        );
    }
}

// ─── Pagination ───────────────────────────────────────────────────────────────
class ExoPagination {
    constructor(container, onPage) {
        this.container = container;
        this.onPage    = onPage;
    }

    render(current, total) {
        if (!this.container) return;
        if (total <= 1) { this.container.innerHTML = ""; return; }

        const MAX_VISIBLE = 5;
        let start = Math.max(0, current - Math.floor(MAX_VISIBLE / 2));
        let end   = Math.min(total, start + MAX_VISIBLE);
        start     = Math.max(0, end - MAX_VISIBLE);

        let html = "";
        // Précédent
        html += `<button class="exo-page-btn" data-page="${current - 1}"
                         ${current === 0 ? "disabled" : ""}
                         aria-label="Page précédente">
                   <i class="fa fa-chevron-left" aria-hidden="true"></i>
                 </button>`;
        // Première page si hors fenêtre
        if (start > 0) {
            html += `<button class="exo-page-btn" data-page="0">1</button>`;
            if (start > 1) html += `<span class="exo-page-info">…</span>`;
        }
        // Pages visibles
        for (let i = start; i < end; i++) {
            html += `<button class="exo-page-btn ${i === current ? "active" : ""}"
                             data-page="${i}"
                             aria-current="${i === current ? "page" : "false"}">
                       ${i + 1}
                     </button>`;
        }
        // Dernière page si hors fenêtre
        if (end < total) {
            if (end < total - 1) html += `<span class="exo-page-info">…</span>`;
            html += `<button class="exo-page-btn" data-page="${total - 1}">${total}</button>`;
        }
        // Suivant
        html += `<button class="exo-page-btn" data-page="${current + 1}"
                         ${current === total - 1 ? "disabled" : ""}
                         aria-label="Page suivante">
                   <i class="fa fa-chevron-right" aria-hidden="true"></i>
                 </button>`;

        this.container.innerHTML = html;
        this.container.querySelectorAll(".exo-page-btn:not([disabled])").forEach(btn => {
            btn.addEventListener("click", () => this.onPage(parseInt(btn.dataset.page, 10)));
        });
    }
}

// ─── Classe principale ────────────────────────────────────────────────────────
class ExoSidebarFilter {
    constructor(sidebar) {
        this.sidebar      = sidebar;

        // Cible la grille native Odoo (o_wsale_products_list) ou notre wrapper
        this.grid = (
            document.querySelector("#exo-products-grid") ||
            document.querySelector(".o_wsale_products_list") ||
            document.querySelector(".o_wsale_products_grid_wrapper")?.parentElement ||
            null
        );

        // Wrap la grille native dans un div qu'on peut remplacer
        if (this.grid && !this.grid.id) {
            this.grid.id = "exo-products-grid";
        }
        this.countEl      = qs("#exo-result-count",  sidebar);
        this.countText    = qs(".exo-count-text",     sidebar);
        this.spinner      = qs(".exo-spinner",        sidebar);
        this.searchInput  = qs("#exo-search-input",   sidebar);
        this.sortSelect   = qs("#exo-sort-select",    sidebar);
        this.minPrice     = qs("#exo-min-price",      sidebar);
        this.maxPrice     = qs("#exo-max-price",      sidebar);
        this.tagsContainer = qs("#exo-active-tags",   sidebar);

        // Crée ou récupère le conteneur de pagination
        this.paginationEl = qs("#exo-pagination") || (() => {
            const el = document.createElement("div");
            el.id = "exo-pagination";
            this.grid?.parentNode?.insertBefore(el, this.grid.nextSibling);
            return el;
        })();

        this._state = {
            catIds:   this._readActiveCatIds(),
            search:   this.searchInput?.value || "",
            sort:     "",
            minPrice: null,
            maxPrice: null,
            page:     0,
        };

        this._accordion  = new ExoAccordion(sidebar);
        this._tags       = new ExoTags(this.tagsContainer, cb => this._onTagRemove(cb));
        this._pagination = new ExoPagination(this.paginationEl, page => this._goPage(page));

        this._bindCheckboxes();
        this._bindClearAll();
        this._bindSearch();
        this._bindSort();
        this._bindPrice();
        this._tags.update(sidebar);

        // L'accordéon fonctionne toujours, même sans grille AJAX
        // Si des filtres sont déjà actifs (restauration URL), lance une requête
        if (this.grid && (this._state.catIds.length || this._state.search)) {
            this._fetch();
        } else {
            this._showCount(null);
        }
    }

    // ── Lecture état initial depuis l'URL ─────────────────────────────────

    _readActiveCatIds() {
        const param = new URLSearchParams(window.location.search).get("cat_ids") || "";
        return param.split(",").filter(Boolean).map(Number);
    }

    // ── Checkboxes ────────────────────────────────────────────────────────

    _bindCheckboxes() {
        // Niveau 1
        qsa(".exo-cat-head input[type='checkbox']", this.sidebar).forEach(cb => {
            cb.addEventListener("change", e => {
                stopProp(e);
                ExoCheckboxSync.syncDown(cb, cb.checked);
                this._onFilterChange();
            });
            cb.addEventListener("click", stopProp);
        });
        // Niveau 2
        qsa(".exo-subcat-head input[type='checkbox']", this.sidebar).forEach(cb => {
            cb.addEventListener("change", e => {
                stopProp(e);
                ExoCheckboxSync.syncDown(cb, cb.checked);
                ExoCheckboxSync.syncAncestors(cb);
                this._onFilterChange();
            });
            cb.addEventListener("click", stopProp);
        });
        // Niveau 3
        qsa(".exo-child-item input[type='checkbox']", this.sidebar).forEach(cb => {
            cb.addEventListener("change", e => {
                stopProp(e);
                ExoCheckboxSync.syncAncestors(cb);
                this._onFilterChange();
            });
            cb.addEventListener("click", stopProp);
        });
    }

    _onFilterChange() {
        this._state.catIds = qsa("input[type='checkbox']:checked", this.sidebar)
            .map(cb => parseInt(cb.dataset.catId || cb.value, 10))
            .filter(Boolean);
        this._state.page = 0;
        this._tags.update(this.sidebar);
        this._fetch();
    }

    // ── Tag supprimé ──────────────────────────────────────────────────────

    _onTagRemove(cb) {
        cb.checked      = false;
        cb.indeterminate = false;
        ExoCheckboxSync.syncAncestors(cb);
        this._onFilterChange();
    }

    // ── Tout effacer ──────────────────────────────────────────────────────

    _bindClearAll() {
        qs(".exo-clear-all", this.sidebar)?.addEventListener("click", () => {
            ExoCheckboxSync.clearAll(this.sidebar);
            if (this.searchInput) this.searchInput.value = "";
            if (this.sortSelect)  this.sortSelect.value  = "";
            if (this.minPrice)    this.minPrice.value     = "";
            if (this.maxPrice)    this.maxPrice.value     = "";
            this._state = { catIds: [], search: "", sort: "", minPrice: null, maxPrice: null, page: 0 };
            this._tags.update(this.sidebar);
            this._fetch();
        });
    }

    reset() { qs(".exo-clear-all", this.sidebar)?.click(); }

    // ── Recherche ─────────────────────────────────────────────────────────

    _bindSearch() {
        if (!this.searchInput) return;
        const debouncedFetch = debounce(() => {
            this._state.search = this.searchInput.value.trim();
            this._state.page   = 0;
            this._fetch();
        }, DEBOUNCE);
        this.searchInput.addEventListener("input", debouncedFetch);
    }

    // ── Tri ───────────────────────────────────────────────────────────────

    _bindSort() {
        if (!this.sortSelect) return;
        this.sortSelect.addEventListener("change", () => {
            this._state.sort = this.sortSelect.value;
            this._state.page = 0;
            this._fetch();
        });
    }

    // ── Prix ──────────────────────────────────────────────────────────────

    _bindPrice() {
        const debouncedFetch = debounce(() => {
            this._state.minPrice = this.minPrice?.value ? parseFloat(this.minPrice.value) : null;
            this._state.maxPrice = this.maxPrice?.value ? parseFloat(this.maxPrice.value) : null;
            this._state.page     = 0;
            this._fetch();
        }, PRICE_WAIT);

        this.minPrice?.addEventListener("input", debouncedFetch);
        this.maxPrice?.addEventListener("input", debouncedFetch);
    }

    // ── Pagination ────────────────────────────────────────────────────────

    _goPage(page) {
        this._state.page = page;
        this._fetch();
        // Scroll doux vers le haut de la grille
        this.grid?.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // ── Requête AJAX principale ───────────────────────────────────────────

    async _fetch() {
        this._setLoading(true);

        const params = {
            cat_ids:   this._state.catIds,
            page:      this._state.page,
            search:    this._state.search,
            sort:      this._state.sort,
            min_price: this._state.minPrice,
            max_price: this._state.maxPrice,
        };

        try {
            const result = await ExoAjax.call(params);
            this._applyResult(result);
        } catch (err) {
            console.error("[ExoSidebar] Erreur AJAX :", err);
            this._showError();
        } finally {
            this._setLoading(false);
        }
    }

    _applyResult(result) {
        // 1. Mise à jour de la grille produits
        if (this.grid) {
            this.grid.innerHTML = result.products_html || "";
        }

        // 2. Compteur résultats
        this._showCount(result.product_count);

        // 3. Mise à jour des badges de compteurs par catégorie
        if (result.cat_counts) {
            this._updateCatCounts(result.cat_counts);
        }

        // 4. Pagination
        this._pagination.render(result.current_page, result.page_count);

        // 5. Mise à jour de l'URL (sans rechargement)
        this._updateURL();
    }

    // ── Compteurs catégories ──────────────────────────────────────────────

    _updateCatCounts(counts) {
        qsa(".exo-count-badge[data-cat-id]", this.sidebar).forEach(badge => {
            const catId = parseInt(badge.dataset.catId, 10);
            const count = counts[catId] ?? 0;
            badge.textContent = count;
            badge.classList.toggle("zero", count === 0);
        });
    }

    // ── Compteur résultats ────────────────────────────────────────────────

    _showCount(n) {
        if (!this.countEl) return;
        if (n === null) { this.countEl.style.display = "none"; return; }
        this.countEl.style.display = "flex";
        if (this.countText) {
            this.countText.textContent =
                n === 0 ? "Aucun résultat"
              : n === 1 ? "1 produit trouvé"
              : `${n} produits trouvés`;
        }
    }

    // ── Etat chargement ───────────────────────────────────────────────────

    _setLoading(loading) {
        this.grid?.classList.toggle("exo-loading", loading);
        if (this.spinner) this.spinner.style.display = loading ? "inline-block" : "none";
    }

    // ── Erreur réseau ─────────────────────────────────────────────────────

    _showError() {
        if (this.grid) {
            this.grid.innerHTML = `
                <div class="exo-empty-state">
                    <i class="fa fa-exclamation-triangle fa-2x" aria-hidden="true"></i>
                    <p>Une erreur est survenue. Veuillez réessayer.</p>
                </div>`;
        }
        this._showCount(0);
    }

    // ── URL ───────────────────────────────────────────────────────────────

    _updateURL() {
        const url = new URL(window.location.href);
        if (this._state.catIds.length) {
            url.searchParams.set("cat_ids", this._state.catIds.join(","));
        } else {
            url.searchParams.delete("cat_ids");
        }
        if (this._state.search) {
            url.searchParams.set("search", this._state.search);
        } else {
            url.searchParams.delete("search");
        }
        if (this._state.page > 0) {
            url.searchParams.set("page", this._state.page);
        } else {
            url.searchParams.delete("page");
        }
        window.history.replaceState({}, "", url.toString());
    }
}

// ─── Singleton public ─────────────────────────────────────────────────────────
const ExoSidebar = {
    _instance: null,

    init() {
        const sidebar = document.querySelector("#exo-sidebar");
        if (!sidebar || sidebar.dataset.exoInit) return;
        sidebar.dataset.exoInit = "1";
        this._instance = new ExoSidebarFilter(sidebar);
    },

    reset() { this._instance?.reset(); },
};

// Point d'entrée — Odoo 19 SPA
// On tente à DOMContentLoaded, puis au chargement Odoo, puis avec un délai de secours
function _exoTryInit() { ExoSidebar.init(); }

document.addEventListener("DOMContentLoaded", _exoTryInit);
document.addEventListener("o_website_content_loaded", _exoTryInit);
// Filet de sécurité : si le sidebar est injecté tardivement
setTimeout(_exoTryInit, 300);
setTimeout(_exoTryInit, 800);

// Observer les mutations DOM pour détecter l'injection du sidebar
if (typeof MutationObserver !== "undefined") {
    const _exoObserver = new MutationObserver(() => {
        if (document.querySelector("#exo-sidebar:not([data-exo-init])")) {
            _exoTryInit();
        }
    });
    document.addEventListener("DOMContentLoaded", () => {
        _exoObserver.observe(document.body, { childList: true, subtree: true });
        // Arrête l'observation après 10s pour économiser les ressources
        setTimeout(() => _exoObserver.disconnect(), 10000);
    });
}

// Export global pour les boutons inline (exo-empty-state reset)
window.ExoSidebar = ExoSidebar;
