document.addEventListener("DOMContentLoaded", () => {

    const hero = document.querySelector(".sn-hero");

    if (!hero) {
        return;
    }

    const slides = hero.querySelectorAll(".sn-slide");
    const dots = hero.querySelectorAll(".sn-slider-dots span");
    const nextBtn = hero.querySelector(".sn-slider-next");
    const prevBtn = hero.querySelector(".sn-slider-prev");

    if (!slides.length) {
        return;
    }

    let currentSlide = 0;
    const totalSlides = slides.length;

    function showSlide(index) {

        slides.forEach((slide) => slide.classList.remove("active"));
        dots.forEach((dot) => dot.classList.remove("active"));

        slides[index].classList.add("active");

        if (dots[index]) {
            dots[index].classList.add("active");
        }

        currentSlide = index;
    }

    function nextSlide() {
        showSlide((currentSlide + 1) % totalSlides);
    }

    function previousSlide() {
        showSlide((currentSlide - 1 + totalSlides) % totalSlides);
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", nextSlide);
    }

    if (prevBtn) {
        prevBtn.addEventListener("click", previousSlide);
    }

    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => showSlide(index));
    });

    // Pas d'auto-défilement : navigation manuelle uniquement (flèches + dots).

});