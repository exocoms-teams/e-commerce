(function () {

    var confirmationSection = document.querySelector(".sn-confirmation");
    if (!confirmationSection) return;

    // RÉCUPÉRER LE NUMÉRO DE COMMANDE DEPUIS L'UR
    var urlParams  = new URLSearchParams(window.location.search);
    var orderRef   = urlParams.get("order") || "";

    if (orderRef) {
        var orderNumberEl = document.querySelector(".sn-order-number, .sn-confirmation-ref");
        if (orderNumberEl) {
            orderNumberEl.textContent = orderRef;
        }

        // Met aussi à jour dans le titre si présent
        var pageTitleRef = document.querySelector(".sn-order-ref-display");
        if (pageTitleRef) pageTitleRef.textContent = orderRef;
    }

    //  VIDER LE PANIER APRÈS CONFIRMATION 
    clearLocalCart();

    // TÉLÉCHARGEMENT PDF FACTURE 
    var downloadBtn = document.querySelector(".sn-download-invoice, .sn-invoice-btn");

    if (downloadBtn) {
        downloadBtn.addEventListener("click", function (e) {
            e.preventDefault();

            var orderId = this.dataset.orderId || orderRef || "";

            /*BACKEND — Générer et télécharger la facture PDF */

            var pdfUrl = "/sneakers/static/src/pdf/invoice.pdf";
            var link   = document.createElement("a");
            link.href     = pdfUrl;
            link.download = "facture-" + (orderId || "commande") + ".pdf";
            document.body.appendChild(link);
            link.click();
            link.remove();

            if (window.snShowToast) window.snShowToast("Téléchargement de la facture en cours...");
        });
    }

    // LIEN DE SUIVI DE COMMANDE
    var trackBtn = document.querySelector(".sn-track-order, .sn-order-track-btn");

    if (trackBtn && orderRef) {
        trackBtn.href = "/account/order/" + orderRef;

        /* BACKEND — Page de suivi de commande */
    }

    launchConfetti();

    var shareButtons = document.querySelectorAll("[data-share]");
    shareButtons.forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            var platform = this.dataset.share;
            var text     = encodeURIComponent("Je viens de commander mes sneakers sur SNEAKERS Store ! 👟");
            var url      = encodeURIComponent(window.location.origin);

            var shareUrls = {
                twitter:   "https://twitter.com/intent/tweet?text=" + text + "&url=" + url,
                facebook:  "https://www.facebook.com/sharer/sharer.php?u=" + url,
                whatsapp:  "https://wa.me/?text=" + text + "%20" + url,
            };

            if (shareUrls[platform]) {
                window.open(shareUrls[platform], "_blank", "noopener,noreferrer,width=600,height=400");
            }
        });
    });

    function clearLocalCart() {
        var badge = document.querySelector(".sn-cart-count");
        if (badge) {
            badge.textContent   = "0";
            badge.style.display = "none";
        }
    }

    function launchConfetti() {
        
        var COLORS   = ["#111111", "#FFFFFF", "#F9FAFB", "#22C55E", "#6B7280", "#E5E7EB"];
        var container = document.createElement("div");
        container.style.cssText = [
            "position:fixed", "top:0", "left:0", "width:100%", "height:100%",
            "pointer-events:none", "z-index:9999", "overflow:hidden"
        ].join(";");
        document.body.appendChild(container);

        var pieces = 60;
        for (var i = 0; i < pieces; i++) {
            (function (i) {
                setTimeout(function () {
                    var piece = document.createElement("div");
                    var size  = Math.random() * 10 + 6;

                    piece.style.cssText = [
                        "position:absolute",
                        "width:" + size + "px",
                        "height:" + size + "px",
                        "left:" + (Math.random() * 100) + "%",
                        "top:-20px",
                        "background:" + COLORS[Math.floor(Math.random() * COLORS.length)],
                        "border-radius:" + (Math.random() > 0.5 ? "50%" : "2px"),
                        "opacity:0.9",
                        "transition:none"
                    ].join(";");

                    container.appendChild(piece);

                    var startTime = null;
                    var duration  = Math.random() * 2000 + 1500;
                    var startLeft = parseFloat(piece.style.left);
                    var drift     = (Math.random() - 0.5) * 200;
                    var rotation  = Math.random() * 720;

                    function fall(ts) {
                        if (!startTime) startTime = ts;
                        var elapsed = ts - startTime;
                        var pct     = Math.min(elapsed / duration, 1);

                        piece.style.top       = (pct * 110) + "vh";
                        piece.style.left      = (startLeft + drift * pct) + "%";
                        piece.style.opacity   = String(1 - pct * 0.8);
                        piece.style.transform = "rotate(" + (rotation * pct) + "deg)";

                        if (pct < 1) {
                            requestAnimationFrame(fall);
                        } else {
                            piece.remove();
                        }
                    }

                    requestAnimationFrame(fall);
                }, i * 40);
            })(i);
        }

        setTimeout(function () { container.remove(); }, 5000);
    }

})();
