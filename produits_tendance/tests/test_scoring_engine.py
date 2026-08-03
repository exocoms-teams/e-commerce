#!/usr/bin/env python3
"""
Script de test pour vérifier l'implémentation de ScoringEngine
conforme à l'objectif 2 : Logique prédictive
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'produits_tendance', 'services'))

from scoring_engine import ScoringEngine
import math

def test_known_values():
    """Test avec des valeurs connues pour vérifier la précision"""
    print("=== Test avec valeurs connues ===")
    engine = ScoringEngine()

    # Exemple provenant vraisemblablement des spécifications
    current_metrics = {'ventes': 100, 'likes': 50, 'partages': 20, 'ads': 5}
    previous_metrics = {'ventes': 80, 'likes': 40, 'partages': 10, 'ads': 3}
    source_score = 0.8

    # Calcul manuel selon la formule spécifiée:
    # Vol_T = 1.0*100 + 0.1*50 + 0.3*20 + 0.5*5 = 100 + 5 + 6 + 2.5 = 113.5
    # Vol_T_prev = 1.0*80 + 0.1*40 + 0.3*10 + 0.5*3 = 80 + 4 + 3 + 1.5 = 88.5
    # Growth_T = (113.5 - 88.5) / (88.5 + 1.0) = 25.0 / 89.5 = 0.279329...
    # score_final = 0.279329 * ln(1 + 113.5) * (1 + 0.2 * 0.8)
    #           = 0.279329 * ln(114.5) * (1 + 0.16)
    #           = 0.279329 * 4.7405 * 1.16
    #           = 1.534... (à vérifier)

    vol_t = 1.0*100 + 0.1*50 + 0.3*20 + 0.5*5
    vol_t_prev = 1.0*80 + 0.1*40 + 0.3*10 + 0.5*3
    growth = (vol_t - vol_t_prev) / (vol_t_prev + 1.0)
    expected = growth * math.log(1 + vol_t) * (1 + 0.2 * 0.8)

    print(f"Vol_T = {vol_t}")
    print(f"Vol_T_prev = {vol_t_prev}")
    print(f"Growth_T = {growth}")
    print(f"Résultat attendu = {expected}")

    actual = engine.calculate_trend_score(current_metrics, previous_metrics, source_score)
    print(f"Résultat obtenu = {actual}")
    print(f"Différence = {abs(actual - expected)}")
    print(f"Test passé (tolérance 0.0001) : {abs(actual - expected) < 0.0001}")
    print()

def test_zero_growth():
    """Test du cas où growth <= 0 doit retourner 0.0 immédiatement"""
    print("=== Test cas croissance nulle ou négative ===")
    engine = ScoringEngine()

    # Cas où Vol_T <= Vol_T_prev (growth <= 0)
    current_metrics = {'ventes': 50, 'likes': 20, 'partages': 10, 'ads': 2}
    previous_metrics = {'ventes': 80, 'likes': 30, 'partages': 15, 'ads': 5}  # Plus élevé
    source_score = 0.5

    result = engine.calculate_trend_score(current_metrics, previous_metrics, source_score)
    print(f"Cas décroissance : résultat = {result} (devrait être 0.0)")
    print(f"Test passé : {result == 0.0}")
    print()

    # Cas où les deux sont zéro
    current_metrics = {'ventes': 0, 'likes': 0, 'partages': 0, 'ads': 0}
    previous_metrics = {'ventes': 0, 'likes': 0, 'partages': 0, 'ads': 0}
    source_score = 0.5

    result = engine.calculate_trend_score(current_metrics, previous_metrics, source_score)
    print(f"Cas zéro zéro : résultat = {result} (devrait être 0.0)")
    print(f"Test passé : {result == 0.0}")
    print()

def test_previous_metrics_zero():
    """Test du cas spécial où previous_metrics sont tous à zéro (vol_t_prev=0)"""
    print("=== Test previous_metrics à zéro ===")
    engine = ScoringEngine()

    # Quand previous_metrics = tout zéro, Vol_T_prev = 0
    # Growth_T = (Vol_T - 0) / (0 + 1.0) = Vol_T / 1.0 = Vol_T
    # Donc growth devrait être positif si Vol_T > 0
    current_metrics = {'ventes': 30, 'likes': 10, 'partages': 5, 'ads': 2}
    previous_metrics = {'ventes': 0, 'likes': 0, 'partages': 0, 'ads': 0}  # Tout à zéro
    source_score = 0.6

    # Calcul manuel
    vol_t = 1.0*30 + 0.1*10 + 0.3*5 + 0.5*2  # = 30 + 1 + 1.5 + 1 = 33.5
    vol_t_prev = 0  # Parce que tout est zéro
    growth = (vol_t - vol_t_prev) / (vol_t_prev + 1.0)  # = 33.5 / 1.0 = 33.5
    expected = growth * math.log(1 + vol_t) * (1 + 0.2 * 0.6)

    print(f"Vol_T = {vol_t}")
    print(f"Vol_T_prev = {vol_t_prev}")
    print(f"Growth_T = {growth}")
    print(f"Résultat attendu = {expected}")

    result = engine.calculate_trend_score(current_metrics, previous_metrics, source_score)
    print(f"Résultat obtenu = {result}")
    print(f"Différence = {abs(result - expected)}")
    print(f"Test passé (pas de division par zéro) : {abs(result - expected) < 0.0001}")
    print()

def test_no_odoo_dependencies():
    """Vérifier qu'il n'y a pas de dépendances Odoo"""
    print("=== Vérification de l'indépendance d'Odoo ===")
    import inspect
    source = inspect.getsource(ScoringEngine)
    # Chercher des imports Odoo spécifiques, pas juste '_'
    odoo_indicators = ['import odoo', 'from odoo', 'odoo.models', 'odoo.fields', 'odoo.api']
    found = [imp for imp in odoo_indicators if imp in source.lower()]
    print(f"Indicteurs Odoo trouvés dans le source : {found}")
    print(f"Test passé (aucune dépendance Odoo) : {len(found) == 0}")
    print()

def test_constants_match_spec():
    """Vérifier que les constantes correspondent à la spécification"""
    print("=== Vérification des constantes ===")
    from scoring_engine import W_VENTES, W_LIKES, W_PARTAGES, W_ADS, ALPHA, EPSILON

    # Constantes attendues selon le ticket ScoringEngine/Objectif 1
    expected = {
        'W_VENTES': 1.0,   # w_v
        'W_LIKES': 0.1,    # w_l
        'W_PARTAGES': 0.3, # w_p
        'W_ADS': 0.5,      # w_a
        'ALPHA': 0.2,      # alpha
        'EPSILON': 1.0     # epsilon
    }

    actual = {
        'W_VENTES': W_VENTES,
        'W_LIKES': W_LIKES,
        'W_PARTAGES': W_PARTAGES,
        'W_ADS': W_ADS,
        'ALPHA': ALPHA,
        'EPSILON': EPSILON
    }

    print("Constantes attendues :", expected)
    print("Constantes réelles   :", actual)

    all_match = True
    for key in expected:
        if expected[key] != actual[key]:
            print(f"  ERREUR : {key} attendu {expected[key]}, obtenu {actual[key]}")
            all_match = False
        else:
            print(f"  OK : {key} = {actual[key]}")

    print(f"Test passed : {all_match}")
    print()
    return all_match

def test_return_type_and_precision():
    """Vérifier le type de retour et la précision"""
    print("=== Vérification du type de retour et précision ===")
    engine = ScoringEngine()

    current_metrics = {'ventes': 100, 'likes': 50, 'partages': 20, 'ads': 5}
    previous_metrics = {'ventes': 90, 'likes': 40, 'partages': 15, 'ads': 3}
    source_score = 0.5

    result = engine.calculate_trend_score(current_metrics, previous_metrics, source_score)

    print(f"Type de retour : {type(result)}")
    print(f"Valeur de retour : {result}")
    print(f"Est un float : {isinstance(result, float)}")

    # Vérifier que c'est bien arrondi à 4 décimales
    multiplied = result * 10000
    is_integer = abs(multiplied - round(multiplied)) < 1e-10
    print(f"Arrondi à 4 décimales : {is_integer}")
    print()

if __name__ == "__main__":
    print("Tests de validation pour l'objectif 2 : Logique prédictive")
    print("=" * 60)

    try:
        test_constants_match_spec()
        test_known_values()
        test_zero_growth()
        test_previous_metrics_zero()
        test_no_odoo_dependencies()
        test_return_type_and_precision()

        print("=" * 60)
        print("Tous les tests terminés!")
    except Exception as e:
        print(f"Erreur lors des tests : {e}")
        import traceback
        traceback.print_exc()