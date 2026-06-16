/** @odoo-module **/
/**
 * EXOCOMS – Options Website Builder pour le snippet Filtre Sidebar
 * snippet_editor.js  |  Odoo 19
 *
 * En Odoo 19, les options snippet utilisent le système we-* XML (data-js)
 * combiné avec une classe JS héritant de SnippetOption.
 *
 * Le composant est enregistré via le registry "website_snippet_options"
 * avec un sélecteur CSS correspondant au data-js dans snippet_options.xml.
 */

import { SnippetOption } from "@website/js/editor/snippets.options";
import { registry } from "@web/core/registry";

const ExoFilterSidebarOption = SnippetOption.extend({

    /**
     * Appelé quand l'utilisateur change le nombre de produits par page
     * via le we-select dans snippet_options.xml.
     * @param {boolean} previewMode
     * @param {string} widgetValue - valeur sélectionnée
     * @param {Object} params
     */
    async setProductsPerPage(previewMode, widgetValue, params) {
        this.$target[0].dataset.productsPerPage = widgetValue;
    },

    /**
     * Retourne la valeur actuelle de productsPerPage pour que le
     * we-select affiche la bonne option sélectionnée.
     */
    async _computeWidgetState(methodName, params) {
        if (methodName === 'setProductsPerPage') {
            return this.$target[0].dataset.productsPerPage || '12';
        }
        return this._super(...arguments);
    },
});

// Enregistrement dans le registry Odoo 19 snippet options
// data-js="ExoFilterSidebarOption" dans snippet_options.xml
// pointe vers cette clé du registry
registry.category("website_snippet_options").add(
    "ExoFilterSidebarOption",
    ExoFilterSidebarOption
);
