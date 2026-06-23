/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

/**
 * Sidebar de filtres e-commerce EXOCOMS (Modèle 1 - Cartes).
 * Framework d'interactions publiques natif Odoo 19 (remplace publicWidget).
 */
export class ExocomsSidebar extends Interaction {
    static selector = ".s_exocoms_sidebar";

    get dynamicContent() {
        return {
            "[data-toggle-cat]": { "t-on-click.stop": this.onToggleCategory.bind(this) },
            ".exo_facet_head":   { "t-on-click":       this.onToggleFacet.bind(this) },
            ".exo_cat_cb":       { "t-on-change":       this.onFilterChange.bind(this) },
            ".exo_brand_cb":     { "t-on-change":       this.onFilterChange.bind(this) },
            ".exo_sort":         { "t-on-change":       this.onFilterChange.bind(this) },
            ".exo_search_input": { "t-on-input":        this.onSearchInput.bind(this) },
            ".exo_range":        { "t-on-input":        this.onPriceInput.bind(this) },
            ".exo_reset":        { "t-on-click":        this.onReset.bind(this) },
            ".exo_chip_remove":  { "t-on-click":        this.onRemoveChip.bind(this) },
            ".exo_cmp_cb":       { "t-on-change":       this.onToggleCompare.bind(this) },
            ".exo_cmp_go":       { "t-on-click":        this.onOpenCompare.bind(this) },
            ".exo_cmp_remove":   { "t-on-click":        this.onRemoveCompare.bind(this) },
            ".exo_cmp_clear":    { "t-on-click":        this.onClearCompare.bind(this) },
            ".exo_modal_close":  { "t-on-click":        this.onCloseModal.bind(this) },
            ".exo_modal":        { "t-on-click":        this.onModalBackdrop.bind(this) },
            ".exo_add_cart":     { "t-on-click":        this.onAddToCart.bind(this) },
            ".exo_page_prev":    { "t-on-click":        this.onPagePrev.bind(this) },
            ".exo_page_next":    { "t-on-click":        this.onPageNext.bind(this) },
            ".exo_page_num":     { "t-on-click":        this.onPageNum.bind(this) },
        };
    }

    setup() {
        this.root = this.el;
        this.ppg = parseInt(this.root.dataset.exoPpg || "24", 10);
        this.searchTimer = null;
        this.page = 1;
        this.pageCount = 1;
        this.compare = [];      // ids de templates sélectionnés
        this.cmpInfo = {};      // id -> {name, img}
        // Désactivation possible depuis le Website Builder (classe posée par l'option)
        this.compareEnabled = !this.root.classList.contains("o_exo_compare_off");

        const priceCard = this.root.querySelector(".exo_price_card");
        this.priceMin = parseInt(priceCard?.dataset.min || "0", 10);
        this.priceMax = parseInt(priceCard?.dataset.max || "2000", 10);
        this.curMin = this.priceMin;
        this.curMax = this.priceMax;

        this._updatePriceFill();
        this._refreshCount();
        // Applique le nb de produits/page et rafraîchit la grille au chargement
        this._refresh(true);
    }

    // ---------------- Repli / dépli ----------------
    onToggleCategory(ev) {
        ev.stopPropagation();
        const id = ev.currentTarget.dataset.toggleCat;
        const cat = this.root.querySelector(`.exo_cat[data-cat-id="${id}"]`);
        if (cat) { cat.classList.toggle("exo_open"); return; }
        const leaf = ev.currentTarget.closest(".exo_leaf");
        if (leaf) leaf.classList.toggle("exo_open");
    }

    onToggleFacet(ev) {
        ev.currentTarget.closest(".exo_facet").classList.toggle("exo_open");
    }

    // ---------------- Filtres ----------------
    onSearchInput() {
        clearTimeout(this.searchTimer);
        this.searchTimer = setTimeout(() => { this.page = 1; this._refresh(); }, 350);
    }

