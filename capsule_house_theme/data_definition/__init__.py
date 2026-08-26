# -*- coding: utf-8 -*-
"""
Sourcing des données statiques pour le site vitrine Odoo
=========================================================
Module      : website_capsule_catalog (développement spécifique Odoo)
Fichier     : data/gammes_data.py
Auteur      : Équipe Dev Odoo
Dernière modif: 2026-08-13
Contexte    : Fichier de configuration alimentant le controller HTTP `/nos-gammes`.
             Ce fichier fournit les données pour le template QWeb sans passer par
             des modèles PostgreSQL (Performance & Agilité de contenu).

Règles Métier & Demandes Client :
- Contenu exclusivement INFORMATIF (pas de vente e-commerce directe).
- Changement de structure : Studio/Duo/Panorama deviennent des 'formats' de la gamme Capsule,
  et non plus des catégories de produits de premier niveau dans le menu Odoo.
- Statut 'disponible' = fiches d'information prêtes (le badge affiché est "Détails disponibles").
  Cela NE veut PAS dire "produit en stock / achetable" dans la boutique Odoo.
- Statut 'a_confirmer' = gamme annoncée mais spécifications non arrêtées.
- Flag 'indicative': True = les métriques (kW, dimensions) reposent sur un standard
  du marché en attendant la validation définitive du fournisseur.
- Les normes techniques (NF EN 1279, NF EN 14351-1, NF C 15-100, RE2020) sont des
  références légales vérifiables applicables aux constructions modulaires.
"""

# -----------------------------------------------------------------------------
# CONSTANTES DE STATUT (Utilisées pour le filtrage dans le template QWeb)
# -----------------------------------------------------------------------------
# SOURCE : Spécification fonctionnelle - Affichage dynamique des badges
GAMME_STATUS_DISPONIBLE = 'disponible'      # Affiche les détails informatifs[cite: 1]
GAMME_STATUS_A_CONFIRMER = 'a_confirmer'    # Affiche le masque "à définir / à confirmer"[cite: 1]


