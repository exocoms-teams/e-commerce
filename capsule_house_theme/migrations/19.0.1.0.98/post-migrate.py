# -*- coding: utf-8 -*-
"""
Rejoue run_theme_maintenance() après une mise à jour du module vers la
version 19.0.1.0.98.

CORRECTIF DE CONTENU (pas structurel) sur les cartes "Nos gammes" de
l'accueil, suite à un retour client avec capture d'écran : 3 des 5
cartes (Cabine, Modulaire, Pliable) affichaient encore le badge
"À confirmer" / "To be confirmed" et une tagline générique ("Formats à
définir"). Ce texte avait été écrit en dur en 19.0.1.0.87 et jamais mis
à jour depuis.

Or GAMMES_DATA (data_definition/__init__.py), qui pilote les vraies
pages détail /nos-gammes/<slug>, marque les 5 gammes en
'status': GAMME_STATUS_DISPONIBLE, avec un tagline_fr/tagline_en
complet pour chacune — les pages détail sont prêtes depuis longtemps,
seules les cartes statiques de l'accueil étaient en retard sur cette
donnée.

Fix : les 3 cartes concernées (FR et EN) reprennent maintenant le badge
"Détails disponibles" / "Details available" et le tagline exact de
GAMMES_DATA :
- Cabine : "3 tailles disponibles · 10 à 25 m²" / "3 sizes available ·
  10 to 25 sqm"
- Modulaire : "Système extensible · modules combinables à volonté" /
  "Extensible system · modules combinable as needed"
- Pliable : "3 tailles disponibles · 14 à 38 m²" / "3 sizes available ·
  14 to 38 sqm"

Fichier modifié : views/partials/home_gammes.xml. Aucun changement
structurel (la correction de sélection des blocs de 19.0.1.0.97 reste
inchangée).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo.addons.capsule_house_theme import run_theme_maintenance

    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "capsule_house_theme: post-migrate 19.0.1.0.98 — cartes "
        "Cabine/Modulaire/Pliable de l'accueil passées de 'À confirmer' "
        "à 'Détails disponibles', avec le vrai tagline de GAMMES_DATA "
        "(les pages détail étaient déjà prêtes, seules les cartes "
        "statiques de l'accueil étaient en retard sur cette donnée)."
    )
    run_theme_maintenance(env)
