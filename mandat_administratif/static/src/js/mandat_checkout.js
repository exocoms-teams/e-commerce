(function() {
    'use strict';

    // On écoute le clic sur TOUT le document, mais en mode CAPTURE (le paramètre true à la fin)
    document.addEventListener('click', async function(ev) {
        
        // On vérifie si l'élément cliqué est le bouton de paiement d'Odoo
        const button = ev.target.closest('button[name="o_payment_submit_button"], .o_payment_submit_button');
        if (!button) return;

        const mandatForm = document.getElementById('mandat_administratif_form');
        const isMandatSelected = mandatForm && mandatForm.offsetParent !== null;

        // Si le mandat administratif est l'option sélectionnée à l'écran
        if (isMandatSelected) {
            
            // 🛑 ICI ON COUPE DIRECTEMENT L'HERBE SOUS LE PIED D'ODOO
            ev.preventDefault();
            ev.stopPropagation();
            ev.stopImmediatePropagation();

            console.log("🎯 Interception native absolue du Mandat Administratif.");

            const siret = document.getElementById('mandat_siret')?.value?.trim();
            const iban = document.getElementById('mandat_iban')?.value?.trim();
            const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
            const comptable = document.getElementById('mandat_comptable')?.value?.trim();
            const errorDiv = document.getElementById('mandat_form_error');

            // Validation des champs
            if (!siret || !iban || !ordonnateur || !comptable) {
                if (errorDiv) errorDiv.style.display = 'block';
                return;
            }
            if (errorDiv) errorDiv.style.display = 'none';

            // Effet visuel de chargement sur le bouton
            const originalHtml = button.innerHTML;
            button.disabled = true;
            button.classList.add('disabled');
            button.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Traitement en cours...';

            try {
                // Envoi des données en JSON-RPC standard vers ton contrôleur Python
                const response = await fetch('/mandat/save_checkout_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
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

                // Gestion d'une erreur venant du Python
                if (result.error) {
                    console.error("Erreur serveur Odoo:", result.error);
                    alert("Erreur serveur : " + (result.error.data?.message || result.error.message));
                    button.disabled = false;
                    button.classList.remove('disabled');
                    button.innerHTML = originalHtml;
                    return;
                }

                console.log("✅ Données sauvegardées, redirection...");
                window.location.assign('/payment/status');

            } catch (err) {
                console.error("Erreur réseau / Fetch:", err);
                alert("Une erreur technique est survenue lors de la communication avec le serveur.");
                button.disabled = false;
                button.classList.remove('disabled');
                button.innerHTML = originalHtml;
            }
        }
    }, true); // <-- CE 'TRUE' EST LA CLÉ : Phase de capture pour s'exécuter AVANT Odoo
})();
