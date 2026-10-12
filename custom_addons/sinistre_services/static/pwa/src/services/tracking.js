/**
 * Tracking — partage de la position de l'artisan pendant son trajet.
 * Démarre avec « Je suis en route », s'arrête à l'arrivée (Démarrer) ou
 * dès que le serveur répond que la mission n'est plus en route.
 * Limite : le navigateur coupe le GPS si l'appli passe en arrière-plan.
 */
const Tracking = (() => {
    const INTERVALLE = 10000; // ms entre deux envois
    let _missionId = null, _watchId = null, _timer = null;
    let _derniere = null, _dernierEnvoi = 0;

    function _envoyer() {
        if (!_missionId || !_derniere) return;
        const maintenant = Date.now();
        if (maintenant - _dernierEnvoi < INTERVALLE - 500) return;
        _dernierEnvoi = maintenant;
        API.sendPosition(_missionId, _derniere.lat, _derniere.lng)
            .then(res => { if (res && res.en_route === false) stop(); })
            .catch(() => { /* hors ligne : on réessaiera */ });
    }

    function start(missionId) {
        if (_missionId === missionId && _watchId !== null) return; // déjà actif
        stop();
        if (!navigator.geolocation) {
            Toast.show('GPS non disponible sur cet appareil', 'warning');
            return;
        }
        _missionId = missionId;
        _watchId = navigator.geolocation.watchPosition(
            pos => {
                _derniere = { lat: pos.coords.latitude, lng: pos.coords.longitude };
                _envoyer();
            },
            () => Toast.show('Activez la localisation pour partager votre trajet', 'warning'),
            { enableHighAccuracy: true, maximumAge: 5000, timeout: 20000 }
        );
        _timer = setInterval(_envoyer, INTERVALLE);
    }

    function stop() {
        if (_watchId !== null && navigator.geolocation) navigator.geolocation.clearWatch(_watchId);
        if (_timer) clearInterval(_timer);
        _missionId = null; _watchId = null; _timer = null; _derniere = null;
    }

    function isActive(missionId) {
        return _missionId === missionId && _watchId !== null;
    }

    return { start, stop, isActive };
})();
