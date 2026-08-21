/** @odoo-module **/

import { whenReady } from "@odoo/owl";

function showCopyConfirmation(confirmation) {
    if (!confirmation) {
        return;
    }

    confirmation.classList.add("visible");

    setTimeout(() => {
        confirmation.classList.remove("visible");
    }, 2500);
}

whenReady(() => {
    const fichePage = document.querySelector(".fiche-technique-page");

    if (!fichePage) {
        return;
    }

    const printButton = fichePage.querySelector("#btn-fiche-imprimer");
    const shareButton = fichePage.querySelector("#btn-fiche-partager");
    const confirmation = fichePage.querySelector(
        "#fiche-partage-confirmation"
    );

    if (printButton) {
        printButton.addEventListener("click", () => {
            window.print();
        });
    }

    if (shareButton) {
        shareButton.addEventListener("click", async () => {
            const url = window.location.href;
            const shareData = {
                title: document.title,
                url,
            };

            if (navigator.share) {
                try {
                    await navigator.share(shareData);
                    return;
                } catch (error) {
                    if (error.name === "AbortError") {
                        return;
                    }
                }
            }

            if (navigator.clipboard?.writeText) {
                try {
                    await navigator.clipboard.writeText(url);
                    showCopyConfirmation(confirmation);
                } catch (error) {
                    console.warn(
                        "Impossible de copier le lien de la fiche technique.",
                        error
                    );
                }
            }
        });
    }
});
