/** @odoo-module **/

import { BaseOptionComponent } from "@html_builder/core/utils";
import { BuilderAction } from "@html_builder/core/builder_action";
import { Plugin } from "@html_editor/plugin";
import { registry } from "@web/core/registry";

/**
 * Options d'éditeur Website Builder du snippet EXOCOMS (Odoo 19) :
 *  - Mise en page : Cartes (Modèle 1) / Accordéon (Modèle 2)  -> classAction
 *  - Comparaison de produits : activée / désactivée            -> classAction
 *  - Filtre Marques : affiché / masqué                         -> classAction
 *  - Produits par page : 24 / 48 / 72                          -> action custom
 */
export class ExocomsSidebarOption extends BaseOptionComponent {
    static template = "exocoms_sidebar_cards.SidebarOption";
    static selector = ".s_exocoms_sidebar";
}

/** Définit l'attribut data-exo-ppg utilisé au rendu initial et par l'AJAX. */
export class ExocomsPpgAction extends BuilderAction {
    static id = "exocomsPpg";

    apply({ editingElement, params: { mainParam } }) {
        editingElement.dataset.exoPpg = mainParam;
    }

    isApplied({ editingElement, params: { mainParam } }) {
        return (editingElement.dataset.exoPpg || "24") === String(mainParam);
    }
}

export class ExocomsSidebarOptionPlugin extends Plugin {
    static id = "exocomsSidebarOption";
    resources = {
        builder_options: [ExocomsSidebarOption],
        builder_actions: { ExocomsPpgAction },
    };
}

registry
    .category("website-plugins")
    .add(ExocomsSidebarOptionPlugin.id, ExocomsSidebarOptionPlugin);