    onPriceInput(ev) {
        const minEl = this.root.querySelector(".exo_range_min");
        const maxEl = this.root.querySelector(".exo_range_max");
        let lo = parseInt(minEl.value, 10);
        let hi = parseInt(maxEl.value, 10);
        const step = 50;
        if (ev.currentTarget.classList.contains("exo_range_min")) {
            if (lo > hi - step) { lo = hi - step; minEl.value = lo; }
        } else if (hi < lo + step) { hi = lo + step; maxEl.value = hi; }
        this.curMin = lo;
        this.curMax = hi;
        this.root.querySelector(".exo_pmin_lbl").textContent = lo + "€";
        this.root.querySelector(".exo_pmax_lbl").textContent = hi + "€";
        this._updatePriceFill();
        clearTimeout(this.searchTimer);
        this.searchTimer = setTimeout(() => { this.page = 1; this._refresh(); }, 250);
    }

    onFilterChange() { this.page = 1; this._refresh(); }

    onReset() {
        this.root.querySelectorAll(".exo_cat_cb, .exo_brand_cb")
            .forEach((cb) => (cb.checked = false));
        const minEl = this.root.querySelector(".exo_range_min");
        const maxEl = this.root.querySelector(".exo_range_max");
        if (minEl) { minEl.value = this.priceMin; this.curMin = this.priceMin; }
        if (maxEl) { maxEl.value = this.priceMax; this.curMax = this.priceMax; }
        const s = this.root.querySelector(".exo_search_input");
        if (s) s.value = "";
        const sort = this.root.querySelector(".exo_sort");
        if (sort) sort.value = "name asc";
        this.root.querySelector(".exo_pmin_lbl").textContent = this.priceMin + "€";
        this.root.querySelector(".exo_pmax_lbl").textContent = this.priceMax + "€";
        this._updatePriceFill();
        this.page = 1;
        this._refresh();
    }

    onRemoveChip(ev) {
        const { catId, brandId, kind } = ev.currentTarget.dataset;
        if (kind === "price") { this.onReset(); return; }
        if (catId) {
            const cb = this.root.querySelector(`.exo_cat_cb[data-category-id="${catId}"]`);
            if (cb) cb.checked = false;
        }
        if (brandId) {
            const cb = this.root.querySelector(`.exo_brand_cb[data-brand-id="${brandId}"]`);
            if (cb) cb.checked = false;
        }
        this.page = 1;
        this._refresh();
    }

    // ---------------- Rafraîchissement AJAX ----------------
    async _refresh(silent = false) {
        const categoryIds = [...this.root.querySelectorAll(".exo_cat_cb:checked")]
            .map((cb) => parseInt(cb.dataset.categoryId, 10));
        const brandIds = [...this.root.querySelectorAll(".exo_brand_cb:checked")]
            .map((cb) => parseInt(cb.dataset.brandId, 10));
        const search = this.root.querySelector(".exo_search_input")?.value || "";
        const sort = this.root.querySelector(".exo_sort")?.value || "name asc";
        const ppg = parseInt(this.root.dataset.exoPpg || "24", 10);

        const wrap = this.root.querySelector(".exo_products");
        if (!silent) wrap.classList.add("exo_loading");

        const res = await this.waitFor(rpc("/exocoms/sidebar/filter", {
            category_ids: categoryIds,
            brand_ids: brandIds,
            price_min: this.curMin,
            price_max: this.curMax,
            search, sort, ppg, page: this.page,
        }));

        wrap.innerHTML = res.html;
        wrap.classList.remove("exo_loading");
        this.page = res.page;
        this.pageCount = res.page_count;
        this.root.querySelector(".exo_count_n").textContent = res.count;
        this._renderChips(categoryIds, brandIds);
        this._renderPagination(res.page, res.page_count);
        this._syncCompareUI();
    }

    _refreshCount() {
        const n = this.root.querySelectorAll(".exo_products .exo_prod").length;
        const el = this.root.querySelector(".exo_count_n");
        if (el) el.textContent = n;
    }

    _labelOf(cb) {
        return cb.closest(".exo_check")?.querySelector(".exo_leaf_name")?.textContent || "";
    }

