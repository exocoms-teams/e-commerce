document.addEventListener('DOMContentLoaded', function () {

    // ── Dropdown menu sidebar
    var dropdown = document.querySelector('.tsp-nav-dropdown');
    if (dropdown) {
        var chevron = dropdown.querySelector('.tsp-chevron');
        if (chevron) {
            chevron.addEventListener('click', function (e) {
                e.stopPropagation();
                e.preventDefault();
                var submenu = dropdown.querySelector('.tsp-submenu');
                if (submenu) submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
            });
        }
    }

    // ── Wishlist
    document.querySelectorAll('.tsp-wishlist-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var icon = this.querySelector('i');
            if (icon.classList.contains('fa-heart-o')) {
                icon.classList.replace('fa-heart-o', 'fa-heart');
                icon.style.color = '#ef4444';
            } else {
                icon.classList.replace('fa-heart', 'fa-heart-o');
                icon.style.color = '';
            }
        });
    });

    // ── Bouton Ajouter → Ajouté !
    document.querySelectorAll('button.tsp-btn-add').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var original = this.innerHTML;
            this.innerHTML = '<i class="fa fa-check"></i> Ajouté !';
            this.style.background = '#16a34a';
            var self = this;
            setTimeout(function () {
                self.innerHTML = original;
                self.style.background = '';
            }, 1500);
        });
    });

    // ── Newsletter
    var newsletterBtn = document.querySelector('.tsp-newsletter-btn');
    if (newsletterBtn) {
        newsletterBtn.addEventListener('click', function () {
            var input = document.querySelector('.tsp-newsletter-form input');
            if (!input || !input.value || !input.value.includes('@')) {
                alert('Veuillez entrer une adresse email valide.');
                return;
            }
            var form = document.querySelector('.tsp-newsletter-form');
            if (form) form.innerHTML = '<span style="color:white;font-weight:600"><i class="fa fa-check-circle"></i> Merci ! Vous êtes bien inscrit(e) 🎉</span>';
        });
    }

    // ── Custom selects (dropdowns filtres)
    document.querySelectorAll('.tsp-custom-select').forEach(function (select) {
        var selected = select.querySelector('.tsp-custom-selected');
        var options = select.querySelector('.tsp-custom-options');
        if (!selected || !options) return;

        selected.addEventListener('click', function (e) {
            e.stopPropagation();
            document.querySelectorAll('.tsp-custom-select').forEach(function (s) {
                if (s !== select) s.classList.remove('open');
            });
            select.classList.toggle('open');
        });

        options.addEventListener('click', function (e) {
            e.stopPropagation();
        });

        options.querySelectorAll('input[type="checkbox"]').forEach(function (checkbox) {
            checkbox.addEventListener('change', function () {
                var checked = options.querySelectorAll('input[type="checkbox"]:checked');
                if (checked.length === 0) {
                    selected.innerHTML = 'Toutes <i class="fa fa-chevron-down"></i>';
                } else if (checked.length === 1) {
                    selected.innerHTML = '1 sélectionné <i class="fa fa-chevron-down"></i>';
                } else {
                    selected.innerHTML = checked.length + ' sélectionnés <i class="fa fa-chevron-down"></i>';
                }
            });
        });
    });

    document.addEventListener('click', function () {
        document.querySelectorAll('.tsp-custom-select').forEach(function (s) {
            s.classList.remove('open');
        });
    });

    // ══════════════════════════════════════════
    // CARROUSEL avis homepage 
    // ══════════════════════════════════════════
    const carousel = document.getElementById('hp-avis-carousel');
    if (carousel) {
        const wrap = carousel.closest('.hp-avis-carousel-wrap');
        let isDown = false;
        let startX;
        let scrollLeft;

        wrap.addEventListener('mousedown', (e) => {
            isDown = true;
            wrap.classList.add('dragging');
            startX = e.pageX - carousel.offsetLeft;
            scrollLeft = carousel.scrollLeft;
        });

        wrap.addEventListener('mouseleave', () => {
            isDown = false;
            wrap.classList.remove('dragging');
        });

        wrap.addEventListener('mouseup', () => {
            isDown = false;
            wrap.classList.remove('dragging');
        });

        wrap.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - carousel.offsetLeft;
            const walk = (x - startX) * 2;
            carousel.scrollLeft = scrollLeft - walk;
        });
    }


    // ══════════════════════════════════════════
    // FORMULAIRE AVIS en ajax
    // ══════════════════════════════════════════
    const avisForm = document.querySelector('.avis-form-wrap form');
    if (avisForm) {
        avisForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = new FormData(avisForm);

            await fetch('/avis/submit', {
                method: 'POST',
                body: formData,
            });

            // Animation rétrécissement
            const wrap = document.querySelector('.avis-form-wrap');
            wrap.style.transition = 'all 0.5s ease';
            wrap.style.overflow = 'hidden';
            wrap.style.height = wrap.offsetHeight + 'px';

            setTimeout(() => {
                wrap.style.height = '0';
                wrap.style.padding = '0';
                wrap.style.opacity = '0';
            }, 100);

            setTimeout(() => {
                wrap.innerHTML = `
                <div style="text-align:center; padding: 40px 20px;">
                    <i class="fa fa-check-circle" style="font-size:3rem; color:#16a34a; margin-bottom:16px; display:block"></i>
                    <h2 style="font-size:1.5rem; font-weight:800; margin-bottom:12px;">Merci pour votre avis !</h2>
                    <p style="color:var(--muted); font-size:0.95rem;">Votre avis a bien été reçu. Il sera publié après validation par notre équipe.</p>
                    <a href="/avis" style="display:inline-block; margin-top:24px; padding:10px 24px; background:var(--blue); color:white; border-radius:var(--radius-sm); font-weight:600; text-decoration:none;">
                        Retour à l'accueil
                    </a>
                </div>
            `;
                wrap.style.height = '';
                wrap.style.padding = '36px';
                wrap.style.opacity = '1';
            }, 600);
        });
    }

    // ══════════════════════════════════════════
    // FILTRES /shop 
    // ══════════════════════════════════════════

    const CATEGORY_FILTERS = {
        'smartphones-1': ['Systeme', 'Stockage', 'Taille'],
        'montres-2': ['Compatibilite'],
        'accessoires-3': ['Compatibilite'],
        'tv-4': ['Taille', 'Resolution'],
    };

    if (!window.location.pathname.startsWith('/shop')) return;

    // Récupère l'ID d'un attribut par son nom
    async function getAttributeId(name) {
        const res = await fetch('/web/dataset/call_kw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    model: 'product.attribute',
                    method: 'search_read',
                    args: [[['name', '=', name]]],
                    kwargs: { fields: ['id', 'name'] }
                }
            })
        });
        const data = await res.json();
        return data.result?.[0]?.id || null;
    }

    // Récupère les valeurs d'un attribut
    async function getAttributeValues(attributeId) {
        const res = await fetch('/web/dataset/call_kw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    model: 'product.attribute.value',
                    method: 'search_read',
                    args: [[['attribute_id', '=', attributeId]]],
                    kwargs: { fields: ['id', 'name'] }
                }
            })
        });
        const data = await res.json();
        return data.result || [];
    }

    // Peuple un dropdown dynamiquement
    function populateDropdown(filterName, values, attrId) {
        const ul = document.querySelector(
            `.tsp-custom-select[data-filter="${filterName}"] .tsp-custom-options`
        );
        if (!ul) return;

        ul.querySelectorAll('li:not([data-value=""])').forEach(li => li.remove());

        values.forEach(val => {
            const li = document.createElement('li');
            li.setAttribute('data-value', `${attrId}-${val.id}`);
            li.innerHTML = `
                <input type="checkbox" id="${filterName}-${val.id}"/>
                <label for="${filterName}-${val.id}">${val.name}</label>
            `;
            ul.appendChild(li);

            // Branche le event change sur la nouvelle checkbox
            const cb = li.querySelector('input[type="checkbox"]');
            const parentSelect = ul.closest('.tsp-custom-select');
            const selectedDiv = parentSelect?.querySelector('.tsp-custom-selected');
            if (cb && selectedDiv) {
                cb.addEventListener('change', function () {
                    const checked = ul.querySelectorAll('input[type="checkbox"]:checked');
                    if (checked.length === 0) {
                        selectedDiv.innerHTML = 'Toutes <i class="fa fa-chevron-down"></i>';
                    } else if (checked.length === 1) {
                        selectedDiv.innerHTML = '1 sélectionné <i class="fa fa-chevron-down"></i>';
                    } else {
                        selectedDiv.innerHTML = checked.length + ' sélectionnés <i class="fa fa-chevron-down"></i>';
                    }
                });
            }
        });
    }
    //Injecte filtre dynamique selon categorie
    async function injectCategoryFilters() {
        const path = window.location.pathname;
        const match = path.match(/\/shop\/category\/([^\/]+)/);
        if (!match) return;

        const slug = match[1];
        const attrNames = CATEGORY_FILTERS[slug];
        if (!attrNames) return;

        const container = document.getElementById('tsp-category-filters');
        if (!container) return;

        for (const name of attrNames) {
            const attrId = await getAttributeId(name);
            if (!attrId) continue;

            const values = await getAttributeValues(attrId);
            if (!values.length) continue;

            //creer filtre group
            const group = document.createElement('div');
            group.className = 'tsp-filter-group';
            group.innerHTML = `
                <label>${name}</label>
                <div class="tsp-custom-select" data-filter="${name.toLowerCase()}">
                    <div class="tsp-custom-selected">Tous<i class="fa fa-chevron-down"></i></div>
                    <ul class="tsp-custom-options">
                        <li data-value="">Tous</li>
                    </ul>
                </div>
            `;
            container.appendChild(group);

            //peuple valeurs
            populateDropdown(name.toLowerCase(), values, attrId);

            //branche fonctionnement de l ouverture/fermeture du dropdown
            const select = group.querySelector('.tsp-custom-select');
            const selected = group.querySelector('.tsp-custom-selected');
            const options = group.querySelector('.tsp-custom-options');
            selected.addEventListener('click', function (e) {
                e.stopPropagation();
                document.querySelectorAll('.tsp-custom-select').forEach(s => {
                    if (s !== select) s.classList.remove('open');
                });
                select.classList.toggle('open');
            });
            options.addEventListener('click', e => e.stopPropagation());
        }
        const btn = document.getElementById('tsp-apply-filters');
        if (btn) container.appendChild(btn);
    }

    // Init dropdowns marque + couleur
    async function initFilters() {
        const [brandId, colorId] = await Promise.all([
            getAttributeId('Brand'),
            getAttributeId('Color')
        ]);

        if (brandId) {
            const brands = await getAttributeValues(brandId);
            populateDropdown('marque', brands, brandId);
        }

        if (colorId) {
            const colors = await getAttributeValues(colorId);
            populateDropdown('couleur', colors, colorId);
        }

        await injectCategoryFilters();
    }

    // Récupère les attribs cochés (format "attrId-valueId")
    function getCheckedAttribs() {
        const attribs = [];
        document.querySelectorAll('.tsp-custom-options input[type="checkbox"]:checked').forEach(cb => {
            const li = cb.closest('li');
            const val = li?.getAttribute('data-value');
            if (val) attribs.push(val);
        });
        return attribs;
    }

    // Bouton Filtrer
    const filterBtn = document.getElementById('tsp-apply-filters');
    if (filterBtn) {
        filterBtn.addEventListener('click', function () {
            const params = new URLSearchParams();

            // Prix
            const minPrice = document.getElementById('filter-price-min')?.value;
            const maxPrice = document.getElementById('filter-price-max')?.value;
            if (minPrice) params.set('min_price', minPrice);
            if (maxPrice) params.set('max_price', maxPrice);

            // Attributs (marque + couleur)
            getCheckedAttribs().forEach(attrib => {
                params.append('attribute_values', attrib);
            });

            // Garde la catégorie courante
            const currentParams = new URLSearchParams(window.location.search);
            if (currentParams.get('category')) {
                params.set('category', currentParams.get('category'));
            }

            //garde path de category si on est sur /shop/category/...
            const pathMatch = window.location.pathname.match(/\/shop\/category\/([^\/]+)/);
            const redirect = pathMatch
                ? '/shop/category/' + pathMatch[1] + '?' + params.toString()
                : '/shop?' + params.toString();

            window.location.href = redirect;
        });
    }


    initFilters();
});