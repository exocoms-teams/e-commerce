# -*- coding: utf-8 -*-

DEVIS_SUR_MESURE_DATA = {
    'slug': 'sur-mesure',
    'title_fr': 'Demande de devis personnalisé',
    'title_en': 'Custom quote request',
    'subtitle_fr': 'Concevez votre capsule-house ou cabine selon vos contraintes et besoins spécifiques.',
    'subtitle_en': 'Design your capsule house or cabin according to your specific constraints and needs.',
    
    'step_gammes': [
        {'slug': 'capsule', 'name_fr': 'Gamme Capsule', 'name_en': 'Capsule Range'},
        {'slug': 'cabine', 'name_fr': 'Gamme Cabine', 'name_en': 'Cabin Range'},
        {'slug': 'dome', 'name_fr': 'Gamme Dôme', 'name_en': 'Dome Range'},
        {'slug': 'modulaire', 'name_fr': 'Gamme Modulaire', 'name_en': 'Modular Range'},
        {'slug': 'pliable', 'name_fr': 'Gamme Pliable', 'name_en': 'Foldable Range'},
        {'slug': 'autre', 'name_fr': 'Projet spécial / Inconnu', 'name_en': 'Special project / Unknown'},
    ],
    
    'terrain_specs': [
        {
            'id': 'acces_camion',
            'label_fr': 'Accessibilité du terrain',
            'label_en': 'Site accessibility',
            'options': [
                {'value': 'facile', 'label_fr': 'Accès poids lourd direct (< 10m)', 'label_en': 'Direct truck access (< 10m)'},
                {'value': 'moyen', 'label_fr': 'Accès restreint / Grutage nécessaire (10-30m)', 'label_en': 'Restricted access / Crane needed (10-30m)'},
                {'value': 'difficile', 'label_fr': 'Accès très difficile / Grande grue (> 30m)', 'label_en': 'Very difficult access / Heavy crane (> 30m)'},
            ]
        },
        {
            'id': 'fondations',
            'label_fr': 'Type de fondation envisagé',
            'label_en': 'Planned foundation type',
            'options': [
                {'value': 'vis', 'label_fr': 'Pieux vissés (recommandé / écologique)', 'label_en': 'Screw piles (recommended / eco-friendly)'},
                {'value': 'plots', 'label_fr': 'Plots en béton', 'label_en': 'Concrete pads'},
                {'value': 'dalle', 'label_fr': 'Dalle béton existante', 'label_en': 'Existing concrete slab'},
                {'value': 'a_definir', 'label_fr': 'À définir avec votre équipe', 'label_en': 'To be defined with your team'},
            ]
        }
    ],

    'options_techniques': [
        {
            'category_fr': 'Autonomie & Énergie',
            'category_en': 'Autonomy & Energy',
            'items': [
                {'code': 'OPT_SOLAR', 'label_fr': 'Kit panneaux solaires + batteries', 'label_en': 'Solar panel kit + batteries'},
                {'code': 'OPT_OFFGRID_WATER', 'label_fr': 'Récupérateur d\'eau de pluie & filtration', 'label_en': 'Rainwater harvesting & filtration'},
                {'code': 'OPT_COMPOST_WC', 'label_fr': 'Toilettes sèches / à incinération (Hors-réseau)', 'label_en': 'Dry / Incinerating toilets (Off-grid)'},
                {'code': 'OPT_PAC', 'label_fr': 'Pompe à chaleur réversible (Chaud/Froid)', 'label_en': 'Reversible heat pump (Heating/Cooling)'},
            ]
        },
        {
            'category_fr': 'Aménagement & Finitions',
            'category_en': 'Fit-out & Finishes',
            'items': [
                {'code': 'OPT_KITCHEN', 'label_fr': 'Cuisine sur-mesure intégrée', 'label_en': 'Integrated custom kitchen'},
                {'code': 'OPT_MEUBLE', 'label_fr': 'Pack mobilier optimisé (Lit escamotable, rangements)', 'label_en': 'Optimised furniture pack (Murphy bed, storage)'},
                {'code': 'OPT_TERRASSE', 'label_fr': 'Terrasse en bois composite intégrable', 'label_en': 'Integrable composite wooden deck'},
                {'code': 'OPT_DOMOTIQUE', 'label_fr': 'Pack domotique (Accès serrure connectée, gestion énergie)', 'label_en': 'Smart home pack (Connected lock, energy control)'},
            ]
        }
    ],

    'usages_projet': [
        {'value': 'principal', 'label_fr': 'Résidence principale / Studio de jardin', 'label_en': 'Main residence / Garden studio'},
        {'value': 'pro', 'label_fr': 'Bureau / Espace professionnel', 'label_en': 'Office / Professional space'},
        {'value': 'tourisme', 'label_fr': 'Projet touristique / Airbnb (1 à 3 unités)', 'label_en': 'Tourism project / Airbnb (1 to 3 units)'},
        {'value': 'parc_touristique', 'label_fr': 'Domaine / Camping / Parc (> 3 unités)', 'label_en': 'Resort / Campsite / Park (> 3 units)'},
    ]
}