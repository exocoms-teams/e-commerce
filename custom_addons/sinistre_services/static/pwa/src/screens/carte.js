/**
 * carte.js — Carte Google Maps temps réel
 * Utilise l'API officielle Google Maps avec gmp-map Web Component
 */

window.gm_authFailure = function() {
    var el = document.getElementById('googleMap');
    if (el) el.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;background:#FEF2F2;color:#991B1B;padding:20px;text-align:center;font-size:14px">❌ Clé API invalide</div>';
};

window.CarteMap = (() => {
    let _map = null;          // instance google.maps.Map
    let _mapEl = null;        // élément gmp-map
    let _userMarker = null;
    let _markers = [];
    let _directionsRenderer = null;
    let _trafficLayer = null;
    let _userPos = null;
    let _missions = [];
    let _selected = null;
    let _ready = false;

    const COLORS = {
        serrurerie: '#14B8A6', plomberie: '#3B82F6', electricite: '#F59E0B',
        vitrerie: '#10B981', menuiserie_int: '#8B5CF6', menuiserie_ext: '#8B5CF6', autre: '#6B7280',
    };
    const LABELS = {
        serrurerie: 'Serrurerie', plomberie: 'Plomberie', electricite: 'Électricité',
        vitrerie: 'Vitrerie', menuiserie_int: 'Menuiserie', menuiserie_ext: 'Menuiserie', autre: 'Autre',
    };

    /* ══ INIT ══════════════════════════════════════════════════════ */

    function onGoogleMapsReady() {
        _ready = true;
        console.log('[CarteMap] ✓ Google Maps prêt');
        var view = document.getElementById('view-carte');
        if (view && view.classList.contains('active')) {
            _doInit();
        }
    }

    function init() {
        console.log('[CarteMap] init() ready=' + _ready + ' map=' + !!_map);

        if (!_ready) {
            // Attendre Google Maps
            var n = 0;
            var t = setInterval(function() {
                n++;
                if (_ready) { clearInterval(t); _doInit(); }
                if (n > 30) clearInterval(t);
            }, 300);
            return;
        }

        if (_map) {
            // Déjà initialisé — resize
            google.maps.event.trigger(_map, 'resize');
            if (_userPos) _map.setCenter(_userPos);
            _loadMissions();
            return;
        }

        _doInit();
    }

    function _doInit() {
        _mapEl = document.getElementById('googleMap');
        if (!_mapEl) { console.error('[CarteMap] #googleMap introuvable'); return; }

        console.log('[CarteMap] _doInit taille=' + _mapEl.offsetWidth + 'x' + _mapEl.offsetHeight);

        // Récupérer l'instance google.maps.Map depuis le Web Component gmp-map
        // Le Web Component expose innerMap une fois rendu
        _waitForInnerMap(_mapEl);
    }

    function _waitForInnerMap(el) {
        // gmp-map expose sa carte interne via el.innerMap après le rendu
        if (el.innerMap) {
            _onMapReady(el.innerMap);
            return;
        }
        // Sinon créer manuellement une carte dans le div
        _createFallbackMap(el);
    }

    function _createFallbackMap(el) {
        console.log('[CarteMap] Création carte (fallback)');
        // Remplacer gmp-map par un div normal
        var div = document.createElement('div');
        div.style.width = '100%';
        div.style.height = '560px';
        el.parentNode.replaceChild(div, el);
        _mapEl = div;

        var map = new google.maps.Map(div, {
            center: { lat: 48.8566, lng: 2.3522 },
            zoom: 13,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false,
            styles: _styles(),
        });
        _onMapReady(map);
    }

    function _onMapReady(map) {
        _map = map;
        console.log('[CarteMap] ✓ Carte initialisée');

        _directionsRenderer = new google.maps.DirectionsRenderer({
            suppressMarkers: true,
            polylineOptions: { strokeColor: '#1E40AF', strokeWeight: 5, strokeOpacity: 0.8 },
        });
        _directionsRenderer.setMap(_map);
        _trafficLayer = new google.maps.TrafficLayer();
        _map.addListener('click', closeInfoPanel);

        setTimeout(function() {
            google.maps.event.trigger(_map, 'resize');
        }, 200);

        _startGPS();
        _loadMissions();
    }

    /* ══ GPS ════════════════════════════════════════════════════════ */

    function _startGPS() {
        if (!navigator.geolocation) { _setGPS('GPS non disponible', false); return; }
        navigator.geolocation.getCurrentPosition(
            function(p) { _onPos(p); },
            function()  { _setGPS('Activez la localisation', false); },
            { enableHighAccuracy: true, timeout: 10000 }
        );
        navigator.geolocation.watchPosition(
            function(p) { _onPos(p); }, function() {},
            { enableHighAccuracy: true, maximumAge: 10000, timeout: 15000 }
        );
    }

    function _onPos(pos) {
        var lat = pos.coords.latitude, lng = pos.coords.longitude;
        var acc = Math.round(pos.coords.accuracy);
        _userPos = { lat: lat, lng: lng };
        _setGPS('GPS actif · Précision ' + acc + 'm', true);

        if (!_userMarker) {
            _userMarker = new google.maps.Marker({
                position: _userPos, map: _map,
                icon: { path: google.maps.SymbolPath.CIRCLE, scale: 10, fillColor: '#1E40AF', fillOpacity: 1, strokeColor: 'white', strokeWeight: 3 },
                title: 'Ma position', zIndex: 1000,
            });
            _map.setCenter(_userPos);
            _map.setZoom(14);
        } else {
            _userMarker.setPosition(_userPos);
        }

        // Géocodage inverse
        new google.maps.Geocoder().geocode({ location: _userPos }, function(res, st) {
            if (st === 'OK' && res[0]) {
                var comps = res[0].address_components;
                var city = ((comps.find(function(c){ return c.types.includes('sublocality_level_1'); }) ||
                             comps.find(function(c){ return c.types.includes('locality'); })) || {}).long_name || '';
                var route = ((comps.find(function(c){ return c.types.includes('route'); })) || {}).long_name || '';
                var num   = ((comps.find(function(c){ return c.types.includes('street_number'); })) || {}).long_name || '';
                _set('carteCityName', city);
                _set('carteAddrName', num ? num + ' ' + route : route || res[0].formatted_address);
                _set('carteSubtitle', "Zone d'intervention · GPS actif");
                var gc = document.getElementById('gpsCoords');
                if (gc) gc.textContent = lat.toFixed(5) + ', ' + lng.toFixed(5);
            }
        });

        _updateDistances();
    }

    function _setGPS(msg, active) {
        var dot = document.getElementById('gpsDot');
        var txt = document.getElementById('gpsStatus');
        if (dot) dot.style.background = active ? '#10B981' : '#EF4444';
        if (txt) txt.textContent = msg;
    }

    /* ══ MISSIONS ═══════════════════════════════════════════════════ */

    async function _loadMissions() {
        const ACTIVE = ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'];
        try {
            var data = await API.getMissions();
            _missions = (data.missions || []).filter(function(m) { return ACTIVE.includes(m.state); });
        } catch(e) {
            try { _missions = JSON.parse(localStorage.getItem('ss_missions_cache') || '[]').filter(function(m){ return ACTIVE.includes(m.state); }); } catch(e2){}
        }

        // Supprimer anciens marqueurs
        _markers.forEach(function(m) { m.marker.setMap(null); });
        _markers = [];

        var geocoder = new google.maps.Geocoder();
        _missions.forEach(function(mission) {
            var addr = mission.adresse_intervention || mission.adresse;
            if (!addr) return;
            geocoder.geocode({ address: addr + ', France' }, function(res, st) {
                if (st !== 'OK' || !res[0]) return;
                var pos    = res[0].geometry.location;
                var color  = COLORS[mission.type_intervention] || '#6B7280';
                var urgent = mission.urgence === 'urgente' || mission.urgence === 'tres_urgente';

                var marker = new google.maps.Marker({
                    position: pos, map: _map,
                    icon: _icon(color, urgent),
                    title: mission.description_sinistre || mission.reference,
                    animation: urgent ? google.maps.Animation.BOUNCE : null,
                });
                if (urgent) setTimeout(function(){ marker.setAnimation(null); }, 3000);
                marker.addListener('click', function(){ _select(mission, pos); });
                _markers.push({ marker: marker, mission: mission, pos: pos });
                _updateLegend();
                _updateNext();
                _updateProches();
            });
        });

        _updateLegend();
        _updateNext();
        _updateProches();
    }

    function _select(mission, pos) {
        _selected = mission;
        var panel = document.getElementById('carteInfoPanel');
        if (!panel) return;
        panel.style.display = 'block';

        var color  = COLORS[mission.type_intervention] || '#6B7280';
        var label  = LABELS[mission.type_intervention] || mission.type_intervention;
        var urgent = mission.urgence === 'urgente' || mission.urgence === 'tres_urgente';

        document.getElementById('carteInfoBadges').innerHTML =
            '<span style="background:' + color + '20;color:' + color + ';padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">' + label + '</span>' +
            (urgent ? ' <span style="background:#FEE2E2;color:#991B1B;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">Urgente</span>' : '');
        _set('carteInfoTitle',   mission.description_sinistre || mission.description || '—');
        _set('carteInfoAddr',    mission.adresse_intervention  || mission.adresse    || '—');
        _set('carteInfoMontant', mission.montant ? mission.montant.toLocaleString('fr-FR') + ' €' : '—');
        _set('carteInfoDuree', _userPos ? 'Calcul…' : '—');
        _set('carteInfoDist',  '—');

        _map.panTo(pos);
        _map.setZoom(15);

        if (_userPos) {
            new google.maps.DistanceMatrixService().getDistanceMatrix({
                origins: [_userPos],
                destinations: [{ lat: pos.lat(), lng: pos.lng() }],
                travelMode: google.maps.TravelMode.DRIVING,
                drivingOptions: { departureTime: new Date(), trafficModel: 'bestguess' },
            }, function(resp, st) {
                if (st === 'OK') {
                    var el = resp.rows[0].elements[0];
                    if (el.status === 'OK') {
                        _set('carteInfoDuree', el.duration_in_traffic ? el.duration_in_traffic.text : el.duration.text);
                        _set('carteInfoDist',  el.distance.text);
                    }
                }
            });
        }
    }

    function _updateDistances() {
        if (!_userPos || !_markers.length) return;
        var dests = _markers.map(function(m) { return { lat: m.pos.lat(), lng: m.pos.lng() }; });
        new google.maps.DistanceMatrixService().getDistanceMatrix({
            origins: [_userPos], destinations: dests,
            travelMode: google.maps.TravelMode.DRIVING,
            drivingOptions: { departureTime: new Date(), trafficModel: 'bestguess' },
        }, function(resp, st) {
            if (st !== 'OK') return;
            (resp.rows[0].elements || []).forEach(function(el, i) {
                if (el.status === 'OK' && _markers[i]) {
                    _markers[i].dist    = el.distance.value;
                    _markers[i].distTxt = el.distance.text;
                    _markers[i].durTxt  = el.duration_in_traffic ? el.duration_in_traffic.text : el.duration.text;
                }
            });
            _markers.sort(function(a, b){ return (a.dist||9e9) - (b.dist||9e9); });
            _updateNext();
            _updateProches();
        });
    }

    function _updateLegend() {
        var el = document.getElementById('carteLegend');
        if (!el) return;
        if (!_missions.length) { el.innerHTML = '<div style="color:#9CA3AF;font-size:12px">Aucune mission</div>'; return; }
        var counts = {};
        _missions.forEach(function(m){ var t = m.type_intervention||'autre'; counts[t]=(counts[t]||0)+1; });
        el.innerHTML = Object.entries(counts).map(function(e){
            return '<div class="legend-item"><span class="legend-dot" style="background:'+(COLORS[e[0]]||'#6B7280')+'"></span>'+(LABELS[e[0]]||e[0])+'<span class="legend-count">'+e[1]+'</span></div>';
        }).join('');
    }

    function _updateNext() {
        var el = document.getElementById('carteNextContent');
        if (!el) return;
        var mm = _markers[0]; var m = mm ? mm.mission : (_missions[0]||null);
        if (!m) { el.innerHTML = '<div style="color:#9CA3AF;font-size:13px">Aucune mission active</div>'; return; }
        el.innerHTML = '<div style="font-size:14px;font-weight:700;margin-bottom:4px">'+(m.description_sinistre||'—')+'</div>'+
            '<div style="font-size:12px;color:#6B7280;margin-bottom:10px">'+(m.adresse_intervention||m.adresse||'—')+'</div>'+
            (mm&&mm.distTxt?'<div style="font-size:12px;color:#374151;margin-bottom:10px">🚗 '+mm.durTxt+' · 📍 '+mm.distTxt+'</div>':'')+
            '<button onclick="CarteMap.launchRoute()" style="width:100%;padding:8px;border-radius:8px;border:none;background:#0F1B33;color:white;font-size:12px;font-weight:600;cursor:pointer">Itinéraire</button>';
        _selected = m;
    }

    function _updateProches() {
        var el = document.getElementById('carteMissionsProches');
        if (!el) return;
        if (!_markers.length) { el.innerHTML = '<div style="color:#9CA3AF;font-size:12px">Aucune mission</div>'; return; }
        el.innerHTML = _markers.slice(0,5).map(function(mm){
            var m = mm.mission, color = COLORS[m.type_intervention]||'#6B7280';
            return '<div class="carte-mission-item" onclick="CarteMap._selectById(\''+m.id+'\')">'
                +'<div class="carte-mission-dot" style="background:'+color+'"></div>'
                +'<div class="carte-mission-info">'
                +'<div class="carte-mission-title">'+(m.description_sinistre||LABELS[m.type_intervention]||'—')+'</div>'
                +'<div class="carte-mission-meta">'+(mm.distTxt?'📍 '+mm.distTxt:'')+(mm.durTxt?' · 🚗 '+mm.durTxt:'')+'</div>'
                +'</div>'
                +'<div class="carte-mission-price">'+(m.montant?m.montant+' €':'—')+'</div>'
                +'</div>';
        }).join('');
    }

    /* ══ ACTIONS ════════════════════════════════════════════════════ */

    function launchRoute() {
        if (!_selected) return;
        var addr = (_selected.adresse_intervention || _selected.adresse || '') + ', France';
        if (_userPos && _map) {
            new google.maps.DirectionsService().route({
                origin: _userPos, destination: addr,
                travelMode: google.maps.TravelMode.DRIVING,
                drivingOptions: { departureTime: new Date(), trafficModel: 'bestguess' },
            }, function(res, st) {
                if (st === 'OK' && _directionsRenderer) _directionsRenderer.setDirections(res);
            });
        }
        var orig = _userPos ? _userPos.lat + ',' + _userPos.lng : '';
        window.open('https://www.google.com/maps/dir/' + orig + '/' + encodeURIComponent(addr), '_blank');
    }

    function callClient() {
        if (!_selected || !_selected.tel_sur_place) { if(window.Toast) Toast.show('Pas de téléphone', 'warning'); return; }
        window.location.href = 'tel:' + _selected.tel_sur_place;
    }
    function openMission() { if (_selected && _selected.id) { closeInfoPanel(); if(window.MissionDetail) MissionDetail.open(_selected.id); } }
    function closeInfoPanel() { var p = document.getElementById('carteInfoPanel'); if(p) p.style.display='none'; }
    function centerOnUser() { if(_userPos&&_map){ _map.panTo(_userPos); _map.setZoom(15); } else if(window.Toast) Toast.show('GPS non disponible','warning'); }
    function toggleTraffic() {
        if(!_trafficLayer) return;
        var btn = document.getElementById('btnTraffic');
        if(_trafficLayer.getMap()){ _trafficLayer.setMap(null); if(btn) btn.style.opacity='0.5'; }
        else { _trafficLayer.setMap(_map); if(btn) btn.style.opacity='1'; }
    }
    function _selectById(id) { var mm=_markers.find(function(m){ return String(m.mission.id)===String(id); }); if(mm) _select(mm.mission,mm.pos); }

    /* ══ HELPERS ════════════════════════════════════════════════════ */

    function _set(id, txt) { var el=document.getElementById(id); if(el) el.textContent=txt; }

    function _icon(color, urgent) {
        var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="44" viewBox="0 0 36 44">'
            + '<circle cx="18" cy="18" r="16" fill="'+color+'" stroke="white" stroke-width="2.5"/>'
            + '<circle cx="18" cy="18" r="6" fill="white"/>'
            + (urgent?'<circle cx="27" cy="7" r="7" fill="#EF4444" stroke="white" stroke-width="2"/><text x="27" y="11" text-anchor="middle" fill="white" font-size="9" font-weight="bold">!</text>':'')
            + '<line x1="18" y1="34" x2="18" y2="44" stroke="'+color+'" stroke-width="3"/></svg>';
        return { url:'data:image/svg+xml;charset=UTF-8,'+encodeURIComponent(svg), scaledSize:new google.maps.Size(36,44), anchor:new google.maps.Point(18,44) };
    }

    function _styles() {
        return [
            {featureType:'poi',stylers:[{visibility:'off'}]},
            {featureType:'transit',elementType:'labels.icon',stylers:[{visibility:'off'}]},
            {featureType:'road',elementType:'geometry',stylers:[{color:'#ffffff'}]},
            {featureType:'road.highway',elementType:'geometry',stylers:[{color:'#e8e8e8'}]},
            {featureType:'water',elementType:'geometry',stylers:[{color:'#93C5FD'}]},
            {featureType:'landscape',elementType:'geometry',stylers:[{color:'#f0f4f8'}]},
        ];
    }

    return { init, onGoogleMapsReady, launchRoute, callClient, openMission, closeInfoPanel, centerOnUser, toggleTraffic, _selectById };
})();
