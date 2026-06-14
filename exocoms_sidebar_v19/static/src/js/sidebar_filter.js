/** @odoo-module **/
/**
 * EXOCOMS — Sidebar Filter
 * JavaScript pour Odoo 19
 *
 * Odoo 19 utilise le système de modules ES natif avec @odoo-module.
 * Le chargement est géré par le bundle web.assets_frontend.
 * On n'utilise PAS require() ni odoo.define() (API Odoo < 16).
 *
 * Fonctionnalités :
 *   - Accordéon 3 niveaux (catégorie → sous-cat → enfant)
 *   - Synchronisation cases à cocher (parent ↔ enfants)
 *   - Tags actifs avec suppression individuelle
 *   - Bouton "Tout effacer"
 *   - Bouton "Appliquer" → navigation URL (?cat_ids=...)
 *   - Restauration de l'état depuis l'URL au chargement
 *   - Accessibilité clavier (Enter/Space sur les en-têtes)
 */

// ─── Classe principale ────────────────────────────────────────────────────────

class ExoSidebarFilter {
    /**
     * @param {HTMLElement} el  L'élément <aside class="exo-sidebar">
     */
    constructor(el) {
        this.el = el;
        this._bindAll();
        this._restoreFromURL();
        this._updateTags();
    }

    // ─── Binding global ───────────────────────────────────────────────────

    _bindAll() {
        this._bindCategoryHeads();
        this._bindSubcatHeads();
        this._bindCheckboxes();
        this._bindClearAll();
        this._bindApply();
        this._bindKeyboard();
    }

    // ─── Accordéon niveau 1 ───────────────────────────────────────────────

    _bindCategoryHeads() {
        this.el.querySelectorAll(".exo-cat-head").forEach((head) => {
            head.addEventListener("click", (e) => {
                if (e.target.type === "checkbox") return;
                this._toggleAccordion(head, `#${head.dataset.subcatsId}`);
            });
        });
    }

    // ─── Accordéon niveau 2 ───────────────────────────────────────────────

    _bindSubcatHeads() {
        this.el.querySelectorAll(".exo-subcat-head[data-has-children]").forEach((head) => {
            head.addEventListener("click", (e) => {
                if (e.target.type === "checkbox") return;
                const childrenEl = head.nextElementSibling;
                if (!childrenEl?.classList.contains("exo-children")) return;
                const isOpen = head.classList.contains("open");
                head.classList.toggle("open", !isOpen);
                head.setAttribute("aria-expanded", String(!isOpen));
                childrenEl.classList.toggle("open", !isOpen);
            });
        });
    }

    _toggleAccordion(head, targetSelector) {
        const target = this.el.querySelector(targetSelector);
        const isOpen = head.classList.contains("open");
        head.classList.toggle("open", !isOpen);
        head.setAttribute("aria-expanded", String(!isOpen));
        if (target) target.classList.toggle("open", !isOpen);
    }

    // ─── Cases à cocher ───────────────────────────────────────────────────

    _bindCheckboxes() {
        // Niveau 1 : propagation vers tous les descendants
        this.el.querySelectorAll(".exo-cat-head input[type='checkbox']").forEach((cb) => {
            cb.addEventListener("change", (e) => {
                e.stopPropagation();
                const block = cb.closest(".exo-cat-block");
                block?.querySelectorAll("input[type='checkbox']").forEach((c) => {
                    c.checked = cb.checked;
                    c.indeterminate = false;
                });
                this._updateTags();
            });
            cb.addEventListener("click", (e) => e.stopPropagation());
        });

        // Niveau 2 : propagation vers les enfants + remontée niveau 1
        this.el.querySelectorAll(".exo-subcat-head input[type='checkbox']").forEach((cb) => {
            cb.addEventListener("change", (e) => {
                e.stopPropagation();
                const block = cb.closest(".exo-subcat-block");
                block?.querySelectorAll(".exo-child-item input[type='checkbox']").forEach((c) => {
                    c.checked = cb.checked;
                });
                const label = cb.parentElement?.querySelector(".exo-subcat-label");
                label?.classList.toggle("checked", cb.checked);
                this._syncAncestors(cb);
                this._updateTags();
            });
            cb.addEventListener("click", (e) => e.stopPropagation());
        });

        // Niveau 3 : remontée uniquement
        this.el.querySelectorAll(".exo-child-item input[type='checkbox']").forEach((cb) => {
            cb.addEventListener("change", (e) => {
                e.stopPropagation();
                this._syncAncestors(cb);
                this._updateTags();
            });
            cb.addEventListener("click", (e) => e.stopPropagation());
        });
    }

    /**
     * Remonte l'état coché vers les ancêtres (sous-cat et cat racine).
     * Gère aussi l'état indéterminé (certains enfants cochés, pas tous).
     */
    _syncAncestors(cb) {
        // ── Synchronise la sous-catégorie parente (niveau 2) ──
        const subBlock = cb.closest(".exo-subcat-block");
        if (subBlock) {
            const subCb = subBlock.querySelector(":scope > .exo-subcat-head input[type='checkbox']");
            const children = [...subBlock.querySelectorAll(".exo-child-item input[type='checkbox']")];
            if (subCb && children.length) {
                const all = children.every((c) => c.checked);
                const some = children.some((c) => c.checked);
                subCb.checked = all;
                subCb.indeterminate = some && !all;
                const label = subCb.parentElement?.querySelector(".exo-subcat-label");
                label?.classList.toggle("checked", some);
            }
        }

        // ── Synchronise la catégorie racine (niveau 1) ──
        const catBlock = cb.closest(".exo-cat-block");
        if (catBlock) {
            const catCb = catBlock.querySelector(":scope > .exo-cat-head input[type='checkbox']");
            const subs = [...catBlock.querySelectorAll(".exo-subcat-head input, .exo-child-item input")];
            if (catCb && subs.length) {
                const all = subs.every((c) => c.checked);
                const some = subs.some((c) => c.checked);
                catCb.checked = all;
                catCb.indeterminate = some && !all;
            }
        }
    }

