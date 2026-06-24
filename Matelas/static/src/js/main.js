// Page avis

// Gestion des étoiles
document.querySelectorAll('.star').forEach(star => {
    star.addEventListener('mouseover', function() {
        const val = this.dataset.value;
        document.querySelectorAll('.star').forEach(s => {
            s.classList.toggle('active', s.dataset.value <= val);
        });
    });

    star.addEventListener('click', function() {
        document.getElementById('avis-note').value = this.dataset.value;
    });
});

document.getElementById('star-rating').addEventListener('mouseleave', function() {
    const note = document.getElementById('avis-note').value;
    document.querySelectorAll('.star').forEach(s => {
        s.classList.toggle('active', s.dataset.value <= note);
    });
});

// Envoyer l'avis (stocké en local pour l'instant)
function envoyerAvis() {
    const nom = document.getElementById('avis-nom').value.trim();
    const note = document.getElementById('avis-note').value;
    const produit = document.getElementById('avis-produit').value.trim();
    const commentaire = document.getElementById('avis-commentaire').value.trim();

    if (!nom || note == 0 || !commentaire) {
        alert('Merci de remplir tous les champs obligatoires (*)');
        return;
    }

    // Créer la carte avis
    const stars = '★'.repeat(note) + '☆'.repeat(5 - note);
    const card = `
        <div class="col-md-4 mb-4">
            <div class="avis-card">
                <div class="avis-stars">${stars}</div>
                ${produit ? `<p class="avis-produit">🛏️ ${produit}</p>` : ''}
                <p class="avis-texte">"${commentaire}"</p>
                <strong class="avis-auteur">${nom}</strong>
                <span class="avis-date"> — à l'instant</span>
            </div>
        </div>
    `;

    document.getElementById('avis-container').innerHTML += card;
    document.getElementById('avis-success').style.display = 'block';

    // Reset
    document.getElementById('avis-nom').value = '';
    document.getElementById('avis-note').value = 0;
    document.getElementById('avis-produit').value = '';
    document.getElementById('avis-commentaire').value = '';
    document.querySelectorAll('.star').forEach(s => s.classList.remove('active'));

    // Scroll vers les avis
    document.getElementById('avis-container').scrollIntoView({behavior: 'smooth'});
}


function lancerRecherche() {
    const query = document.getElementById('search-input').value.trim();
    if (query) {
        window.location.href = '/shop?search=' + encodeURIComponent(query);
    }
}

// Lancer recherche avec Entrée
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('search-input');
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') lancerRecherche();
        });
    }
});

// Page contact
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

    window.scrollTo({top: 0, behavior: 'smooth'});
}