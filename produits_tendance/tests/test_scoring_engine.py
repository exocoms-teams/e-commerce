from odoo.tests.common import BaseCase
from odoo.addons.produits_tendance.services.scoring_engine import ScoringEngine
import math

class TestScoringEngine(BaseCase):
    
    def setUp(self):
        super().setUp()
        self.engine = ScoringEngine()

    def test_known_values(self):
        """Test avec des valeurs connues pour vérifier la précision"""
        current_metrics = {'ventes': 100, 'likes': 50, 'partages': 20, 'ads': 5}
        previous_metrics = {'ventes': 80, 'likes': 40, 'partages': 10, 'ads': 3}
        source_score = 0.8

        vol_t = 1.0*100 + 0.1*50 + 0.3*20 + 0.5*5
        vol_t_prev = 1.0*80 + 0.1*40 + 0.3*10 + 0.5*3
        growth = (vol_t - vol_t_prev) / (vol_t_prev + 1.0)
        expected = growth * math.log(1 + vol_t) * (1 + 0.2 * 0.8)

        actual = self.engine.calculate_trend_score(current_metrics, previous_metrics, source_score)
        
        # Utilisation de assertAlmostEqual pour les floats avec une tolérance de 4 décimales
        self.assertAlmostEqual(actual, expected, places=4, msg="Le calcul du score de tendance est incorrect")

    def test_zero_growth(self):
        """Test du cas où growth <= 0 doit retourner 0.0 immédiatement"""
        # Cas où Vol_T <= Vol_T_prev (growth <= 0)
        current_metrics = {'ventes': 50, 'likes': 20, 'partages': 10, 'ads': 2}
        previous_metrics = {'ventes': 80, 'likes': 30, 'partages': 15, 'ads': 5}
        source_score = 0.5

        result = self.engine.calculate_trend_score(current_metrics, previous_metrics, source_score)
        self.assertEqual(result, 0.0)

        # Cas où les deux sont zéro
        current_metrics = {'ventes': 0, 'likes': 0, 'partages': 0, 'ads': 0}
        previous_metrics = {'ventes': 0, 'likes': 0, 'partages': 0, 'ads': 0}
        result = self.engine.calculate_trend_score(current_metrics, previous_metrics, source_score)
        self.assertEqual(result, 0.0)

    def test_previous_metrics_zero(self):
        """Test du cas spécial où previous_metrics sont tous à zéro (vol_t_prev=0)"""
        current_metrics = {'ventes': 30, 'likes': 10, 'partages': 5, 'ads': 2}
        previous_metrics = {'ventes': 0, 'likes': 0, 'partages': 0, 'ads': 0}
        source_score = 0.6

        vol_t = 1.0*30 + 0.1*10 + 0.3*5 + 0.5*2 
        vol_t_prev = 0
        growth = (vol_t - vol_t_prev) / (vol_t_prev + 1.0) 
        expected = growth * math.log(1 + vol_t) * (1 + 0.2 * 0.6)

        result = self.engine.calculate_trend_score(current_metrics, previous_metrics, source_score)
        self.assertAlmostEqual(result, expected, places=4)

    def test_return_type(self):
        """Vérifier le type de retour"""
        current_metrics = {'ventes': 100, 'likes': 50, 'partages': 20, 'ads': 5}
        previous_metrics = {'ventes': 90, 'likes': 40, 'partages': 15, 'ads': 3}
        
        result = self.engine.calculate_trend_score(current_metrics, previous_metrics, 0.5)
        self.assertIsInstance(result, float)