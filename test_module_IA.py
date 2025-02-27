#!/usr/bin/env python3
"""
Script de test pour le module_IA
Ce script vérifie les fonctionnalités du module d'intelligence artificielle
"""
import os
import sys
import json
import logging
import unittest
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import du module à tester
try:
    from module_IA import SecurityAI, NetworkOptimizer
    logger.info("Module d'IA importé avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation du module_IA: {e}")
    sys.exit(1)

class TestModuleIA(unittest.TestCase):
    """Tests unitaires pour le module_IA"""
    
    def setUp(self):
        """Initialisation des tests"""
        self.security_ai = SecurityAI()
        self.network_optimizer = NetworkOptimizer()
        
        # Données de test
        self.test_networks = [
            {
                "ssid": "Réseau_Test_WPA2",
                "bssid": "00:11:22:33:44:55",
                "security": "WPA2",
                "encryption": "AES",
                "authentication": "PSK",
                "strength": -65,
                "frequency": "2.4GHz",
                "channel": 6
            },
            {
                "ssid": "Réseau_Test_WEP",
                "bssid": "AA:BB:CC:DD:EE:FF",
                "security": "WEP",
                "encryption": None,
                "authentication": None,
                "strength": -70,
                "frequency": "2.4GHz",
                "channel": 11
            },
            {
                "ssid": "Réseau_Test_OPEN",
                "bssid": "11:22:33:44:55:66",
                "security": "OPEN",
                "encryption": None,
                "authentication": None,
                "strength": -60,
                "frequency": "2.4GHz",
                "channel": 1
            },
            {
                "ssid": "Réseau_Test_WPA3",
                "bssid": "22:33:44:55:66:77",
                "security": "WPA3",
                "encryption": "GCMP",
                "authentication": "SAE",
                "strength": -55,
                "frequency": "5GHz",
                "channel": 36
            }
        ]
        
        self.test_topology = {
            "devices": [
                {
                    "mac_address": "00:11:22:33:44:55",
                    "name": "Routeur principal",
                    "type": "router",
                    "ip_address": "192.168.1.1",
                    "security_score": 85,
                    "firmware_updated": True
                },
                {
                    "mac_address": "AA:BB:CC:DD:EE:FF",
                    "name": "Ordinateur portable",
                    "type": "laptop",
                    "ip_address": "192.168.1.100",
                    "security_score": 40,
                    "firmware_updated": False
                },
                {
                    "mac_address": "11:22:33:44:55:66",
                    "name": "Téléphone mobile",
                    "type": "phone",
                    "ip_address": "192.168.1.101",
                    "security_score": 75,
                    "firmware_updated": True
                }
            ],
            "connections": [
                {
                    "source": "00:11:22:33:44:55",
                    "target": "AA:BB:CC:DD:EE:FF",
                    "type": "wifi",
                    "strength": -65,
                    "encrypted": True
                },
                {
                    "source": "00:11:22:33:44:55",
                    "target": "11:22:33:44:55:66",
                    "type": "wifi",
                    "strength": -60,
                    "encrypted": False
                }
            ]
        }
        
        logger.info("Initialisation des tests terminée")
    
    def test_wifi_security_analysis(self):
        """Test de l'analyse de sécurité WiFi"""
        logger.info("Test de l'analyse de sécurité WiFi...")
        
        # Exécution de l'analyse
        result = self.security_ai.analyze_wifi_security(self.test_networks)
        
        # Vérifications
        self.assertIsNotNone(result)
        self.assertIn('overall_score', result)
        self.assertIn('networks_analyzed', result)
        self.assertIn('security_levels', result)
        self.assertIn('recommendations', result)
        
        # Vérification du nombre de réseaux analysés
        self.assertEqual(result['networks_analyzed'], len(self.test_networks))
        
        # Vérification des niveaux de sécurité
        self.assertGreaterEqual(sum(result['security_levels'].values()), len(self.test_networks))
        
        # Vérification des recommandations
        self.assertGreaterEqual(len(result['recommendations']), 1)
        
        logger.info(f"Score global de sécurité WiFi: {result['overall_score']:.2f}")
        logger.info(f"Niveaux de sécurité: {result['security_levels']}")
        logger.info(f"Nombre de recommandations: {len(result['recommendations'])}")
        
        logger.info("Test de l'analyse de sécurité WiFi terminé avec succès")
    
    def test_network_optimization(self):
        """Test de l'optimisation du réseau"""
        logger.info("Test de l'optimisation du réseau...")
        
        # Exécution de l'optimisation
        result = self.network_optimizer.optimize_network_security(self.test_topology)
        
        # Vérifications
        self.assertIsNotNone(result)
        self.assertIn('optimality_score', result)
        self.assertIn('vulnerability_statistics', result)
        self.assertIn('recommendations', result)
        
        # Vérification du score d'optimalité
        self.assertGreaterEqual(result['optimality_score'], 0)
        self.assertLessEqual(result['optimality_score'], 100)
        
        # Vérification des vulnérabilités
        self.assertIn('raw_vulnerabilities', result)
        self.assertIsInstance(result['raw_vulnerabilities'], list)
        
        # Vérification des recommandations
        self.assertIn('priority', result['recommendations'])
        self.assertIn('medium', result['recommendations'])
        self.assertIn('low', result['recommendations'])
        
        logger.info(f"Score d'optimalité du réseau: {result['optimality_score']:.2f}")
        logger.info(f"Statistiques de vulnérabilités: {result['vulnerability_statistics']}")
        logger.info(f"Nombre de recommandations prioritaires: {len(result['recommendations']['priority'])}")
        
        logger.info("Test de l'optimisation du réseau terminé avec succès")
    
    def test_network_vulnerabilities_prediction(self):
        """Test de la prédiction des vulnérabilités du réseau"""
        logger.info("Test de la prédiction des vulnérabilités...")
        
        # Exécution de la prédiction
        vulnerabilities = self.network_optimizer.predict_network_vulnerabilities(self.test_topology)
        
        # Vérifications
        self.assertIsNotNone(vulnerabilities)
        self.assertIsInstance(vulnerabilities, list)
        
        # Vérification des détails des vulnérabilités
        if vulnerabilities:
            for vuln in vulnerabilities:
                self.assertIn('vulnerability_type', vuln)
                self.assertIn('severity', vuln)
                self.assertIn('probability', vuln)
                self.assertIn('description', vuln)
                self.assertIn('recommendation', vuln)
        
        logger.info(f"Nombre de vulnérabilités prédites: {len(vulnerabilities)}")
        for i, vuln in enumerate(vulnerabilities):
            logger.info(f"Vulnérabilité {i+1}: {vuln['vulnerability_type']} - {vuln['severity']} - {vuln['description']}")
        
        logger.info("Test de la prédiction des vulnérabilités terminé avec succès")
    
    def test_recommendations_generation(self):
        """Test de la génération des recommandations"""
        logger.info("Test de la génération des recommandations...")
        
        # Analyse WiFi pour obtenir les scores et niveaux de sécurité
        wifi_analysis = self.security_ai.analyze_wifi_security(self.test_networks)
        
        # Exécution de la génération de recommandations
        recommendations = self.security_ai._generate_recommendations(
            wifi_analysis['network_scores'],
            wifi_analysis['security_levels']
        )
        
        # Vérifications
        self.assertIsNotNone(recommendations)
        self.assertIsInstance(recommendations, list)
        
        # Vérification des détails des recommandations
        if recommendations:
            for rec in recommendations:
                self.assertIn('priority', rec)
                self.assertIn('title', rec)
                self.assertIn('description', rec)
                self.assertIn('action_items', rec)
                self.assertIsInstance(rec['action_items'], list)
        
        logger.info(f"Nombre de recommandations générées: {len(recommendations)}")
        for i, rec in enumerate(recommendations):
            logger.info(f"Recommandation {i+1}: [{rec['priority']}] {rec['title']}")
        
        logger.info("Test de la génération des recommandations terminé avec succès")
    
    def tearDown(self):
        """Nettoyage après les tests"""
        # Supprimer les fichiers temporaires générés pendant les tests
        try:
            history_path = os.path.join('config', 'optimization_history.json')
            trends_path = os.path.join('config', 'security_trends.json')
            
            if os.path.exists(history_path):
                logger.info(f"Suppression du fichier temporaire: {history_path}")
                os.remove(history_path)
            
            if os.path.exists(trends_path):
                logger.info(f"Suppression du fichier temporaire: {trends_path}")
                os.remove(trends_path)
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage des fichiers temporaires: {e}")
        
        logger.info("Nettoyage des tests terminé")


