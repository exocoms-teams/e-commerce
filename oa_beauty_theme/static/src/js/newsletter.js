/**
 * oa_beauty_theme — Newsletter Subscription Handler
 * 1) Envoie l'email au controller Odoo (/newsletter/subscribe)
 *    → Odoo appelle directement l'API Brevo (ex-Sendinblue)
 *    → Odoo peut aussi déclencher le webhook n8n (optionnel)
 * 2) Fallback : si Odoo échoue, essaie le webhook n8n directement
 */

(function () {
    'use strict';

    // ── Configuration ──────────────────────────────────────────────────────────
    // URL du webhook n8n (utilisé en fallback uniquement)
    const N8N_WEBHOOK_URL = 'http://82.165.251.136:5678/webhook/newsletter';

    // ── Helpers ────────────────────────────────────────────────────────────────
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
    }

    function showFeedback(container, type, message) {
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

        div.textContent = (isSuccess ? '\u2713  ' : '\u26A0  ') + message;
        container.appendChild(div);

        requestAnimationFrame(function() { div.style.opacity = '1'; });

        if (isSuccess) {
            setTimeout(function() {
                div.style.opacity = '0';
                setTimeout(function() { div.remove(); }, 400);
            }, 7000);
        }
    }

    function setLoading(btn, emailInput, loading) {
        btn.disabled = loading;
        emailInput.disabled = loading;
        btn.textContent = loading ? 'Envoi...' : "S'abonner";
        btn.style.opacity = loading ? '0.7' : '1';
    }

    // ── Appel principal : controller Odoo → Mailchimp ──────────────────────────
    function subscribeViaOdoo(email) {
        return fetch('/newsletter/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                id: 1,
                params: { email: email },
            }),
        })
        .then(function(response) {
            if (!response.ok) throw new Error('HTTP ' + response.status);
            return response.json();
        })
        .then(function(data) {
            return data.result || {};
        });
    }

    // ── Fallback : webhook n8n direct ─────────────────────────────────────────
    function subscribeViaN8n(email) {
        return fetch(N8N_WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: email,
                source: 'footer_newsletter',
                site: window.location.hostname,
                subscribed_at: new Date().toISOString(),
            }),
        })
        .then(function(response) {
            if (!response.ok) throw new Error('n8n HTTP ' + response.status);
            return { success: true, message: 'Bienvenue dans le Cercle O&A Beauty ! Vous recevrez bientot nos exclusivites.' };
        });
    }

    // ── Main Handler ───────────────────────────────────────────────────────────
    function initNewsletterForm() {
        if (!document.body.classList.contains('oa-atelier-theme')) return;
        var forms = document.querySelectorAll('.oa-newsletter-form');

        forms.forEach(function(form) {
            var emailInput = form.querySelector('.oa-newsletter-email');
            var submitBtn  = form.querySelector('.oa-newsletter-btn');
            var wrapper    = form.closest('.oa-newsletter-wrapper') || form;

            if (!emailInput || !submitBtn) return;

            submitBtn.addEventListener('click', function(e) {
                e.preventDefault();

                var email = emailInput.value.trim();

                if (!email) {
                    showFeedback(wrapper, 'error', 'Veuillez saisir votre adresse e-mail.');
                    emailInput.focus();
                    return;
                }
                if (!isValidEmail(email)) {
                    showFeedback(wrapper, 'error', 'Adresse e-mail invalide. Veuillez la verifier.');
                    emailInput.focus();
                    return;
                }

                setLoading(submitBtn, emailInput, true);

                // 1) Priorite : Odoo → Mailchimp
                subscribeViaOdoo(email)
                    .catch(function(odooErr) {
                        // 2) Fallback : n8n direct
                        console.warn('[OA Newsletter] Odoo indisponible, fallback n8n:', odooErr);
                        return subscribeViaN8n(email);
                    })
                    .then(function(result) {
                        if (result.success) {
                            showFeedback(wrapper, 'success', result.message || 'Inscription reussie !');
                            emailInput.value = '';
                        } else {
                            showFeedback(wrapper, 'error', result.message || 'Une erreur est survenue.');
                        }
                    })
                    .catch(function(err) {
                        console.error('[OA Newsletter] Toutes les methodes ont echoue:', err);
                        showFeedback(wrapper, 'error', 'Une erreur est survenue. Veuillez reessayer ou nous contacter directement.');
                    })
                    .finally(function() {
                        setLoading(submitBtn, emailInput, false);
                    });
            });

            // Soumission par touche Entree
            emailInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') submitBtn.click();
            });
        });
    }

    // Initialisation apres chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNewsletterForm);
    } else {
        initNewsletterForm();
    }

})();
