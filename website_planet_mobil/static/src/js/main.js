document.addEventListener('DOMContentLoaded', function () {

    
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    
    fetch('/shop/cart/quantity')
        .then(function (res) { return res.json(); })
        .then(function (data) {
            const count = document.querySelector('.cart-count');
            if (count && data.quantity !== undefined) {
                count.textContent = data.quantity;
                count.style.display = data.quantity > 0 ? 'flex' : 'none';
            }
        })
        .catch(function () {});

    
    const btn = document.querySelector('.newsletter-btn');
    const input = document.querySelector('.newsletter-input');
    if (btn && input) {
        btn.addEventListener('click', function () {
            const email = input.value.trim();
            if (email && email.includes('@')) {
                alert('Merci ! Vous êtes inscrit à notre newsletter.');
                input.value = '';
            } else {
                alert('Veuillez entrer une adresse email valide.');
            }
        });
    }

});