def run_tests():
    """Exécute les tests unitaires"""
    logger.info("Démarrage des tests unitaires pour le module_IA...")
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestModuleIA)
    result = runner.run(test_suite)
    
    # Vérification des résultats
    if result.wasSuccessful():
        logger.info("Tous les tests ont réussi !")
        return 0
    else:
        logger.error(f"Certains tests ont échoué: {len(result.failures)} échecs, {len(result.errors)} erreurs")
        return 1


def test_integration():
    """Tests d'intégration avec d'autres modules du projet"""
    logger.info("Démarrage des tests d'intégration...")
    
    # Vérification de l'existence des autres modules requis
    required_modules = [
        'assistant_securite.py',
        'network_topology.py',
        'security_scoring.py',
        'gamification.py',
        'protocol_analyzer.py'
    ]
    
    missing_modules = []
    for module in required_modules:
        if not os.path.exists(module):
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Modules manquants pour l'intégration: {', '.join(missing_modules)}")
        return False
    
    # Tests d'intégration simplifiés
    security_ai = SecurityAI()
    network_optimizer = NetworkOptimizer()
    
    # Test d'intégration avec les données de topologie
    try:
        # Utilisation de données de test
        test_topology = {
            "devices": [
                {
                    "mac_address": "00:11:22:33:44:55",
                    "name": "Routeur principal",
                    "type": "router",
                    "ip_address": "192.168.1.1",
                    "security_score": 85
                }
            ],
            "connections": []
        }
        
        # Test de l'optimisation
        result = network_optimizer.optimize_network_security(test_topology)
        logger.info(f"Intégration avec topologie réseau: Score d'optimalité = {result['optimality_score']:.2f}")
        
    except Exception as e:
        logger.error(f"Erreur lors du test d'intégration avec la topologie: {e}")
        return False
    
    # Test d'intégration avec les données WiFi
    try:
        # Utilisation de données de test
        test_networks = [
            {
                "ssid": "Test_Network",
                "bssid": "00:11:22:33:44:55",
                "security": "WPA2",
                "encryption": "AES",
                "authentication": "PSK",
                "strength": -65,
                "frequency": "2.4GHz",
                "channel": 6
            }
        ]
        
        # Test de l'analyse
        result = security_ai.analyze_wifi_security(test_networks)
        logger.info(f"Intégration avec analyse WiFi: Score global = {result['overall_score']:.2f}")
        
    except Exception as e:
        logger.error(f"Erreur lors du test d'intégration avec l'analyse WiFi: {e}")
        return False
    
    logger.info("Tests d'intégration terminés avec succès")
    return True


