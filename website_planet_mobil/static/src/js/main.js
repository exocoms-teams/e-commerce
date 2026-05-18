
document.addEventListener('DOMContentLoaded', function () {

    var dropdown = document.querySelector('.tsp-nav-dropdown');
    if(dropdown){
        var chevron = dropdown.querySelector('.tsp-chevron');
        chevron.addEventListener("click", function(e){
            e.preventDefault();
            dropdown.classList.toggle('open');
            var submenu = dropdown.querySelector('.tsp-submenu');
            if(submenu) submenu.style.display = dropdown.classList.contains('open')? 'block' : 'none';
        })

    }

   
    document.querySelectorAll('.tsp-wishlist-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var icon = this.querySelector('i');
            if (icon.classList.contains('fa-heart-o')) {
                icon.classList.replace('fa-heart-o', 'fa-heart');
                icon.style.color = '#ef4444';
            } else {
                icon.classList.replace('fa-heart', 'fa-heart-o');
                icon.style.color = '';
            }
        });
    });

   
    document.querySelectorAll('.tsp-btn-add').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var original = this.innerHTML;
            this.innerHTML = '<i class="fa fa-check"></i> Ajouté !';
            this.style.background = '#16a34a';
            var self = this;
            setTimeout(function() {
                self.innerHTML = original;
                self.style.background = '';
            }, 1500);
        });
    });

   
    var newsletterBtn = document.querySelector('.tsp-newsletter-btn');
    if (newsletterBtn) {
        newsletterBtn.addEventListener('click', function() {
            var input = document.querySelector('.tsp-newsletter-form input');
            if (!input || !input.value || !input.value.includes('@')) {
                alert('Veuillez entrer une adresse email valide.');
                return;
            }
            var form = document.querySelector('.tsp-newsletter-form');
            if (form) form.innerHTML = '<span style="color:white;font-weight:600"><i class="fa fa-check-circle"></i> Merci ! Vous êtes bien inscrit(e) 🎉</span>';
        });
    }
});
