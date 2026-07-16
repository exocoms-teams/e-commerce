/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class SellerDashBoard extends Component {
    static template = "SellerDashBoard";

    setup() {
        this.actionService = useService("action");
        onMounted(async () => {
            try {
                const res = await rpc("/seller_dashboard");
                if (!res) return;
                this._populate(res);
                this._bindClicks(res);
            } catch(e) {
                console.error("Dashboard load error:", e);
            }
        });
    }

    _set(id, val) {
        const el = document.getElementById(id);
        if (el) el.textContent = val ?? "";
    }

    _populate(res) {
        this._set("pending", res.pending);
        this._set("approved", res.approved);
        this._set("rejected", res.rejected);
        this._set("seller_pending", res.seller_pending);
        this._set("seller_approved", res.seller_approved);
        this._set("seller_rejected", res.seller_rejected);
        this._set("inventory_pending", res.inventory_pending);
        this._set("inventory_approved", res.inventory_approved);
        this._set("inventory_rejected", res.inventory_rejected);
        this._set("payment_pending", res.payment_pending);
        this._set("payment_approved", res.payment_approved);
        this._set("payment_rejected", res.payment_rejected);
        this._set("order_pending", res.order_pending);
        this._set("order_approved", res.order_approved);
        this._set("order_shipped", res.order_shipped);
        this._set("order_cancel", res.order_cancel);

        if (res.user_type === false) {
            const el = document.getElementById("check_user_type");
            if (el) el.style.display = "none";
        }
    }

    _bindClicks(res) {
        const bind = (id, model, viewMode, views, domain) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.style.cursor = "pointer";
            el.addEventListener("click", () => {
                this.actionService.doAction({
                    type: "ir.actions.act_window",
                    name: id,
                    res_model: model,
                    view_mode: viewMode,
                    views: views,
                    domain: domain,
                });
            });
        };

        bind("product_pending", "product.template", "kanban,form",
            [[res.product_kanban_id, "kanban"], [false, "form"]],
            [["state", "=", "pending"]]);
        bind("product_approved", "product.template", "kanban,form",
            [[res.product_kanban_id, "kanban"], [false, "form"]],
            [["state", "=", "approved"]]);
        bind("product_rejected", "product.template", "kanban,form",
            [[res.product_kanban_id, "kanban"], [false, "form"]],
            [["state", "=", "rejected"]]);
        bind("divseller_pending", "res.partner", "kanban,form",
            [[false, "kanban"], [false, "form"]],
            [["state", "=", "Pending for Approval"]]);
        bind("divseller_approved", "res.partner", "kanban,form",
            [[false, "kanban"], [false, "form"]],
            [["state", "=", "Approved"]]);
        bind("divseller_rejected", "res.partner", "kanban,form",
            [[false, "kanban"], [false, "form"]],
            [["state", "=", "Denied"]]);
        bind("div_payment_pending", "seller.payment", "list,form",
            [[false, "list"], [false, "form"]],
            [["state", "=", "Requested"]]);
        bind("div_payment_approved", "seller.payment", "list,form",
            [[false, "list"], [false, "form"]],
            [["state", "=", "Validated"]]);
        bind("div_payment_rejected", "seller.payment", "list,form",
            [[false, "list"], [false, "form"]],
            [["state", "=", "Rejected"]]);
        bind("divorder_pending", "sale.order.line", "kanban,form",
            [[res.sale_order_kanban_id, "kanban"], [res.sale_order_form_id, "form"]],
            [["state", "=", "pending"]]);
        bind("divorder_approved", "sale.order.line", "kanban,form",
            [[res.sale_order_kanban_id, "kanban"], [res.sale_order_form_id, "form"]],
            [["state", "=", "approved"]]);
        bind("divorder_shipped", "sale.order.line", "kanban,form",
            [[res.sale_order_kanban_id, "kanban"], [res.sale_order_form_id, "form"]],
            [["state", "=", "shipped"]]);
        bind("divorder_cancel", "sale.order.line", "kanban,form",
            [[res.sale_order_kanban_id, "kanban"], [res.sale_order_form_id, "form"]],
            [["state", "=", "cancel"]]);
        bind("inv_req_pending", "inventory.request", "kanban,form",
            [[false, "kanban"], [false, "form"]],
            [["state", "=", "Requested"]]);
        bind("inv_req_approved", "inventory.request", "kanban,form",
            [[false, "kanban"], [false, "form"]],
            [["state", "=", "Approved"]]);
        bind("inv_req_rejected", "inventory.request", "kanban,form",
            [[false, "kanban"], [false, "form"]],
            [["state", "=", "Rejected"]]);
    }
}

registry.category("actions").add("seller_dashboard_tag", SellerDashBoard);