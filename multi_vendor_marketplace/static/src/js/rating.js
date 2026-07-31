/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".prod_redirect").forEach(function (el) {
        el.addEventListener("click", function () {
            const url = el.getAttribute("href");
            const newUrl = url.replaceAll(" ", "-");
            el.setAttribute("href", newUrl);
        });
    });

    const postBtn = document.getElementById("post");
    if (postBtn) {
        postBtn.addEventListener("click", async function () {
            const sellerId = document.getElementById("seller")?.value;
            const customerId = document.getElementById("customer")?.value;
            const messageId = document.getElementById("msg")?.value;

            if (!messageId) {
                window.swal({ text: "Please Fill Your Comments!", button: "Close!" });
                return;
            }

            let rating = 0;
            for (let i = 11; i <= 15; i++) {
                const input = document.getElementById("rating" + i);
                if (input && input.checked) {
                    rating = input.value;
                }
            }

            await rpc("/web/dataset/call_kw", {
                model: "seller.review",
                method: "rate_review",
                args: [{
                    seller_id: sellerId,
                    customer_id: customerId,
                    rating: rating,
                    message: messageId,
                }],
                kwargs: {},
            });

            window.swal({
                title: "Rated!",
                text: "Thank You For Your Rating!",
                icon: "success",
                button: "Close!",
            }).then(function () {
                location.reload();
            });
        });
    }

    const postYesBtn = document.getElementById("post_yes");
    if (postYesBtn) {
        postYesBtn.addEventListener("click", async function () {
            const sellerId = document.getElementById("seller")?.value;
            const customerId = document.getElementById("customer")?.value;
            await rpc("/web/dataset/call_kw", {
                model: "seller.recommend",
                method: "recommend_func",
                args: [{ seller_id: sellerId, customer_id: customerId, recommend: "yes" }],
                kwargs: {},
            });
            window.swal({ text: "Thank You!", button: "Close!" });
        });
    }

    const postNoBtn = document.getElementById("post_no");
    if (postNoBtn) {
        postNoBtn.addEventListener("click", async function () {
            const sellerId = document.getElementById("seller")?.value;
            const customerId = document.getElementById("customer")?.value;
            await rpc("/web/dataset/call_kw", {
                model: "seller.recommend",
                method: "recommend_func",
                args: [{ seller_id: sellerId, customer_id: customerId, recommend: "no" }],
                kwargs: {},
            });
            window.swal({ text: "Thank You!", button: "Close!" });
        });
    }
});