// Page avis

document.addEventListener('DOMContentLoaded', function () {

    // ===== ÉTOILES =====
    document.querySelectorAll('.star').forEach(star => {
        star.addEventListener('mouseover', function () {
            const val = this.dataset.value;
            document.querySelectorAll('.star').forEach(s => {
                s.classList.toggle('active', s.dataset.value <= val);
            });
        });

        star.addEventListener('click', function () {
            document.getElementById('avis-note').value = this.dataset.value;
        });
    });

    document.getElementById('star-rating').addEventListener('mouseleave', function () {
        const note = document.getElementById('avis-note').value;
        document.querySelectorAll('.star').forEach(s => {
            s.classList.toggle('active', s.dataset.value <= note);
        });
    });
    // ===== RECHERCHE =====
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') lancerRecherche();
        });
    }

    // ===== NEWSLETTER =====
    const btnNewsletter = document.querySelector('.btn-newsletter');
    if (btnNewsletter) {
        btnNewsletter.addEventListener('click', function (e) {
            e.preventDefault();
            const input = document.querySelector('.newsletter-input');
            if (!input.value.trim()) {
                alert('Merci de saisir votre adresse email.');
                return;
            }
            // Message de confirmation
            input.value = '';
            btnNewsletter.textContent = '✅ Inscrit !';
            btnNewsletter.style.backgroundColor = '#2C3A4B';
            setTimeout(() => {
                btnNewsletter.textContent = "S'inscrire →";
                btnNewsletter.style.backgroundColor = '';
            }, 3000);
        });
    }

});

// ===== AVIS =====
function envoyerAvis() {
    const nom = document.getElementById('avis-nom').value.trim();
    const note = document.getElementById('avis-note').value;
    const produit = document.getElementById('avis-produit').value.trim();
    const commentaire = document.getElementById('avis-commentaire').value.trim();

    if (!nom || note == 0 || !commentaire) {
        alert('Merci de remplir tous les champs obligatoires (*)');
        return;
    }

    const starsHtml = '★'.repeat(note) + '☆'.repeat(5 - note);
    const card = `
        <div class="col-md-4 mb-4">
            <div class="avis-card">
                <div class="avis-stars">${starsHtml}</div>
                ${produit ? `<p class="avis-produit">🛏️ ${produit}</p>` : ''}
                <p class="avis-texte">"${commentaire}"</p>
                <strong class="avis-auteur">${nom}</strong>
                <span class="avis-date"> — à l'instant</span>
            </div>
        </div>
    `;

    document.getElementById('avis-container').innerHTML += card;
    document.getElementById('avis-success').style.display = 'block';

    document.getElementById('avis-nom').value = '';
    document.getElementById('avis-note').value = 0;
    document.getElementById('avis-produit').value = '';
    document.getElementById('avis-commentaire').value = '';
    document.querySelectorAll('.star').forEach(s => s.classList.remove('active'));

    document.getElementById('avis-container').scrollIntoView({ behavior: 'smooth' });
}

// ===== CONTACT =====
function envoyerContact() {
    const nom = document.getElementById('c-nom').value.trim();
    const prenom = document.getElementById('c-prenom').value.trim();
    const email = document.getElementById('c-email').value.trim();
    const message = document.getElementById('c-message').value.trim();

    if (!nom || !prenom || !email || !message) {
        alert('Merci de remplir tous les champs obligatoires (*)');
        return;
    }

    document.getElementById('contact-success').style.display = 'block';

    document.getElementById('c-nom').value = '';
    document.getElementById('c-prenom').value = '';
    document.getElementById('c-email').value = '';
    document.getElementById('c-tel').value = '';
    document.getElementById('c-sujet').value = '';
    document.getElementById('c-message').value = '';

    window.scrollTo({
        top: document.querySelector('.contact-form-box').offsetTop - 100,
        behavior: 'smooth'
    });
}

// ===== FAQ ACCORDION =====
function toggleFaq(btn) {
    const answer = btn.nextElementSibling;
    const isOpen = answer.classList.contains('open');

    
    document.querySelectorAll('.faq-answer').forEach(a => {
        a.classList.remove('open');
    });
    document.querySelectorAll('.faq-question').forEach(q => {
        q.classList.remove('active');
    });


    if (!isOpen) {
        answer.classList.add('open');
        btn.classList.add('active');
    }
}