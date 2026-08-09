(function () {

    // BOUTONS "AJOUTER AU PANIER"
    initAddToCart();

    // FORMULAIRE NEWSLETTER
    initNewsletter();

    // ANIMATION COMPTEURS
    initCounterAnimation();


    // FONCTION : Ajouter au panier
    function initAddToCart() {

        document.addEventListener("click", function (e) {

            var btn = e.target.closest(".sn-add-to-cart");
            if (!btn) return;

            e.preventDefault();

            var productId  = btn.dataset.productId  || "0";
            var productQty = parseInt(btn.dataset.qty || "1", 10);

            addToCart(productId, productQty, btn);
        });
    }

    function addToCart(productId, qty, btn) {

        var originalText = btn.textContent;
        btn.textContent  = "Adding...";
        btn.disabled     = true;
        btn.classList.add("sn-btn--loading");

        /* backend ajouter au panier odoo */

        
        setTimeout(function () {
            btn.textContent = "✓ Added!";
            btn.classList.remove("sn-btn--loading");
            btn.classList.add("sn-btn--success");

            updateCartBadge(qty);

            showToast("Produit ajouté au panier !");

            setTimeout(function () {
                btn.textContent = originalText;
                btn.disabled    = false;
                btn.classList.remove("sn-btn--success");
            }, 2000);

        }, 600);
    }


    // mise à jour du badge panier dans le header
    function updateCartBadge(addedQty) {
        var badge = document.querySelector(".sn-cart-count");
        if (!badge) return;

        var current = parseInt(badge.textContent, 10) || 0;
        var next    = current + addedQty;

        badge.textContent = next;
        badge.style.display = next > 0 ? "flex" : "none";

        badge.classList.remove("sn-cart-count--bump");
        badge.classList.add("sn-cart-count--bump");
    }

    function showToast(message, type) {
        type = type || "success";

        var existing = document.querySelector(".sn-toast");
        if (existing) existing.remove();

        var toast = document.createElement("div");
        toast.className   = "sn-toast sn-toast--" + type;
        toast.textContent = message;

        document.body.appendChild(toast);

        requestAnimationFrame(function () {
            toast.classList.add("sn-toast--visible");
        });

        setTimeout(function () {
            toast.classList.remove("sn-toast--visible");
            setTimeout(function () { toast.remove(); }, 400);
        }, 3000);
    }

    window.snShowToast = showToast;


    // Formulaire Newsletter
    function initNewsletter() {

        var form = document.querySelector(".sn-newsletter-form form");
        if (!form) return;

        form.addEventListener("submit", function (e) {
            e.preventDefault();

            var emailInput = form.querySelector('input[type="email"]');
            var email      = emailInput ? emailInput.value.trim() : "";

            if (!email || !isValidEmail(email)) {
                showToast("Veuillez saisir une adresse email valide.", "error");
                if (emailInput) emailInput.focus();
                return;
            }

            var submitBtn = form.querySelector("button[type='submit']");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = "Envoi...";
            }

            /* BACKEND — Inscription newsletter */
            fetch('/newsletter/subscribe', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email: email})
            })
            .then(function(r) { return r.json(); })
            .then(function(res) {
                if (res.success) {
                    showToast("Merci ! Vous êtes inscrit à notre newsletter.");
                    form.reset();
                } else {
                    showToast(res.error || "Erreur lors de l'inscription.", "error");
                }
            })
            .catch(function() {
                showToast("Erreur réseau. Réessayez.", "error");
            })
            .finally(function() {
                if (submitBtn) {
                    submitBtn.disabled    = false;
                    submitBtn.textContent = "Subscribe";
                }
            });
        });
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }


    function initCounterAnimation() {
        var counters = document.querySelectorAll(".sn-counter");
        if (!counters.length) return;

        var DURATION = 1500; // ms

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;

                var el     = entry.target;
                var target = parseInt(el.dataset.target || el.textContent, 10);
                var suffix = el.dataset.suffix || "";
                var start  = 0;
                var startTime = null;

                function step(timestamp) {
                    if (!startTime) startTime = timestamp;
                    var progress = Math.min((timestamp - startTime) / DURATION, 1);
                    var value    = Math.floor(progress * target);

                    el.textContent = value.toLocaleString("fr-FR") + suffix;

                    if (progress < 1) {
                        requestAnimationFrame(step);
                    } else {
                        el.textContent = target.toLocaleString("fr-FR") + suffix;
                    }
                }

                requestAnimationFrame(step);
                observer.unobserve(el);
            });
        }, { threshold: 0.5 });

        counters.forEach(function (counter) {
            observer.observe(counter);
        });
    }

    function initFaqToggle() {

        document.addEventListener("click", function (e) {

            var question = e.target.closest(".sn-static-content h3");
            if (!question) return;

            question.classList.toggle("open");
        });
    }

})();