# -----------------------------------------------------------------------------
# CATALOGUE DE INFORMATIONS GAMMES (`GAMMES_DATA`)
# -----------------------------------------------------------------------------
# SOURCE : Cahier des charges / CDC "Nos Gammes" (v19.0.1.0.71)
# Injecté directement dans le contexte du Controller Odoo (request.render)
GAMMES_DATA = [
    {
        # --- GAMME CAPSULE ---
        # SOURCE : Demande client du 2026-08-13 - Format de référence du site
        'slug': 'capsule',
        'status': GAMME_STATUS_DISPONIBLE,
        'icon': 'fa-home',  # Icône FontAwesome (Odoo Frontend Standard)
        'name': 'Capsule',
        'gender': 'f',
        'indicative': True,  # Activer le bandeau d'avertissement "Données indicatives"[cite: 1]
        'tagline_fr': '3 tailles disponibles · 18 à 40 m²',
        'tagline_en': '3 sizes available · 18 to 40 sqm',
        
        # SOURCE : Spécifications techniques standardisées & Normes Françaises
        'performances': [
            {'icon': 'fa-square-o', 'title_fr': 'Vitrage isolant', 'title_en': 'Insulating glazing',
             'desc_fr': 'Double vitrage, isolation optimale (NF EN 1279)', 'desc_en': 'Double glazing, optimal insulation (NF EN 1279)'},
            {'icon': 'fa-lock', 'title_fr': 'Serrure sécurisée', 'title_en': 'Secure lock',
             'desc_fr': 'Accès à code, sécurité renforcée', 'desc_en': 'Code access, enhanced security'},
            {'icon': 'fa-lightbulb-o', 'title_fr': 'Éclairage LED encastré', 'title_en': 'Recessed LED lighting',
             'desc_fr': 'Lumière chaude + rubans LED étanches extérieurs', 'desc_en': 'Warm light + weatherproof outdoor LED strips'},
            {'icon': 'fa-bath', 'title_fr': 'Salle de bain équipée', 'title_en': 'Equipped bathroom',
             'desc_fr': 'Miroir, vasque, douche vitrée', 'desc_en': 'Mirror, sink, glass shower'},
            {'icon': 'fa-sun-o', 'title_fr': 'Puits de lumière', 'title_en': 'Skylight',
             'desc_fr': 'Vitrage isolant + store motorisé', 'desc_en': 'Insulating glazing + motorised blind'},
            {'icon': 'fa-paint-brush', 'title_fr': 'Design aluminium', 'title_en': 'Aluminium design',
             'desc_fr': 'Panneaux aluminium intérieur et extérieur', 'desc_en': 'Aluminium panels inside and out'},
            {'icon': 'fa-bolt', 'title_fr': 'Alimentation électrique', 'title_en': 'Electrical supply',
             'desc_fr': 'Câblage cuivre, installation NF C 15-100', 'desc_en': 'Copper wiring, NF C 15-100 installation'},
            {'icon': 'fa-arrows-v', 'title_fr': 'Escalier 3 marches', 'title_en': '3-step staircase',
             'desc_fr': 'Acier léger + bois composite inclus', 'desc_en': 'Lightweight steel + composite wood included'},
            {'icon': 'fa-building-o', 'title_fr': 'Structure solide', 'title_en': 'Solid structure',
             'desc_fr': 'Anneau de levage + support galvanisé', 'desc_en': 'Lifting ring + galvanised support'},
        ],
        
        # SOURCE : Restructuration menu client - Anciennes catégories converties en sous-formats
        'formats': [
            {'name': 'Studio', 'surface_fr': '18-20 m²', 'surface_en': '18-20 sqm', 'note_fr': 'Compact', 'note_en': 'Compact'},
            {'name': 'Duo', 'surface_fr': '26-30 m²', 'surface_en': '26-30 sqm', 'note_fr': "Jusqu'à 4 pers.", 'note_en': 'Up to 4 people'},
            {'name': 'Panorama', 'surface_fr': '36-40 m²', 'surface_en': '36-40 sqm', 'note_fr': '4 à 6 pers.', 'note_en': '4 to 6 people'},
        ],
        
        # SOURCE : Législation et normes de construction applicables
        'specs_ext': [
            {'label_fr': 'Façade', 'label_en': 'Facade', 'value_fr': 'Panneau aluminium', 'value_en': 'Aluminium panel'},
            {'label_fr': "Porte d'entrée", 'label_en': 'Entrance door', 'value_fr': 'Inox + serrure à code', 'value_en': 'Stainless steel + code lock'},
            {'label_fr': 'Vitrage', 'label_en': 'Glazing', 'value_fr': 'Vitrage isolant NF EN 1279', 'value_en': 'Insulating glazing NF EN 1279'},
            {'label_fr': 'Fenêtres', 'label_en': 'Windows', 'value_fr': 'Performances NF EN 14351-1', 'value_en': 'Performance NF EN 14351-1'},
        ],
        'specs_int': [
            {'label_fr': 'Sol principal', 'label_en': 'Main floor', 'value_fr': 'Revêtement SPC', 'value_en': 'SPC flooring'},
            {'label_fr': 'Électricité', 'label_en': 'Electrical', 'value_fr': 'Installation NF C 15-100', 'value_en': 'NF C 15-100 wiring'},
            {'label_fr': 'Automatismes', 'label_en': 'Automation', 'value_fr': 'Store motorisé (option)', 'value_en': 'Motorised blind (option)'},
        ],
        'equipements_fr': [
            'Cadre acier galvanisé', 'Fenêtres double vitrage',
            'Construction isolée et étanche', 'Sanitaire équipé (WC, douche, lavabo)',
            'Installation électrique NF C 15-100', 'Verrouillage sécurisé',
        ],
        'equipements_en': [
            'Galvanised steel frame', 'Double-glazed windows',
            'Insulated, weatherproof construction', 'Equipped bathroom (toilet, shower, sink)',
            'NF C 15-100 electrical wiring', 'Secure locking',
        ],
        'options_fr': ['Chauffage additionnel', 'Isolation renforcée', 'Triple vitrage', 'Aménagement sur mesure'],
        'options_en': ['Additional heating', 'Reinforced insulation', 'Triple glazing', 'Custom fit-out'],
        'usages': ['Logement', 'Bureau', 'Résidence secondaire', 'Location & Airbnb'],
    },
    {
        # --- GAMME CABINE ---
        # SOURCE : Extension gamme produit (Micro-offices / Bureaux de jardin)
        'slug': 'cabine',
        'status': GAMME_STATUS_DISPONIBLE,
        'icon': 'fa-th-large',
        'name': 'Cabine',
        'gender': 'f',
        'indicative': True,
        'tagline_fr': '3 tailles disponibles · 10 à 25 m²',
        'tagline_en': '3 sizes available · 10 to 25 sqm',
        'performances': [
            {'icon': 'fa-tree', 'title_fr': 'Structure bois & acier', 'title_en': 'Wood & steel structure',
             'desc_fr': 'Châssis robuste et bardage haute résistance', 'desc_en': 'Robust chassis and high-resistance cladding'},
            {'icon': 'fa-sun-o', 'title_fr': 'Lumière naturelle', 'title_en': 'Natural light',
             'desc_fr': 'Grande baie vitrée panoramique', 'desc_en': 'Large panoramic glass window'},
            {'icon': 'fa-shield', 'title_fr': 'Isolation thermique', 'title_en': 'Thermal insulation',
             'desc_fr': 'Isolation 4 saisons (mousse haute densité / laine de roche)', 'desc_en': '4-season insulation (high-density foam / rock wool)'},
            {'icon': 'fa-plug', 'title_fr': 'Plug & Play', 'title_en': 'Plug & Play',
             'desc_fr': 'Prête à raccorder (électricité + eau)', 'desc_en': 'Ready to connect (electricity + water)'},
            {'icon': 'fa-volume-off', 'title_fr': 'Isolation acoustique', 'title_en': 'Acoustic insulation',
             'desc_fr': 'Confort phonique optimisé pour le travail', 'desc_en': 'Optimised sound comfort for work'},
            {'icon': 'fa-compress', 'title_fr': 'Emprise optimisée', 'title_en': 'Optimised footprint',
             'desc_fr': "S'intègre facilement dans tous les jardins", 'desc_en': 'Easily integrates into any garden'},
            {'icon': 'fa-bolt', 'title_fr': 'Électricité intégrée', 'title_en': 'Integrated electricity',
             'desc_fr': 'Prises, interrupteurs et tableau pré-câblé NF C 15-100', 'desc_en': 'Outlets, switches and pre-wired NF C 15-100 panel'},
            {'icon': 'fa-paint-brush', 'title_fr': 'Finition moderne', 'title_en': 'Modern finish',
             'desc_fr': 'Habillage intérieur bois chaleureux ou design contemporain', 'desc_en': 'Warm interior wood panelling or contemporary design'},
        ],
        'formats': [
            {'name': 'Solo / Bureau', 'surface_fr': '10-12 m²', 'surface_en': '10-12 sqm', 'note_fr': 'Idéal télétravail / Micro-office', 'note_en': 'Ideal for home office'},
            {'name': 'Comfort', 'surface_fr': '15-18 m²', 'surface_en': '15-18 sqm', 'note_fr': "Chambre d'amis / Studio", 'note_en': 'Guest room / Studio'},
            {'name': 'Lodge', 'surface_fr': '20-25 m²', 'surface_en': '20-25 sqm', 'note_fr': 'Hébergement équipé (2 à 4 pers.)', 'note_en': 'Equipped accommodation (2 to 4 people)'},
        ],
        'specs_ext': [
            {'label_fr': 'Bardage', 'label_en': 'Cladding', 'value_fr': 'Bois composite / Acier traité', 'value_en': 'Composite wood / Treated steel'},
            {'label_fr': 'Baies & Ouvertures', 'label_en': 'Openings', 'value_fr': 'Châssis aluminium rupture de pont thermique', 'value_en': 'Thermal break aluminium frames'},
            {'label_fr': 'Toiture', 'label_en': 'Roofing', 'value_fr': 'Étanchéité EPDM / Bac acier isolé', 'value_en': 'EPDM waterproofing / Insulated steel deck'},
            {'label_fr': 'Vitrage', 'label_en': 'Glazing', 'value_fr': 'Double vitrage feuilleté sécurit', 'value_en': 'Double-glazed laminated safety glass'},
        ],
        'specs_int': [
            {'label_fr': 'Revêtement sol', 'label_en': 'Flooring', 'value_fr': 'Parquet stratifié ou vinyle haut passage', 'value_en': 'Laminate or heavy-duty vinyl flooring'},
            {'label_fr': 'Murs & Plafond', 'label_en': 'Walls & Ceiling', 'value_fr': 'Panneaux bois PEFC / Placo peint', 'value_en': 'PEFC wood panels / Painted plasterboard'},
            {'label_fr': 'Électricité', 'label_en': 'Electrical', 'value_fr': 'Installation conforme NF C 15-100', 'value_en': 'NF C 15-100 compliant installation'},
        ],
        'equipements_fr': [
            'Châssis autoportant en acier', 'Isolation thermique et acoustique renforcée',
            'Éclairage LED intérieur encastré', 'Tableau électrique pré-équipé',
            "Ventilation mécanique / Grilles d'aération", 'Serrure de sécurité à clé ou digicode',
        ],
        'equipements_en': [
            'Self-supporting steel frame', 'Reinforced thermal and acoustic insulation',
            'Recessed interior LED lighting', 'Pre-equipped electrical panel',
            'Mechanical ventilation / Air vents', 'Key or keypad security lock',
        ],
        'options_fr': [
            'Climatisation réversible (Pompe à chaleur)', 'Panneaux solaires en toiture',
            'Kitchinette équipée', "Salle d'eau compacte (WC + douche)", 'Terrasse extérieure en bois',
        ],
        'options_en': [
            'Reversible air conditioning (Heat pump)', 'Rooftop solar panels',
            'Equipped kitchenette', 'Compact bathroom (toilet + shower)', 'Outdoor wooden deck',
        ],
        'usages': [
            'Bureau de jardin / Télétravail', "Chambre d'amis / Studio d'adolescent",
            "Atelier d'artiste / Salle de sport", 'Gîte / Hébergement insolite',
        ],
    },
    {
        # --- GAMME DÔME ---
        # SOURCE : Gamme hébergements insolites / dômes géodésiques
        'slug': 'dome',
        'status': GAMME_STATUS_DISPONIBLE,
        'icon': 'fa-circle-o',
        'name': 'Dôme',
        'gender': 'm',
        'indicative': True,
        'tagline_fr': '3 tailles disponibles · 19 à 50 m²',
        'tagline_en': '3 sizes available · 19 to 50 sqm',
        'performances': [
            {'icon': 'fa-refresh', 'title_fr': 'Structure triangulée', 'title_en': 'Triangulated structure',
            'desc_fr': 'Excellente résistance aux vents forts et à la neige', 'desc_en': 'Strong resistance to high winds and snow load'},
            {'icon': 'fa-square-o', 'title_fr': 'Vitrage isolant', 'title_en': 'Insulating glazing',
            'desc_fr': 'Double vitrage sécurit, isolation optimale (NF EN 1279)', 'desc_en': 'Tempered double glazing, optimal insulation (NF EN 1279)'},
            {'icon': 'fa-thermometer-half', 'title_fr': 'Isolation renforcée', 'title_en': 'Enhanced insulation',
            'desc_fr': 'Panneaux isolants, faibles déperditions grâce à la forme sans angles', 'desc_en': 'Insulated panels, low heat loss thanks to the angle-free shape'},
            {'icon': 'fa-bath', 'title_fr': 'Salle de bain équipée', 'title_en': 'Equipped bathroom',
            'desc_fr': 'Miroir, vasque, douche vitrée', 'desc_en': 'Mirror, sink, glass shower'},
            {'icon': 'fa-lightbulb-o', 'title_fr': 'Éclairage LED encastré', 'title_en': 'Recessed LED lighting',
            'desc_fr': 'Lumière chaude intérieure et extérieure', 'desc_en': 'Warm interior and exterior lighting'},
            {'icon': 'fa-building-o', 'title_fr': 'Structure aluminium', 'title_en': 'Aluminium structure',
            'desc_fr': 'Ossature légère et durable, laquée', 'desc_en': 'Lightweight, durable, lacquered frame'},
            {'icon': 'fa-bolt', 'title_fr': 'Alimentation électrique', 'title_en': 'Electrical supply',
            'desc_fr': 'Câblage cuivre, installation NF C 15-100', 'desc_en': 'Copper wiring, NF C 15-100 installation'},
            {'icon': 'fa-tint', 'title_fr': 'Ventilation anti-humidité', 'title_en': 'Anti-humidity ventilation',
            'desc_fr': 'Circulation d\'air optimisée par la forme sphérique', 'desc_en': 'Optimised air circulation thanks to the spherical shape'},
        ],
        'formats': [
            {'name': 'Compact', 'surface_fr': '19-20 m²', 'surface_en': '19-20 sqm', 'note_fr': 'Jusqu\'à 2 pers.', 'note_en': 'Up to 2 people'},
            {'name': 'Confort', 'surface_fr': '28-30 m²', 'surface_en': '28-30 sqm', 'note_fr': 'Jusqu\'à 4 pers.', 'note_en': 'Up to 4 people'},
            {'name': 'Panoramique', 'surface_fr': '38-50 m²', 'surface_en': '38-50 sqm', 'note_fr': '4 à 6 pers.', 'note_en': '4 to 6 people'},
        ],
        'specs_ext': [
            {'label_fr': 'Structure', 'label_en': 'Structure', 'value_fr': 'Aluminium laqué triangulé', 'value_en': 'Triangulated lacquered aluminium'},
            {'label_fr': 'Vitrage', 'label_en': 'Glazing', 'value_fr': 'Double vitrage sécurit NF EN 1279', 'value_en': 'Tempered double glazing NF EN 1279'},
            {'label_fr': 'Porte d\'entrée', 'label_en': 'Entrance door', 'value_fr': 'Aluminium + verre trempé', 'value_en': 'Aluminium + tempered glass'},
            {'label_fr': 'Résistance au vent', 'label_en': 'Wind resistance', 'value_fr': 'Jusqu\'à 100 km/h', 'value_en': 'Up to 100 km/h'},
        ],
        'specs_int': [
            {'label_fr': 'Sol principal', 'label_en': 'Main floor', 'value_fr': 'Revêtement SPC', 'value_en': 'SPC flooring'},
            {'label_fr': 'Isolation', 'label_en': 'Insulation', 'value_fr': 'Panneaux isolants PIR', 'value_en': 'PIR insulation panels'},
            {'label_fr': 'Électricité', 'label_en': 'Electrical', 'value_fr': 'Installation NF C 15-100', 'value_en': 'NF C 15-100 wiring'},
        ],
        'equipements_fr': [
            'Structure aluminium triangulée', 'Vitrage double sécurit',
            'Isolation thermique renforcée', 'Sanitaire équipé (WC, douche, lavabo)',
            'Installation électrique NF C 15-100', 'Ventilation anti-humidité',
        ],
        'equipements_en': [
            'Triangulated aluminium structure', 'Tempered double glazing',
            'Enhanced thermal insulation', 'Equipped bathroom (toilet, shower, sink)',
            'NF C 15-100 electrical wiring', 'Anti-humidity ventilation',
        ],
        'options_fr': ['Chauffage additionnel', 'Kit autonomie énergie (photovoltaïque)', 'Mezzanine (formats 38 m² et +)', 'Occultation extérieure'],
        'options_en': ['Additional heating', 'Energy autonomy kit (solar)', 'Mezzanine (38 sqm+ formats)', 'Outdoor blackout cover'],
        'usages': ['Logement', 'Bureau', 'Résidence secondaire', 'Location & Airbnb'],
    },
    {
        # --- GAMME MODULAIRE ---
        # SOURCE : Gamme extensions RE2020 combinables
        'slug': 'modulaire',
        'status': GAMME_STATUS_DISPONIBLE,
        'icon': 'fa-puzzle-piece',
        'name': 'Modulaire',
        'gender': 'm',
        'indicative': True,
        'tagline_fr': 'Système extensible · modules combinables à volonté',
        'tagline_en': 'Extensible system · modules combinable as needed',
        'performances': [
            {'icon': 'fa-cubes', 'title_fr': 'Modules combinables', 'title_en': 'Combinable modules',
            'desc_fr': 'Assemblez plusieurs unités pour agrandir votre espace', 'desc_en': 'Assemble several units to expand your space'},
            {'icon': 'fa-industry', 'title_fr': 'Fabrication en atelier', 'title_en': 'Workshop manufacturing',
            'desc_fr': 'Précision industrielle, qualité constante d\'un module à l\'autre', 'desc_en': 'Industrial precision, consistent quality across modules'},
            {'icon': 'fa-square-o', 'title_fr': 'Isolation renforcée', 'title_en': 'Enhanced insulation',
            'desc_fr': 'Conforme RE2020, ossature bois ou acier au choix', 'desc_en': 'RE2020 compliant, timber or steel frame available'},
            {'icon': 'fa-bath', 'title_fr': 'Salle de bain équipée', 'title_en': 'Equipped bathroom',
            'desc_fr': 'Miroir, vasque, douche vitrée', 'desc_en': 'Mirror, sink, glass shower'},
            {'icon': 'fa-lightbulb-o', 'title_fr': 'Éclairage LED encastré', 'title_en': 'Recessed LED lighting',
            'desc_fr': 'Lumière chaude intérieure et extérieure', 'desc_en': 'Warm interior and exterior lighting'},
            {'icon': 'fa-clock-o', 'title_fr': 'Montage rapide', 'title_en': 'Quick assembly',
            'desc_fr': 'Installation en quelques jours, hors gros œuvre', 'desc_en': 'Installed in a few days, no heavy groundwork'},
            {'icon': 'fa-bolt', 'title_fr': 'Alimentation électrique', 'title_en': 'Electrical supply',
            'desc_fr': 'Câblage cuivre, installation NF C 15-100', 'desc_en': 'Copper wiring, NF C 15-100 installation'},
            {'icon': 'fa-arrows-alt', 'title_fr': 'Configuration libre', 'title_en': 'Free configuration',
            'desc_fr': 'Plain-pied ou superposé selon votre terrain', 'desc_en': 'Single-storey or stacked, depending on your plot'},
        ],
        'formats': [
            {'name': 'Module simple', 'surface_fr': '16-20 m²', 'surface_en': '16-20 sqm', 'note_fr': '1 module · jusqu\'à 2 pers.', 'note_en': '1 module · up to 2 people'},
            {'name': 'Module double', 'surface_fr': '30-38 m²', 'surface_en': '30-38 sqm', 'note_fr': '2 modules assemblés · jusqu\'à 4 pers.', 'note_en': '2 modules combined · up to 4 people'},
            {'name': 'Module triple', 'surface_fr': '45-57 m²', 'surface_en': '45-57 sqm', 'note_fr': '3 modules assemblés · 4 à 6 pers.', 'note_en': '3 modules combined · 4 to 6 people'},
        ],
        'specs_ext': [
            {'label_fr': 'Structure', 'label_en': 'Structure', 'value_fr': 'Ossature bois ou acier au choix', 'value_en': 'Timber or steel frame, your choice'},
            {'label_fr': 'Vitrage', 'label_en': 'Glazing', 'value_fr': 'Double vitrage NF EN 1279', 'value_en': 'Double glazing NF EN 1279'},
            {'label_fr': 'Isolation thermique', 'label_en': 'Thermal insulation', 'value_fr': 'Conforme RE2020', 'value_en': 'RE2020 compliant'},
            {'label_fr': 'Fondations', 'label_en': 'Foundations', 'value_fr': 'Plots réglables ou pieux métalliques', 'value_en': 'Adjustable pads or metal piles'},
        ],
        'specs_int': [
            {'label_fr': 'Sol principal', 'label_en': 'Main floor', 'value_fr': 'Revêtement SPC', 'value_en': 'SPC flooring'},
            {'label_fr': 'Électricité', 'label_en': 'Electrical', 'value_fr': 'Installation NF C 15-100', 'value_en': 'NF C 15-100 wiring'},
            {'label_fr': 'Chauffage', 'label_en': 'Heating', 'value_fr': 'Pompe à chaleur (option)', 'value_en': 'Heat pump (option)'},
        ],
        'equipements_fr': [
            'Ossature isolée conforme RE2020', 'Vitrage double isolant',
            'Fabrication et contrôle qualité en atelier', 'Sanitaire équipé (WC, douche, lavabo)',
            'Installation électrique NF C 15-100', 'Modules assemblables sans limite de configuration',
        ],
        'equipements_en': [
            'RE2020-compliant insulated frame', 'Insulated double glazing',
            'Workshop manufacturing and quality control', 'Equipped bathroom (toilet, shower, sink)',
            'NF C 15-100 electrical wiring', 'Modules combinable with no configuration limit',
        ],
        'options_fr': ['Pompe à chaleur', 'Panneaux photovoltaïques', 'Triple vitrage', 'Module supplémentaire (extension)'],
        'options_en': ['Heat pump', 'Solar panels', 'Triple glazing', 'Extra module (extension)'],
        'usages': ['Logement', 'Bureau', 'Résidence secondaire', 'Location & Airbnb'],
    },
    {
        # --- GAMME PLIABLE ---
        # SOURCE : Gamme transportable repliable (Note interne : validation Marini requise)
        'slug': 'pliable',
        'status': GAMME_STATUS_DISPONIBLE,
        'icon': 'fa-inbox',
        'name': 'Pliable',
        'gender': 'm',
        'indicative': True,
        'tagline_fr': '3 tailles disponibles · 14 à 38 m²',
        'tagline_en': '3 sizes available · 14 to 38 sqm',
        'performances': [
            {'icon': 'fa-cube', 'title_fr': 'Cadre acier galvanisé', 'title_en': 'Galvanised steel frame',
            'desc_fr': 'Forte épaisseur, résiste aux pliages et dépliages répétés', 'desc_en': 'Heavy-duty, withstands repeated folding and unfolding'},
            {'icon': 'fa-clock-o', 'title_fr': 'Déploiement rapide', 'title_en': 'Rapid deployment',
            'desc_fr': "Installation en quelques heures une fois livré sur site", 'desc_en': 'Set up in a few hours once delivered on site'},
            {'icon': 'fa-square-o', 'title_fr': 'Isolation renforcée', 'title_en': 'Enhanced insulation',
            'desc_fr': 'Panneaux sandwich isolants, conforme RE2020', 'desc_en': 'Insulated sandwich panels, RE2020 compliant'},
            {'icon': 'fa-bath', 'title_fr': 'Salle de bain équipée', 'title_en': 'Equipped bathroom',
            'desc_fr': 'Miroir, vasque, douche vitrée', 'desc_en': 'Mirror, sink, glass shower'},
            {'icon': 'fa-lightbulb-o', 'title_fr': 'Éclairage LED encastré', 'title_en': 'Recessed LED lighting',
            'desc_fr': 'Lumière chaude intérieure et extérieure', 'desc_en': 'Warm interior and exterior lighting'},
            {'icon': 'fa-tint', 'title_fr': 'Étanchéité toutes conditions', 'title_en': 'All-weather sealing',
            'desc_fr': 'Panneaux résistants aux intempéries', 'desc_en': 'Weather-resistant panels'},
            {'icon': 'fa-bolt', 'title_fr': 'Alimentation électrique', 'title_en': 'Electrical supply',
            'desc_fr': 'Câblage cuivre, installation NF C 15-100', 'desc_en': 'Copper wiring, NF C 15-100 installation'},
            {'icon': 'fa-truck', 'title_fr': 'Transport facilité', 'title_en': 'Easy transport',
            'desc_fr': 'Livré replié, encombrement réduit sur route', 'desc_en': 'Delivered folded, reduced footprint on the road'},
        ],
        'formats': [
            {'name': 'Compact', 'surface_fr': '14-18 m²', 'surface_en': '14-18 sqm', 'note_fr': 'Jusqu\'à 2 pers.', 'note_en': 'Up to 2 people'},
            {'name': 'Confort', 'surface_fr': '25-29 m²', 'surface_en': '25-29 sqm', 'note_fr': 'Jusqu\'à 4 pers.', 'note_en': 'Up to 4 people'},
            {'name': 'Panoramique', 'surface_fr': '35-38 m²', 'surface_en': '35-38 sqm', 'note_fr': '4 à 6 pers.', 'note_en': '4 to 6 people'},
        ],
        'specs_ext': [
            {'label_fr': 'Structure', 'label_en': 'Structure', 'value_fr': 'Cadre acier galvanisé pliable', 'value_en': 'Foldable galvanised steel frame'},
            {'label_fr': 'Façade', 'label_en': 'Facade', 'value_fr': 'Panneaux sandwich isolants', 'value_en': 'Insulated sandwich panels'},
            {'label_fr': 'Vitrage', 'label_en': 'Glazing', 'value_fr': 'Double vitrage NF EN 1279', 'value_en': 'Double glazing NF EN 1279'},
            {'label_fr': 'Isolation thermique', 'label_en': 'Thermal insulation', 'value_fr': 'Conforme RE2020', 'value_en': 'RE2020 compliant'},
        ],
        'specs_int': [
            {'label_fr': 'Sol principal', 'label_en': 'Main floor', 'value_fr': 'Revêtement SPC', 'value_en': 'SPC flooring'},
            {'label_fr': 'Électricité', 'label_en': 'Electrical', 'value_fr': 'Installation NF C 15-100', 'value_en': 'NF C 15-100 wiring'},
            {'label_fr': 'Ventilation', 'label_en': 'Ventilation', 'value_fr': 'VMC anti-condensation', 'value_en': 'Anti-condensation ventilation'},
        ],
        'equipements_fr': [
            'Cadre acier galvanisé renforcé', 'Panneaux sandwich résistants aux intempéries',
            'Isolation thermique RE2020', 'Sanitaire équipé (WC, douche, lavabo)',
            'Installation électrique NF C 15-100', 'Livraison repliée, montage rapide',
        ],
        'equipements_en': [
            'Reinforced galvanised steel frame', 'Weather-resistant sandwich panels',
            'RE2020 thermal insulation', 'Equipped bathroom (toilet, shower, sink)',
            'NF C 15-100 electrical wiring', 'Delivered folded, quick assembly',
        ],
        'options_fr': ['Chauffage additionnel', 'Isolation renforcée', 'Triple vitrage', 'Module supplémentaire (extension)'],
        'options_en': ['Additional heating', 'Reinforced insulation', 'Triple glazing', 'Extra module (extension)'],
        'usages': ['Logement', 'Bureau', 'Résidence secondaire', 'Location & Airbnb'],
    },
]


