/** @odoo-module **/

// En Odoo 19, on cible directement l'alias du module de paiement officiel
import paymentForm from '@payment/js/payment_form';

paymentForm.include({
    /**
     * Surcharge de la soumission globale du formulaire en Odoo 19
     * @override
     */
    async submitForm(ev) {
        const mandatForm = document.getElementById('mandat_administratif_form');
        // Détection propre : est-ce que le bloc de notre mandat est visible à l'écran ?
        const isMandatSelected = mandatForm && mandatForm.offsetParent !== null;

        if (isMandatSelected) {
            if (ev) {
                ev.preventDefault();
                ev.stopPropagation();
            }

            console.log("🎯 Interception Odoo 19 : Traitement du Mandat Administratif.");

            const siret = document.getElementById('mandat_siret')?.value?.trim();
            const iban = document.getElementById('mandat_iban')?.value?.trim();
            const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
            const comptable = document.getElementById('mandat_comptable')?.value?.trim();
            const errorDiv = document.getElementById('mandat_form_error');

            // 1. Validation de sécurité des entrées
            if (!siret || !iban || !ordonnateur || !comptable) {
                if (errorDiv) errorDiv.style.display = 'block';
                
                // Réactivation des boutons via les helpers natifs d'Odoo 19
                this._enableButton?.();
                const button = document.querySelector('.o_payment_submit_button, button[name="o_payment_submit_button"]');
                if (button) {
                    button.disabled = false;
                    button.classList.remove('disabled');
                }
                return; // Bloque le paiement
            }

            if (errorDiv) errorDiv.style.display = 'none';

            // 2. Gestion visuelle du Loader sur le bouton
            const button = document.querySelector('.o_payment_submit_button, button[name="o_payment_submit_button"]');
            let originalHtml = "";
            if (button) {
                originalHtml = button.innerHTML;
                button.disabled = true;
                button.classList.add('disabled');
                button.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Traitement en cours...';
            }

            // 3. Traitement Backend (Transmission JSON-RPC sécurisée vers ton contrôleur Python)
            try {
                const response = await fetch('/mandat/save_checkout_data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: {
                            siret: siret,
                            iban: iban,
                            ordonnateur: ordonnateur,
                            qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                            comptable: comptable,
                            ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                            service: document.getElementById('mandat_service')?.value?.trim() || '',
                            reference: document.getElementById('mandat_reference')?.value?.trim() || ''
                        }
                    })
                });

                const result = await response.json();

                if (result.error) {
                    console.error("Erreur serveur Odoo 19 :", result.error);
                    alert("Une erreur est survenue sur le serveur : " + (result.error.data?.message || result.error.message));
                    if (button) {
                        button.disabled = false;
                        button.classList.remove('disabled');
                        button.innerHTML = originalHtml;
                    }
                    this._enableButton?.();
                    return;
                }

                // 4. Succès -> Redirection standard Odoo 19
                console.log("✅ Enregistrement validé. Transfert vers le statut final.");
                window.location.assign('/payment/status');

            } catch (err) {
                console.error("Échec de la communication réseau :", err);
                alert("Impossible de joindre le serveur de validation.");
                if (button) {
                    button.disabled = false;
                    button.classList.remove('disabled');
                    button.innerHTML = originalHtml;
                }
                this._enableButton?.();
            }

            // Retenir le flux : on ne fait volontairement PAS appel à this._super()
            // afin de neutraliser le déclenchement de la méthode _processRedirectFlow d'Odoo.
            return;
        }

        // Si l'utilisateur a choisi Stripe, PayPal, etc., on redonne la main à l'implémentation standard
        return this._super(...arguments);
    }
});
