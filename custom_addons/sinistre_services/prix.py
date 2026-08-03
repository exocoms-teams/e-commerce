# -*- coding: utf-8 -*-
"""
Grilles tarifaires fixes par métier — Sinistre Services.

Source des tarifs : file.md (prix fixes pour + de 400 interventions).
Chaque métier expose :
  - slug   : identifiant d'URL (/prix/<slug>)
  - name   : libellé du métier
  - icon   : icône Font Awesome
  - desc   : courte description
  - prices : liste de tuples (prestation, prix)
"""

PRIX_METIERS = {
    'serrurerie': {
        'slug': 'serrurerie',
        'name': 'Serrurerie',
        'icon': 'fa-lock',
        'desc': (
            "Ouverture de porte, remplacement de cylindre ou de serrure, "
            "sécurisation après effraction. Intervention sans destruction "
            "dans la majorité des cas."
        ),
        'prices': [
            ('Ouverture porte simple claquée', '110 € - 135 €'),
            ('Clé cassée dans la serrure', 'À partir de 120 €'),
            ('Dégrippage de serrure', '100 € - 180 €'),
            ('Installation cylindre simple européen', '110 € - 150 €'),
            ('Installation serrure blindée 3 points', '390 € - sur devis'),
        ],
    },
    'plomberie': {
        'slug': 'plomberie',
        'name': 'Plomberie',
        'icon': 'fa-tint',
        'desc': (
            "Fuite d'eau, dégât des eaux, canalisation bouchée. Plombiers "
            "disponibles 24h/24 pour limiter les dommages et sécuriser le logement."
        ),
        'prices': [
            ('Débouchage de canalisation', '290 € - 390 €'),
            ('Fuite d\'eau', '149 € - 199 €'),
            ('Débouchage de WC', '130 € - 200 €'),
            ('Réparation chasse d\'eau', '150 € - 250 €'),
            ('Recherche de fuite', '120 € - 380 €'),
        ],
    },
    'chauffage': {
        'slug': 'chauffage',
        'name': 'Chauffage',
        'icon': 'fa-fire',
        'desc': (
            "Dépannage et entretien de chaudière gaz ou fioul, réparation "
            "du chauffage et du ballon d'eau chaude. Rétablissement rapide."
        ),
        'prices': [
            ('Réparation de chaudière', '150 € - 350 €'),
            ('Réparation du chauffage', '200 € - 300 €'),
            ('Entretien de chaudière', '90 € - 250 €'),
            ('Fuite de chaudière', '149 € - 200 €'),
            ('Réparation ballon d\'eau chaude', '150 € - 350 €'),
        ],
    },
    'electricite': {
        'slug': 'electricite',
        'name': 'Électricité',
        'icon': 'fa-bolt',
        'desc': (
            "Recherche de panne, réparation de tableau et de prises, mise aux "
            "normes. Électriciens Qualifelec certifiés, intervention sécurisée."
        ),
        'prices': [
            ('Recherche de panne électrique', '110 € - 135 € TTC'),
            ('Réparation tableau électrique', '150 € - 250 € TTC'),
            ('Réparation de prises électriques', '110 € - 150 € TTC'),
            ('Mise aux normes', 'Devis sur-mesure'),
            ('Réparation d\'un radiateur électrique', '200 € - 250 € TTC'),
        ],
    },
    'assainissement': {
        'slug': 'assainissement',
        'name': 'Assainissement',
        'icon': 'fa-recycle',
        'desc': (
            "Vidange de fosse septique, pompage de bac à graisse, entretien de "
            "canalisation avec matériel haute pression et camion aspirateur."
        ),
        'prices': [
            ('Vidange de fosse septique', '250 € - 500 € TTC'),
            ('Entretien canalisation', '250 € - 400 € TTC'),
            ('Pompage bac à graisse', '250 € - 500 € TTC'),
            ('Installation micro-station', 'Devis sur-mesure (dès 250 € TTC)'),
            ('Mise aux normes fosse septique', 'Devis sur-mesure (dès 250 € TTC)'),
        ],
    },
    'vitrerie': {
        'slug': 'vitrerie',
        'name': 'Vitrerie Miroiterie',
        'icon': 'fa-th-large',
        'desc': (
            "Changement de vitre ou de double vitrage, réparation de fenêtre, "
            "vitrines commerciales. Bâche provisoire posée dans l'heure."
        ),
        'prices': [
            ('Changement de vitre cassée (double vitrage)', '250 € - 500 € TTC'),
            ('Installation d\'une crémone de fenêtre', '150 € - 250 € TTC'),
            ('Réparation de fenêtre', '120 € - 210 €'),
            ('Changement de vitrine de magasin', 'Devis sur-mesure (dès 2 900 € TTC)'),
            ('Installation d\'une fenêtre en bois', '650 € - 1 000 € TTC'),
        ],
    },
    'nuisibles': {
        'slug': 'nuisibles',
        'name': 'Traitement des nuisibles',
        'icon': 'fa-bug',
        'desc': (
            "Dératisation, désinsectisation punaises de lit, blattes, cafards "
            "et guêpes. Traitement professionnel conforme aux normes sanitaires."
        ),
        'prices': [
            ('Désinsectisation punaises de lit', '200 € - 400 €'),
            ('Dératisation (souris, rats)', '200 € - 600 € TTC'),
            ('Désinsectisation de blattes', '200 € - 600 € TTC'),
            ('Désinsectisation de cafards', '200 € - 600 € TTC'),
            ('Désinsectisation de guêpes', '200 € - 600 € TTC'),
        ],
    },
    'travaux': {
        'slug': 'travaux',
        'name': 'Travaux et bricolage',
        'icon': 'fa-wrench',
        'desc': (
            "Peinture, pose de carrelage et de sols, démontage et petits travaux "
            "de bricolage par des artisans polyvalents."
        ),
        'prices': [
            ('Démontage d\'un lit', '50 € - 300 € TTC'),
            ('Peinture de plafond (peinture classique)', '20 € - 30 € TTC / m²'),
            ('Pose de carrelage', '30 € - 50 € TTC / m²'),
            ('Pose de sol stratifié', '30 € - 50 € / m²'),
            ('Pose de parquet flottant', '30 € - 60 € / m²'),
        ],
    },
}
