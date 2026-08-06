/**
 * oa_beauty_theme — Newsletter Subscription Handler
 * Envoie l'adresse email à n8n via webhook (POST JSON)
 * N8N peut ensuite ajouter le contact à Mailchimp ou toute autre liste.
 */

(function () {
    'use strict';

    // ── Configuration ──────────────────────────────────────────────────────────
    // Remplacez cette URL par l'URL de votre webhook n8n
    const N8N_WEBHOOK_URL = 'http://82.165.251.136:5678/webhook/newsletter';

    // ── Helpers ────────────────────────────────────────────────────────────────
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
    }

    function showFeedback(container, type, message) {
        // Supprimer ancien feedback
        const old = container.querySelector('.oa-newsletter-feedback');
        if (old) old.remove();

        const div = document.createElement('div');
        div.className = 'oa-newsletter-feedback';
        div.setAttribute('role', 'alert');
        div.setAttribute('aria-live', 'polite');

        const isSuccess = type === 'success';
        div.style.cssText = [
            'margin-top: 14px',
            'padding: 12px 20px',
            'border-radius: 8px',
            'font-size: 0.85rem',
            'letter-spacing: 0.05em',
            'font-family: var(--oa-font-body, sans-serif)',
            'text-align: center',
            'opacity: 0',
            'transition: opacity 0.4s ease',
            isSuccess
                ? 'background: rgba(54,34,59,0.08); color: var(--oa-prune, #36223b); border: 1px solid rgba(54,34,59,0.2);'
                : 'background: rgba(220,53,69,0.08); color: #a0243c; border: 1px solid rgba(220,53,69,0.2);',
        ].join(';');

        const icon = isSuccess ? '✓' : '⚠';
        div.textContent = icon + '  ' + message;
        container.appendChild(div);

        // Fade-in
        requestAnimationFrame(() => { div.style.opacity = '1'; });

        // Auto-hide après 6 s pour les succès
        if (isSuccess) {
            setTimeout(() => {
                div.style.opacity = '0';
                setTimeout(() => div.remove(), 400);
            }, 6000);
        }
    }

    function setLoading(btn, emailInput, loading) {
        btn.disabled = loading;
        emailInput.disabled = loading;
        btn.textContent = loading ? 'Envoi…' : "S'abonner";
        btn.style.opacity = loading ? '0.7' : '1';
    }

    // ── Main Handler ───────────────────────────────────────────────────────────
    function initNewsletterForm() {
        const forms = document.querySelectorAll('.oa-newsletter-form');

        forms.forEach(function (form) {
            const emailInput = form.querySelector('.oa-newsletter-email');
            const submitBtn  = form.querySelector('.oa-newsletter-btn');
            const wrapper    = form.closest('.oa-newsletter-wrapper') || form;

            if (!emailInput || !submitBtn) return;

            submitBtn.addEventListener('click', async function (e) {
                e.preventDefault();

                const email = emailInput.value.trim();

                // Validation côté client
                if (!email) {
                    showFeedback(wrapper, 'error', 'Veuillez saisir votre adresse e-mail.');
                    emailInput.focus();
                    return;
                }
                if (!isValidEmail(email)) {
                    showFeedback(wrapper, 'error', 'Adresse e-mail invalide. Veuillez la vérifier.');
                    emailInput.focus();
                    return;
                }

                setLoading(submitBtn, emailInput, true);

                try {
                    const response = await fetch(N8N_WEBHOOK_URL, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: email,
                            source: 'footer_newsletter',
                            site: window.location.hostname,
                            subscribed_at: new Date().toISOString(),
                        }),
                    });

                    if (response.ok) {
                        showFeedback(
                            wrapper,
                            'success',
                            'Bienvenue dans le Cercle O&A Beauty ! 🌸 Vous recevrez bientôt nos exclusivités.'
                        );
                        emailInput.value = '';
                    } else {
                        throw new Error('Réponse serveur : ' + response.status);
                    }
                } catch (err) {
                    console.warn('[OA Newsletter] Erreur webhook n8n :', err);
                    // Fallback : enregistrement local via Odoo (si disponible)
                    try {
                        await fetch('/web/dataset/call_kw', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                jsonrpc: '2.0',
                                method: 'call',
                                params: {
                                    model: 'mailing.contact',
                                    method: 'create',
                                    args: [{ name: email, email: email }],
                                    kwargs: {},
                                },
                            }),
                        });
                        showFeedback(
                            wrapper,
                            'success',
                            'Inscription enregistrée ! Nous vous contacterons bientôt. 🌸'
                        );
                        emailInput.value = '';
                    } catch (_) {
                        showFeedback(
                            wrapper,
                            'error',
                            'Une erreur est survenue. Veuillez réessayer ou nous contacter directement.'
                        );
                    }
                } finally {
                    setLoading(submitBtn, emailInput, false);
                }
            });

            // Soumission par touche Entrée
            emailInput.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') submitBtn.click();
            });
        });
    }

    // Initialisation après chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNewsletterForm);
    } else {
        initNewsletterForm();
    }

})();
