odoo.define('website_planet_mobil.animations', function (require) {
'use strict';
window.addEventListener('scroll', function () {
const cards = document.querySelectorAll(
'.review-card, .product-card'
);
cards.forEach((card) => {
const screen = window.innerHeight;
});
});
const position = card.getBoundingClientRect().top;
if (position < screen- 100) {
card.style.opacity = '1';
card.style.transform = 'translateY(0px)';
}
});