var priceMaxInput = document.getElementById('o_winners_filter_price_max');
var sourceSelect = document.getElementById('o_winners_filter_source');

function applyFilters() {
    var params = new URLSearchParams();
    if (categorySelect && categorySelect.value) { params.set('category_id', categorySelect.value); }
    if (countrySelect && countrySelect.value) { params.set('country', countrySelect.value); }
    if (priceMaxInput && priceMaxInput.value) { params.set('price_max', priceMaxInput.value); }
    if (sourceSelect && sourceSelect.value) { params.set('source', sourceSelect.value); }
    if (priceInput && priceInput.value) { params.set('price_max', priceInput.value); }
    if (sourceSelect && sourceSelect.value) { params.set('source', sourceSelect.value); }
    // ... reste inchangé
}

if (priceMaxInput) { priceMaxInput.addEventListener('input', applyFilters); }
if (sourceSelect) { sourceSelect.addEventListener('change', applyFilters); }
// dans le reset :
if (priceMaxInput) { priceMaxInput.value = ''; }
if (sourceSelect) { sourceSelect.value = ''; }