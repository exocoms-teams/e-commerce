// Monetiques.fr - Premium Interactions and Security
document.addEventListener('DOMContentLoaded', function () {
    // 1. Prevent Double Form Submission (Security)
    const callbackForm = document.querySelector('form[action="/contrat/callback"]');
    if (callbackForm) {
        callbackForm.addEventListener('submit', function (e) {
            const submitBtn = callbackForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                // Disable button to prevent spamming
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i> Envoi en cours...';
            }
        });
    }

    // 2. Interactive Product Card Elevation Glow (Design)
    const cards = document.querySelectorAll('.product-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.borderColor = 'rgba(6, 182, 212, 0.4)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.borderColor = 'rgba(226, 232, 240, 0.8)';
        });
    });
});
