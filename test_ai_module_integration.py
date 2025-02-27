#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier l'intégration du module d'IA dans NetSecure Pro
Ce script vérifie en particulier la fonctionnalité de gestion des clones IA
et la cohérence des données entre les différents modules.
"""

import json
import logging
import os
import sys
import time
import unittest
from typing import Dict, List, Any, Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Vérification des dépendances
try:
    from ai_clone_manager import AICloneManager, AIClone, get_clone_manager
    logger.info("Module ai_clone_manager importé avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation du module ai_clone_manager: {e}")
    sys.exit(1)

try:
    from module_IA import SecurityAnalysisAI
    logger.info("Module module_IA importé avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation du module module_IA: {e}")
    sys.exit(1)

class TestAIModuleIntegration(unittest.TestCase):
    """Tests d'intégration pour le module IA et la gestion des clones"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = 'test_ai_data'
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        
        # Créer un fichier de configuration de test
        self.config_path = os.path.join(self.test_dir, 'test_clones.json')
        
        # Initialiser le gestionnaire de clones avec le fichier de test
        self.clone_manager = AICloneManager(config_path=self.config_path)
        
        # Réinitialiser le fichier de configuration
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        
        logger.info("Configuration initiale terminée")

    def test_01_clone_creation(self):
        """Test de la création de clones IA"""
        logger.info("Test de création de clones...")
        
        # Créer plusieurs clones
        clone1 = self.clone_manager.create_clone(
            name="Clone Test 1",
            specialization="network",
            learning_rate=0.3,
            confidence_threshold=0.7
        )
        
        clone2 = self.clone_manager.create_clone(
            name="Clone Test 2",
            specialization="protocol",
            learning_rate=0.5,
            confidence_threshold=0.8
        )
        
        clone3 = self.clone_manager.create_clone(
            name="Clone Test 3",
            specialization="vulnerability",
            learning_rate=0.7,
            confidence_threshold=0.6
        )
        
        # Vérifier que les clones ont été créés correctement
        self.assertIsNotNone(clone1)
        self.assertIsNotNone(clone2)
        self.assertIsNotNone(clone3)
        
        # Vérifier que les attributs sont correctement définis
        self.assertEqual(clone1.name, "Clone Test 1")
        self.assertEqual(clone1.specialization, "network")
        self.assertEqual(clone1.learning_rate, 0.3)
        self.assertEqual(clone1.confidence_threshold, 0.7)
        
        # Vérifier que les clones ont été enregistrés
        clones = self.clone_manager.get_all_clones()
        self.assertEqual(len(clones), 3)
        
        logger.info(f"Clones créés: {len(clones)}")
        
        # Vérifier l'unicité des IDs
        clone_ids = [c['clone_id'] for c in clones]
        self.assertEqual(len(clone_ids), len(set(clone_ids)))
        
        # Vérifier que le fichier de configuration a été créé
        self.assertTrue(os.path.exists(self.config_path))
        
        # Vérifier le contenu du fichier de configuration
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
            self.assertEqual(len(config_data), 3)
        
        logger.info("Test de création de clones réussi")

    def test_02_clone_update(self):
        """Test de la mise à jour des clones IA"""
        logger.info("Test de mise à jour des clones...")
        
        # Créer un clone
        clone = self.clone_manager.create_clone(
            name="Clone à mettre à jour",
            specialization="general",
            learning_rate=0.5,
            confidence_threshold=0.7
        )
        
        clone_id = clone.clone_id
        
        # Mettre à jour le clone
        updated_clone = self.clone_manager.update_clone(
            clone_id=clone_id,
            updates={
                "name": "Clone mis à jour",
                "learning_rate": 0.8,
                "confidence_threshold": 0.9
            }
        )
        
        # Vérifier que le clone a été mis à jour
        self.assertIsNotNone(updated_clone)
        self.assertEqual(updated_clone.name, "Clone mis à jour")
        self.assertEqual(updated_clone.learning_rate, 0.8)
        self.assertEqual(updated_clone.confidence_threshold, 0.9)
        
        # Vérifier la persistance des mises à jour
        retrieved_clone = self.clone_manager.get_clone(clone_id)
        self.assertEqual(retrieved_clone.name, "Clone mis à jour")
        
        logger.info("Test de mise à jour des clones réussi")

    def test_03_clone_training(self):
        """Test de l'entraînement des clones IA"""
        logger.info("Test d'entraînement des clones...")
        
        # Créer un clone
        clone = self.clone_manager.create_clone(
            name="Clone d'entraînement",
            specialization="network",
            learning_rate=0.5,
            confidence_threshold=0.7
        )
        
        clone_id = clone.clone_id
        
        # Démarrer l'entraînement
        training_params = {
            "epochs": 10,
            "batch_size": 32,
            "dataset": "network_security",
            "validation_split": 0.2
        }
        
        start_result = clone.start_training(training_params)
        
        # Vérifier le démarrage de l'entraînement
        self.assertIn("status", start_result)
        self.assertEqual(start_result["status"], "training_started")
        self.assertIn("session_id", start_result)
        
        session_id = start_result["session_id"]
        
        # Simuler l'entraînement
        time.sleep(0.5)  # Attendre un peu pour simuler l'entraînement
        
        # Compléter l'entraînement
        training_results = {
            "accuracy": 0.85,
            "loss": 0.15,
            "precision": 0.87,
            "recall": 0.82,
            "f1_score": 0.84,
            "improvements": ["Meilleure détection des attaques DoS", "Réduction des faux positifs"]
        }
        
        completion_result = clone.complete_training(session_id, training_results)
        
        # Vérifier la complétion de l'entraînement
        self.assertIn("status", completion_result)
        self.assertEqual(completion_result["status"], "training_completed")
        
        # Vérifier que les métriques de performance ont été mises à jour
        updated_clone = self.clone_manager.get_clone(clone_id)
        self.assertGreater(updated_clone.performance_metrics["accuracy"], 0)
        self.assertEqual(len(updated_clone.training_sessions), 1)
        
        logger.info("Test d'entraînement des clones réussi")

    def test_04_request_processing(self):
        """Test du traitement des demandes par les clones IA"""
        logger.info("Test de traitement des demandes...")
        
        # Créer des clones spécialisés
        network_clone = self.clone_manager.create_clone(
            name="Clone Réseau",
            specialization="network",
            learning_rate=0.5,
            confidence_threshold=0.7
        )
        
        protocol_clone = self.clone_manager.create_clone(
            name="Clone Protocol",
            specialization="protocol",
            learning_rate=0.5,
            confidence_threshold=0.7
        )
        
        # Créer des demandes
        network_request = {
            "devices": [
                {"name": "Router", "ip": "192.168.1.1", "mac": "00:11:22:33:44:55"},
                {"name": "Laptop", "ip": "192.168.1.100", "mac": "AA:BB:CC:DD:EE:FF"}
            ],
            "scan_date": "2025-02-27T12:00:00",
            "scan_type": "full"
        }
        
        protocol_request = {
            "protocol": "WPA2",
            "encryption": "AES",
            "authentication": "PSK",
            "ssid": "TestNetwork",
            "bssid": "00:11:22:33:44:55"
        }
        
        # Traiter les demandes
        network_result = self.clone_manager.process_request(
            request_type="analyze_network", 
            data=network_request,
            clone_id=network_clone.clone_id
        )
        
        protocol_result = self.clone_manager.process_request(
            request_type="analyze_protocol", 
            data=protocol_request,
            clone_id=protocol_clone.clone_id
        )
        
        # Vérifier les résultats
        self.assertIn("result", network_result)
        self.assertIn("confidence", network_result)
        self.assertIn("processing_time", network_result)
        self.assertIn("clone_info", network_result)
        
        self.assertIn("result", protocol_result)
        self.assertIn("confidence", protocol_result)
        self.assertIn("processing_time", protocol_result)
        self.assertIn("clone_info", protocol_result)
        
        # Vérifier que le clone approprié a été utilisé
        self.assertEqual(network_result["clone_info"]["clone_id"], network_clone.clone_id)
        self.assertEqual(protocol_result["clone_info"]["clone_id"], protocol_clone.clone_id)
        
        # Tester le traitement automatique (sans spécifier de clone)
        auto_result = self.clone_manager.process_request(
            request_type="analyze_network", 
            data=network_request
        )
        
        self.assertIn("result", auto_result)
        self.assertIn("clone_info", auto_result)
        self.assertEqual(auto_result["clone_info"]["specialization"], "network")
        
        logger.info("Test de traitement des demandes réussi")

    def test_05_statistics_generation(self):
        """Test de la génération de statistiques"""
        logger.info("Test de génération de statistiques...")
        
        # Créer plusieurs clones de différents types
        for i in range(5):
            self.clone_manager.create_clone(
                name=f"Clone {i}",
                specialization="network" if i % 3 == 0 else "protocol" if i % 3 == 1 else "vulnerability",
                learning_rate=0.5,
                confidence_threshold=0.7
            )
        
        # Générer des statistiques
        stats = self.clone_manager.get_clone_statistics()
        
        # Vérifier la structure des statistiques
        self.assertIn("total_clones", stats)
        self.assertIn("status", stats)
        self.assertIn("specializations", stats)
        
        # Vérifier les valeurs
        self.assertEqual(stats["total_clones"], 5)
        self.assertEqual(sum(stats["status"].values()), 5)
        self.assertEqual(sum(stats["specializations"].values()), 5)
        
        logger.info("Test de génération de statistiques réussi")

    def test_06_clone_deletion(self):
        """Test de la suppression de clones"""
        logger.info("Test de suppression de clones...")
        
        # Créer un clone à supprimer
        clone = self.clone_manager.create_clone(
            name="Clone à supprimer",
            specialization="general",
            learning_rate=0.5,
            confidence_threshold=0.7
        )
        
        clone_id = clone.clone_id
        
        # Vérifier que le clone existe
        self.assertIsNotNone(self.clone_manager.get_clone(clone_id))
        
        # Supprimer le clone
        result = self.clone_manager.delete_clone(clone_id)
        
        # Vérifier que la suppression a réussi
        self.assertTrue(result)
        
        # Vérifier que le clone n'existe plus
        self.assertIsNone(self.clone_manager.get_clone(clone_id))
        
        # Vérifier la persistance de la suppression
        clones = self.clone_manager.get_all_clones()
        clone_ids = [c["clone_id"] for c in clones]
        self.assertNotIn(clone_id, clone_ids)
        
        logger.info("Test de suppression de clones réussi")

    def test_07_singleton_instance(self):
        """Test de l'accès à l'instance singleton du gestionnaire de clones"""
        logger.info("Test de l'instance singleton...")
        
        # Obtenir l'instance singleton
        singleton_manager = get_clone_manager()
        
        # Créer un clone depuis l'instance singleton
        clone = singleton_manager.create_clone(
            name="Clone Singleton",
            specialization="general",
            learning_rate=0.5,
            confidence_threshold=0.7
        )
        
        # Vérifier que le clone a été créé
        self.assertIsNotNone(clone)
        
        # Vérifier que l'instance singleton est différente de l'instance de test
        # mais qu'elle accède aux mêmes données
        all_clones = singleton_manager.get_all_clones()
        self.assertGreaterEqual(len(all_clones), 1)
        
        logger.info("Test de l'instance singleton réussi")

    def test_08_ai_clone_interaction(self):
        """Test de l'interaction entre les clones IA et le module d'IA principal"""
        logger.info("Test d'interaction IA...")
        
        try:
            # Créer une instance du module d'IA principal
            ai_module = SecurityAnalysisAI()
            
            # Créer un clone IA
            clone = self.clone_manager.create_clone(
                name="Clone d'interaction",
                specialization="network",
                learning_rate=0.5,
                confidence_threshold=0.7
            )
            
            # Simuler une demande d'analyse réseau
            network_data = {
                "ssid": "TestNetwork",
                "bssid": "00:11:22:33:44:55",
                "security": "WPA2",
                "encryption": "AES",
                "authentication": "PSK",
                "strength": -65,
                "frequency": "2.4 GHz",
                "channel": 6
            }
            
            # Obtenir des recommandations du module d'IA
            recommendation = ai_module.generate_recommendation_insight({
                "title": "Mettre à jour le firmware",
                "priority": "high",
                "impact": "critical"
            })
            
            # Traiter la demande avec le clone
            result = clone.process_request("analyze_network", {"network": network_data})
            
            # Vérifier que les résultats sont cohérents
            self.assertIsNotNone(result)
            self.assertIn("result", result)
            
            logger.info("Test d'interaction IA réussi")
        except Exception as e:
            logger.error(f"Erreur lors du test d'interaction IA: {e}")
            self.fail(f"Test d'interaction IA échoué: {e}")

    def test_09_load_save_integration(self):
        """Test de l'intégration du chargement et de la sauvegarde des clones"""
        logger.info("Test d'intégration chargement/sauvegarde...")
        
        # Créer des clones
        for i in range(3):
            self.clone_manager.create_clone(
                name=f"Clone de persistance {i}",
                specialization="general",
                learning_rate=0.5,
                confidence_threshold=0.7
            )
        
        # Forcer la sauvegarde
        self.clone_manager.save_clones()
        
        # Créer une nouvelle instance du gestionnaire
        new_manager = AICloneManager(config_path=self.config_path)
        
        # Charger les clones
        new_manager.load_clones()
        
        # Vérifier que les clones ont été chargés
        clones = new_manager.get_all_clones()
        self.assertGreaterEqual(len(clones), 3)
        
        # Vérifier l'intégrité des données
        for clone in clones:
            self.assertIn("clone_id", clone)
            self.assertIn("name", clone)
            self.assertIn("specialization", clone)
            self.assertIn("learning_rate", clone)
            self.assertIn("confidence_threshold", clone)
        
        logger.info("Test d'intégration chargement/sauvegarde réussi")

    def tearDown(self):
        """Nettoyage après les tests"""
        # Supprimer le fichier de configuration de test
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        
        # Supprimer le répertoire de test
        if os.path.exists(self.test_dir):
            try:
                import shutil
                shutil.rmtree(self.test_dir)
            except Exception as e:
                logger.warning(f"Erreur lors de la suppression du répertoire de test: {e}")
        
        logger.info("Nettoyage terminé")

def run_tests():
    """Exécute les tests unitaires"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAIModuleIntegration)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()

def main():
    """Fonction principale"""
    logger.info("Démarrage des tests d'intégration du module IA...")
    success = run_tests()
    
    if success:
        logger.info("Tous les tests ont réussi!")
        return 0
    else:
        logger.error("Des tests ont échoué!")
        return 1

if __name__ == "__main__":
    sys.exit(main())