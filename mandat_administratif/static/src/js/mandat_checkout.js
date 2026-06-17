/** @odoo-module **/
import { PaymentForm } from '@payment/js/payment_form';
import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';

patch(PaymentForm.prototype, {

    async submitForm() {
        // On récupère directement notre bloc de formulaire dans le DOM
        const mandatForm = document.getElementById('mandat_administratif_form');
        
        // condition absolue : si le formulaire existe ET qu'il est visible à l'écran
        const isMandatSelected = mandatForm && mandatForm.offsetParent !== null;

        console.log("=== CHECK LOGIQUE MANDAT ===");
        console.log("Formulaire trouvé ?", !!mandatForm);
        console.log("Le mandat est-il l'option cochée ?", isMandatSelected);

        if (isMandatSelected) {
            console.log("🎯 Mandat détecté ! Interception complète du flux Odoo.");
            
            const siret = document.getElementById('mandat_siret')?.value?.trim();
            const iban = document.getElementById('mandat_iban')?.value?.trim();
            const ordonnateur = document.getElementById('mandat_ordonnateur')?.value?.trim();
            const comptable = document.getElementById('mandat_comptable')?.value?.trim();
            const errorDiv = document.getElementById('mandat_form_error');

            // Validation des champs requis
            if (!siret || !iban || !ordonnateur || !comptable) {
                if (errorDiv) errorDiv.style.display = 'block';
                console.log("❌ Formulaire incomplet : arrêt du traitement.");
                return; 
            }
            if (errorDiv) errorDiv.style.display = 'none';

            // Envoi des données vers le serveur (Python)
            await rpc('/mandat/save_checkout_data', {
                siret, iban, ordonnateur,
                qualite: document.getElementById('mandat_qualite')?.value?.trim() || '',
                comptable,
                ej: document.getElementById('mandat_ej')?.value?.trim() || '',
                service: document.getElementById('mandat_service')?.value?.trim() || '',
                reference: document.getElementById('mandat_reference')?.value?.trim() || '',
            });

            console.log("🚀 Données sauvegardées avec succès. Redirection...");
            window.location.assign('/payment/status');
            return; // Bloque définitivement le traitement natif d'Odoo
        }
        
        // Si ce n'est pas le mandat, on laisse Odoo faire son travail habituel
        return super.submitForm(...arguments);
    },
});
