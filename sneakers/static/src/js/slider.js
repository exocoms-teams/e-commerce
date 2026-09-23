(function () {

    var hero = document.querySelector(".sn-hero");
    if (!hero) return;

    var slides    = hero.querySelectorAll(".sn-slide");
    var dots      = hero.querySelectorAll(".sn-slider-dots span");
    var nextBtn   = hero.querySelector(".sn-slider-next");
    var prevBtn   = hero.querySelector(".sn-slider-prev");

    if (!slides.length) return;

    var currentSlide = 0;
    var totalSlides  = slides.length;
    var autoInterval = null;
    var AUTO_DELAY   = 5000;

    function showSlide(index) {
        slides.forEach(function (s) { s.classList.remove("active"); });
        dots.forEach(function (d)   { d.classList.remove("active"); });

        currentSlide = (index + totalSlides) % totalSlides;

        slides[currentSlide].classList.add("active");
        if (dots[currentSlide]) dots[currentSlide].classList.add("active");
    }

    function nextSlide() { showSlide(currentSlide + 1); }
    function prevSlide()  { showSlide(currentSlide - 1); }

    function startAuto() {
        stopAuto();
        autoInterval = setInterval(nextSlide, AUTO_DELAY);
    }

    function stopAuto() {
        if (autoInterval) {
            clearInterval(autoInterval);
            autoInterval = null;
        }
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", function () {
            nextSlide();
            startAuto();
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener("click", function () {
            prevSlide();
            startAuto();
        });
    }

    dots.forEach(function (dot, i) {
        dot.addEventListener("click", function () {
            showSlide(i);
            startAuto();
        });
    });

    hero.addEventListener("mouseenter", stopAuto);
    hero.addEventListener("mouseleave", startAuto);

    var touchStartX = 0;
    var touchEndX   = 0;
    var SWIPE_MIN   = 50;

    hero.addEventListener("touchstart", function (e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    hero.addEventListener("touchend", function (e) {
        touchEndX = e.changedTouches[0].screenX;
        var diff  = touchStartX - touchEndX;

        if (Math.abs(diff) > SWIPE_MIN) {
            if (diff > 0) {
                nextSlide();
            } else {
                prevSlide();
            }
            startAuto();
        }
    }, { passive: true });

    showSlide(0);
    startAuto();

})();
