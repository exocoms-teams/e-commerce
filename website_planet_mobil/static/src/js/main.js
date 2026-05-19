
document.addEventListener('DOMContentLoaded', function () {

    var dropdown = document.querySelector('.tsp-nav-dropdown');
    if(dropdown){
        var chevron = dropdown.querySelector('.tsp-chevron');
        console.log('chevron trouver', chevron);
        chevron.addEventListener("click", function(e){
            e.stopPropagation();
            e.preventDefault();
            var submenu = dropdown.querySelector('.tsp-submenu');
        if(submenu) submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
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


    document.querySelectorAll('.tsp-custom-select').forEach(function(select){
        var selected = select.querySelector('.tsp-custom-selected');
        var options = select.querySelector('.tsp-custom-options');

        selected.addEventListener('click', function(e){
            e.stopPropagation();
            document.querySelectorAll('.tsp-custom-select').forEach(function(s){
                if(s!==select) s.classList.remove('open');
            });
            select.classList.toggle('open');
        });

        options.querySelectorAll('input[type"checkbox"]').forEach(function(checkbox){
            checkbox.addEventListener('change', function(){
                var checked = options.querySelectorAll('input[type="checkbox"]:checked');
                if(checked.lenght===0){
                    selected.innerHTML='Toutes les <i class="fa fa-chevron-down"></i>';
                }else if(checked.lenght===1){
                        selected.innerHTML='1 sélectionné <i class="fa fa-chevron-down"></i>';
                }else{
                    selected.innerHTML= checked.length + ' sélectionnés <i class="fa fa-chevron-down"></i>';   
                }
  
            });
        });
    });

    document.addEventListener('click', function(){
        document.querySelectorAll('.tsp-custom-select').forEach(function(s){
            s.classList.remove('open');
        })
    })

    document.querySelector('.tsp-filter-btn').addEventListener('click', function(){
        var params = new URLSearchParams(window.location.search);
        
        var category = new URLSearchParams(window.location.search).get('category');
        if (category) params.set('category', category);

        document.querySelectorAll('.tsp-custom-select').forEach(function(select){
            var filter = select.dataset.filter;
            var checked = select.querySelectorAll('input[type="checkbox"]:checked');

            if(checked.lenght>0){
                var values = Array.from(checked).map(function(cb){
                    return cb.closest('li').dataset.value;
                });
                params.set(filter, values.join(','));
            }
        });

        var priceMin = document.querySelector('[data-filter="price_min"]');
        var priceMax = document.querySelector('[data-filter="price_max"]');
        if(priceMin.value) params.set('price_min', priceMin.value);
        else params.delete('price_min');
        if(priceMax.value) params.set('price_max', priceMax.value);
        else params.delete('price_max');

        window.location.href = '/shop?' + params.toString();
    })
});