# -----------------------------------------------------------------------------
# ARBORESCENCE DU FORMULAIRE DE DEVIS SUR MESURE (`DEVIS_SUR_MESURE_DATA`)
# -----------------------------------------------------------------------------
# SOURCE : Tunnel de qualification CRM / Génération automatique de crm.lead
# Les clés / valeurs sont mappées sur les champs personnalisés Odoo (x_studio_*)
DEVIS_SUR_MESURE_DATA = {
    'slug': 'sur-mesure',
    'title_fr': 'Demande de devis personnalisé',
    'title_en': 'Custom quote request',
    'subtitle_fr': 'Concevez votre capsule-house, cabine ou module selon vos contraintes, matériaux et besoins spécifiques.',
    'subtitle_en': 'Design your capsule house, cabin or module according to your specific constraints, materials and needs.',
    
    # -------------------------------------------------------------------------
    # ÉTAPE 1 — SÉLECTION DE LA GAMME & FORMAT/TAILLE
    # -------------------------------------------------------------------------
    'step_gammes': [
        {
            'slug': 'capsule',
            'name_fr': 'Gamme Capsule',
            'name_en': 'Capsule Range',
            'description_fr': 'Design futuriste aluminium, 18 à 40 m²',
            'description_en': 'Futuristic aluminium design, 18 to 40 sqm',
            'formats': [
                {'code': 'CAP_STUDIO', 'label_fr': 'Studio (18 - 20 m²)', 'label_en': 'Studio (18 - 20 sqm)'},
                {'code': 'CAP_DUO', 'label_fr': 'Duo (26 - 30 m²)', 'label_en': 'Duo (26 - 30 sqm)'},
                {'code': 'CAP_PANORAMA', 'label_fr': 'Panorama (36 - 40 m²)', 'label_en': 'Panorama (36 - 40 sqm)'},
                {'code': 'CAP_CUSTOM', 'label_fr': 'Dimensions sur-mesure', 'label_en': 'Custom dimensions'},
            ]
        },
        {
            'slug': 'cabine',
            'name_fr': 'Gamme Cabine',
            'name_en': 'Cabin Range',
            'description_fr': 'Style bois & acier, idéale bureau ou studio de jardin (10 à 25 m²)',
            'description_en': 'Wood & steel style, ideal for office or garden studio (10 to 25 sqm)',
            'formats': [
                {'code': 'CAB_SOLO', 'label_fr': 'Solo / Bureau (10 - 12 m²)', 'label_en': 'Solo / Office (10 - 12 sqm)'},
                {'code': 'CAB_COMFORT', 'label_fr': 'Comfort (15 - 18 m²)', 'label_en': 'Comfort (15 - 18 sqm)'},
                {'code': 'CAB_LODGE', 'label_fr': 'Lodge (20 - 25 m²)', 'label_en': 'Lodge (20 - 25 sqm)'},
                {'code': 'CAB_CUSTOM', 'label_fr': 'Dimensions sur-mesure', 'label_en': 'Custom dimensions'},
            ]
        },
        {
            'slug': 'dome',
            'name_fr': 'Gamme Dôme',
            'name_en': 'Dome Range',
            'description_fr': 'Structure géodésique triangulée panoramique (19 à 50 m²)',
            'description_en': 'Triangulated geodesic panoramic structure (19 to 50 sqm)',
            'formats': [
                {'code': 'DOM_COMPACT', 'label_fr': 'Compact (19 - 20 m²)', 'label_en': 'Compact (19 - 20 sqm)'},
                {'code': 'DOM_CONFORT', 'label_fr': 'Confort (28 - 30 m²)', 'label_en': 'Confort (28 - 30 sqm)'},
                {'code': 'DOM_PANORAMIQUE', 'label_fr': 'Panoramique (38 - 50 m²)', 'label_en': 'Panoramic (38 - 50 sqm)'},
                {'code': 'DOM_CUSTOM', 'label_fr': 'Diamètre / Surface sur-mesure', 'label_en': 'Custom diameter / surface'},
            ]
        },
        {
            'slug': 'modulaire',
            'name_fr': 'Gamme Modulaire',
            'name_en': 'Modular Range',
            'description_fr': 'Système extensible RE2020 par juxtaposition de modules',
            'description_en': 'RE2020 extensible system by assembling modules',
            'formats': [
                {'code': 'MOD_1', 'label_fr': 'Module simple (16 - 20 m²)', 'label_en': 'Single module (16 - 20 sqm)'},
                {'code': 'MOD_2', 'label_fr': 'Module double (30 - 38 m²)', 'label_en': 'Double module (30 - 38 sqm)'},
                {'code': 'MOD_3', 'label_fr': 'Module triple (45 - 57 m²)', 'label_en': 'Triple module (45 - 57 sqm)'},
                {'code': 'MOD_PLUS', 'label_fr': 'Projet sur-mesure (> 4 modules / Étage)', 'label_en': 'Custom project (> 4 modules / Multi-storey)'},
            ]
        },
        {
            'slug': 'pliable',
            'name_fr': 'Gamme Pliable',
            'name_en': 'Foldable Range',
            'description_fr': 'Structure rédéployable rapidement (14 à 38 m²)',
            'description_en': 'Quickly deployable structure (14 to 38 sqm)',
            'formats': [
                {'code': 'PLI_COMPACT', 'label_fr': 'Compact (14 - 18 m²)', 'label_en': 'Compact (14 - 18 sqm)'},
                {'code': 'PLI_CONFORT', 'label_fr': 'Confort (25 - 29 m²)', 'label_en': 'Confort (25 - 29 sqm)'},
                {'code': 'PLI_PANORAMIQUE', 'label_fr': 'Panoramique (35 - 38 m²)', 'label_en': 'Panoramic (35 - 38 sqm)'},
            ]
        },
        {
            'slug': 'autre',
            'name_fr': 'Projet spécial / Architecture sur-mesure',
            'name_en': 'Special project / Custom architecture',
            'description_fr': 'Étude personnalisée hors catalogue standard',
            'description_en': 'Custom study outside standard catalog',
            'formats': []
        },
    ],

    # -------------------------------------------------------------------------
    # ÉTAPE 2 — PRÉCISIONS SUPERFICIE ET AGENCEMENT
    # -------------------------------------------------------------------------
    'superficie_specs': {
        'surface_cible': {
            'label_fr': 'Superficie globale souhaitée (m²)',
            'label_en': 'Desired total floor area (sqm)',
            'type': 'number',
            'placeholder': 'ex: 28',
            'min': 10,
            'max': 200,
        },
        'hauteur_plafond': {
            'label_fr': 'Hauteur sous plafond souhaitée',
            'label_en': 'Desired ceiling height',
            'options': [
                {'value': 'standard', 'label_fr': 'Standard (2,40 m)', 'label_en': 'Standard (2.40 m)'},
                {'value': 'haut', 'label_fr': 'Hauteur augmentée (2,60 m - 2,80 m)', 'label_en': 'Increased height (2.60 m - 2.80 m)'},
                {'value': 'mezzanine', 'label_fr': 'Espace pour Mezzanine (> 3,20 m)', 'label_en': 'Space for Mezzanine (> 3.20 m)'},
            ]
        },
        'agencement': {
            'label_fr': 'Nombre de pièces principales',
            'label_en': 'Number of main rooms',
            'options': [
                {'value': 'studio_open', 'label_fr': 'Open-space / Studio monopièce', 'label_en': 'Open-space / Single room studio'},
                {'value': 't2', 'label_fr': '2 pièces (1 Chambre séparée + Séjour)', 'label_en': '2 rooms (1 Separate bedroom + Living room)'},
                {'value': 't3', 'label_fr': '3 pièces (2 Chambres + Séjour)', 'label_en': '3 rooms (2 Bedrooms + Living room)'},
                {'value': 'custom_layout', 'label_fr': 'Agencement spécifique sur plan', 'label_en': 'Specific layout from custom plan'},
            ]
        }
    },

    # -------------------------------------------------------------------------
    # ÉTAPE 3 — SELECTION DES MATÉRIAUX (EXTÉRIEUR & INTÉRIEUR)
    # -------------------------------------------------------------------------
    'materiaux_specs': [
        {
            'category_fr': 'Bardage & Revêtement Extérieur',
            'category_en': 'External Cladding & Coating',
            'options': [
                {'code': 'MAT_EXT_ALU', 'label_fr': 'Panneaux aluminium laqué (Look futuriste)', 'label_en': 'Lacquered aluminium panels (Futuristic look)'},
                {'code': 'MAT_EXT_BOIS_NAT', 'label_fr': 'Bardage Bois naturel PEFC (Mélèze / Douglas / Cèdre)', 'label_en': 'Natural PEFC wood cladding (Larch / Douglas / Cedar)'},
                {'code': 'MAT_EXT_BOIS_COMP', 'label_fr': 'Bardage Bois composite (Sans entretien)', 'label_en': 'Composite wood cladding (Maintenance free)'},
                {'code': 'MAT_EXT_ACIER_ZINC', 'label_fr': 'Acier traité / Zinc joint debout', 'label_en': 'Treated steel / Standing seam zinc'},
                {'code': 'MAT_EXT_MIXTE', 'label_fr': 'Finition mixte (Bois & Aluminium/Acier)', 'label_en': 'Mixed finish (Wood & Aluminium/Steel)'},
            ]
        },
        {
            'category_fr': 'Sol Intérieur',
            'category_en': 'Interior Flooring',
            'options': [
                {'code': 'MAT_SOL_SPC', 'label_fr': 'Revêtement SPC haute résistance (Effet parquet / béton)', 'label_en': 'High-resistance SPC flooring (Parquet / concrete effect)'},
                {'code': 'MAT_SOL_PARQUET', 'label_fr': 'Parquet contrecollé bois massif', 'label_en': 'Engineered hardwood flooring'},
                {'code': 'MAT_SOL_VINYLE', 'label_fr': 'Vinyle PVC passage intensif (Grand confort acoustique)', 'label_en': 'Heavy-duty PVC vinyl (High acoustic comfort)'},
                {'code': 'MAT_SOL_RESINE', 'label_fr': 'Résine coulée aspect béton ciré', 'label_en': 'Poured resin with polished concrete effect'},
            ]
        },
        {
            'category_fr': 'Murs & Plafonds Intérieurs',
            'category_en': 'Interior Walls & Ceilings',
            'options': [
                {'code': 'MAT_INT_BOIS', 'label_fr': 'Habillage bois chaleureux (Contreplaqué bouleau / Epicéa)', 'label_en': 'Warm wood panelling (Birch plywood / Spruce)'},
                {'code': 'MAT_INT_PLACO', 'label_fr': 'Panneaux de finition peints (Blanc / Couleurs au choix)', 'label_en': 'Painted finish panels (White / Custom colours)'},
                {'code': 'MAT_INT_ALU', 'label_fr': 'Panneaux aluminium / Composite contemporain', 'label_en': 'Aluminium / Contemporary composite panels'},
            ]
        },
        {
            'category_fr': 'Menuiseries & Vitrages',
            'category_en': 'Joinery & Glazing',
            'options': [
                {'code': 'MAT_VIT_DV_STD', 'label_fr': 'Double vitrage isolant renforcé (NF EN 1279)', 'label_en': 'Reinforced insulating double glazing (NF EN 1279)'},
                {'code': 'MAT_VIT_TV', 'label_fr': 'Triple vitrage haute performance thermique', 'label_en': 'High thermal performance triple glazing'},
                {'code': 'MAT_VIT_FEUILLETE', 'label_fr': 'Vitrage feuilleté Sécurit anti-effraction', 'label_en': 'Laminated burglar-resistant safety glass'},
                {'code': 'MAT_VIT_TEINTE', 'label_fr': 'Vitrage teinté / Miroir sans étain (Intimité extérieure)', 'label_en': 'Tinted glass / One-way mirror glass (Exterior privacy)'},
            ]
        },
        {
            'category_fr': 'Isolation Thermique & Acoustique',
            'category_en': 'Thermal & Acoustic Insulation',
            'options': [
                {'code': 'ISO_RE2020', 'label_fr': 'Isolation standard RE2020 (Laine de roche / PUR)', 'label_en': 'Standard RE2020 insulation (Rock wool / PUR)'},
                {'code': 'ISO_BIO', 'label_fr': 'Isolation biosourcée (Laine de bois / Chanvre / Coton)', 'label_en': 'Bio-based insulation (Wood fibre / Hemp / Cotton)'},
                {'code': 'ISO_PHONIQUE_PLUS', 'label_fr': 'Renforcement acoustique haute densité', 'label_en': 'High-density acoustic reinforcement'},
            ]
        }
    ],

    # -------------------------------------------------------------------------
    # ÉTAPE 4 — ÉQUIPEMENTS DE CONFORT & OPTIONS
    # -------------------------------------------------------------------------
    'options_interieures': [
        {
            'category_fr': 'Cuisine & Coin Repas',
            'category_en': 'Kitchen & Dining Area',
            'items': [
                {'code': 'OPT_KITCHEN_COMPACT', 'label_fr': 'Kitchenette compacte (Plaques 2 feux, frigo top, évier)', 'label_en': 'Compact kitchenette (2 burners, top fridge, sink)'},
                {'code': 'OPT_KITCHEN_FULL', 'label_fr': 'Cuisine équipée complète (Four, lave-vaisselle encastré, hotte)', 'label_en': 'Full equipped kitchen (Oven, built-in dishwasher, hood)'},
                {'code': 'OPT_KITCHEN_ISLAND', 'label_fr': 'Ilot central de repas / Plan de travail sur-mesure', 'label_en': 'Central dining island / Custom worktop'},
                {'code': 'OPT_KITCHEN_NONE', 'label_fr': 'Attentes fluides seules (Cuisine non fournie)', 'label_en': 'Utility connections only (Kitchen not supplied)'},
            ]
        },
        {
            'category_fr': 'Salle d\'eau & Sanitaires',
            'category_en': 'Bathroom & Toilets',
            'items': [
                {'code': 'OPT_BATH_STD', 'label_fr': 'Salle d\'eau clé en main (Douche italienne/vitrée, vasque, meuble)', 'label_en': 'Turnkey bathroom (Walk-in/glass shower, sink, cabinet)'},
                {'code': 'OPT_BATH_LUXE', 'label_fr': 'Pack Salle d\'eau Premium (Robinetterie encastrée, miroir LED chauffant)', 'label_en': 'Premium bathroom pack (Built-in taps, heated LED mirror)'},
                {'code': 'OPT_WC_SUSPENDU', 'label_fr': 'WC suspendu traditionnel (Raccordé au réseau)', 'label_en': 'Traditional wall-hung toilet (Connected to mains)'},
                {'code': 'OPT_WC_INCINERATEUR', 'label_fr': 'Toilettes à incinération ou sèches haut de gamme (Autonome)', 'label_en': 'Incinerating or high-end dry toilets (Off-grid)'},
            ]
        },
        {
            'category_fr': 'Chauffage, Ventillat & Climatisation',
            'category_en': 'Heating, Ventilation & Air Conditioning',
            'items': [
                {'code': 'OPT_PAC_AIR_AIR', 'label_fr': 'Climatisation réversible Pompe à Chaleur (Chaud/Froid)', 'label_en': 'Reversible Heat Pump air conditioning (Heating/Cooling)'},
                {'code': 'OPT_PLANCHER_CHAUFFANT', 'label_fr': 'Plancher chauffant électrique très basse consommation', 'label_en': 'Very low consumption electric underfloor heating'},
                {'code': 'OPT_VMC_DF', 'label_fr': 'VMC Double Flux (Qualité de l\'air & économies d\'énergie)', 'label_en': 'Dual-flow MVHR (Air quality & energy savings)'},
                {'code': 'OPT_POELE_BOIS', 'label_fr': 'Attente conduit de cheminée / Poêle à granulés compact', 'label_en': 'Chimney flue connection / Compact pellet stove'},
            ]
        },
        {
            'category_fr': 'Aménagement, Mobilier & Domotique',
            'category_en': 'Layout, Furniture & Home Automation',
            'items': [
                {'code': 'OPT_MEUBLE_ESCAMOTABLE', 'label_fr': 'Lit escamotable au plafond / armoire lit gain de place', 'label_en': 'Ceiling-mounted foldaway bed / space-saving wall bed'},
                {'code': 'OPT_MEZZANINE', 'label_fr': 'Mezzanine de couchage ou de rangement avec échelle/escalier', 'label_en': 'Sleeping or storage mezzanine with ladder/staircase'},
                {'code': 'OPT_DOMOTIQUE_PACK', 'label_fr': 'Pack Domotique (Gestion chauffage à distance, serrure connectée)', 'label_en': 'Smart Home Pack (Remote heating control, smart lock)'},
                {'code': 'OPT_STORE_MOT', 'label_fr': 'Stores / Occultants motorisés intégrés', 'label_en': 'Integrated motorised blinds / blackout shades'},
            ]
        },
        {
            'category_fr': 'Autonomie & Énergie Extérieure',
            'category_en': 'Autonomy & Outdoor Energy',
            'items': [
                {'code': 'OPT_SOLAR_PACK', 'label_fr': 'Kit Panneaux photovoltaïques en toiture + Onduleur', 'label_en': 'Rooftop solar panel kit + Inverter'},
                {'code': 'OPT_BATTERY', 'label_fr': 'Batterie de stockage d\'énergie (Pour autonomie complète)', 'label_en': 'Energy storage battery (For full off-grid autonomy)'},
                {'code': 'OPT_WATER_HARVEST', 'label_fr': 'Système de récupération & filtration d\'eau de pluie', 'label_en': 'Rainwater harvesting & filtration system'},
                {'code': 'OPT_TERRASSE_BOIS', 'label_fr': 'Terrasse extérieure sur-mesure (Bois composite / Pin autoclave)', 'label_en': 'Custom outdoor deck (Composite wood / Pressure-treated pine)'},
            ]
        }
    ],

    # -------------------------------------------------------------------------
    # ÉTAPE 5 — FAISABILITÉ LOGISTIQUE & TERRAIN
    # -------------------------------------------------------------------------
    'terrain_specs': [
        {
            'id': 'acces_camion',
            'label_fr': 'Accessibilité du terrain pour livraison',
            'label_en': 'Site accessibility for delivery',
            'options': [
                {'value': 'facile', 'label_fr': 'Accès poids lourd direct (< 10m du site)', 'label_en': 'Direct truck access (< 10m from site)'},
                {'value': 'moyen', 'label_fr': 'Accès restreint / Grutage nécessaire (10-30m)', 'label_en': 'Restricted access / Crane needed (10-30m)'},
                {'value': 'difficile', 'label_fr': 'Accès très difficile / Grande grue ou transport héliporté (> 30m)', 'label_en': 'Very difficult access / Heavy crane or helicopter (> 30m)'},
            ]
        },
        {
            'id': 'fondations',
            'label_fr': 'Type de fondation envisagé',
            'label_en': 'Planned foundation type',
            'options': [
                {'value': 'vis', 'label_fr': 'Pieux vissés (recommandé / réversible & écologique)', 'label_en': 'Screw piles (recommended / reversible & eco-friendly)'},
                {'value': 'plots', 'label_fr': 'Plots en béton', 'label_en': 'Concrete pads'},
                {'value': 'dalle', 'label_fr': 'Dalle béton existante ou à couler', 'label_en': 'Existing or to-be-poured concrete slab'},
                {'value': 'a_definir', 'label_fr': 'À définir après étude de sol avec vos techniciens', 'label_en': 'To be defined after soil study with your technicians'},
            ]
        },
        {
            'id': 'raccordements',
            'label_fr': 'Raccordements aux réseaux',
            'label_en': 'Network connections',
            'options': [
                {'value': 'reseau_existant', 'label_fr': 'Terrain déjà viabilisé (Eau, Électricité, Tout-à-l\'égout à proximité)', 'label_en': 'Serviced plot (Water, Electricity, Mains drainage nearby)'},
                {'value': 'partiel', 'label_fr': 'Viabilisation partielle (Électricité seule / Fosse septique nécessaire)', 'label_en': 'Partial servicing (Electricity only / Septic tank needed)'},
                {'value': '100_autonome', 'label_fr': 'Projet 100% Autonome (Hors-réseau / Off-grid)', 'label_en': '100% Autonomous project (Off-grid)'},
            ]
        }
    ],

    # -------------------------------------------------------------------------
    # ÉTAPE 6 — SEGMENTATION USAGES ET CADRE RÉGLEMENTAIRE
    # -------------------------------------------------------------------------
    'usages_projet': [
        {'value': 'principal', 'label_fr': 'Résidence principale / Extension de maison', 'label_en': 'Main residence / House extension'},
        {'value': 'studio_jardin', 'label_fr': 'Studio de jardin / Chambre d\'amis', 'label_en': 'Garden studio / Guest room'},
        {'value': 'pro', 'label_fr': 'Bureau / Cabinet / Espace professionnel', 'label_en': 'Office / Consulting room / Professional space'},
        {'value': 'tourisme', 'label_fr': 'Projet touristique / Airbnb (1 à 3 unités)', 'label_en': 'Tourism project / Airbnb (1 to 3 units)'},
        {'value': 'parc_touristique', 'label_fr': 'Domaine / Camping / Hôtellerie de plein air (> 3 unités)', 'label_en': 'Resort / Campsite / Outdoor hotel (> 3 units)'},
    ],
    
    'cadre_urbanisme': [
        {'value': 'dp', 'label_fr': 'Déclaration Préalable de travaux (< 20 m² ou < 40 m² en zone U)', 'label_en': 'Prior declaration (< 20 sqm)'},
        {'value': 'pc', 'label_fr': 'Permis de Construire nécessaire (> 20 m² / > 40 m²)', 'label_en': 'Building Permit required'},
        {'value': 'mobile', 'label_fr': 'Usage temporaire / Mobile sans fondation lourde', 'label_en': 'Temporary / Mobile use without heavy foundations'},
        {'value': 'a_verifier', 'label_fr': 'Besoin d\'accompagnement sur les démarches administratives', 'label_en': 'Need assistance with administrative procedures'},
    ]
}

