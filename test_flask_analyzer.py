
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour l'analyseur de projets Flask
"""
import os
import json
import logging
import unittest
from flask_analyzer import FlaskProjectAnalyzer

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFlaskAnalyzer(unittest.TestCase):
    """Tests unitaires pour l'analyseur de projets Flask"""
    
    def setUp(self):
        """Initialisation des tests"""
        self.analyzer = FlaskProjectAnalyzer()
        
        # Vérifier si nous sommes dans un projet Flask
        self.is_flask_project = False
        for file in os.listdir('.'):
            if file.endswith('.py'):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'Flask(' in content:
                            self.is_flask_project = True
                            break
                except Exception:
                    pass
        
        logger.info(f"Tests initialisés, projet Flask détecté: {self.is_flask_project}")
    
    def test_project_structure(self):
        """Test de l'analyse de la structure du projet"""
        structure = self.analyzer.analyze_project_structure()
        
        self.assertIsNotNone(structure)
        self.assertIn('directories', structure)
        self.assertIn('files', structure)
        self.assertIn('file_types', structure)
        
        logger.info(f"Structure du projet analysée: {len(structure['files'])} fichiers")
    
    def test_interactions(self):
        """Test de l'analyse des interactions"""
        # D'abord analyser la structure
        self.analyzer.analyze_project_structure()
        
        # Ensuite analyser les interactions
        interactions = self.analyzer.analyze_interactions()
        
        self.assertIsNotNone(interactions)
        self.assertIn('imports', interactions)
        self.assertIn('routes', interactions)
        self.assertIn('models', interactions)
        
        logger.info(f"Interactions analysées: {len(interactions['routes'])} routes")
    
    def test_error_detection(self):
        """Test de la détection des erreurs"""
        # D'abord analyser la structure
        self.analyzer.analyze_project_structure()
        
        # Analyser les interactions
        self.analyzer.analyze_interactions()
        
        # Détecter les erreurs
        errors = self.analyzer.detect_errors()
        
        self.assertIsNotNone(errors)
        self.assertIsInstance(errors, list)
        
        if errors:
            for error in errors:
                self.assertIn('type', error)
                self.assertIn('severity', error)
                self.assertIn('description', error)
        
        logger.info(f"Erreurs détectées: {len(errors)}")
    
    def test_duplicates(self):
        """Test de la détection des fichiers dupliqués"""
        # D'abord analyser la structure
        self.analyzer.analyze_project_structure()
        
        # Détecter les doublons
        duplicates = self.analyzer.find_duplicates()
        
        self.assertIsNotNone(duplicates)
        self.assertIsInstance(duplicates, list)
        
        if duplicates:
            for duplicate in duplicates:
                self.assertIn('type', duplicate)
                self.assertIn('file1', duplicate)
                self.assertIn('file2', duplicate)
        
        logger.info(f"Fichiers dupliqués détectés: {len(duplicates)}")
    
    def test_statistics(self):
        """Test de la génération des statistiques"""
        # Analyser le projet complet
        self.analyzer.analyze_project_structure()
        self.analyzer.analyze_interactions()
        self.analyzer.detect_errors()
        self.analyzer.find_duplicates()
        
        # Générer les statistiques
        statistics = self.analyzer.generate_statistics()
        
        self.assertIsNotNone(statistics)
        self.assertIn('file_count', statistics)
        self.assertIn('error_count', statistics)
        self.assertIn('duplicate_count', statistics)
        
        logger.info(f"Statistiques générées: {statistics['file_count']} fichiers")
    
    def test_recommendations(self):
        """Test de la génération des recommandations"""
        # Analyser le projet complet
        self.analyzer.analyze_project_structure()
        self.analyzer.analyze_interactions()
        self.analyzer.detect_errors()
        self.analyzer.find_duplicates()
        self.analyzer.generate_statistics()
        
        # Générer les recommandations
        recommendations = self.analyzer.generate_recommendations()
        
        self.assertIsNotNone(recommendations)
        self.assertIsInstance(recommendations, list)
        
        if recommendations:
            for rec in recommendations:
                self.assertIn('priority', rec)
                self.assertIn('title', rec)
                self.assertIn('description', rec)
        
        logger.info(f"Recommandations générées: {len(recommendations)}")
    
    def test_complete_analysis(self):
        """Test de l'analyse complète"""
        # Analyser le projet complet en une seule fois
        results = self.analyzer.analyze_project()
        
        self.assertIsNotNone(results)
        self.assertIn('structure', results)
        self.assertIn('interactions', results)
        self.assertIn('errors', results)
        self.assertIn('duplicates', results)
        self.assertIn('statistics', results)
        self.assertIn('recommendations', results)
        self.assertIn('is_compliant', results)
        
        # Vérifier l'évaluation binaire
        self.assertIn('result', results['is_compliant'])
        self.assertIn(results['is_compliant']['result'], ['oui', 'non'])
        
        logger.info(f"Analyse complète terminée, conformité: {results['is_compliant']['result'].upper()}")
        logger.info(f"Score de conformité: {results['is_compliant']['score']}/100")
    
    def tearDown(self):
        """Nettoyage après les tests"""
        pass


def run_tests():
    """Exécute les tests unitaires"""
    logger.info("Démarrage des tests unitaires pour l'analyseur Flask...")
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestFlaskAnalyzer)
    result = runner.run(test_suite)
    
    # Vérification des résultats
    if result.wasSuccessful():
        logger.info("Tous les tests ont réussi !")
        return 0
    else:
        logger.error(f"Certains tests ont échoué: {len(result.failures)} échecs, {len(result.errors)} erreurs")
        return 1


if __name__ == "__main__":
    print("=" * 80)
    print("TESTS DE L'ANALYSEUR DE PROJETS FLASK")
    print("=" * 80)
    print()
    
    # Exécution des tests unitaires
    exit_code = run_tests()
    
    # Exécuter une analyse complète en mode démo
    print("\n" + "=" * 80)
    print("DÉMONSTRATION DE L'ANALYSEUR")
    print("=" * 80)
    
    analyzer = FlaskProjectAnalyzer()
    results = analyzer.analyze_project()
    
    # Sauvegarder les résultats pour référence
    try:
        with open('flask_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("Résultats d'analyse sauvegardés dans flask_analysis_results.json")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des résultats: {e}")
    
    # Afficher un résumé
    print("\nRÉSUMÉ DE L'ANALYSE:")
    print(f"- {results['statistics'].get('file_count', 0)} fichiers analysés")
    print(f"- {results['statistics'].get('error_count', 0)} erreurs détectées")
    print(f"- {results['statistics'].get('duplicate_count', 0)} fichiers dupliqués")
    print(f"- {len(results.get('recommendations', []))} recommandations")
    
    # Afficher le résultat binaire
    print("\nÉVALUATION BINAIRE:")
    print(f"Résultat: {results['is_compliant']['result'].upper()}")
    print(f"Score: {results['is_compliant']['score']}/100")
    for reason in results['is_compliant']['justification']:
        print(f"- {reason}")
    
    sys.exit(exit_code)
