/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.WinnersIngestionWidget = publicWidget.Widget.extend({
    selector: '.o_winners_dashboard_header',
    
    events: {
        'click #btn_run_scan': '_onRunEbayScan',
        'click #btn_run_meta_scan': '_onRunMetaScan',
    },

    /**
     * Fonction centralisée pour gérer l'état UI et les requêtes RPC
     */
    async _executeScan(route, params, $btn, $alert, originalText, successTemplate) {
        // État de chargement visuel
        $btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> Traitement en cours...');
        $alert.addClass('d-none').removeClass('alert-warning alert-success alert-danger');

        try {
            // Appel AJAX (RPC) vers le contrôleur Python
            const data = await rpc(route, params);
            
            // Restauration du bouton
            $btn.prop('disabled', false).html(originalText);
            $alert.removeClass('d-none');
            
            if (data.status === 'success') {
                $alert.addClass('alert-success')
                      .html('<strong>✅ Succès !</strong> ' + successTemplate.replace('{count}', data.inserted));
            } else {
                $alert.addClass('alert-danger')
                      .html('<strong>❌ Erreur :</strong> ' + (data.message || "Réponse serveur invalide."));
            }
        } catch (error) {
            // Erreur serveur (500) ou réseau
            $btn.prop('disabled', false).html(originalText);
            $alert.removeClass('d-none').addClass('alert-danger')
                  .html('<strong>❌ Erreur :</strong> Problème de communication avec le serveur Odoo.');
            console.error("Erreur RPC Ingestion:", error);
        }
    },

    /**
     * Action : Scanner sur eBay
     */
    async _onRunEbayScan(ev) {
        ev.preventDefault();
        const keyword = this.$('#ebay_keyword').val().trim();
        const $alert = this.$('#ebay_alert');
        const $btn = this.$('#btn_run_scan');

        if (!keyword) {
            $alert.removeClass('d-none alert-success alert-danger').addClass('alert-warning')
                  .html('⚠️ Veuillez entrer un mot-clé pour eBay.');
            return;
        }

        await this._executeScan(
            '/dashboard/run_ebay_scan',
            { keyword: keyword },
            $btn,
            $alert,
            '<i class="fa fa-download"></i> Lancer l\'ingestion eBay',
            '{count} produits qualifiés ont été injectés.'
        );
    },

    /**
     * Action : Scanner manuel sur Meta Ads
     */
    async _onRunMetaScan(ev) {
        ev.preventDefault();
        const keyword = this.$('#meta_keyword').val().trim();
        const $alert = this.$('#meta_alert');
        const $btn = this.$('#btn_run_meta_scan');

        if (!keyword) {
            $alert.removeClass('d-none alert-success alert-danger').addClass('alert-warning')
                  .html('⚠️ Veuillez entrer un mot-clé pour Meta Ads.');
            return;
        }

        await this._executeScan(
            '/dashboard/run_meta_scan',
            { keyword: keyword },
            $btn,
            $alert,
            '<i class="fa fa-search"></i> Scanner les publicités',
            '{count} publicités ont été liées.'
        );
    }

});