def run_performance_test():
    """Tests de performance du module_IA"""
    logger.info("Démarrage des tests de performance...")
    
    # Initialisation des objets
    security_ai = SecurityAI()
    network_optimizer = NetworkOptimizer()
    
    # Génération de données de test à grande échelle
    large_network_list = []
    large_topology = {"devices": [], "connections": []}
    
    # Génération de 100 réseaux WiFi
    for i in range(100):
        security_type = "WPA2" if i % 3 != 0 else ("WPA" if i % 5 != 0 else ("WEP" if i % 7 != 0 else "OPEN"))
        encryption = "AES" if security_type == "WPA2" else ("TKIP" if security_type == "WPA" else None)
        authentication = "PSK" if security_type in ["WPA", "WPA2"] else None
        
        network = {
            "ssid": f"Network_{i}",
            "bssid": f"{i:02}:{i:02}:{i:02}:{i:02}:{i:02}:{i:02}",
            "security": security_type,
            "encryption": encryption,
            "authentication": authentication,
            "strength": -50 - (i % 50),
            "frequency": "2.4GHz" if i % 2 == 0 else "5GHz",
            "channel": i % 14 + 1
        }
        large_network_list.append(network)
    
    # Génération de 50 appareils
    for i in range(50):
        device = {
            "mac_address": f"{i:02}:{i:02}:{i:02}:{i:02}:{i:02}:{i:02}",
            "name": f"Device_{i}",
            "type": "router" if i == 0 else ("laptop" if i % 3 == 0 else ("phone" if i % 5 == 0 else "iot")),
            "ip_address": f"192.168.1.{i+1}",
            "security_score": 100 - (i % 80),
            "firmware_updated": i % 2 == 0
        }
        large_topology["devices"].append(device)
    
    # Génération de 100 connexions
    for i in range(100):
        source_idx = i % 50
        target_idx = (i + 1) % 50
        
        if source_idx != target_idx:
            connection = {
                "source": large_topology["devices"][source_idx]["mac_address"],
                "target": large_topology["devices"][target_idx]["mac_address"],
                "type": "wifi" if i % 3 == 0 else ("ethernet" if i % 5 == 0 else "bluetooth"),
                "strength": -50 - (i % 50) if i % 3 == 0 else None,
                "encrypted": i % 7 != 0
            }
            large_topology["connections"].append(connection)
    
    # Test de performance pour l'analyse WiFi
    import time
    start_time = time.time()
    
    wifi_result = security_ai.analyze_wifi_security(large_network_list)
    
    wifi_duration = time.time() - start_time
    logger.info(f"Analyse WiFi de {len(large_network_list)} réseaux en {wifi_duration:.2f} secondes")
    logger.info(f"Score moyen: {wifi_result['overall_score']:.2f}")
    
    # Test de performance pour l'optimisation réseau
    start_time = time.time()
    
    optimization_result = network_optimizer.optimize_network_security(large_topology)
    
    optimization_duration = time.time() - start_time
    logger.info(f"Optimisation de {len(large_topology['devices'])} appareils en {optimization_duration:.2f} secondes")
    logger.info(f"Score d'optimalité: {optimization_result['optimality_score']:.2f}")
    logger.info(f"Vulnérabilités détectées: {len(optimization_result['raw_vulnerabilities'])}")
    
    # Résultats des tests de performance
    performance_results = {
        "wifi_analysis": {
            "networks_count": len(large_network_list),
            "duration_seconds": wifi_duration,
            "networks_per_second": len(large_network_list) / wifi_duration if wifi_duration > 0 else 0
        },
        "network_optimization": {
            "devices_count": len(large_topology["devices"]),
            "connections_count": len(large_topology["connections"]),
            "duration_seconds": optimization_duration,
            "devices_per_second": len(large_topology["devices"]) / optimization_duration if optimization_duration > 0 else 0,
            "vulnerabilities_count": len(optimization_result["raw_vulnerabilities"])
        }
    }
    
    # Sauvegarde des résultats de performance
    try:
        os.makedirs("results", exist_ok=True)
        with open(os.path.join("results", "performance_results.json"), "w", encoding="utf-8") as f:
            json.dump(performance_results, f, indent=2)
        logger.info("Résultats de performance sauvegardés dans results/performance_results.json")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des résultats de performance: {e}")
    
    logger.info("Tests de performance terminés")
    return performance_results


