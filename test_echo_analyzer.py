
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le module d'analyse de données écho
"""
import os
import logging
import json
import unittest
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from echo_data_analyzer import EchoDataAnalyzer
    logger.info("Module d'analyse d'écho importé avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation du module echo_data_analyzer: {e}")
    exit(1)

class TestEchoAnalyzer(unittest.TestCase):
    """Tests pour l'analyseur de données d'écho"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.test_data_dir = "instance/test_echo_data"
        self.test_results_dir = "instance/test_echo_results"
        
        # Créer les répertoires de test s'ils n'existent pas
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.test_results_dir, exist_ok=True)
        
        # Initialiser l'analyseur avec les répertoires de test
        self.analyzer = EchoDataAnalyzer(
            data_dir=self.test_data_dir,
            results_dir=self.test_results_dir
        )
        
        # Générer des données de test
        self.test_filename = "test_echo_data.json"
        self.analyzer.generate_test_data(self.test_filename, entries=20)
        logger.info("Jeu de données de test généré")
    
    def test_01_load_data(self):
        """Test du chargement des données"""
        data = self.analyzer.load_echo_data(self.test_filename)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 20)
        logger.info("Test de chargement de données réussi")
    
    def test_02_analyze_rtt(self):
        """Test de l'analyse des temps d'aller-retour"""
        data = self.analyzer.load_echo_data(self.test_filename)
        results = self.analyzer.analyze_round_trip_times(data)
        
        self.assertIn("avg_rtt_ms", results)
        self.assertIn("min_rtt_ms", results)
        self.assertIn("max_rtt_ms", results)
        self.assertIn("anomalies_count", results)
        
        logger.info(f"RTT moyen: {results['avg_rtt_ms']} ms")
        logger.info("Test d'analyse RTT réussi")
    
    def test_03_analyze_packet_loss(self):
        """Test de l'analyse des pertes de paquets"""
        data = self.analyzer.load_echo_data(self.test_filename)
        results = self.analyzer.analyze_packet_loss(data)
        
        self.assertIn("packets_sent", results)
        self.assertIn("packets_received", results)
        self.assertIn("packets_lost", results)
        self.assertIn("loss_rate_percentage", results)
        
        logger.info(f"Taux de perte: {results['loss_rate_percentage']}%")
        logger.info("Test d'analyse de perte de paquets réussi")
    
    def test_04_analyze_hop_count(self):
        """Test de l'analyse du nombre de sauts"""
        data = self.analyzer.load_echo_data(self.test_filename)
        results = self.analyzer.analyze_hop_count(data)
        
        self.assertIn("avg_hop_count", results)
        self.assertIn("min_hop_count", results)
        self.assertIn("max_hop_count", results)
        
        logger.info(f"Nombre moyen de sauts: {results['avg_hop_count']}")
        logger.info("Test d'analyse de sauts réussi")
    
    def test_05_analyze_patterns(self):
        """Test de l'analyse des patterns"""
        data = self.analyzer.load_echo_data(self.test_filename)
        results = self.analyzer.analyze_echo_patterns(data)
        
        self.assertIn("data_points", results)
        self.assertIn("is_regular_pattern", results)
        
        logger.info(f"Pattern régulier: {results['is_regular_pattern']}")
        logger.info("Test d'analyse de patterns réussi")
    
    def test_06_full_analysis(self):
        """Test de l'analyse complète"""
        results = self.analyzer.perform_full_analysis(self.test_filename)
        
        self.assertIn("filename", results)
        self.assertIn("timestamp", results)
        self.assertIn("data_points", results)
        self.assertIn("analyses", results)
        self.assertIn("network_health", results)
        self.assertIn("recommendations", results)
        
        logger.info(f"Score de santé réseau: {results['network_health']['score']}/100")
        logger.info(f"Niveau de santé: {results['network_health']['level']}")
        logger.info("Test d'analyse complète réussi")
        
        # Vérifier la sauvegarde des résultats
        self.assertIsNotNone(self.analyzer.last_analysis)
        result_path = os.path.join(self.test_results_dir, self.analyzer.last_analysis)
        self.assertTrue(os.path.exists(result_path))
    
    def test_07_save_results(self):
        """Test de la sauvegarde des résultats"""
        test_results = {
            "test": "save_results",
            "timestamp": datetime.now().isoformat()
        }
        
        saved = self.analyzer.save_analysis_results(test_results, "test_results.json")
        self.assertTrue(saved)
        
        result_path = os.path.join(self.test_results_dir, "test_results.json")
        self.assertTrue(os.path.exists(result_path))
        
        # Charger et vérifier
        with open(result_path, 'r') as f:
            loaded = json.load(f)
        
        self.assertEqual(loaded["test"], "save_results")
        logger.info("Test de sauvegarde des résultats réussi")

def main():
    """Fonction principale pour exécuter les tests"""
    unittest.main()

if __name__ == "__main__":
    main()
