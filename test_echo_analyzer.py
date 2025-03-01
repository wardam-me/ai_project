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
    raise

class TestEchoDataAnalyzer(unittest.TestCase):
    """Tests unitaires pour l'analyseur de données d'écho"""

    def setUp(self):
        """Initialise l'environnement de test"""
        self.analyzer = EchoDataAnalyzer()
        self.test_filename = "test_echo_unittest.json"

        # Générer des données de test
        self.assertTrue(self.analyzer.generate_test_data(self.test_filename, entries=10, with_anomalies=True))

    def tearDown(self):
        """Nettoie l'environnement après les tests"""
        # Supprimer le fichier de test s'il existe
        test_path = os.path.join(self.analyzer.data_dir, self.test_filename)
        if os.path.exists(test_path):
            os.remove(test_path)

    def test_load_echo_data(self):
        """Teste le chargement des données d'écho"""
        data = self.analyzer.load_echo_data(self.test_filename)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 10)

    def test_analyze_round_trip_times(self):
        """Teste l'analyse des temps d'aller-retour"""
        data = self.analyzer.load_echo_data(self.test_filename)
        results = self.analyzer.analyze_round_trip_times(data)

        self.assertIn("avg_rtt_ms", results)
        self.assertIn("min_rtt_ms", results)
        self.assertIn("max_rtt_ms", results)

    def test_analyze_packet_loss(self):
        """Teste l'analyse des pertes de paquets"""
        data = self.analyzer.load_echo_data(self.test_filename)
        results = self.analyzer.analyze_packet_loss(data)

        self.assertIn("packets_sent", results)
        self.assertIn("packets_received", results)
        self.assertIn("loss_rate_percentage", results)

    def test_perform_full_analysis(self):
        """Teste l'analyse complète"""
        results = self.analyzer.perform_full_analysis(self.test_filename)

        self.assertIn("network_health", results)
        self.assertIn("score", results["network_health"])
        self.assertIn("level", results["network_health"])
        self.assertIn("analyses", results)
        self.assertIn("recommendations", results)

        # Vérifier que le fichier de résultat a bien été créé
        self.assertIsNotNone(self.analyzer.last_analysis)
        result_path = os.path.join(self.analyzer.results_dir, self.analyzer.last_analysis)
        self.assertTrue(os.path.exists(result_path))

if __name__ == "__main__":
    # Créer les répertoires nécessaires
    os.makedirs("instance/echo_data", exist_ok=True)
    os.makedirs("instance/echo_reports", exist_ok=True)

    # Exécuter les tests
    unittest.main()