if __name__ == "__main__":
    print("=" * 80)
    print("TEST DU MODULE D'IA POUR L'ANALYSE DE SÉCURITÉ RÉSEAU")
    print("=" * 80)
    print()
    
    # Exécution des tests unitaires
    print("\n" + "=" * 40)
    print("TESTS UNITAIRES")
    print("=" * 40)
    unit_test_result = run_tests()
    
    # Exécution des tests d'intégration
    print("\n" + "=" * 40)
    print("TESTS D'INTÉGRATION")
    print("=" * 40)
    integration_test_result = test_integration()
    
    # Exécution des tests de performance
    print("\n" + "=" * 40)
    print("TESTS DE PERFORMANCE")
    print("=" * 40)
    performance_results = run_performance_test()
    
    # Résumé des résultats
    print("\n" + "=" * 40)
    print("RÉSUMÉ DES TESTS")
    print("=" * 40)
    print(f"Tests unitaires : {'SUCCÈS' if unit_test_result == 0 else 'ÉCHEC'}")
    print(f"Tests d'intégration : {'SUCCÈS' if integration_test_result else 'ÉCHEC'}")
    print(f"Tests de performance :")
    print(f"  - Analyse WiFi : {performance_results['wifi_analysis']['networks_count']} réseaux en {performance_results['wifi_analysis']['duration_seconds']:.2f} secondes")
    print(f"  - Optimisation réseau : {performance_results['network_optimization']['devices_count']} appareils en {performance_results['network_optimization']['duration_seconds']:.2f} secondes")
    print()
    
    # Verdict final
    if unit_test_result == 0 and integration_test_result:
        print("VERDICT : Le module_IA est fonctionnel et prêt à être intégré au projet.")
        sys.exit(0)
    else:
        print("VERDICT : Le module_IA présente des problèmes qui doivent être corrigés avant l'intégration.")
        sys.exit(1)