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

        // ===== HEADER : icône compte (remplace le nom, garde le menu déroulant natif) =====
        const logoutLink = header.querySelector('a[href*="/web/session/logout"]');

        if (logoutLink) {
            // Cas connecté : on retrouve le vrai bouton qui affiche le nom (le "toggle"
            // du menu déroulant), en remontant depuis le lien de déconnexion qui, lui,
            // est stable quelle que soit la version/thème.
            const menu = logoutLink.closest('.dropdown-menu, ul, div[class*="dropdown"]');
            const parentItem = menu ? (menu.parentElement || menu.closest('li')) : null;
            const toggle = parentItem
                ? parentItem.querySelector('.dropdown-toggle, a[data-bs-toggle="dropdown"], button[data-bs-toggle="dropdown"]')
                : null;

            if (toggle && !toggle.classList.contains('matelas-account-link')) {
                toggle.classList.add('matelas-account-link');
                toggle.innerHTML = '<i class="bi bi-person-circle"></i>';
                toggle.title = 'Mon compte';
            }
        } else {
            // Cas déconnecté : simple lien "Se connecter"
            const signInLink = header.querySelector('a[href^="/web/login"]');
            if (signInLink && !signInLink.classList.contains('matelas-account-link')) {
                signInLink.classList.add('matelas-account-link');
                signInLink.innerHTML = '<i class="bi bi-person"></i>';
                signInLink.title = 'Se connecter';
            }
        }

        // ===== AJOUT AU PANIER (best-sellers) =====
        // Reproduit exactement le formulaire natif de la fiche produit Odoo :
        // POST vers la page du produit lui-même, avec les mêmes champs cachés
        // (confirmé en inspectant le vrai bouton "Add to cart" du site).
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
                cookiesText.innerHTML = '🍪 Nous utilisons des cookies pour vous garantir une navigation fluide, mémoriser votre panier et vos préférences, et améliorer votre expérience sur Matelas. Vous pouvez tout accepter ou choisir uniquement les cookies essentiels.';
            }
            // On matche par texte visible (plus fiable que deviner les classes,
            // qui changent selon la version d'Odoo).
            cookiesBar.querySelectorAll('a, button').forEach(function(b) {
                const t = b.textContent.trim().toLowerCase();
                if (t === 'i agree' || t.indexOf('agree') !== -1 || t.indexOf('accept all') !== -1) {
                    b.textContent = 'Tout accepter';
                } else if (t.indexOf('essential') !== -1) {
                    b.textContent = 'Essentiels uniquement';
                }
            });
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