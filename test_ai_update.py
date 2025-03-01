#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le système de mise à jour automatique des modèles IA
"""

import os
import sys
import time
import json
import logging
import unittest
import threading
import tempfile
import shutil
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_ai_update")

# Ajouter le répertoire courant au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importer les modules à tester
from ai_auto_update import AIAutoUpdater
from ai_update_integration import AIUpdateIntegration

class TestAIAutoUpdater(unittest.TestCase):
    """Tests pour le gestionnaire de mise à jour automatique des modèles IA"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.mkdtemp()
        self.original_model_path = "modele_ia.h5"
        self.test_model_path = os.path.join(self.test_dir, "modele_ia.h5")
        self.test_backup_dir = os.path.join(self.test_dir, "backups")
        
        # Créer un fichier modèle factice pour les tests
        os.makedirs(self.test_backup_dir, exist_ok=True)
        with open(self.test_model_path, 'wb') as f:
            f.write(b'x' * 1024)  # Factice 1KB
        
        # Initialiser l'updater
        self.updater = AIAutoUpdater()
        
        logger.info(f"Configuration des tests dans le répertoire temporaire: {self.test_dir}")
    
    def tearDown(self):
        """Nettoyage après les tests"""
        # Arrêter l'updater s'il est en cours d'exécution
        if hasattr(self, 'updater') and self.updater:
            self.updater.stop()
        
        # Supprimer le répertoire temporaire
        try:
            shutil.rmtree(self.test_dir)
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du répertoire de test: {e}")
    
    def test_01_initialization(self):
        """Test de l'initialisation du gestionnaire de mise à jour"""
        self.assertIsNotNone(self.updater)
        logger.info("Test d'initialisation réussi")
    
    def test_02_start_stop(self):
        """Test des méthodes de démarrage et d'arrêt"""
        # Démarrer l'updater
        self.updater.start()
        self.assertTrue(self.updater.running)
        
        # Vérifier que le thread est en cours d'exécution
        self.assertIsNotNone(self.updater.update_thread)
        self.assertTrue(self.updater.update_thread.is_alive())
        
        # Arrêter l'updater
        self.updater.stop()
        
        # Attendre que le thread se termine
        if self.updater.update_thread:
            self.updater.update_thread.join(timeout=5)
        
        self.assertFalse(self.updater.running)
        logger.info("Test de démarrage/arrêt réussi")
    
    def test_03_model_hash(self):
        """Test de la fonction de calcul de hash"""
        # Calculer le hash du modèle de test
        hash_value = self.updater._get_model_hash(self.test_model_path)
        
        # Vérifier que le hash n'est pas vide
        self.assertIsNotNone(hash_value)
        self.assertNotEqual(hash_value, "")
        
        # Vérifier la longueur du hash MD5 (32 caractères)
        self.assertEqual(len(hash_value), 32)
        
        # Vérifier que les hash sont identiques pour le même fichier
        hash_value2 = self.updater._get_model_hash(self.test_model_path)
        self.assertEqual(hash_value, hash_value2)
        
        # Vérifier que les hash sont différents pour des fichiers différents
        # Créer un fichier différent
        different_file = os.path.join(self.test_dir, "different.h5")
        with open(different_file, 'wb') as f:
            f.write(b'y' * 1024)
            
        hash_value3 = self.updater._get_model_hash(different_file)
        self.assertNotEqual(hash_value, hash_value3)
        
        logger.info("Test de calcul de hash réussi")
    
    def test_04_backup_model(self):
        """Test de la création de sauvegarde du modèle"""
        # Remplacer les chemins de l'updater
        original_model_path = self.updater.MODEL_PATH
        original_backup_dir = self.updater.MODEL_BACKUP_DIR
        
        try:
            # Remplacer par nos chemins de test
            self.updater.MODEL_PATH = self.test_model_path
            self.updater.MODEL_BACKUP_DIR = self.test_backup_dir
            
            # Créer une sauvegarde
            backup_success = self.updater._backup_current_model()
            
            # Vérifier que la sauvegarde a réussi
            self.assertTrue(backup_success)
            
            # Vérifier qu'il y a un fichier de sauvegarde dans le répertoire
            backup_files = [f for f in os.listdir(self.test_backup_dir)
                          if f.startswith("model_backup_") and f.endswith(".h5")]
            
            self.assertGreater(len(backup_files), 0)
            
            logger.info(f"Test de sauvegarde réussi, fichiers: {backup_files}")
        finally:
            # Restaurer les chemins originaux
            self.updater.MODEL_PATH = original_model_path
            self.updater.MODEL_BACKUP_DIR = original_backup_dir
    
    def test_05_cleanup_old_backups(self):
        """Test du nettoyage des anciennes sauvegardes"""
        # Remplacer les chemins de l'updater
        original_backup_dir = self.updater.MODEL_BACKUP_DIR
        original_max_backups = self.updater.MAX_BACKUPS
        
        try:
            # Remplacer par nos chemins de test
            self.updater.MODEL_BACKUP_DIR = self.test_backup_dir
            self.updater.MAX_BACKUPS = 3
            
            # Créer 5 sauvegardes factices avec des timestamps différents
            for i in range(5):
                # Simuler des fichiers avec des dates différentes
                backup_file = os.path.join(self.test_backup_dir, f"model_backup_202203{i:02d}_120000.h5")
                with open(backup_file, 'wb') as f:
                    f.write(b'x' * 1024)
                
                # Modifier l'heure de modification pour simuler différentes dates
                mod_time = time.time() - (i * 3600)  # 1 heure d'écart
                os.utime(backup_file, (mod_time, mod_time))
                
            # Lister les fichiers avant nettoyage
            before_files = sorted([f for f in os.listdir(self.test_backup_dir)
                                if f.startswith("model_backup_") and f.endswith(".h5")])
            
            logger.info(f"Fichiers avant nettoyage: {before_files}")
            
            # Exécuter le nettoyage
            self.updater._cleanup_old_backups()
            
            # Lister les fichiers après nettoyage
            after_files = sorted([f for f in os.listdir(self.test_backup_dir)
                               if f.startswith("model_backup_") and f.endswith(".h5")])
            
            logger.info(f"Fichiers après nettoyage: {after_files}")
            
            # Vérifier qu'il reste seulement MAX_BACKUPS fichiers
            self.assertEqual(len(after_files), self.updater.MAX_BACKUPS)
            
            # Vérifier que les fichiers les plus récents sont conservés
            self.assertEqual(set(after_files), set(before_files[:self.updater.MAX_BACKUPS]))
            
        finally:
            # Restaurer les valeurs originales
            self.updater.MODEL_BACKUP_DIR = original_backup_dir
            self.updater.MAX_BACKUPS = original_max_backups
    
    def test_06_get_status(self):
        """Test de la récupération du statut"""
        # Obtenir le statut
        status = self.updater.get_status()
        
        # Vérifier les clés attendues
        self.assertIn('running', status)
        self.assertIn('last_update_time', status)
        self.assertIn('metrics', status)
        self.assertIn('available_backups', status)
        
        # Vérifier les métriques
        self.assertIn('total_updates', status['metrics'])
        self.assertIn('failed_updates', status['metrics'])
        self.assertIn('updates', status['metrics'])
        
        logger.info(f"Test de récupération du statut réussi: {status}")