    _renderChips(categoryIds, brandIds) {
        const box = this.root.querySelector(".exo_active_filters");
        const chips = [];
        categoryIds.forEach((id) => {
            const cb = this.root.querySelector(`.exo_cat_cb[data-category-id="${id}"]`);
            chips.push(`<span class="exo_chip">${this._labelOf(cb)}` +
                `<i class="fa fa-times exo_chip_remove" data-cat-id="${id}"></i></span>`);
        });
        brandIds.forEach((id) => {
            const cb = this.root.querySelector(`.exo_brand_cb[data-brand-id="${id}"]`);
            chips.push(`<span class="exo_chip">${this._labelOf(cb)}` +
                `<i class="fa fa-times exo_chip_remove" data-brand-id="${id}"></i></span>`);
        });
        if (this.curMin > this.priceMin || this.curMax < this.priceMax) {
            chips.push(`<span class="exo_chip">${this.curMin}€ – ${this.curMax}€` +
                `<i class="fa fa-times exo_chip_remove" data-kind="price"></i></span>`);
        }
        box.innerHTML = chips.length ? chips.join("")
            : `<span class="exo_active_empty">Aucun filtre actif</span>`;
    }

    _updatePriceFill() {
        const fill = this.root.querySelector(".exo_slider_fill");
        if (!fill) return;
        const span = this.priceMax - this.priceMin || 1;
        const lo = ((this.curMin - this.priceMin) / span) * 100;
        const hi = ((this.curMax - this.priceMin) / span) * 100;
        fill.style.left = lo + "%";
        fill.style.width = (hi - lo) + "%";
    }

    // ---------------- Pagination ----------------
    _pageWindow(page, pageCount) {
        const wanted = new Set([1, pageCount, page, page - 1, page + 1]);
        const valid = [...wanted].filter((p) => p >= 1 && p <= pageCount)
            .sort((a, b) => a - b);
        const out = [];
        let prev = 0;
        valid.forEach((p) => {
            if (p - prev > 1) out.push("…");
            out.push(p);
            prev = p;
        });
        return out;
    }

    _renderPagination(page, pageCount) {
        const box = this.root.querySelector(".exo_pagination");
        if (!box) return;
        if (pageCount <= 1) { box.innerHTML = ""; return; }
        const nums = this._pageWindow(page, pageCount).map((n) =>
            n === "…"
                ? `<span class="exo_page_gap">…</span>`
                : `<button type="button" class="exo_page_num${n === page ? " active" : ""}" data-page="${n}">${n}</button>`
        ).join("");
        box.innerHTML =
            `<div class="exo_pager">` +
            `<button type="button" class="exo_page_prev"${page <= 1 ? " disabled" : ""}>` +
            `<i class="fa fa-chevron-left"></i> Précédent</button>` +
            `<div class="exo_pages">${nums}</div>` +
            `<button type="button" class="exo_page_next"${page >= pageCount ? " disabled" : ""}>` +
            `Suivant <i class="fa fa-chevron-right"></i></button>` +
            `</div>`;
    }

