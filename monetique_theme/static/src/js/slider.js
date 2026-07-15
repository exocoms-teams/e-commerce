document.addEventListener("DOMContentLoaded", () => {

    const slides = document.querySelectorAll(".sn-slide");
    const dots = document.querySelectorAll(".sn-slider-dots span");
    const nextBtn = document.querySelector(".sn-slider-next");
    const prevBtn = document.querySelector(".sn-slider-prev");

    if (!slides.length) {
        return;
    }

    let currentSlide = 0;
    const totalSlides = slides.length;

    function showSlide(index) {

        slides.forEach((slide) => {
            slide.classList.remove("active");
        });

        dots.forEach((dot) => {
            dot.classList.remove("active");
        });

        slides[index].classList.add("active");

        if (dots[index]) {
            dots[index].classList.add("active");
        }

        currentSlide = index;
    }

    function nextSlide() {

        let index = currentSlide + 1;

        if (index >= totalSlides) {
            index = 0;
        }

        showSlide(index);
    }

    function previousSlide() {

        let index = currentSlide - 1;

        if (index < 0) {
            index = totalSlides - 1;
        }

        showSlide(index);
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", nextSlide);
    }

    if (prevBtn) {
        prevBtn.addEventListener("click", previousSlide);
    }

    dots.forEach((dot, index) => {

        dot.addEventListener("click", () => {

            showSlide(index);

        });

    });

    setInterval(nextSlide, 5000);

});