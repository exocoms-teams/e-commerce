import math

# Constants for volume calculation (W_VENTES, W_LIKES, W_PARTAGES, W_ADS)
# Alpha for source score bonus, Epsilon for division by zero smoothing
W_VENTES = 1.0
W_LIKES = 0.1
W_PARTAGES = 0.3
W_ADS = 0.5
ALPHA = 0.2
EPSILON = 1.0


class ScoringEngine:
    def calculate_trend_score(self, current_metrics: dict, previous_metrics: dict, source_score: float = 0.0) -> float:
        """
        Calcule le score de tendance final.

        Args:
            current_metrics (dict): {'ventes', 'likes', 'partages', 'ads'} pour la période T.
            previous_metrics (dict): mêmes clés pour la période précédente T_prev (doit être fourni, pas None).
            source_score (float): fiabilité de la source, normalisée entre 0.0 et 1.0 (valeur par défaut 0.0).

        Returns:
            float: score arrondi à 4 décimales, ou 0.0 si Growth_T <= 0.
        """
        # Sécurité interne : utilisation de .get avec valeur par défaut 0 pour gérer les dictionnaires vides ou clés manquantes
        vol_t = (
            W_VENTES * current_metrics.get('ventes', 0)
            + W_LIKES * current_metrics.get('likes', 0)
            + W_PARTAGES * current_metrics.get('partages', 0)
            + W_ADS * current_metrics.get('ads', 0)
        )
        vol_t_prev = (
            W_VENTES * previous_metrics.get('ventes', 0)
            + W_LIKES * previous_metrics.get('likes', 0)
            + W_PARTAGES * previous_metrics.get('partages', 0)
            + W_ADS * previous_metrics.get('ads', 0)
        )

        # Calcul de la croissance avec lissage anti division par zéro
        growth = (vol_t - vol_t_prev) / (vol_t_prev + EPSILON)

        # Filtrage : croissance nulle ou négative -> produit non "tendance"
        if growth <= 0:
            return 0.0

        # Facteur volume et bonus source (avec normalisation de sécurité du source_score)
        volume_factor = math.log(1 + vol_t)
        source_score = max(0.0, min(source_score, 1.0))  # Normalisation entre 0 et 1 pour éviter les valeurs aberrantes

        final_score = growth * volume_factor * (1 + ALPHA * source_score)

        return round(final_score, 4)