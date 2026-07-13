var PM_FR = (document.documentElement.lang || '').toLowerCase().indexOf('fr') === 0;
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
            this.innerHTML = '<i class="fa fa-check"></i> ' + (PM_FR ? 'Ajouté !' : 'Added!');
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
                    selected.innerHTML = (PM_FR ? 'Toutes' : 'All') + ' <i class="fa fa-chevron-down"></i>';
                } else if (checked.length === 1) {
                    selected.innerHTML = (PM_FR ? '1 sélectionné' : '1 selected') + ' <i class="fa fa-chevron-down"></i>';
                } else {
                    selected.innerHTML = checked.length + (PM_FR ? ' sélectionnés' : ' selected') + ' <i class="fa fa-chevron-down"></i>';
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
    function initCarousel(carouselId) {
        const carousel = document.getElementById(carouselId);
        if (!carousel) return;
        const wrap = carousel.closest('.hp-products-carousel-wrap, .hp-avis-carousel-wrap');
        if (!wrap) return;
        let isDown = false;
        let startX;
        let scrollLeft;

        wrap.addEventListener('mousedown', (e) => {
            isDown = true;
            wrap.classList.add('dragging');
            startX = e.pageX - carousel.offsetLeft;
            scrollLeft = carousel.scrollLeft;
        });
        wrap.addEventListener('mouseleave', () => { isDown = false; wrap.classList.remove('dragging'); });
        wrap.addEventListener('mouseup', () => { isDown = false; wrap.classList.remove('dragging'); });
        wrap.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - carousel.offsetLeft;
            const walk = (x - startX) * 2;
            carousel.scrollLeft = scrollLeft - walk;
        });
    }

    initCarousel('hp-avis-carousel');


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
                    <h2 style="font-size:1.5rem; font-weight:800; margin-bottom:12px;">${PM_FR ? 'Merci pour votre avis !' : 'Thank you for your review!'}</h2>
                    <p style="color:var(--muted); font-size:0.95rem;">${PM_FR ? 'Votre avis a bien été reçu. Il sera publié après validation par notre équipe.' : 'Your review has been received. It will be published after moderation by our team.'}</p>
                    <a href="/accueil" style="display:inline-block; margin-top:24px; padding:10px 24px; background:var(--blue); color:white; border-radius:var(--radius-sm); font-weight:600; text-decoration:none;">
                        ${PM_FR ? "Retour à l'accueil" : 'Back to home'}
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

    if (!window.location.pathname.includes('/shop')) return;
    // Pré-coche le filtre promotion si dans l'URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('x_is_promotion')) {
        const promo = document.getElementById('filter-promotion');
        if (promo) promo.checked = true;
    }

    // Essaie chaque nom dans l'ordre jusqu'à trouver un attribut avec des valeurs
    async function getAttributeId(names) {
        const nameList = Array.isArray(names) ? names : [names];
        for (const name of nameList) {
            try {
                const res = await fetch('/web/dataset/call_kw', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        jsonrpc: '2.0', method: 'call', id: 1,
                        params: {
                            model: 'product.attribute',
                            method: 'search_read',
                            args: [[['name', '=', name], ['create_variant', '=', 'no_variant']]],
                            kwargs: { fields: ['id', 'name'], limit: 1 }
                        }
                    })
                });
                const data = await res.json();
                if (data.error || !data.result?.length) continue;
                const id = data.result[0].id;
                const values = await getAttributeValues(id);
                if (values.length > 0) {
                    console.log('[PM Filtres] Attribut retenu:', name, '→ id', id, '(', values.length, 'valeurs)');
                    return id;
                }
                console.warn('[PM Filtres]', name, 'trouvé mais sans valeurs, essai suivant...');
            } catch (e) {
                console.warn('[PM Filtres] Erreur pour', name, ':', e);
            }
        }
        console.warn('[PM Filtres] Aucun attribut avec valeurs pour:', nameList);
        return null;
    }

    // Récupère les valeurs d'un attribut
    async function getAttributeValues(attributeId) {
        try {
            const res = await fetch('/web/dataset/call_kw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    id: 2,
                    params: {
                        model: 'product.attribute.value',
                        method: 'search_read',
                        args: [[['attribute_id', '=', attributeId]]],
                        kwargs: { fields: ['id', 'name'] }
                    }
                })
            });
            const data = await res.json();
            if (data.error) {
                console.warn('[PM Filtres] Erreur API getAttributeValues:', data.error);
                return [];
            }
            return data.result || [];
        } catch (e) {
            console.warn('[PM Filtres] Fetch error getAttributeValues:', e);
            return [];
        }
    }

    //Recupere attributs lié a une categorie
    async function getCategoryAttributes(categoryId){
        const res = await fetch('/web/dataset/call_kw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method:'call',
                params: {
                    model: 'product.attribute',
                    method: 'search_read',
                    args: [[['x_product_categ_ids', 'in', [categoryId]]]],
                    kwargs: { fields: ['id', 'name'] }
                }  
            })          
        });
        const data = await res.json();
        return data.result || []
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
                        selectedDiv.innerHTML = (PM_FR ? 'Toutes' : 'All') + ' <i class="fa fa-chevron-down"></i>';
                    } else if (checked.length === 1) {
                        selectedDiv.innerHTML = '1 sélectionné <i class="fa fa-chevron-down"></i>';
                    } else {
                        selectedDiv.innerHTML = checked.length + ' sélectionnés <i class="fa fa-chevron-down"></i>';
                    }
                });
            }
        });
    }

    //Inject filtre dynamiques selon categories
    async function injectCategoryFilters(){
        const path = window.location.pathname;
        const match = path.match(/\/shop\/category\/([^\/]+)/);
        if (!match) return;

        const slug = match[1];
        //extrait id depuis slug, smartphones-1 -> 1
        const idMatch = slug.match(/-(\d+)$/);
        if (!idMatch) return;
        const categoryId = parseInt(idMatch[1]);

        const attributes = await getCategoryAttributes(categoryId);
        if (!attributes.length) return;

        const container = document.getElementById('tsp-category-filters');
        if (!container) return;

        // Récupère toutes les valeurs en parallèle (pas d'imbrication → safe)
        const allValues = await Promise.all(attributes.map(attr => getAttributeValues(attr.id)));

        // Construit tous les éléments d'abord, puis injection unique dans le DOM
        const fragment = document.createDocumentFragment();
        const groups = [];

        attributes.forEach((attr, i) => {
            const values = allValues[i];
            if (!values.length) { groups.push(null); return; }

            const group = document.createElement('div');
            group.className = 'tsp-filter-group';
            group.innerHTML = `
                <label>${attr.name}</label>
                <div class="tsp-custom-select" data-filter="${attr.name.toLowerCase()}">
                    <div class="tsp-custom-selected">${PM_FR ? "Tous" : "All"} <i class="fa fa-chevron-down"></i></div>
                    <ul class="tsp-custom-options">
                        <li data-value="">${PM_FR ? "Tous" : "All"}</li>
                    </ul>
                </div>
            `;
            fragment.appendChild(group);
            groups.push({ group, attr, values });
        });

        // Un seul reflow : tout apparaît d'un coup
        container.appendChild(fragment);

        // Attache les events et peuple les dropdowns après insertion
        groups.forEach(item => {
            if (!item) return;
            const { group, attr, values } = item;
            populateDropdown(attr.name.toLowerCase(), values, attr.id);
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
        });

        const btn = document.getElementById('tsp-apply-filters');

        // Sur mobile : toggle "More filters" pour ne pas noyer les produits
        if (window.innerWidth < 992 && groups.some(g => g !== null)) {
            const toggle = document.createElement('button');
            toggle.className = 'tsp-cat-filters-toggle';
            toggle.innerHTML = (PM_FR ? 'Plus de filtres' : 'More filters') + ' <i class="fa fa-chevron-down"></i>';
            container.before(toggle);
            container.style.display = 'none';
            toggle.addEventListener('click', () => {
                const isOpen = container.style.display !== 'none';
                container.style.display = isOpen ? 'none' : 'flex';
                toggle.classList.toggle('open', !isOpen);
            });
            // Bouton Filter après le toggle, toujours visible
            if (btn) toggle.after(btn);
        } else {
            // Desktop : bouton Filter en fin du container catégorie
            if (btn) container.appendChild(btn);
        }
    }

    

    // Init dropdowns marque + couleur
    async function initFilters() {
        // Lance les filtres catégorie immédiatement sans attendre Brand/Color
        const categoryPromise = injectCategoryFilters();

        // Brand et Color restent séquentiels (cf. pièges connus CLAUDE.md)
        const brandId = await getAttributeId(['Brand', 'brand', 'Marque', 'marque']);
        const colorId = await getAttributeId(['Color', 'color', 'Couleur', 'couleur']);

        if (brandId) {
            const brands = await getAttributeValues(brandId);
            console.log('[PM Filtres] Marques:', brands);
            if (brands.length) populateDropdown('marque', brands, brandId);
        }

        if (colorId) {
            const colors = await getAttributeValues(colorId);
            console.log('[PM Filtres] Couleurs:', colors);
            if (colors.length) populateDropdown('couleur', colors, colorId);
        }

        await categoryPromise;
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

            // Promotion ← ajoute ici
            const promotion = document.getElementById('filter-promotion');
            if (promotion && promotion.checked) {
                params.set('x_is_promotion', '1');
            }

            // Attributs (marque + couleur)
            getCheckedAttribs().forEach(attrib => {
                params.append('attribute_values', attrib);
            });

            // Garde la catégorie courante
            const currentParams = new URLSearchParams(window.location.search);
            if (currentParams.get('category')) {
                params.set('category', currentParams.get('category'));
            }

            //garde path de category si on est sur /en/shop/category/...
            const pathMatch = window.location.pathname.match(/(\/(?:[a-z]{2}\/)?shop(?:\/category\/[^\/]+)?)/);
            const basePath = pathMatch ? pathMatch[1] : '/shop';
            window.location.href = basePath + '?' + params.toString();
        });
    }


    initFilters();

    // ── Checkout : message livraison hors France
    if (window.location.pathname.includes('/shop/checkout')) {
        const isEn = window.location.pathname.startsWith('/en/') ||
                     document.documentElement.lang === 'en' ||
                     document.documentElement.lang === 'en-US';
        function fixNoDeliveryMessage() {
            const alertEl = document.querySelector('#o_delivery_form .alert-warning');
            if (alertEl && alertEl.textContent.includes('No suitable delivery method') && !alertEl.dataset.pmFixed) {
                alertEl.dataset.pmFixed = '1';
                if (isEn) {
                    alertEl.innerHTML =
                        '<i class="fa fa-map-marker me-2"></i>' +
                        '<strong>Delivery not available for this address</strong><br>' +
                        '<small>Planet Mobil only ships within mainland France. ' +
                        'Please update your delivery address.</small>';
                } else {
                    alertEl.innerHTML =
                        '<i class="fa fa-map-marker me-2"></i>' +
                        '<strong>Livraison non disponible pour cette adresse</strong><br>' +
                        '<small>Planet Mobil livre uniquement en France métropolitaine. ' +
                        'Veuillez modifier votre adresse de livraison.</small>';
                }
            }
        }

        fixNoDeliveryMessage();

        const deliveryForm = document.getElementById('o_delivery_form');
        if (deliveryForm) {
            new MutationObserver(fixNoDeliveryMessage).observe(deliveryForm, { childList: true, subtree: true });
        }
    }

});