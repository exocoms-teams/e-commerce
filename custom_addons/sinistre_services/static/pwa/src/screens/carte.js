/**
 * carte.js — Carte temps réel Google Maps
 * Géolocalisation live, marqueurs missions, itinéraires, trafic
 */

window.CarteMap = (() => {
    let _map            = null;
    let _userMarker     = null;
    let _missionMarkers = [];
    let _directionsRenderer = null;
    let _trafficLayer   = null;
    let _watchId        = null;
    let _userPos        = null;
    let _missions       = [];
    let _selectedMission= null;
    let _googleReady    = false;
    let _geocoder       = null;
    let _distService    = null;

    // Couleurs par type d'intervention
    const TYPE_COLORS = {
        serrurerie:     '#14B8A6',
        plomberie:      '#3B82F6',
        electricite:    '#F59E0B',
        vitrerie:       '#10B981',
        menuiserie_int: '#8B5CF6',
        menuiserie_ext: '#8B5CF6',
        autre:          '#6B7280',
    };
    const TYPE_LABELS = {
        serrurerie:     'Serrurerie',
        plomberie:      'Plomberie',
        electricite:    'Électricité',
        vitrerie:       'Vitrerie',
        menuiserie_int: 'Menuiserie',
        menuiserie_ext: 'Menuiserie',
        autre:          'Autre',
    };

    /* ═══════ INIT ══════════════════════════════════════════════════ */

    function onGoogleMapsReady() {
        _googleReady = true;
        // Si la carte est déjà visible, l'initialiser
        if (document.getElementById('view-carte')?.classList.contains('active')) {
            _initMap();
        }
    }

    function init() {
        if (!_googleReady) {
            // Google Maps pas encore chargé — afficher message d'attente
            _showMapError('Chargement de Google Maps…');
            return;
        }
        if (_map) {
            // Déjà initialisée — juste recentrer et recharger missions
            _loadMissions();
            return;
        }
        _initMap();
    }

    function _initMap() {
        const container = document.getElementById('googleMap');
        if (!container) return;

        // Centre par défaut : Paris
        const defaultCenter = { lat: 48.8566, lng: 2.3522 };

        _map = new google.maps.Map(container, {
            center:    defaultCenter,
            zoom:      13,
            mapTypeId: 'roadmap',
            styles:    _mapStyles(),
            mapTypeControl:      false,
            streetViewControl:   false,
            fullscreenControl:   false,
            zoomControlOptions: {
                position: google.maps.ControlPosition.RIGHT_CENTER,
            },
        });

        _geocoder    = new google.maps.Geocoder();
        _distService = new google.maps.DistanceMatrixService();
        _directionsRenderer = new google.maps.DirectionsRenderer({
            suppressMarkers:      true,
            polylineOptions:      { strokeColor: '#1E40AF', strokeWeight: 5, strokeOpacity: 0.8 },
        });
        _directionsRenderer.setMap(_map);

        _trafficLayer = new google.maps.TrafficLayer();

        // Démarrer géolocalisation
        _startGPS();

        // Charger les missions
        _loadMissions();

        // Fermer info panel si clic sur la carte
        _map.addListener('click', () => closeInfoPanel());
    }

    /* ═══════ GPS ═══════════════════════════════════════════════════ */

    function _startGPS() {
        if (!navigator.geolocation) {
            _setGPSStatus('GPS non disponible', false);
            return;
        }

        // Première position rapide
        navigator.geolocation.getCurrentPosition(
            pos => _onPosition(pos),
            err => _setGPSStatus('GPS refusé — activez la localisation', false),
            { enableHighAccuracy: true, timeout: 10000 }
        );

        // Suivi continu
        _watchId = navigator.geolocation.watchPosition(
            pos => _onPosition(pos),
            err => _setGPSStatus('Erreur GPS', false),
            { enableHighAccuracy: true, maximumAge: 10000, timeout: 15000 }
        );
    }

    function _onPosition(pos) {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        const acc = Math.round(pos.coords.accuracy);
        _userPos = { lat, lng };

        _setGPSStatus(`GPS actif · Précision ${acc}m`, true);

        // Mettre à jour le marqueur utilisateur
        if (!_userMarker) {
            _userMarker = new google.maps.Marker({
                position: { lat, lng },
                map:      _map,
                icon:     _userIcon(),
                title:    'Ma position',
                zIndex:   1000,
            });
            _map.setCenter({ lat, lng });
            _map.setZoom(14);
        } else {
            _userMarker.setPosition({ lat, lng });
        }

        // Géocodage inverse pour afficher l'adresse
        _reverseGeocode(lat, lng);

        // Mettre à jour les distances des missions
        _updateMissionDistances();

        // Coordonnées
        const coordEl = document.getElementById('gpsCoords');
        if (coordEl) coordEl.textContent = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    }

    function _reverseGeocode(lat, lng) {
        if (!_geocoder) return;
        _geocoder.geocode({ location: { lat, lng } }, (results, status) => {
            if (status === 'OK' && results[0]) {
                const comps    = results[0].address_components;
                const locality = comps.find(c => c.types.includes('locality'))?.long_name || '';
                const district = comps.find(c => c.types.includes('sublocality_level_1'))?.long_name || locality;
                const route    = comps.find(c => c.types.includes('route'))?.long_name || '';
                const num      = comps.find(c => c.types.includes('street_number'))?.long_name || '';

                const city = document.getElementById('carteCityName');
                const addr = document.getElementById('carteAddrName');
                const sub  = document.getElementById('carteSubtitle');
                if (city) city.textContent = district || locality;
                if (addr) addr.textContent = num ? `${num} ${route}` : (route || results[0].formatted_address);
                if (sub)  sub.textContent  = `Zone d'intervention · GPS actif`;
            }
        });
    }

    function _setGPSStatus(msg, active) {
        const dot = document.getElementById('gpsDot');
        const txt = document.getElementById('gpsStatus');
        if (dot) dot.style.background = active ? '#10B981' : '#EF4444';
        if (txt) txt.textContent = msg;
    }

    /* ═══════ MISSIONS ══════════════════════════════════════════════ */

    async function _loadMissions() {
        try {
            const data = await API.getMissions();
            _missions  = (data.missions || []).filter(m =>
                ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'].includes(m.state)
            );
        } catch(e) {
            // Fallback localStorage
            try {
                _missions = JSON.parse(localStorage.getItem('ss_missions_cache') || '[]').filter(m =>
                    ['assigne','rdv_planifie','en_cours','devis_envoye','devis_accepte','travaux_en_cours','nouveau'].includes(m.state)
                );
            } catch(e2) { _missions = []; }
        }

        _placeMissionMarkers();
        _updateLegend();
        _updateNextMission();
        _updateMissionsProches();
    }

    function _placeMissionMarkers() {
        // Supprimer anciens marqueurs
        _missionMarkers.forEach(m => m.marker.setMap(null));
        _missionMarkers = [];

        _missions.forEach(mission => {
            const adresse = mission.adresse_intervention || mission.adresse;
            if (!adresse) return;

            _geocodeMission(mission, adresse);
        });
    }

    function _geocodeMission(mission, adresse) {
        if (!_geocoder) return;
        _geocoder.geocode({ address: adresse + ', France' }, (results, status) => {
            if (status !== 'OK' || !results[0]) return;

            const pos   = results[0].geometry.location;
            const color = TYPE_COLORS[mission.type_intervention] || '#6B7280';
            const isUrgent = mission.urgence === 'urgente' || mission.urgence === 'tres_urgente';

            const marker = new google.maps.Marker({
                position: pos,
                map:      _map,
                icon:     _missionIcon(color, isUrgent),
                title:    mission.description_sinistre || mission.reference,
                animation: isUrgent ? google.maps.Animation.BOUNCE : null,
            });

            // Stopper le bounce après 3s
            if (isUrgent) setTimeout(() => marker.setAnimation(null), 3000);

            marker.addListener('click', () => _selectMission(mission, pos, marker));

            _missionMarkers.push({ marker, mission, pos });
        });
    }

    function _selectMission(mission, pos, marker) {
        _selectedMission = mission;

        // Panel info
        const panel = document.getElementById('carteInfoPanel');
        if (!panel) return;
        panel.style.display = 'block';

        // Badges
        const color = TYPE_COLORS[mission.type_intervention] || '#6B7280';
        const label = TYPE_LABELS[mission.type_intervention] || mission.type_intervention;
        let badges  = `<span style="background:${color}20;color:${color};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">${label}</span>`;
        if (mission.urgence === 'urgente' || mission.urgence === 'tres_urgente') {
            badges += ' <span style="background:#FEE2E2;color:#991B1B;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">Urgente</span>';
        }

        const el = id => document.getElementById(id);
        el('carteInfoBadges').innerHTML = badges;
        el('carteInfoTitle').textContent  = mission.description_sinistre || mission.description || '—';
        el('carteInfoAddr').textContent   = mission.adresse_intervention  || mission.adresse || '—';
        el('carteInfoMontant').textContent = mission.montant ? mission.montant.toLocaleString('fr-FR') + ' €' : '—';
        el('carteInfoDuree').textContent  = 'Calcul itinéraire…';
        el('carteInfoDist').textContent   = '—';

        // Calculer itinéraire si position GPS connue
        if (_userPos && _distService) {
            _distService.getDistanceMatrix({
                origins:      [_userPos],
                destinations: [pos.toJSON ? pos.toJSON() : pos],
                travelMode:   google.maps.TravelMode.DRIVING,
                drivingOptions: { departureTime: new Date(), trafficModel: 'bestguess' },
            }, (resp, status) => {
                if (status === 'OK') {
                    const el2 = resp.rows[0]?.elements[0];
                    if (el2?.status === 'OK') {
                        el('carteInfoDuree').textContent = el2.duration_in_traffic?.text || el2.duration?.text || '—';
                        el('carteInfoDist').textContent  = el2.distance?.text || '—';
                    }
                }
            });
        }

        // Centrer sur la mission
        _map.panTo(pos);
        _map.setZoom(15);
    }

    /* ═══════ ITINÉRAIRE ════════════════════════════════════════════ */

    function launchRoute() {
        if (!_selectedMission) return;
        const adresse = _selectedMission.adresse_intervention || _selectedMission.adresse;
        if (!adresse) return;

        if (_userPos) {
            // Tracer l'itinéraire sur la carte
            const dirService = new google.maps.DirectionsService();
            dirService.route({
                origin:      _userPos,
                destination: adresse + ', France',
                travelMode:  google.maps.TravelMode.DRIVING,
                drivingOptions: { departureTime: new Date(), trafficModel: 'bestguess' },
            }, (result, status) => {
                if (status === 'OK') {
                    _directionsRenderer.setDirections(result);
                    // Afficher dans Google Maps natif aussi
                    _openGoogleMapsRoute(adresse);
                } else {
                    _openGoogleMapsRoute(adresse);
                }
            });
        } else {
            _openGoogleMapsRoute(adresse);
        }
    }

    function _openGoogleMapsRoute(destination) {
        const dest = encodeURIComponent(destination);
        const orig = _userPos ? `${_userPos.lat},${_userPos.lng}` : '';
        const url  = orig
            ? `https://www.google.com/maps/dir/${orig}/${dest}`
            : `https://www.google.com/maps/dir//${dest}`;
        window.open(url, '_blank');
    }

    function callClient() {
        if (!_selectedMission?.tel_sur_place) {
            Toast.show('Pas de téléphone renseigné', 'warning');
            return;
        }
        window.location.href = `tel:${_selectedMission.tel_sur_place}`;
    }

    function openMission() {
        if (!_selectedMission?.id) return;
        closeInfoPanel();
        MissionDetail.open(_selectedMission.id);
    }

    function closeInfoPanel() {
        const panel = document.getElementById('carteInfoPanel');
        if (panel) panel.style.display = 'none';
        _selectedMission = null;
    }

    /* ═══════ UI UPDATES ════════════════════════════════════════════ */

    function _updateMissionDistances() {
        if (!_userPos || !_missionMarkers.length || !_distService) return;

        const destinations = _missionMarkers.map(m => m.pos.toJSON ? m.pos.toJSON() : m.pos);
        if (!destinations.length) return;

        _distService.getDistanceMatrix({
            origins:      [_userPos],
            destinations: destinations,
            travelMode:   google.maps.TravelMode.DRIVING,
            drivingOptions: { departureTime: new Date(), trafficModel: 'bestguess' },
        }, (resp, status) => {
            if (status !== 'OK') return;
            const elements = resp.rows[0]?.elements || [];
            elements.forEach((el, i) => {
                if (el.status === 'OK' && _missionMarkers[i]) {
                    _missionMarkers[i].dist    = el.distance?.value || 9999999;
                    _missionMarkers[i].distTxt = el.distance?.text || '—';
                    _missionMarkers[i].durTxt  = el.duration_in_traffic?.text || el.duration?.text || '—';
                }
            });
            // Trier par distance
            _missionMarkers.sort((a, b) => (a.dist || 9999) - (b.dist || 9999));
            _updateNextMission();
            _updateMissionsProches();
        });
    }

    function _updateLegend() {
        const el = document.getElementById('carteLegend');
        if (!el) return;
        if (!_missions.length) {
            el.innerHTML = '<div style="color:#9CA3AF;font-size:12px">Aucune mission active</div>';
            return;
        }
        // Compter par type
        const counts = {};
        _missions.forEach(m => {
            const t = m.type_intervention || 'autre';
            counts[t] = (counts[t] || 0) + 1;
        });
        el.innerHTML = Object.entries(counts).map(([type, n]) => `
            <div class="legend-item">
                <span class="legend-dot" style="background:${TYPE_COLORS[type] || '#6B7280'}"></span>
                ${TYPE_LABELS[type] || type}
                <span class="legend-count">${n}</span>
            </div>
        `).join('');
    }

    function _updateNextMission() {
        const el = document.getElementById('carteNextContent');
        if (!el) return;

        const first = _missionMarkers[0]?.mission || _missions[0];
        if (!first) {
            el.innerHTML = '<div style="color:#9CA3AF;font-size:13px">Aucune mission active</div>';
            return;
        }
        const mm    = _missionMarkers[0];
        const color = TYPE_COLORS[first.type_intervention] || '#6B7280';
        el.innerHTML = `
            <div style="font-size:14px;font-weight:700;margin-bottom:4px">${first.description_sinistre || '—'}</div>
            <div style="font-size:12px;color:#6B7280;margin-bottom:10px">${first.adresse_intervention || first.adresse || '—'}</div>
            ${mm?.distTxt ? `
            <div style="display:flex;gap:16px;font-size:12px;color:#374151">
                <span>🚗 ${mm.durTxt || '—'}</span>
                <span>📍 ${mm.distTxt}</span>
            </div>` : ''}
            <div style="margin-top:10px;display:flex;gap:8px">
                <button onclick="CarteMap.launchRoute()" style="flex:1;padding:8px;border-radius:8px;border:none;background:#0F1B33;color:white;font-size:12px;font-weight:600;cursor:pointer">
                    Itinéraire
                </button>
            </div>
        `;
        // Sélectionner automatiquement cette mission
        if (mm) _selectedMission = mm.mission;
    }

    function _updateMissionsProches() {
        const el = document.getElementById('carteMissionsProches');
        if (!el) return;
        if (!_missionMarkers.length) {
            el.innerHTML = '<div style="color:#9CA3AF;font-size:12px">Aucune mission</div>';
            return;
        }
        el.innerHTML = _missionMarkers.slice(0, 5).map(({ mission, distTxt, durTxt }) => {
            const color = TYPE_COLORS[mission.type_intervention] || '#6B7280';
            const label = TYPE_LABELS[mission.type_intervention] || mission.type_intervention;
            const isUrgent = mission.urgence === 'urgente' || mission.urgence === 'tres_urgente';
            return `
                <div class="carte-mission-item" onclick="CarteMap._selectByRef('${mission.id}')">
                    <div class="carte-mission-dot" style="background:${color}"></div>
                    <div class="carte-mission-info">
                        <div class="carte-mission-title">${mission.description_sinistre || label}</div>
                        <div class="carte-mission-meta">
                            ${distTxt ? `📍 ${distTxt}` : ''}
                            ${durTxt  ? ` · 🚗 ${durTxt}` : ''}
                            ${isUrgent ? ' · <span style="color:#EF4444;font-weight:600">Urgente</span>' : ''}
                        </div>
                    </div>
                    <div class="carte-mission-price">${mission.montant ? mission.montant + ' €' : '—'}</div>
                </div>`;
        }).join('');
    }

    /* ═══════ ACTIONS ═══════════════════════════════════════════════ */

    function centerOnUser() {
        if (_userPos && _map) {
            _map.panTo(_userPos);
            _map.setZoom(15);
        } else {
            Toast.show('Position GPS non disponible', 'warning');
        }
    }

    function toggleTraffic() {
        if (!_map || !_trafficLayer) return;
        const btn = document.getElementById('btnTraffic');
        if (_trafficLayer.getMap()) {
            _trafficLayer.setMap(null);
            if (btn) btn.style.opacity = '0.6';
        } else {
            _trafficLayer.setMap(_map);
            if (btn) btn.style.opacity = '1';
        }
    }

    function _selectByRef(id) {
        const mm = _missionMarkers.find(m => String(m.mission.id) === String(id));
        if (mm) _selectMission(mm.mission, mm.pos, mm.marker);
    }

    function _showMapError(msg) {
        const el = document.getElementById('googleMap');
        if (el) el.innerHTML = `
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#6B7280;gap:12px">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#D1D5DB" stroke-width="1.5"><circle cx="12" cy="10" r="3"/><path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z"/></svg>
                <div style="font-size:14px">${msg}</div>
            </div>`;
    }

    /* ═══════ ICÔNES ════════════════════════════════════════════════ */

    function _userIcon() {
        return {
            path: google.maps.SymbolPath.CIRCLE,
            scale:       10,
            fillColor:   '#1E40AF',
            fillOpacity: 1,
            strokeColor: 'white',
            strokeWeight: 3,
        };
    }

    function _missionIcon(color, urgent) {
        const svg = `
            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="44" viewBox="0 0 36 44">
                <circle cx="18" cy="18" r="16" fill="${color}" stroke="white" stroke-width="2.5"/>
                <circle cx="18" cy="18" r="6" fill="white"/>
                ${urgent ? `<circle cx="26" cy="6" r="6" fill="#EF4444" stroke="white" stroke-width="2"/>` : ''}
                <path d="M18 34 L18 44" stroke="${color}" stroke-width="2.5" stroke-linecap="round"/>
            </svg>`;
        return {
            url:    'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg),
            scaledSize: new google.maps.Size(36, 44),
            anchor:     new google.maps.Point(18, 44),
        };
    }

    /* ═══════ MAP STYLES ════════════════════════════════════════════ */

    function _mapStyles() {
        return [
            { featureType: 'poi', elementType: 'labels', stylers: [{ visibility: 'off' }] },
            { featureType: 'transit', elementType: 'labels.icon', stylers: [{ visibility: 'off' }] },
            { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#ffffff' }] },
            { featureType: 'road.arterial', elementType: 'geometry', stylers: [{ color: '#f5f5f5' }] },
            { featureType: 'road.highway', elementType: 'geometry', stylers: [{ color: '#e8e8e8' }] },
            { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#93C5FD' }] },
            { featureType: 'landscape', elementType: 'geometry', stylers: [{ color: '#f0f4f8' }] },
            { featureType: 'administrative', elementType: 'geometry.stroke', stylers: [{ color: '#D1D5DB' }] },
        ];
    }

    /* ═══════ API PUBLIQUE ══════════════════════════════════════════ */

    return {
        init,
        onGoogleMapsReady,
        centerOnUser,
        toggleTraffic,
        launchRoute,
        callClient,
        openMission,
        closeInfoPanel,
        _selectByRef,
    };
})();