# -----------------------------------------------------------------------------
# ARGUMENTAIRES D'USAGE (`USAGES_DATA`)
# -----------------------------------------------------------------------------
# SOURCE : Contenu éditorial pour la section "Cas d'usage" de la page d'accueil / nos-gammes
USAGES_DATA = [
    {
        'slug': 'logement',
        'icon': 'fa-home',
        'name_fr': 'Logement',
        'name_en': 'Housing',
        'bullets_fr': [
            "Installation plus rapide qu'une construction traditionnelle",
            'Autonome sur un petit terrain',
            'Alternative à un achat immobilier classique',
        ],
        'bullets_en': [
            'Faster to install than traditional construction',
            'Self-contained on a small plot',
            'An alternative to a traditional home purchase',
        ],
    },
    {
        'slug': 'bureau',
        'icon': 'fa-briefcase',
        'name_fr': 'Bureau',
        'name_en': 'Office',
        'bullets_fr': [
            'Espace de travail séparé du logement',
            'Installation indépendante sur votre terrain',
            'Calme et intimité pour se concentrer',
        ],
        'bullets_en': [
            'Work space separate from the home',
            'Standalone installation on your plot',
            'Quiet and private for focused work',
        ],
    },
    {
        'slug': 'residence-secondaire',
        'icon': 'fa-sun-o',
        'name_fr': 'Résidence secondaire',
        'name_en': 'Second home',
        'bullets_fr': [
            'Installation rapide sur un terrain existant',
            'Entretien réduit par rapport à une maison classique',
            "Utilisable selon l'équipement choisi",
        ],
        'bullets_en': [
            'Quick installation on an existing plot',
            'Less upkeep than a traditional house',
            'Usable depending on the equipment chosen',
        ],
    },
    {
        'slug': 'location-airbnb',
        'icon': 'fa-key',
        'name_fr': 'Location & Airbnb',
        'name_en': 'Rental & Airbnb',
        'bullets_fr': [
            'Structure autonome et indépendante',
            'Adaptée à la location courte durée',
            'Installation flexible selon le terrain',
        ],
        'bullets_en': [
            'Self-contained, standalone structure',
            'Suited to short-term rental',
            'Flexible installation depending on the plot',
        ],
    },
    {
        'slug': 'accessoires',
        'icon': 'fa-wrench',
        'name_fr': 'Accessoires',
        'name_en': 'Accessories',
        'bullets_fr': [
            'Personnalisez votre pod selon vos besoins',
            'Ajout possible à la commande',
            'Compatible avec toutes les gammes',
        ],
        'bullets_en': [
            'Customise your pod to your needs',
            'Can be added to your order',
            'Compatible with every range',
        ],
    },
]