class TestAIUpdateIntegration(unittest.TestCase):
    """Tests pour l'intégration des mises à jour avec l'application"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Initialiser l'intégration
        self.integration = AIUpdateIntegration()
        logger.info("Intégration initialisée pour les tests")
    
    def tearDown(self):
        """Nettoyage après les tests"""
        # Arrêter l'intégration si elle est en cours d'exécution
        if hasattr(self, 'integration') and self.integration:
            self.integration.stop()
    
    def test_01_singleton_pattern(self):
        """Test du pattern Singleton"""
        # Créer une deuxième instance
        integration2 = AIUpdateIntegration()
        
        # Vérifier que c'est la même instance
        self.assertIs(self.integration, integration2)
        
        logger.info("Test du pattern Singleton réussi")
    
    def test_02_model_version_info(self):
        """Test de la récupération des informations de version"""
        # Obtenir les informations de version
        version_info = self.integration._get_model_version_info()
        
        # Vérifier les clés attendues
        self.assertIn('version', version_info)
        self.assertIn('creation_date', version_info)
        self.assertIn('size', version_info)
        self.assertIn('framework', version_info)
        
        logger.info(f"Test de récupération des informations de version réussi: {version_info}")
    
    def test_03_update_availability(self):
        """Test de la vérification de disponibilité de mise à jour"""
        # Vérifier la disponibilité
        available = self.integration._check_update_availability()
        
        # Le résultat doit être booléen
        self.assertIsInstance(available, bool)
        
        logger.info(f"Test de vérification de disponibilité réussi: {available}")
    
    def test_04_model_health_check(self):
        """Test de la vérification de santé du modèle"""
        # Effectuer un health check
        health_result = self.integration._perform_model_health_check()
        
        # Le résultat doit être booléen
        self.assertIsInstance(health_result, bool)
        
        logger.info(f"Test de vérification de santé réussi: {health_result}")
    
    def test_05_get_status(self):
        """Test de la récupération du statut complet"""
        # Obtenir le statut
        status = self.integration.get_status()
        
        # Vérifier les clés attendues
        self.assertIn('status', status)
        self.assertIn('last_check', status)
        self.assertIn('version_info', status)
        self.assertIn('update_available', status)
        self.assertIn('auto_update_enabled', status)
        self.assertIn('updater', status)
        self.assertIn('timestamp', status)
        
        logger.info(f"Test de récupération du statut complet réussi")
    
    def test_06_set_auto_update(self):
        """Test de l'activation/désactivation des mises à jour automatiques"""
        # État initial
        initial_state = self.integration.model_status["auto_update_enabled"]
        
        # Changer l'état
        self.integration.set_auto_update(not initial_state)
        
        # Vérifier que l'état a changé
        new_state = self.integration.model_status["auto_update_enabled"]
        self.assertNotEqual(initial_state, new_state)
        
        # Restaurer l'état initial
        self.integration.set_auto_update(initial_state)
        
        logger.info(f"Test d'activation/désactivation réussi")

def run_tests():
    """Exécute les tests unitaires"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter les tests à la suite
    suite.addTests(loader.loadTestsFromTestCase(TestAIAutoUpdater))
    suite.addTests(loader.loadTestsFromTestCase(TestAIUpdateIntegration))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Exécuter les tests
    success = run_tests()
    
    # Définir le code de sortie en fonction du résultat
    sys.exit(0 if success else 1)