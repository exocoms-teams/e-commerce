/**
 * config.js — Configuration centrale de la PWA
 */

window.CONFIG = {

    /* ── Odoo SH ──────────────────────────────────────────────────── */
    ODOO_BASE_URL: '',
    API_BASE: '/api/sinistre/v1',

    /* ── Google Maps ──────────────────────────────────────────────── */
    // Remplacer par votre clé API Google Maps
    // APIs à activer : Maps JavaScript API, Directions API, Distance Matrix API, Geocoding API
    GOOGLE_MAPS_KEY: '__GOOGLE_MAPS_API_KEY__',

    /* ── Firebase ─────────────────────────────────────────────────── */
    FIREBASE: {
        apiKey:            '__FIREBASE_API_KEY__',
        authDomain:        '__FIREBASE_AUTH_DOMAIN__',
        projectId:         '__FIREBASE_PROJECT_ID__',
        storageBucket:     '__FIREBASE_STORAGE_BUCKET__',
        messagingSenderId: '__FIREBASE_SENDER_ID__',
        appId:             '__FIREBASE_APP_ID__',
    },
    FIREBASE_VAPID_KEY: '__FIREBASE_VAPID_KEY__',

    /* ── PWA ──────────────────────────────────────────────────────── */
    SW_PATH:    '/sinistre_services/static/pwa/sw.js',
    CACHE_NAME: 'sinistre-pro-v1',

    /* ── Offline ──────────────────────────────────────────────────── */
    MAX_OFFLINE_QUEUE: 50,
    PHOTO_MAX_SIZE_KB: 800,
    PHOTO_QUALITY:     0.82,

    /* ── Couleurs urgence ─────────────────────────────────────────── */
    URGENCE_COLORS: {
        normale:      { bg: '#E8F5E9', text: '#2E7D32', icon: '🟢' },
        urgente:      { bg: '#FFF3E0', text: '#E65100', icon: '🟠' },
        tres_urgente: { bg: '#FFEBEE', text: '#C62828', icon: '🔴' },
    },

    /* ── Libellés états missions ──────────────────────────────────── */
    STATE_LABELS: {
        nouveau:          { label: 'Nouveau',          icon: '⏳', css: 'state-nouveau'  },
        assigne:          { label: 'Assigné',          icon: '👷', css: 'state-en_cours' },
        rdv_planifie:     { label: 'RDV Planifié',     icon: '📅', css: 'state-en_cours' },
        en_cours:         { label: 'En cours',         icon: '🔧', css: 'state-en_cours' },
        devis_envoye:     { label: 'Devis envoyé',     icon: '📄', css: 'state-en_cours' },
        devis_accepte:    { label: 'Devis accepté',    icon: '✅', css: 'state-en_cours' },
        devis_refuse:     { label: 'Devis refusé',     icon: '❌', css: 'state-default'  },
        travaux_en_cours: { label: 'Travaux en cours', icon: '⚙️', css: 'state-en_cours' },
        termine:          { label: 'Terminé',          icon: '🎉', css: 'state-termine'  },
        facture:          { label: 'Facturé',          icon: '🧾', css: 'state-termine'  },
        clos:             { label: 'Clos',             icon: '✔️',  css: 'state-termine'  },
        annule:           { label: 'Annulé',           icon: '🚫', css: 'state-default'  },
    },

    /* ── Libellés types intervention ─────────────────────────────── */
    TYPE_LABELS: {
        serrurerie:     '🔐 Serrurerie',
        plomberie:      '🔧 Plomberie',
        menuiserie_int: '🚪 Menuiserie Int.',
        menuiserie_ext: '🚪 Menuiserie Ext.',
        vitrerie:       '🪟 Vitrerie',
        electricite:    '⚡ Électricité',
        autre:          '🔨 Autre',
    },
};
