function initCarousel() {
    var slides = document.querySelectorAll('#heroCarousel .mn-carousel__slide');
    if (!slides.length) return;
    var current = 0;
    setInterval(function() {
        slides[current].classList.remove('active');
        current = (current + 1) % slides.length;
        slides[current].classList.add('active');
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initCarousel, 500);
});
