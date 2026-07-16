# -*- coding: utf-8 -*-
"""
Calcul du score de tendance produit.

Implémente la formule définie dans score.md :

    Score_T(p) = Growth_T(p) * ln(1 + Vol_T(p)) * (1 + alpha * S_src(p))

Ce module est volontairement indépendant de l'ORM Odoo : il ne manipule que
des dictionnaires de métriques et des nombres. Cela permet de le tester
unitairement sans base de données ni environnement Odoo, et de le réutiliser
depuis n'importe quel modèle (trend.product, un cron de scoring, etc.).

L'adaptation "Odoo" (lecture de sales_count, score_site_x, et agrégation des
trend.ad liés) se trouve dans trend_product.py, sous forme d'une fonction
`build_current_metrics(product)` qui construit le dict attendu ici à partir
d'un recordset trend.product.
"""

import math

# Coefficients de pondération de Vol_T (cf. score.md, section 2.1)
W_VENTES = 1.0
W_LIKES = 0.1
W_PARTAGES = 0.3
W_ADS = 0.5

ALPHA = 0.2      # plafond du bonus de fiabilité de la source (section 2.3)
EPSILON = 1.0    # lissage anti division-par-zéro (section 2.2)


def compute_volume(metrics):
    """Vol_T(p) = w_v*V_T + w_l*L_T + w_p*P_T + w_a*A_T

    Args:
        metrics (dict): clés 'ventes', 'likes', 'partages', 'ads'
            (les clés manquantes sont traitées comme 0).
    """
    return (
        W_VENTES * metrics.get('ventes', 0)
        + W_LIKES * metrics.get('likes', 0)
        + W_PARTAGES * metrics.get('partages', 0)
        + W_ADS * metrics.get('ads', 0)
    )


def calculate_trend_score(current_metrics, previous_metrics=None, source_score=0.0):
    """Calcule le score de tendance final (score.md, section 3).

    Args:
        current_metrics (dict): {'ventes', 'likes', 'partages', 'ads'} période T.
        previous_metrics (dict|None): mêmes clés pour la période précédente T_prev.
            Si None, on considère qu'aucun historique n'existe encore pour ce
            produit (Vol_T_prev = 0) : c'est le cas d'un produit nouvellement
            suivi, pour lequel toute activité constitue une "croissance".
        source_score (float): fiabilité de la source, normalisée entre 0.0 et 1.0.
            Les valeurs hors bornes sont tronquées ([0, 1]).

    Returns:
        float: score arrondi à 4 décimales, ou 0.0 si Growth_T <= 0.
    """
    if previous_metrics is None:
        previous_metrics = {'ventes': 0, 'likes': 0, 'partages': 0, 'ads': 0}

    vol_t = compute_volume(current_metrics)
    vol_t_prev = compute_volume(previous_metrics)

    growth = (vol_t - vol_t_prev) / (vol_t_prev + EPSILON)

    # Filtrage : croissance nulle ou négative -> produit non "tendance"
    if growth <= 0:
        return 0.0

    volume_factor = math.log(1 + vol_t)
    source_score = max(0.0, min(source_score, 1.0))

    final_score = growth * volume_factor * (1 + ALPHA * source_score)

    return round(final_score, 4)


def build_current_metrics(product):
    """Construit le dict de métriques courantes attendu par calculate_trend_score,
    à partir d'un produit (recordset trend.product ou tout objet "duck-typed"
    exposant les mêmes attributs : sales_count, ad_ids.mapped(...)).

    - ventes   <- product.sales_count
    - likes    <- somme des likes_count de product.ad_ids
    - partages <- somme des shares_count de product.ad_ids
    - ads      <- nombre de trend.ad liés (A_T)
    """
    return {
        'ventes': product.sales_count or 0,
        'likes': sum(product.ad_ids.mapped('likes_count')),
        'partages': sum(product.ad_ids.mapped('shares_count')),
        'ads': len(product.ad_ids),
    }


def normalize_source_score(score_site_x, scale=10.0):
    """Normalise score_site_x (échelle libre du site source, par défaut /10)
    vers [0, 1] pour servir de S_src dans la formule.

    Hypothèse à confirmer avec l'équipe : score_site_x est actuellement noté
    sur 10 par la majorité des sites sources (cf. exemple du contrat API,
    score_site_x=7.8). A ajuster si une autre échelle est utilisée.
    """
    if not score_site_x:
        return 0.0
    return max(0.0, min(score_site_x / scale, 1.0))


def compute_product_trend_score(product, previous_metrics=None):
    """Point d'entrée unique : calcule le score de tendance d'UN produit.

    Args:
        product: un recordset trend.product (un seul enregistrement) ou un
            objet équivalent exposant sales_count, score_site_x, ad_ids.
        previous_metrics (dict|None): métriques de la période précédente,
            pour calculer Growth_T. Voir la note dans calculate_trend_score
            si non fourni.

    Returns:
        float: score de tendance du produit, arrondi à 4 décimales.
    """
    current_metrics = build_current_metrics(product)
    source_score = normalize_source_score(product.score_site_x)
    return calculate_trend_score(current_metrics, previous_metrics, source_score)