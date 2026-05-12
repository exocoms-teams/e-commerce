document.addEventListener('DOMContentLoaded', function() {
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('mn-visible');
            }
        });
    }, { threshold: 0.12 });

    document.querySelectorAll('.mn-stat, .mn-card--solution, .mn-product-card, .mn-review, .mn-section__header, .mn-cta__inner').forEach(function(el, i) {
        el.style.transitionDelay = (i % 4 * 0.08) + 's';
        observer.observe(el);
    });
});
