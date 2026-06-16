/** @odoo-module **/
/**
 * EXOCOMS – Filtre Sidebar Modèle D
 * sidebar.js  |  Odoo 19
 *
 * Odoo 19 : module ES chargé via web.assets_frontend.
 * Pas d'import Odoo nécessaire : on utilise fetch natif + vanilla JS.
 * Le CSRF token est lu depuis le cookie odoo_csrf_token (inchangé v19).
 *
 * Architecture 3 niveaux :
 *   G1 — Groupe service   (icône colorée + accordéon)
 *   G2 — Sous-catégorie   (point coloré + accordéon)
 *   G3 — Item feuille     (checkbox → filtre AJAX)
 */

(function () {
    "use strict";

    /* ============================================================
       GARDE : n'exécuter que si la sidebar est présente
    ============================================================ */
    if (!document.getElementById("exo-sidebar")) return;

    /* ============================================================
       GARDE : détecter les instances dupliquées sur la page
       Ce widget utilise des id HTML fixes lus via getElementById.
       Si le snippet est glissé plusieurs fois sur la même page (ou
       coexiste avec la page /shop intégrée), seule la première
       instance trouvée dans le DOM sera fonctionnelle. On avertit
       clairement plutôt que de planter silencieusement.
    ============================================================ */
    (function warnIfDuplicateInstances() {
        const trueDuplicates = document.querySelectorAll(
            ".s_exo_filter_sidebar, .exo-page"
        );
        if (trueDuplicates.length > 1) {
            console.warn(
                "[ExoFilter] " + trueDuplicates.length + " instances du widget " +
                "filtre sidebar détectées sur cette page. Ce widget ne supporte " +
                "qu'une seule instance par page (id HTML fixes). Seule la " +
                "première sera fonctionnelle ; les autres resteront inertes."
            );
        }
    }());

    /* ============================================================
       ÉTAT GLOBAL
    ============================================================ */
    const S = {
        catIds:      new Set(),
        attrib:      [],
        priceMin:    null,
        priceMax:    null,
        priceAbsMin: 0,
        priceAbsMax: 1000,
        search:      "",
        order:       "name asc",
        page:        0,
    };

    /* ============================================================
       UTILITAIRES
    ============================================================ */
    function debounce(fn, ms) {
        let t;
        return function () {
            const args = arguments;
            clearTimeout(t);
            t = setTimeout(function () { fn.apply(null, args); }, ms);
        };
    }

    function fmt(v) {
        return Math.round(v).toLocaleString("fr-FR") + "\u202f\u20ac";
    }

    function getCsrf() {
        // Odoo 19 : token dans le cookie odoo_csrf_token
        const m = document.cookie.match(/(?:^|;\s*)odoo_csrf_token=([^;]+)/);
        return m ? decodeURIComponent(m[1]) : "";
    }

    async function rpc(route, params) {
        try {
            const res = await fetch(route, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrf(),
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method:  "call",
                    id:      Date.now(),
                    params:  params || {},
                }),
            });
            const data = await res.json();
            if (data.error) {
                console.error("[ExoFilter] RPC error:", data.error);
                return null;
            }
            return data.result;
        } catch (e) {
            console.error("[ExoFilter] fetch error:", e);
            return null;
        }
    }

    function byId(id) {
        return document.getElementById(id);
    }

    /* ============================================================
       ICÔNES DE SERVICE (FontAwesome 4, inclus dans Odoo website)
    ============================================================ */
    const SVC_MAP = [
        { keys: ["informatique", "ordinateur", "pc", "laptop", "serveur", "materiel"],
          fa: "fa-laptop",      cls: "exo-svc-icon--info", sub: "Matériel · Logiciels · Maintenance" },
        { keys: ["monetique", "paiement", "tpe", "caisse", "terminal", "encaissement"],
          fa: "fa-credit-card", cls: "exo-svc-icon--pay",  sub: "TPE · Caisses · Lecteurs" },
        { keys: ["telecom", "telephonie", "mobile", "telephone", "dect"],
          fa: "fa-phone",       cls: "exo-svc-icon--tel",  sub: "Mobiles · Fixes · DECT" },
        { keys: ["reseau", "wifi", "switch", "borne", "routeur", "tv"],
          fa: "fa-wifi",        cls: "exo-svc-icon--net",  sub: "Bornes WiFi · Switches · TV" },
        { keys: ["video", "surveillance", "camera", "nvr", "dvr"],
          fa: "fa-video-camera",cls: "exo-svc-icon--vid",  sub: "Caméras · NVR · Câbles" },
        { keys: ["signaletique", "affichage", "ecran", "display", "player"],
          fa: "fa-television",  cls: "exo-svc-icon--sig",  sub: "Écrans · Media players" },
        { keys: ["distribut", "vending", "automat"],
          fa: "fa-coffee",      cls: "exo-svc-icon--dist", sub: "Distributeurs connectés" },
    ];

    function getSvcMeta(name) {
        // Normalise : accents supprimés, minuscules
        const k = (name || "").toLowerCase()
            .normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        for (let i = 0; i < SVC_MAP.length; i++) {
            const entry = SVC_MAP[i];
            for (let j = 0; j < entry.keys.length; j++) {
                if (k.indexOf(entry.keys[j]) !== -1) return entry;
            }
        }
        return { fa: "fa-folder-o", cls: "exo-svc-icon--info", sub: "" };
    }

    /* ============================================================
       RENDU G1 — Groupes service
    ============================================================ */
    function renderCategories(tree) {
        const container = byId("exo-services-container");
        if (!container) return;

        if (!tree || !tree.length) {
            container.innerHTML =
                '<p style="font-size:12px;color:#888;padding:8px 4px">Aucune catégorie.</p>';
            return;
        }

        container.innerHTML = "";

        tree.forEach(function (svc) {
            const meta  = getSvcMeta(svc.name);
            const g1Id  = "exo-g1-" + svc.id;
            const g1El  = document.createElement("div");
            g1El.className = "exo-g1";

            /* Tête G1 */
            const head1 = document.createElement("button");
            head1.type = "button";
            head1.className = "exo-g1__head exo-g1__head--open";
            head1.setAttribute("aria-expanded", "true");
            head1.setAttribute("aria-controls", g1Id);
            head1.innerHTML =
                '<span class="exo-svc-icon ' + meta.cls + '" aria-hidden="true">' +
                    '<i class="fa ' + meta.fa + '"></i>' +
                '</span>' +
                '<span class="exo-g1__label">' + escHtml(svc.name) +
                    (meta.sub ? '<span class="exo-g1__sublabel">' + meta.sub + '</span>' : '') +
                '</span>' +
                '<i class="fa fa-chevron-right exo-g1__chev" aria-hidden="true"></i>';
            g1El.appendChild(head1);

            /* Corps G1 */
            const body1 = document.createElement("div");
            body1.className = "exo-g1__body exo-g1__body--open";
            body1.id = g1Id;

            if (svc.children && svc.children.length) {
                /* ── G2 : Sous-catégories ── */
                svc.children.forEach(function (sub) {
                    const g2Id  = "exo-g2-" + sub.id;
                    const g2El  = document.createElement("div");
                    g2El.className = "exo-g2";

                    if (sub.children && sub.children.length) {
                        /* Tête G2 avec accordéon */
                        const head2 = document.createElement("button");
                        head2.type = "button";
                        head2.className = "exo-g2__head";
                        head2.setAttribute("aria-expanded", "false");
                        head2.setAttribute("aria-controls", g2Id);
                        head2.innerHTML =
                            '<span class="exo-g2__dot" aria-hidden="true"></span>' +
                            '<span class="exo-g2__label">' + escHtml(sub.name) + '</span>' +
                            '<i class="fa fa-chevron-right exo-g2__chev" aria-hidden="true"></i>';
                        g2El.appendChild(head2);

                        /* Corps G2 */
                        const body2 = document.createElement("div");
                        body2.className = "exo-g2__body";
                        body2.id = g2Id;

                        /* ── G3 : Items feuilles ── */
                        const inner = document.createElement("div");
                        inner.className = "exo-g3__inner";

                        sub.children.forEach(function (item) {
                            const lbl = document.createElement("label");
                            lbl.className = "exo-item";
                            const cb = document.createElement("input");
                            cb.type = "checkbox";
                            cb.className = "exo-cb";
                            cb.dataset.catId   = item.id;
                            cb.dataset.catName = item.name;
                            cb.dataset.parent  = sub.name;
                            cb.dataset.service = svc.name;
                            const span = document.createElement("span");
                            span.className = "exo-item__label";
                            span.textContent = item.name;
                            lbl.appendChild(cb);
                            lbl.appendChild(span);
                            inner.appendChild(lbl);
                        });

                        body2.appendChild(inner);
                        g2El.appendChild(body2);

                        head2.addEventListener("click", function () {
                            toggleG2(head2, body2);
                        });

                    } else {
                        /* G2 sans enfants = item feuille direct */
                        const lbl = document.createElement("label");
                        lbl.className = "exo-item exo-g2-leaf";
                        const cb = document.createElement("input");
                        cb.type = "checkbox";
                        cb.className = "exo-cb";
                        cb.dataset.catId   = sub.id;
                        cb.dataset.catName = sub.name;
                        cb.dataset.service = svc.name;
                        const dot = document.createElement("span");
                        dot.className = "exo-g2__dot";
                        dot.setAttribute("aria-hidden", "true");
                        const span = document.createElement("span");
                        span.className = "exo-g2__label";
                        span.textContent = sub.name;
                        lbl.appendChild(cb);
                        lbl.appendChild(dot);
                        lbl.appendChild(span);
                        g2El.appendChild(lbl);
                    }

                    body1.appendChild(g2El);
                });

            } else {
                /* G1 sans enfants = item feuille direct */
                const cb = document.createElement("input");
                cb.type = "checkbox";
                cb.className = "exo-cb";
                cb.dataset.catId   = svc.id;
                cb.dataset.catName = svc.name;
                cb.dataset.service = svc.name;
                cb.style.marginRight = "6px";
                head1.insertBefore(cb, head1.firstChild);
            }

            head1.addEventListener("click", function (e) {
                if (e.target.classList.contains("exo-cb") ||
                    e.target.closest("input")) return;
                toggleG1(head1, body1);
            });

            g1El.appendChild(body1);
            container.appendChild(g1El);
        });

        /* Événements checkboxes */
        container.querySelectorAll(".exo-cb").forEach(function (cb) {
            cb.addEventListener("change", function () {
                const id = parseInt(cb.dataset.catId, 10);
                if (cb.checked) { S.catIds.add(id); }
                else            { S.catIds.delete(id); }
                S.page = 0;
                fetchProducts();
                renderTags();
            });
        });

        /* Restaurer depuis URL */
        if (S.catIds.size) {
            container.querySelectorAll(".exo-cb").forEach(function (cb) {
                if (S.catIds.has(parseInt(cb.dataset.catId, 10))) {
                    cb.checked = true;
                    const g2Body = cb.closest(".exo-g2__body");
                    if (g2Body) {
                        const g2Head = g2Body.previousElementSibling;
                        if (g2Head) {
                            g2Body.classList.add("exo-g2__body--open");
                            g2Head.classList.add("exo-g2__head--open");
                            g2Head.setAttribute("aria-expanded", "true");
                        }
                    }
                }
            });
        }
    }

    function toggleG1(head, body) {
        const open = body.classList.toggle("exo-g1__body--open");
        head.classList.toggle("exo-g1__head--open", open);
        head.setAttribute("aria-expanded", String(open));
    }

    function toggleG2(head, body) {
        const open = body.classList.toggle("exo-g2__body--open");
        head.classList.toggle("exo-g2__head--open", open);
        head.setAttribute("aria-expanded", String(open));
    }

    /* Sécurité XSS minimale pour les noms injectés en innerHTML */
    function escHtml(s) {
        return (s || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    /* ============================================================
       RENDU ATTRIBUTS
    ============================================================ */
    function renderAttributes(attrs) {
        const container = byId("exo-attrs-container");
        if (!container || !attrs || !attrs.length) return;
        container.innerHTML = "";

        attrs.forEach(function (attr) {
            const bodyId = "exo-attr-body-" + attr.id;
            const sec = document.createElement("div");
            sec.className = "exo-g1 exo-attr-section";

            const head = document.createElement("button");
            head.type = "button";
            head.className = "exo-g1__head";
            head.setAttribute("aria-expanded", "false");
            head.setAttribute("aria-controls", bodyId);
            head.innerHTML =
                '<span class="exo-svc-icon exo-svc-icon--info" aria-hidden="true">' +
                    '<i class="fa fa-tags"></i>' +
                '</span>' +
                '<span class="exo-g1__label">' + escHtml(attr.name) + '</span>' +
                '<i class="fa fa-chevron-right exo-g1__chev" aria-hidden="true"></i>';
            sec.appendChild(head);

            const body = document.createElement("div");
            body.className = "exo-g1__body";
            body.id = bodyId;

            const inner = document.createElement("div");
            inner.className = "exo-g3__inner";

            attr.values.forEach(function (v) {
                const lbl = document.createElement("label");
                lbl.className = "exo-item";
                const cb = document.createElement("input");
                cb.type = "checkbox";
                cb.className = "exo-cb exo-attr-cb";
                cb.dataset.attrId    = attr.id;
                cb.dataset.valueId   = v.id;
                cb.dataset.attrName  = attr.name;
                cb.dataset.valueName = v.name;
                const span = document.createElement("span");
                span.className = "exo-item__label";
                span.textContent = v.name;
                lbl.appendChild(cb);
                lbl.appendChild(span);
                inner.appendChild(lbl);
            });

            body.appendChild(inner);
            sec.appendChild(body);
            container.appendChild(sec);

            head.addEventListener("click", function () { toggleG1(head, body); });

            inner.querySelectorAll(".exo-attr-cb").forEach(function (cb) {
                cb.addEventListener("change", function () {
                    const pair = [parseInt(cb.dataset.attrId, 10),
                                  parseInt(cb.dataset.valueId, 10)];
                    if (cb.checked) {
                        S.attrib.push(pair);
                    } else {
                        S.attrib = S.attrib.filter(function (p) {
                            return !(p[0] === pair[0] && p[1] === pair[1]);
                        });
                    }
                    S.page = 0;
                    fetchProducts();
                    renderTags();
                });
            });
        });
    }

    /* ============================================================
       SLIDER DOUBLE PRIX
    ============================================================ */
    /* Référence partagée pour reset depuis renderTags */
    let _sliderLoEl = null;
    let _sliderHiEl = null;

    function initSlider() {
        const loEl    = byId("exo-range-lo");
        const hiEl    = byId("exo-range-hi");
        const fill    = byId("exo-range-fill");
        const loLabel = byId("exo-price-lo");
        const hiLabel = byId("exo-price-hi");
        const current = byId("exo-price-current");
        const tickLo  = byId("exo-tick-lo");
        const tickMid = byId("exo-tick-mid");
        const tickHi  = byId("exo-tick-hi");
        if (!loEl || !hiEl) return;

        _sliderLoEl = loEl;
        _sliderHiEl = hiEl;

        function applyBounds(absMin, absMax) {
            const range = absMax - absMin;
            const step  = Math.max(1, Math.round(range / 200));
            loEl.min = absMin; loEl.max = absMax; loEl.step = step;
            hiEl.min = absMin; hiEl.max = absMax; hiEl.step = step;
            loEl.value = absMin;
            hiEl.value = absMax;
            if (tickLo)  tickLo.textContent  = fmt(absMin);
            if (tickMid) tickMid.textContent = fmt(absMin + range / 2);
            if (tickHi)  tickHi.textContent  = fmt(absMax);
        }

        function updateFill() {
            const absMin = parseFloat(loEl.min);
            const absMax = parseFloat(loEl.max);
            const lo     = parseFloat(loEl.value);
            const hi     = parseFloat(hiEl.value);
            const range  = absMax - absMin || 1;
            const pLo    = ((lo - absMin) / range) * 100;
            const pHi    = ((hi - absMin) / range) * 100;
            if (fill) {
                fill.style.left  = pLo + "%";
                fill.style.width = (pHi - pLo) + "%";
            }
            if (loLabel)  loLabel.textContent  = fmt(lo);
            if (hiLabel)  hiLabel.textContent  = fmt(hi);
            if (current)  current.textContent  = fmt(lo) + " \u2013 " + fmt(hi);
        }

        const debouncedSlider = debounce(function () {
            const absMin = parseFloat(loEl.min);
            const absMax = parseFloat(loEl.max);
            const lo     = parseFloat(loEl.value);
            const hi     = parseFloat(hiEl.value);
            S.priceMin = lo > absMin ? lo : null;
            S.priceMax = hi < absMax ? hi : null;
            S.page = 0;
            fetchProducts();
            renderTags();
        }, 350);

        loEl.addEventListener("input", function () {
            if (parseFloat(loEl.value) > parseFloat(hiEl.value)) {
                loEl.value = hiEl.value;
            }
            updateFill();
            debouncedSlider();
        });

        hiEl.addEventListener("input", function () {
            if (parseFloat(hiEl.value) < parseFloat(loEl.value)) {
                hiEl.value = loEl.value;
            }
            updateFill();
            debouncedSlider();
        });

        /* Toggle accordéon du bloc prix */
        const toggle = byId("exo-price-toggle");
        const body   = byId("exo-price-body");
        if (toggle && body) {
            toggle.addEventListener("click", function () {
                const open = body.classList.toggle("exo-price__body--open");
                toggle.classList.toggle("exo-price__head--open", open);
                toggle.setAttribute("aria-expanded", String(open));
            });
        }

        /* Exposer pour init() */
        window._exoSlider = { applyBounds: applyBounds, updateFill: updateFill };
        updateFill();
    }

    function resetSlider() {
        if (!_sliderLoEl || !_sliderHiEl) return;
        _sliderLoEl.value = _sliderLoEl.min;
        _sliderHiEl.value = _sliderHiEl.max;
        const sl = window._exoSlider;
        if (sl) sl.updateFill();
        S.priceMin = null;
        S.priceMax = null;
    }

    /* ============================================================
       TAGS FILTRES ACTIFS
    ============================================================ */
    function renderTags() {
        const container = byId("exo-tags");
        if (!container) return;
        const tags = [];

        /* Catégories */
        document.querySelectorAll(".exo-cb[data-cat-id]:checked").forEach(function (cb) {
            const parts = [cb.dataset.service, cb.dataset.parent, cb.dataset.catName]
                .filter(function (x) { return x && x.trim(); });
            /* Dédupliquer (service = catName si item racine) */
            const unique = parts.filter(function (v, i, a) { return a.indexOf(v) === i; });
            const label  = unique.join(" \u203a ");
            tags.push({
                label: label,
                remove: (function (checkbox) {
                    return function () {
                        checkbox.checked = false;
                        S.catIds.delete(parseInt(checkbox.dataset.catId, 10));
                        S.page = 0;
                        fetchProducts();
                        renderTags();
                    };
                }(cb)),
            });
        });

        /* Attributs */
        document.querySelectorAll(".exo-attr-cb:checked").forEach(function (cb) {
            tags.push({
                label: cb.dataset.attrName + " : " + cb.dataset.valueName,
                remove: (function (checkbox) {
                    return function () {
                        checkbox.checked = false;
                        const a = parseInt(checkbox.dataset.attrId, 10);
                        const v = parseInt(checkbox.dataset.valueId, 10);
                        S.attrib = S.attrib.filter(function (p) {
                            return !(p[0] === a && p[1] === v);
                        });
                        S.page = 0;
                        fetchProducts();
                        renderTags();
                    };
                }(cb)),
            });
        });

        /* Prix */
        if (S.priceMin !== null || S.priceMax !== null) {
            const lo = S.priceMin !== null ? S.priceMin : S.priceAbsMin;
            const hi = S.priceMax !== null ? S.priceMax : S.priceAbsMax;
            tags.push({
                label: fmt(lo) + " \u2013 " + fmt(hi),
                remove: function () {
                    resetSlider();
                    S.page = 0;
                    fetchProducts();
                    renderTags();
                },
            });
        }

        /* Recherche */
        if (S.search) {
            tags.push({
                label: "\u201c" + S.search + "\u201d",
                remove: function () {
                    S.search = "";
                    const inp = byId("exo-search");
                    const clr = byId("exo-search-clr");
                    if (inp) inp.value = "";
                    if (clr) clr.classList.add("exo-hidden");
                    S.page = 0;
                    fetchProducts();
                    renderTags();
                },
            });
        }

        if (!tags.length) { container.innerHTML = ""; return; }

        container.innerHTML = tags.map(function (t, i) {
            return '<span class="exo-tag" data-idx="' + i + '">' +
                escHtml(t.label) +
                ' <i class="fa fa-times exo-tag__x" aria-hidden="true"></i>' +
                '</span>';
        }).join("");

        container.querySelectorAll(".exo-tag").forEach(function (el) {
            el.addEventListener("click", function () {
                tags[parseInt(el.dataset.idx, 10)].remove();
            });
        });
    }

    /* ============================================================
       PAGINATION
    ============================================================ */
    function renderPager(page, pages) {
        const pager = byId("exo-pager");
        if (!pager) return;
        if (pages <= 1) { pager.innerHTML = ""; return; }

        const items = [];
        items.push('<button class="exo-page-btn" data-p="' + (page - 1) + '"' +
            (page === 0 ? ' disabled' : '') + ' aria-label="Précédente">' +
            '<i class="fa fa-chevron-left" aria-hidden="true"></i></button>');

        for (let i = 0; i < pages; i++) {
            if (pages > 7 && Math.abs(i - page) > 2 && i !== 0 && i !== pages - 1) {
                if (i === 1 || i === pages - 2) {
                    items.push('<span class="exo-page-btn" style="pointer-events:none;opacity:.4">\u2026</span>');
                }
                continue;
            }
            items.push('<button class="exo-page-btn' + (i === page ? ' exo-page-btn--active' : '') +
                '" data-p="' + i + '" aria-label="Page ' + (i + 1) + '"' +
                (i === page ? ' aria-current="page"' : '') + '>' + (i + 1) + '</button>');
        }

        items.push('<button class="exo-page-btn" data-p="' + (page + 1) + '"' +
            (page >= pages - 1 ? ' disabled' : '') + ' aria-label="Suivante">' +
            '<i class="fa fa-chevron-right" aria-hidden="true"></i></button>');

        pager.innerHTML = items.join("");
        pager.querySelectorAll(".exo-page-btn[data-p]:not([disabled])").forEach(function (btn) {
            btn.addEventListener("click", function () {
                S.page = parseInt(btn.dataset.p, 10);
                fetchProducts();
                const main = byId("exo-main");
                if (main) main.scrollIntoView({ behavior: "smooth", block: "start" });
            });
        });
    }

    /* ============================================================
       FETCH PRODUITS — AJAX principal
    ============================================================ */
    async function fetchProducts() {
        const overlay = byId("exo-overlay");
        const grid    = byId("exo-products");
        const countEl = byId("exo-count");

        if (overlay) overlay.classList.remove("exo-hidden");

        const result = await rpc("/exo/filter/products", {
            category_ids: Array.from(S.catIds).map(String),
            attrib:       S.attrib,
            price_min:    S.priceMin,
            price_max:    S.priceMax,
            search:       S.search,
            order:        S.order,
            page:         S.page,
        });

        if (overlay) overlay.classList.add("exo-hidden");
        if (!result) return;

        if (grid)    grid.innerHTML       = result.html  || "";
        if (countEl) countEl.textContent  = result.total != null ? result.total : 0;

        renderPager(result.page, result.pages);
        pushUrl();
    }

    /* ============================================================
       URL pushState — lien partageable
    ============================================================ */
    function pushUrl() {
        const p = new URLSearchParams();
        if (S.catIds.size)          p.set("categ",     Array.from(S.catIds).join(","));
        if (S.priceMin !== null)    p.set("price_min", S.priceMin);
        if (S.priceMax !== null)    p.set("price_max", S.priceMax);
        if (S.search)               p.set("search",    S.search);
        if (S.order !== "name asc") p.set("order",     S.order);
        if (S.page > 0)             p.set("page",      S.page);
        const qs = p.toString();
        history.replaceState({}, "", location.pathname + (qs ? "?" + qs : ""));
    }

    function restoreUrl() {
        const p = new URLSearchParams(location.search);
        if (p.get("categ")) {
            p.get("categ").split(",").forEach(function (id) {
                const n = parseInt(id, 10);
                if (!isNaN(n)) S.catIds.add(n);
            });
        }
        if (p.get("price_min")) S.priceMin = parseFloat(p.get("price_min"));
        if (p.get("price_max")) S.priceMax = parseFloat(p.get("price_max"));
        if (p.get("search"))    S.search   = p.get("search");
        if (p.get("order"))     S.order    = p.get("order");
        if (p.get("page"))      S.page     = parseInt(p.get("page"), 10) || 0;
    }

    /* ============================================================
       RECHERCHE TEXTE
    ============================================================ */
    function initSearch() {
        const inp = byId("exo-search");
        const clr = byId("exo-search-clr");
        if (!inp) return;

        if (S.search) {
            inp.value = S.search;
            if (clr) clr.classList.remove("exo-hidden");
        }

        const dSearch = debounce(function () {
            S.search = inp.value.trim();
            S.page   = 0;
            fetchProducts();
            renderTags();
        }, 400);

        inp.addEventListener("input", function () {
            if (clr) clr.classList.toggle("exo-hidden", !inp.value);
            dSearch();
        });

        if (clr) {
            clr.addEventListener("click", function () {
                inp.value = "";
                clr.classList.add("exo-hidden");
                S.search = "";
                S.page   = 0;
                fetchProducts();
                renderTags();
                inp.focus();
            });
        }
    }

    /* ============================================================
       TRI
    ============================================================ */
    function initSort() {
        const sel = byId("exo-sort");
        if (!sel) return;
        sel.value = S.order;
        sel.addEventListener("change", function () {
            S.order = sel.value;
            S.page  = 0;
            fetchProducts();
        });
    }

    /* ============================================================
       RÉINITIALISER
    ============================================================ */
    function initReset() {
        const btn = byId("exo-reset");
        if (!btn) return;
        btn.addEventListener("click", function () {
            S.catIds.clear();
            S.attrib = [];
            S.search = "";
            S.page   = 0;
            document.querySelectorAll(".exo-cb").forEach(function (cb) {
                cb.checked = false;
            });
            const inp = byId("exo-search");
            const clr = byId("exo-search-clr");
            if (inp) inp.value = "";
            if (clr) clr.classList.add("exo-hidden");
            resetSlider();
            fetchProducts();
            renderTags();
        });
    }

    /* ============================================================
       TOGGLE SIDEBAR MOBILE
    ============================================================ */
    function initMobileToggle() {
        const btn     = byId("exo-sidebar-toggle");
        const sidebar = byId("exo-sidebar");
        if (!btn || !sidebar) return;
        btn.addEventListener("click", function () {
            const collapsed = sidebar.classList.toggle("exo-sidebar--collapsed");
            btn.setAttribute("aria-expanded", String(!collapsed));
        });
    }

    /* ============================================================
       INITIALISATION
    ============================================================ */
    async function init() {
        restoreUrl();
        initSlider();
        initSearch();
        initSort();
        initReset();
        initMobileToggle();

        const facets = await rpc("/exo/filter/facets", {});
        if (facets) {
            S.priceAbsMin = facets.price_abs_min != null ? facets.price_abs_min : 0;
            S.priceAbsMax = facets.price_abs_max != null ? facets.price_abs_max : 1000;

            const sl = window._exoSlider;
            if (sl) {
                sl.applyBounds(S.priceAbsMin, S.priceAbsMax);
                if (S.priceMin !== null) _sliderLoEl.value = S.priceMin;
                if (S.priceMax !== null) _sliderHiEl.value = S.priceMax;
                sl.updateFill();
            }

            renderCategories(facets.categories || []);
            renderAttributes(facets.attributes  || []);
        }

        await fetchProducts();
        renderTags();
    }

    /* Lancement après DOM ready */
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    /* API publique pour debug */
    window.ExoFilter = { S: S, fetchProducts: fetchProducts, renderTags: renderTags };

}());
