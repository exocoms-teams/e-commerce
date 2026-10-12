/* Carte de suivi de l'artisan sur la page /suivi/<token> (côté client).
   Interroge /suivi/<token>/position toutes les 10 s et déplace le marqueur. */
(function () {
    'use strict';
    var box = document.getElementById('ssSuiviMap');
    var statut = document.getElementById('ssSuiviStatut');
    if (!box || !statut) { return; }

    var url = box.getAttribute('data-url');
    var key = box.getAttribute('data-key');
    var map = null, marker = null, mapsDemandee = false, timer = null;

    function chargerGoogleMaps(callback) {
        if (window.google && window.google.maps) { callback(); return; }
        if (mapsDemandee) { return; }   // déjà en cours de chargement
        mapsDemandee = true;
        window.ssSuiviMapReady = callback;
        var s = document.createElement('script');
        s.src = 'https://maps.googleapis.com/maps/api/js?key=' + encodeURIComponent(key) +
                '&loading=async&callback=ssSuiviMapReady';
        s.async = true;
        document.head.appendChild(s);
    }

    function afficherPosition(data) {
        var pos = { lat: data.lat, lng: data.lng };
        if (map) { marker.setPosition(pos); return; }

        box.style.display = 'block';
        map = new google.maps.Map(box, {
            center: pos, zoom: 14, disableDefaultUI: true, zoomControl: true,
        });
        marker = new google.maps.Marker({ position: pos, map: map, title: 'Votre artisan', label: '🚗' });

        // Adresse d'intervention (coordonnées calculées par Odoo) : 🏠 et cadrage des deux points
        if (data.dest_lat !== undefined) {
            var dest = { lat: data.dest_lat, lng: data.dest_lng };
            new google.maps.Marker({ position: dest, map: map, title: "Adresse d'intervention", label: '🏠' });
            var cadre = new google.maps.LatLngBounds();
            cadre.extend(pos);
            cadre.extend(dest);
            map.fitBounds(cadre);
        }
    }

    function actualiser() {
        fetch(url, { cache: 'no-store' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                // La mission a avancé (artisan arrivé, annulation…) : on recharge la page
                if (['assigne', 'rdv_planifie'].indexOf(data.state) === -1) {
                    clearInterval(timer);
                    window.location.reload();
                    return;
                }
                if (data.en_route) {
                    if (data.lat !== undefined) {
                        statut.textContent = '🚗 ' + (data.artisan || 'Votre artisan') + ' est en route vers vous.';
                        chargerGoogleMaps(function () { afficherPosition(data); });
                    } else {
                        statut.textContent = "🚗 Votre artisan est en route. Sa position s'affichera dans quelques instants.";
                    }
                } else {
                    statut.textContent = "Votre artisan n'est pas encore parti. La carte apparaîtra dès qu'il sera en route.";
                    box.style.display = 'none';
                }
            })
            .catch(function () { /* réseau coupé : on réessaiera au prochain tour */ });
    }

    actualiser();
    timer = setInterval(actualiser, 10000);
})();
