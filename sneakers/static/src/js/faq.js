(function () {

    const questions = document.querySelectorAll(".sn-faq-question");

    if (!questions.length) {
        return;
    }

    questions.forEach(question => {

        question.addEventListener("click", function () {

            const item = this.parentElement;

            const opened = document.querySelector(".sn-faq-item.active");

            if (opened && opened !== item) {

                opened.classList.remove("active");

                opened.querySelector(".sn-faq-icon").textContent = "+";

            }

            item.classList.toggle("active");

            const icon = item.querySelector(".sn-faq-icon");

            icon.textContent = item.classList.contains("active")
                ? "−"
                : "+";

        });

    });

})();