    _gotoPage(p) {
        const target = Math.min(Math.max(1, p), this.pageCount);
        if (target === this.page) return;
        this.page = target;
        this._refresh();
        this.root.querySelector(".exo_toolbar")
            ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    onPagePrev() { this._gotoPage(this.page - 1); }
    onPageNext() { this._gotoPage(this.page + 1); }
    onPageNum(ev) { this._gotoPage(parseInt(ev.currentTarget.dataset.page, 10)); }

    // ---------------- Comparaison ----------------
    onToggleCompare(ev) {
        if (!this.compareEnabled) return;
        const cb = ev.currentTarget;
        const id = parseInt(cb.dataset.productId, 10);
        const card = cb.closest(".exo_prod");
        const k = this.compare.indexOf(id);
        if (k >= 0) {
            this.compare.splice(k, 1);
            delete this.cmpInfo[id];
            cb.checked = false;
            card?.classList.remove("exo_cmp_on");
        } else {
            if (this.compare.length >= 4) { cb.checked = false; return; }
            this.compare.push(id);
            this.cmpInfo[id] = {
                name: card?.querySelector(".exo_prod_name")?.textContent.trim() || "",
                img: card?.querySelector(".exo_prod_img img")?.getAttribute("src") || "",
            };
            cb.checked = true;
            card?.classList.add("exo_cmp_on");
        }
        this._renderTray();
    }

    _renderTray() {
        const tray = this.root.querySelector(".exo_compare_tray");
        if (!this.compare.length) { tray.innerHTML = ""; return; }
        const thumbs = this.compare.map((id) => {
            const info = this.cmpInfo[id] || {};
            return `<div class="exo_cmp_thumb" title="${info.name || ""}">` +
                (info.img ? `<img src="${info.img}" alt=""/>` : "") +
                `<i class="fa fa-times exo_cmp_remove" data-product-id="${id}"></i></div>`;
        }).join("");
        tray.innerHTML =
            `<div class="exo_card exo_cmpbar">` +
            `<span class="exo_cmpbar_lbl">Comparer · ${this.compare.length}/4</span>` +
            `<div class="exo_cmp_thumbs">${thumbs}</div>` +
            `<button type="button" class="exo_cmp_go btn"${this.compare.length < 2 ? " disabled" : ""}>Comparer</button>` +
            `<button type="button" class="exo_cmp_clear btn">Vider</button></div>`;
    }

    onRemoveCompare(ev) {
        const id = parseInt(ev.currentTarget.dataset.productId, 10);
        const k = this.compare.indexOf(id);
        if (k >= 0) this.compare.splice(k, 1);
        delete this.cmpInfo[id];
        const cb = this.root.querySelector(`.exo_cmp_cb[data-product-id="${id}"]`);
        if (cb) { cb.checked = false; cb.closest(".exo_prod")?.classList.remove("exo_cmp_on"); }
        this._renderTray();
    }

    onClearCompare() {
        this.compare = [];
        this.cmpInfo = {};
        this.root.querySelectorAll(".exo_cmp_cb").forEach((cb) => {
            cb.checked = false;
            cb.closest(".exo_prod")?.classList.remove("exo_cmp_on");
        });
        this._renderTray();
    }

    _syncCompareUI() {
        this.compare.forEach((id) => {
            const cb = this.root.querySelector(`.exo_cmp_cb[data-product-id="${id}"]`);
            if (cb) { cb.checked = true; cb.closest(".exo_prod")?.classList.add("exo_cmp_on"); }
        });
    }

    async onOpenCompare() {
        if (!this.compareEnabled || this.compare.length < 2) return;
        const res = await this.waitFor(rpc("/exocoms/sidebar/compare", {
            product_ids: this.compare,
        }));
        const host = this.root.querySelector(".exo_modal_host");
        host.innerHTML =
            `<div class="exo_modal"><div class="exo_modal_panel">` +
            `<div class="exo_modal_head"><span class="exo_modal_title">Comparaison · ${this.compare.length} produits</span>` +
            `<button type="button" class="exo_modal_close btn">&times;</button></div>` +
            `<div class="exo_modal_body">${res.html}</div></div></div>`;
    }

    onCloseModal() {
        const host = this.root.querySelector(".exo_modal_host");
        if (host) host.innerHTML = "";
    }

    onModalBackdrop(ev) {
        if (ev.target.classList.contains("exo_modal")) this.onCloseModal();
    }

    // ---------------- Panier ----------------
    async onAddToCart(ev) {
        const btn = ev.currentTarget;
        const productId = parseInt(btn.dataset.productId, 10);
        if (!productId) return;
        btn.disabled = true;
        try {
            await this.waitFor(rpc("/shop/cart/update_json", {
                product_id: productId, add_qty: 1, display: false,
            }));
            this._toast("Produit ajouté au panier");
        } catch (e) {
            this._toast("Impossible d'ajouter le produit", true);
        } finally {
            btn.disabled = false;
        }
    }

    _toast(message, isError) {
        const t = document.createElement("div");
        t.className = "exo_toast" + (isError ? " exo_toast_err" : "");
        t.textContent = message;
        this.root.appendChild(t);
        this.registerCleanup(() => t.remove());
        setTimeout(() => t.classList.add("exo_toast_show"), 10);
        setTimeout(() => {
            t.classList.remove("exo_toast_show");
            setTimeout(() => t.remove(), 300);
        }, 2200);
    }
}

registry
    .category("public.interactions")
    .add("exocoms_sidebar_cards.sidebar", ExocomsSidebar);
