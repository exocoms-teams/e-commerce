(function() {
    'use strict';

    function initAll() {

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

        // ===== AVIS =====
        const btnAvis = document.getElementById('btn-envoyer-avis');
        if (btnAvis) {
            btnAvis.addEventListener('click', function() {
                const nom = document.getElementById('avis-nom').value.trim();
                const note = document.getElementById('avis-note').value;
                const produit = document.getElementById('avis-produit').value.trim();
                const commentaire = document.getElementById('avis-commentaire').value.trim();

                if (!nom || note == 0 || !commentaire) {
                    alert('Merci de remplir tous les champs obligatoires (*)');
                    return;
                }

                const starsHtml = '★'.repeat(parseInt(note)) + '☆'.repeat(5 - parseInt(note));
                const card = `
                    <div class="col-md-4 mb-4">
                        <div class="avis-card">
                            <div class="avis-stars">${starsHtml}</div>
                            ${produit ? `<p class="avis-produit">🛏️ ${produit}</p>` : ''}
                            <p class="avis-texte">"${commentaire}"</p>
                            <strong class="avis-auteur">${nom}</strong>
                            <span class="avis-date"> — à l'instant</span>
                        </div>
                    </div>
                `;

                document.getElementById('avis-container').innerHTML += card;
                document.getElementById('avis-success').style.display = 'block';
                document.getElementById('avis-nom').value = '';
                document.getElementById('avis-note').value = 0;
                document.getElementById('avis-produit').value = '';
                document.getElementById('avis-commentaire').value = '';
                stars.forEach(s => s.classList.remove('active'));
                document.getElementById('avis-container').scrollIntoView({ behavior: 'smooth' });
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
                    alert('Merci de remplir tous les champs obligatoires (*)');
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

        // ===== NEWSLETTER =====
        const btnNewsletter = document.querySelector('.btn-newsletter');
        if (btnNewsletter) {
            btnNewsletter.addEventListener('click', function(e) {
                e.preventDefault();
                const input = document.querySelector('.newsletter-input');
                if (!input || !input.value.trim()) {
                    alert('Merci de saisir votre adresse email.');
                    return;
                }
                input.value = '';
                btnNewsletter.textContent = '✅ Inscrit !';
                setTimeout(function() {
                    btnNewsletter.textContent = "S'inscrire →";
                }, 3000);
            });
        }

        // ===== HEADER : icône favoris =====
        const header = document.querySelector('header#top') || document.querySelector('header') || document;
        const cartBtn = header.querySelector('.o_cart_btn, a[href="/shop/cart"], a[href*="/shop/cart"]');

        if (cartBtn && !document.querySelector('.matelas-wishlist-btn')) {
            const wishlistLink = document.createElement('a');
            wishlistLink.href = '/shop/wishlist';
            wishlistLink.className = 'matelas-wishlist-btn nav-link';
            wishlistLink.title = 'Mes favoris';
            wishlistLink.innerHTML = '<i class="bi bi-heart"></i>';
            cartBtn.insertAdjacentElement('beforebegin', wishlistLink);
        }

        // ===== HEADER : icône compte avec menu déroulant (connexion/déconnexion) =====
        const accountLink = header.querySelector('a[href="/my/home"], a[href^="/web/login"]');
        if (accountLink && !accountLink.classList.contains('matelas-account-link')) {
            const isLoggedIn = accountLink.getAttribute('href') === '/my/home';
            accountLink.classList.add('matelas-account-link');

            if (isLoggedIn) {
                const parentItem = accountLink.closest('li') || accountLink.parentElement;
                parentItem.classList.add('dropdown', 'matelas-account-item');

                accountLink.setAttribute('href', '#');
                accountLink.setAttribute('role', 'button');
                accountLink.setAttribute('data-bs-toggle', 'dropdown');
                accountLink.setAttribute('aria-expanded', 'false');
                accountLink.classList.add('dropdown-toggle');
                accountLink.innerHTML = '<i class="bi bi-person-circle"></i>';
                accountLink.title = 'Mon compte';

                const menu = document.createElement('div');
                menu.className = 'dropdown-menu dropdown-menu-end';
                menu.innerHTML =
                    '<a class="dropdown-item" href="/my/home"><i class="bi bi-person me-2"></i>Mon compte</a>' +
                    '<a class="dropdown-item" href="/my/orders"><i class="bi bi-bag me-2"></i>Mes commandes</a>' +
                    '<div class="dropdown-divider"></div>' +
                    '<a class="dropdown-item" href="/web/session/logout?redirect=/"><i class="bi bi-box-arrow-right me-2"></i>Déconnexion</a>';
                parentItem.appendChild(menu);
            } else {
                accountLink.innerHTML = '<i class="bi bi-person"></i>';
                accountLink.title = 'Se connecter';
            }
        }

        // ===== AJOUT AU PANIER (best-sellers) =====
        document.querySelectorAll('.btn-add[data-product-id]').forEach(function(btn) {
            if (btn.dataset.bound) { return; }
            btn.dataset.bound = 'true';

            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const productId = parseInt(btn.dataset.productId, 10);
                const originalText = btn.textContent;
                btn.textContent = '...';

                fetch('/shop/cart/update_json', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {
                            product_id: productId,
                            add_qty: 1
                        }
                    })
                })
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        const result = (data && data.result) || {};
                        if (result.cart_quantity === undefined && !result.line_id) {
                            throw new Error('cart update failed');
                        }
                        const cartQty = document.querySelector('.my_cart_quantity');
                        if (cartQty && result.cart_quantity !== undefined) {
                            cartQty.textContent = result.cart_quantity;
                            cartQty.classList.remove('d-none');
                        }
                        btn.textContent = '✅ Ajouté';
                        setTimeout(function() {
                            btn.textContent = originalText;
                        }, 2000);
                    })
                    .catch(function() {
                        btn.textContent = originalText;
                        alert("Impossible d'ajouter ce produit au panier pour le moment.");
                    });
            });
        });

        // ===== BANNIÈRE COOKIES : texte personnalisé =====
        const cookiesBar = document.getElementById('website_cookies_bar');
        if (cookiesBar) {
            const cookiesText = cookiesBar.querySelector('p');
            if (cookiesText) {
                cookiesText.innerHTML = '🍪 Nous utilisons des cookies pour vous garantir une navigation fluide, mémoriser votre panier et vos préférences, et améliorer votre expérience sur Matelas. Vous pouvez tout accepter ou choisir uniquement les cookies essentiels.';
            }
            const btnEssential = cookiesBar.querySelector('.o_cookies_bar_accept_essential');
            if (btnEssential) {
                btnEssential.textContent = 'Essentiels uniquement';
            }
            const btnAll = cookiesBar.querySelector('.o_cookies_bar_accept_all');
            if (btnAll) {
                btnAll.textContent = 'Tout accepter';
            }
        }

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