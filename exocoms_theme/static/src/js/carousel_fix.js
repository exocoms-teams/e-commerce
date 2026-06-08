/** Fix CartService._trackProducts on homepage */
document.addEventListener('DOMContentLoaded', function() {

    // Créer les éléments manquants attendus par CartService
    const selectors = [
        '#o_wsale_products_grid',
        '#product_detail',
        '.o_wsale_products_grid_table',
    ];

    selectors.forEach(function(selector) {
        if (!document.querySelector(selector)) {
            const el = document.createElement('div');
            el.id = selector.replace('#', '').replace('.', '');
            el.style.display = 'none';
            document.body.appendChild(el);
        }
    });

});