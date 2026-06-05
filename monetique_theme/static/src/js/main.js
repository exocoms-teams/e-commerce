document.addEventListener('DOMContentLoaded', function () {

    // ── Carousel ──
    const slides = document.querySelectorAll('.mq-slide');
    const dots = document.querySelectorAll('.mq-dot');
    let current = 0;
    let timer;

    function goTo(n) {
        slides[current].classList.remove('active');
        dots[current].classList.remove('active');
        current = (n + slides.length) % slides.length;
        slides[current].classList.add('active');
        dots[current].classList.add('active');
    }

    function next() { goTo(current + 1); }
    function prev() { goTo(current - 1); }

    function startAuto() {
        clearInterval(timer);
        timer = setInterval(next, 5000);
    }

    if (slides.length > 0) {
        document.getElementById('mq-next')?.addEventListener('click', () => { next(); startAuto(); });
        document.getElementById('mq-prev')?.addEventListener('click', () => { prev(); startAuto(); });
        dots.forEach((dot, i) => dot.addEventListener('click', () => { goTo(i); startAuto(); }));
        startAuto();
    }

    // ── Navbar scroll ──
    const navbar = document.getElementById('mq-navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.style.boxShadow = window.scrollY > 10
                ? '0 2px 20px rgba(10,36,99,.1)' : 'none';
        });
    }

    // ── Smooth scroll ──
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        });
    });

    // ── Fade in on scroll ──
    const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.style.opacity = '1';
                e.target.style.transform = 'translateY(0)';
                obs.unobserve(e.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.mq-pcard, .mq-scard, .mq-rcard, .mq-adv-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity .5s ease, transform .5s ease';
        obs.observe(el);
    });
});