    // ─── Tags actifs ──────────────────────────────────────────────────────

    _updateTags() {
        const container = this.el.querySelector(".exo-active-tags");
        if (!container) return;

        container.innerHTML = "";
        const checked = [...this.el.querySelectorAll("input[type='checkbox']:checked")];

        if (!checked.length) {
            container.classList.remove("visible");
            return;
        }

        container.classList.add("visible");

        checked.forEach((cb) => {
            const labelText = cb.dataset.label || this._findLabel(cb);
            if (!labelText) return;

            const tag = document.createElement("button");
            tag.type = "button";
            tag.className = "exo-tag";
            tag.setAttribute("aria-label", `Supprimer le filtre : ${labelText}`);
            tag.innerHTML = `${this._escapeHtml(labelText)} <i class="fa fa-times" aria-hidden="true"></i>`;
            tag.addEventListener("click", () => {
                cb.checked = false;
                cb.indeterminate = false;
                this._syncAncestors(cb);
                this._updateTags();
            });
            container.appendChild(tag);
        });
    }

    _findLabel(cb) {
        const parent = cb.closest(".exo-cat-head, .exo-subcat-head, .exo-child-item");
        if (!parent) return null;
        return (
            parent.querySelector(".exo-cat-label")?.textContent.trim() ||
            parent.querySelector(".exo-subcat-label")?.textContent.trim() ||
            parent.querySelector("label")?.textContent.trim() ||
            null
        );
    }

    _escapeHtml(str) {
        return str.replace(/[&<>"']/g, (c) =>
            ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
        );
    }

    // ─── Tout effacer ─────────────────────────────────────────────────────

    _bindClearAll() {
        this.el.querySelector(".exo-clear-all")?.addEventListener("click", (e) => {
            e.preventDefault();
            this.el.querySelectorAll("input[type='checkbox']").forEach((cb) => {
                cb.checked = false;
                cb.indeterminate = false;
            });
            this.el.querySelectorAll(".exo-subcat-label").forEach((l) =>
                l.classList.remove("checked")
            );
            this._updateTags();
        });
    }

    // ─── Appliquer → URL (/shop?cat_ids=12,34,56) ────────────────────────

    _bindApply() {
        this.el.querySelector(".exo-apply-btn")?.addEventListener("click", () => {
            const ids = [...this.el.querySelectorAll("input[type='checkbox']:checked")]
                .map((cb) => cb.dataset.catId || cb.value)
                .filter(Boolean);

            const url = new URL(window.location.href);
            if (ids.length) {
                url.searchParams.set("cat_ids", ids.join(","));
            } else {
                url.searchParams.delete("cat_ids");
            }
            url.searchParams.delete("page");   // reset pagination
            window.location.href = url.toString();
        });
    }

    // ─── Restaurer depuis l'URL ───────────────────────────────────────────

    _restoreFromURL() {
        const param = new URLSearchParams(window.location.search).get("cat_ids") || "";
        const activeIds = new Set(param.split(",").filter(Boolean));
        if (!activeIds.size) return;

        this.el.querySelectorAll("input[type='checkbox']").forEach((cb) => {
            const id = cb.dataset.catId || cb.value;
            if (!activeIds.has(id)) return;

            cb.checked = true;
            this._syncAncestors(cb);
            this._openParents(cb);
        });
    }

    _openParents(cb) {
        // Ouvre le bloc sous-catégorie
        const subBlock = cb.closest(".exo-subcat-block");
        if (subBlock) {
            const head = subBlock.querySelector(".exo-subcat-head");
            const children = subBlock.querySelector(".exo-children");
            head?.classList.add("open");
            head?.setAttribute("aria-expanded", "true");
            children?.classList.add("open");
        }
        // Ouvre la catégorie racine
        const catBlock = cb.closest(".exo-cat-block");
        if (catBlock) {
            const head = catBlock.querySelector(".exo-cat-head");
            const subcats = catBlock.querySelector(".exo-subcats");
            head?.classList.add("open");
            head?.setAttribute("aria-expanded", "true");
            subcats?.classList.add("open");
        }
    }

    // ─── Accessibilité clavier ────────────────────────────────────────────

    _bindKeyboard() {
        // Enter / Space ouvrent les accordéons comme un clic
        this.el.querySelectorAll(".exo-cat-head, .exo-subcat-head").forEach((head) => {
            head.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    head.click();
                }
            });
        });
    }
}

// ─── Point d'entrée ───────────────────────────────────────────────────────────
//
// Odoo 19 charge les modules JS après le rendu de la page via son bundle.
// On utilise "load" plutôt que "DOMContentLoaded" pour s'assurer que
// les templates QWeb sont bien dans le DOM.

const initSidebars = () => {
    document.querySelectorAll(".exo-sidebar").forEach((el) => {
        if (!el.dataset.exoInit) {
            el.dataset.exoInit = "1";
            new ExoSidebarFilter(el);
        }
    });
};

// Support SPA Odoo 19 (rechargement partiel via owl router)
document.addEventListener("DOMContentLoaded", initSidebars);
document.addEventListener("o_website_content_loaded", initSidebars);   // hook Odoo 19
