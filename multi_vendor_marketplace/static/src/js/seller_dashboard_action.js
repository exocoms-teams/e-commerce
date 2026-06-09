/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class SellerDashBoard extends Component {
    static template = "SellerDashBoard";

    setup() {
        this.action = useService("action");
        onMounted(() => this._loadDashboard());
    }

    async _loadDashboard() {
        try {
            const res = await rpc("/seller_dashboard");
            if (!res) return;

            const set = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            };

            set("pending", res.pending);
            set("approved", res.approved);
            set("rejected", res.rejected);

            if (res.user_type === false) {
                const el = document.getElementById("check_user_type");
                if (el) el.style.display = "none";
            }

            set("product_pending", res.pending);
            set("product_approved", res.approved);
            set("product_rejected", res.rejected);
            set("seller_pending", res.seller_pending);
            set("seller_approved", res.seller_approved);
            set("seller_rejected", res.seller_rejected);
            set("inventory_pending", res.inventory_pending);
            set("inventory_approved", res.inventory_approved);
            set("inventory_rejected", res.inventory_rejected);
            set("payment_pending", res.payment_pending);
            set("payment_approved", res.payment_approved);
            set("payment_rejected", res.payment_rejected);
            set("order_pending", res.order_pending);
            set("order_approved", res.order_approved);
            set("order_shipped", res.order_shipped);
            set("order_cancel", res.order_cancel);

            this._bindClick("product_pending", "product.template", "kanban",
                [[res.product_kanban_id, "kanban"]], [["state", "=", "pending"]]);
            this._bindClick("product_approved", "product.template", "kanban",
                [[res.product_kanban_id, "kanban"]], [["state", "=", "approved"]]);
            this._bindClick("product_rejected", "product.template", "kanban",
                [[res.product_kanban_id, "kanban"]], [["state", "=", "rejected"]]);
            this._bindClick("divseller_pending", "res.partner", "kanban,form",
                [[false, "kanban"], [false, "form"]], [["state", "=", "Pending for Approval"]]);
            this._bindClick("divseller_approved", "res.partner", "kanban,form",
                [[false, "kanban"], [false, "form"]], [["state", "=", "Approved"]]);
            this._bindClick("divseller_rejected", "res.partner", "kanban,form",
                [[false, "kanban"], [false, "form"]], [["state", "=", "Denied"]]);
            this._bindClick("div_payment_pending", "seller.payment", "list,form",
                [[false, "list"], [false, "form"]], [["state", "=", "Requested"]]);
            this._bindClick("div_payment_approved", "seller.payment", "list,form",
                [[false, "list"], [false, "form"]], [["state", "=", "Validated"]]);
            this._bindClick("div_payment_rejected", "seller.payment", "list,form",
                [[false, "list"], [false, "form"]], [["state", "=", "Rejected"]]);
            this._bindClick("divorder_pending", "sale.order.line", "kanban,form",
                [[res.sale_order_kanban_id, "kanban"], [res.sale_order_form_id, "form"]],
                [["state", "=", "pending"]]);
            this._bindClick("divorder_approved", "sale.order.line", "kanban,form",
                [[res.sale_order_kanban_id, "kanban"], [res.sale_order_form_id, "form"]],
                [["state", "=", "approved"]]);
            this._bindClick("divorder_shipped", "sale.order.line", "kanban,form",
                [[res.sale_order_kanban_id, "kanban"], [res.sale_order_form_id, "form"]],
                [["state", "=", "shipped"]]);
            this._bindClick("divorder_cancel", "sale.order.line", "kanban,form",
                [[res.sale_order_kanban_id, "kanban"], [res.sale_order_form_id, "form"]],
                [["state", "=", "cancel"]]);
        } catch (e) {
            console.error("Dashboard error:", e);
        }
    }

    _bindClick(id, model, viewMode, views, domain) {
        const el = document.getElementById(id);
        if (el) {
            el.style.cursor = "pointer";
            el.addEventListener("click", () => {
                this.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: model,
                    view_mode: viewMode,
                    views: views,
                    domain: domain,
                });
            });
        }
    }
}

registry.category("actions").add("seller_dashboard_tag", SellerDashBoard);