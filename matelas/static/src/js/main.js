(function() {
    'use strict';

   
    function isEnglish() {
        return (document.documentElement.getAttribute('lang') || '').toLowerCase().indexOf('en') === 0;
    }

    function initAll() {
        const en = isEnglish();

        // ===== ÉTOILES AVIS =====
        const stars = document.querySelectorAll('.star');
        const starRating = document.getElementById('star-rating');

        if (stars.length > 0 && starRating) {
            stars.forEach(function(star) {
                star.addEventListener('mouseover', function() {
                    const val = this.dataset.value;
                    stars.forEach(s => s.classList.toggle('active', s.dataset.value <= val));
                });
                star.addEventListener('click', function() {
                    document.getElementById('avis-note').value = this.dataset.value;
                });
            });
            starRating.addEventListener('mouseleave', function() {
                const note = document.getElementById('avis-note').value;
                stars.forEach(s => s.classList.toggle('active', s.dataset.value <= note));
            });
        }

        // ===== AVIS (enregistré réellement en base via /avis/submit) =====
        const btnAvis = document.getElementById('btn-envoyer-avis');
        if (btnAvis) {
            btnAvis.addEventListener('click', function() {
                const nom = document.getElementById('avis-nom').value.trim();
                const profession = document.getElementById('avis-profession').value.trim();
                const note = document.getElementById('avis-note').value;
                const produit = document.getElementById('avis-produit').value.trim();
                const commentaire = document.getElementById('avis-commentaire').value.trim();

                if (!nom || note == 0 || !commentaire) {
                    alert(en ? 'Please fill in all required fields (*)' : 'Merci de remplir tous les champs obligatoires (*)');
                    return;
                }

                btnAvis.disabled = true;

                fetch('/avis/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        id: Date.now(),
                        params: {
                            name: nom,
                            profession: profession,
                            note: parseInt(note),
                            titre: produit,
                            commentaire: commentaire
                        }
                    })
                })
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        const result = data && data.result;
                        if (!result || !result.success) {
                            const message = (result && result.error) ||
                                (en ? 'Something went wrong.' : 'Une erreur est survenue.');
                            alert(message);
                            return;
                        }

                        const starsHtml = '★'.repeat(parseInt(note)) + '☆'.repeat(5 - parseInt(note));
                        const justNow = en ? 'just now' : "à l'instant";
                        const card = `
                            <div class="col-md-4 mb-4">
                                <div class="avis-card">
                                    <div class="avis-stars">${starsHtml}</div>
                                    ${produit ? `<p class="avis-produit">🛏️ ${produit}</p>` : ''}
                                    <p class="avis-texte">"${commentaire}"</p>
                                    <strong class="avis-auteur">${nom}</strong>
                                    ${profession ? `<span class="avis-profession"> — ${profession}</span>` : ''}
                                    <span class="avis-date"> — ${justNow}</span>
                                </div>
                            </div>
                        `;

                        document.getElementById('avis-container').innerHTML += card;
                        document.getElementById('avis-success').style.display = 'block';
                        document.getElementById('avis-nom').value = '';
                        document.getElementById('avis-profession').value = '';
                        document.getElementById('avis-note').value = 0;
                        document.getElementById('avis-produit').value = '';
                        document.getElementById('avis-commentaire').value = '';
                        stars.forEach(s => s.classList.remove('active'));
                        document.getElementById('avis-container').scrollIntoView({ behavior: 'smooth' });
                    })
                    .catch(function() {
                        alert(en ? 'Something went wrong.' : 'Une erreur est survenue.');
                    })
                    .finally(function() {
                        btnAvis.disabled = false;
                    });
            });
        }

        // ===== CONTACT =====
        const btnContact = document.getElementById('btn-contact-send');
        if (btnContact) {
            btnContact.addEventListener('click', function() {
                const nom = document.getElementById('c-nom').value.trim();
                const prenom = document.getElementById('c-prenom').value.trim();
                const email = document.getElementById('c-email').value.trim();
                const message = document.getElementById('c-message').value.trim();

                if (!nom || !prenom || !email || !message) {
                    alert(en ? 'Please fill in all required fields (*)' : 'Merci de remplir tous les champs obligatoires (*)');
                    return;
                }

                document.getElementById('contact-success').style.display = 'block';
                document.getElementById('c-nom').value = '';
                document.getElementById('c-prenom').value = '';
                document.getElementById('c-email').value = '';
                document.getElementById('c-tel').value = '';
                document.getElementById('c-sujet').value = '';
                document.getElementById('c-message').value = '';

                window.scrollTo({
                    top: document.querySelector('.contact-form-box').offsetTop - 100,
                    behavior: 'smooth'
                });
            });
        }

        // ===== FAQ =====
        document.querySelectorAll('.faq-question').forEach(function(btn) {
            btn.addEventListener('click', function() {
                const answer = this.nextElementSibling;
                const isOpen = answer.classList.contains('open');

                document.querySelectorAll('.faq-answer').forEach(a => a.classList.remove('open'));
                document.querySelectorAll('.faq-question').forEach(q => q.classList.remove('active'));

                if (!isOpen) {
                    answer.classList.add('open');
                    this.classList.add('active');
                }
            });
        });

        // ===== NEWSLETTER (vraie inscription via website_mass_mailing) =====
        const btnNewsletter = document.querySelector('.btn-newsletter');
        if (btnNewsletter) {
            btnNewsletter.addEventListener('click', function(e) {
                e.preventDefault();
                const input = document.querySelector('.newsletter-input');
                const email = input ? input.value.trim() : '';
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

                if (!email || !emailRegex.test(email)) {
                    alert(en ? 'Please enter a valid email address.' : 'Merci de saisir une adresse email valide.');
                    return;
                }

                fetch('/newsletter/subscribe', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        id: Date.now(),
                        params: {
                            value: email
                        }
                    })
                })
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        const result = data && data.result;
                        if (result && result.success) {
                            input.value = '';
                            btnNewsletter.textContent = en ? '✅ Subscribed!' : '✅ Inscrit !';
                        } else {
                            const message = (result && result.error) ||
                                (en ? 'Something went wrong.' : 'Une erreur est survenue.');
                            alert(message);
                        }
                    })
                    .catch(function() {
                        alert(en ? 'Something went wrong.' : 'Une erreur est survenue.');
                    })
                    .finally(function() {
                        setTimeout(function() {
                            btnNewsletter.textContent = en ? 'Sign up →' : "S'inscrire →";
                        }, 3000);
                    });
            });
        }

        // ===== HEADER : icône favoris =====
        const header = document.querySelector('header#top') || document.querySelector('header') || document;
        const cartBtn = header.querySelector('.o_cart_btn, a[href="/shop/cart"], a[href*="/shop/cart"]');

        if (cartBtn) {
            cartBtn.classList.add('matelas-icon-btn');
        }

        if (cartBtn && !document.querySelector('.matelas-wishlist-btn')) {
            const wishlistLink = document.createElement('a');
            wishlistLink.href = '/shop/wishlist';
            wishlistLink.className = 'matelas-wishlist-btn matelas-icon-btn nav-link';
            wishlistLink.title = 'Mes favoris';
            wishlistLink.innerHTML = '<i class="bi bi-heart"></i>';
            cartBtn.insertAdjacentElement('beforebegin', wishlistLink);
        }

        // ===== HEADER : icône recherche =====
        const searchIcon = header.querySelector('i.fa-search, i.bi-search, .oe_search_button i');
        const searchBtn = searchIcon ? searchIcon.closest('a, button') : null;
        if (searchBtn) {
            searchBtn.classList.add('matelas-icon-btn');
        }

        // ===== HEADER : cacher le bouton "Contact Us" natif d'Odoo =====
        header.querySelectorAll('a, button').forEach(function(el) {
            const t = el.textContent.trim().toLowerCase();
            if (t === 'contact us' || t === 'contactez-nous' || t === 'nous contacter') {
                el.style.display = 'none';
            }
        });

        // ===== HEADER : icône compte =====
        const logoutLink = header.querySelector('a[href*="/web/session/logout"]');

        if (logoutLink) {
           
            const menu = logoutLink.closest('.dropdown-menu, ul, div[class*="dropdown"]');
            const parentItem = menu ? (menu.parentElement || menu.closest('li')) : null;
            const toggle = parentItem
                ? parentItem.querySelector('.dropdown-toggle, a[data-bs-toggle="dropdown"], button[data-bs-toggle="dropdown"]')
                : null;

            if (toggle && !toggle.classList.contains('matelas-account-link')) {
                toggle.classList.add('matelas-account-link', 'matelas-icon-btn');
                toggle.innerHTML = '<i class="bi bi-person-circle"></i>';
                toggle.title = 'Mon compte';
            }
        } else {
            // Cas déconnecté : simple lien "Se connecter"
            const signInLink = header.querySelector('a[href^="/web/login"]');
            if (signInLink && !signInLink.classList.contains('matelas-account-link')) {
                signInLink.classList.add('matelas-account-link', 'matelas-icon-btn');
                signInLink.innerHTML = '<i class="bi bi-person"></i>';
                signInLink.title = 'Se connecter';
            }
        }

        // ===== AJOUT AU PANIER (best-sellers) =====
        
        function getCsrfToken() {
            if (typeof odoo !== 'undefined' && odoo.csrf_token) {
                return odoo.csrf_token;
            }
            const tokenInput = document.querySelector('input[name="csrf_token"]');
            return tokenInput ? tokenInput.value : '';
        }

        document.querySelectorAll('.btn-add[data-product-url]').forEach(function(btn) {
            if (btn.dataset.bound) { return; }
            btn.dataset.bound = 'true';

            btn.addEventListener('click', function(e) {
                e.preventDefault();

                const form = document.createElement('form');
                form.method = 'POST';
                form.action = btn.dataset.productUrl;
                form.style.display = 'none';

                const fields = {
                    csrf_token: getCsrfToken(),
                    product_id: btn.dataset.productId,
                    product_template_id: btn.dataset.templateId,
                    product_category_id: btn.dataset.categoryId,
                    product_type: btn.dataset.productType,
                    add_qty: '1'
                };
                Object.keys(fields).forEach(function(key) {
                    if (fields[key] === undefined || fields[key] === '') { return; }
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = key;
                    input.value = fields[key];
                    form.appendChild(input);
                });

                document.body.appendChild(form);
                form.submit();
            });
        });

        // ===== BANNIÈRE COOKIES : texte personnalisé =====
        const cookiesBar = document.getElementById('website_cookies_bar');
        if (cookiesBar) {
            const cookiesText = cookiesBar.querySelector('p');
            if (cookiesText) {
                cookiesText.innerHTML = en
                    ? '🍪 We use cookies to ensure smooth browsing, remember your cart and preferences, and improve your experience on Matelas. You can accept all cookies or choose only the essential ones.'
                    : '🍪 Nous utilisons des cookies pour vous garantir une navigation fluide, mémoriser votre panier et vos préférences, et améliorer votre expérience sur Matelas. Vous pouvez tout accepter ou choisir uniquement les cookies essentiels.';
            }
            
            cookiesBar.querySelectorAll('a, button').forEach(function(b) {
                const t = b.textContent.trim().toLowerCase();
                if (t === 'i agree' || t.indexOf('agree') !== -1 || t.indexOf('accept all') !== -1) {
                    b.textContent = en ? 'Accept all' : 'Tout accepter';
                } else if (t.indexOf('essential') !== -1) {
                    b.textContent = en ? 'Essential only' : 'Essentiels uniquement';
                }
            });
        }

        // ===== LIEN VERS LA FICHE TECHNIQUE (page produit) =====
        (function() {
            const addToCartBtn = document.getElementById('add_to_cart');
            if (!addToCartBtn) { return; }
            if (document.querySelector('.matelas-fiche-link')) { return; }

            
            let productId = null;
            const hiddenInput = document.querySelector(
                'form[action*="/shop/cart/update"] input[name="product_template_id"], ' +
                'input[name="product_template_id"]'
            );
            if (hiddenInput && hiddenInput.value) {
                productId = hiddenInput.value;
            } else {
                const match = window.location.pathname.match(
                    /^\/(?:[a-z]{2}(?:_[A-Z]{2})?\/)?shop\/[\w-]+-(\d+)$/
                );
                if (match) {
                    productId = match[1];
                }
            }
            if (!productId) { return; }

            const link = document.createElement('a');
            link.href = '/produit/' + productId + '/fiche';
            link.className = 'matelas-fiche-link';
            link.innerHTML = '<i class="bi bi-file-earmark-text"></i> ' +
                (en ? 'View data sheet' : 'Voir la fiche technique');

            addToCartBtn.insertAdjacentElement('afterend', link);
        })();

        // ===== PRODUITS VUS RÉCEMMENT =====
        (function() {
            const STORAGE_KEY = 'matelas_recently_viewed';
            const MAX_ITEMS = 6;

            function getStored() {
                try {
                    const raw = localStorage.getItem(STORAGE_KEY);
                    return raw ? JSON.parse(raw) : [];
                } catch (e) {
                    return [];
                }
            }

            function saveStored(items) {
                try {
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
                } catch (e) {
                
                }
            }

           
            const addToCartBtn = document.getElementById('add_to_cart');
            if (addToCartBtn) {
                const titleMeta = document.querySelector('meta[property="og:title"]');
                const imageMeta = document.querySelector('meta[property="og:image"]');
                const priceEl = document.querySelector('.oe_currency_value');

                const product = {
                    url: window.location.pathname,
                    title: titleMeta ? titleMeta.content : document.title,
                    image: imageMeta ? imageMeta.content : '',
                    price: priceEl ? priceEl.textContent.trim() : ''
                };

                if (product.url && product.title) {
                    let items = getStored().filter(function(p) {
                        return p.url !== product.url;
                    });
                    items.unshift(product);
                    items = items.slice(0, MAX_ITEMS);
                    saveStored(items);
                }
            }

            // Sur la page d'accueil : on affiche la section si on a des produits
            const container = document.getElementById('recently-viewed-container');
            if (container) {
                const items = getStored();
                if (items.length > 0) {
                    const section = document.getElementById('recently-viewed-section');
                    if (section) {
                        section.style.display = '';
                    }
                    container.innerHTML = '';
                    items.forEach(function(p) {
                        const col = document.createElement('div');
                        col.className = 'bestseller-scroll-item';

                        const card = document.createElement('div');
                        card.className = 'product-card';

                        const link = document.createElement('a');
                        link.href = p.url;

                        const img = document.createElement('img');
                        img.className = 'product-image';
                        img.src = p.image;
                        img.alt = p.title;
                        link.appendChild(img);

                        const type = document.createElement('p');
                        type.className = 'product-type';
                        type.textContent = en ? 'MATTRESS' : 'MATELAS';

                        const title = document.createElement('h4');
                        title.textContent = p.title;

                        const priceWrap = document.createElement('div');
                        priceWrap.className = 'price-action';
                        const price = document.createElement('p');
                        price.className = 'price';
                        price.textContent = p.price;
                        priceWrap.appendChild(price);

                        card.appendChild(link);
                        card.appendChild(type);
                        card.appendChild(title);
                        card.appendChild(priceWrap);
                        col.appendChild(card);
                        container.appendChild(col);
                    });
                }
            }
        })();

        (function() {
            function normalizePaymentButtons() {
                document.querySelectorAll('button, span, a').forEach(function(el) {
                    if (el.children.length > 0) { return; }
                    const t = el.textContent.trim();
                    if (/^(Payer avec|Pay with)\s+\S/i.test(t)) {
                        el.textContent = en ? 'Pay' : 'Payer';
                    }
                });
            }

            normalizePaymentButtons();
            const mo = new MutationObserver(function() {
                normalizePaymentButtons();
            });
            mo.observe(document.body, { childList: true, subtree: true, characterData: true });
        })();

        // ===== Masquer le bandeau "Free Testimonials Slider Widget" d'Elfsight =====
        (function() {
            const temoignages = document.querySelector('.temoignages');
            if (!temoignages) { return; }

            function removeElfsightBadge() {
                temoignages.querySelectorAll('a[href*="elfsight.com/testimonials-slider-widget"]').forEach(function(badge) {
                    badge.remove();
                });
            }

            removeElfsightBadge();
            const badgeObserver = new MutationObserver(removeElfsightBadge);
            badgeObserver.observe(temoignages, { childList: true, subtree: true });
        })();

    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }

    
    window.addEventListener('load', function() {
        initAll();
    });

})();