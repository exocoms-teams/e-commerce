document.addEventListener("DOMContentLoaded", function () {

    const slider = document.querySelector(".sn-slider");

    if (!slider) return;

    const slides = slider.querySelectorAll(".sn-slide");
    const dots = slider.querySelectorAll(".sn-slider-dots span");
    const nextBtn = slider.querySelector(".sn-slider-next");
    const prevBtn = slider.querySelector(".sn-slider-prev");

    let current = 0;
    let timer = null;

    function activateSlide(index){

        slides.forEach((slide)=>{

            slide.classList.remove("active");

        });

        dots.forEach((dot)=>{

            dot.classList.remove("active");

        });

        slides[index].classList.add("active");

        if(dots[index]){

            dots[index].classList.add("active");

        }

        current = index;

    }

    function next(){

        current++;

        if(current >= slides.length){

            current = 0;

        }

        activateSlide(current);

    }

    function previous(){

        current--;

        if(current < 0){

            current = slides.length-1;

        }

        activateSlide(current);

    }

    function start(){

        stop();

        timer = setInterval(next,5000);

    }

    function stop(){

        if(timer){

            clearInterval(timer);

        }

    }

    nextBtn?.addEventListener("click",()=>{

        next();

        start();

    });

    prevBtn?.addEventListener("click",()=>{

        previous();

        start();

    });

    dots.forEach((dot,index)=>{

        dot.addEventListener("click",()=>{

            activateSlide(index);

            start();

        });

    });

    slider.addEventListener("mouseenter",stop);

    slider.addEventListener("mouseleave",start);

    activateSlide(0);

    start();

});