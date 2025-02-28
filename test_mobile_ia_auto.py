
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le module d'IA automatique optimisé pour mobile
"""
import os
import sys
import json
import logging
from typing import Dict, List, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Importer le module d'analyse mobile
try:
    from ia_mobile_auto_analyzer import MobileAutoAnalyzer, quick_mobile_analysis
    MODULE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Erreur d'importation du module d'IA mobile: {e}")
    MODULE_AVAILABLE = False

def run_tests():
    """Exécute une série de tests sur le module d'IA mobile"""
    if not MODULE_AVAILABLE:
        logger.error("Le module d'IA mobile n'est pas disponible. Tests impossibles.")
        return False
    
    logger.info("=== TESTS DU MODULE D'IA MOBILE ===")
    
    # Test 1: Initialisation et configuration
    logger.info("Test 1: Initialisation et configuration...")
    try:
        analyzer = MobileAutoAnalyzer(cache_dir='instance/test_mobile_cache')
        analyzer.set_battery_saver_mode(True)
        analyzer.adjust_for_network_conditions('4g')
        logger.info("✓ Initialisation et configuration réussies")
    except Exception as e:
        logger.error(f"✗ Échec de l'initialisation: {e}")
        return False
    
    # Test 2: Analyse d'une application
    logger.info("Test 2: Analyse d'une application...")
    try:
        app_analysis = analyzer.analyze_installed_app(
            "TestApp", 
            "user", 
            ["INTERNET", "LOCATION", "STORAGE"]
        )
        
        if app_analysis and 'security_score' in app_analysis:
            logger.info(f"✓ Analyse d'application réussie (Score: {app_analysis['security_score']})")
        else:
            logger.error("✗ L'analyse n'a pas produit de résultat valide")
            return False
    except Exception as e:
        logger.error(f"✗ Échec de l'analyse d'application: {e}")
        return False
    
    # Test 3: Vérification des mises à jour système
    logger.info("Test 3: Vérification des mises à jour système...")
    try:
        update_status = analyzer.check_system_updates()
        
        if update_status and 'update_available' in update_status:
            status = "disponible" if update_status['update_available'] else "pas disponible"
            logger.info(f"✓ Vérification des mises à jour réussie (Mise à jour {status})")
        else:
            logger.error("✗ La vérification des mises à jour n'a pas produit de résultat valide")
            return False
    except Exception as e:
        logger.error(f"✗ Échec de la vérification des mises à jour: {e}")
        return False
    
    # Test 4: Génération de rapport
    logger.info("Test 4: Génération de rapport mobile...")
    try:
        report = analyzer.generate_mobile_report([app_analysis], update_status)
        
        if report and 'overall_security_score' in report:
            logger.info(f"✓ Génération de rapport réussie (Score global: {report['overall_security_score']})")
            if 'estimated_work_time' in report:
                logger.info(f"✓ Temps de travail estimé: {report['estimated_work_time']['format']}")
                logger.info(f"  - Temps de base: {report['estimated_work_time']['breakdown']['base_time']} minutes")
                logger.info(f"  - Correction des applications: {report['estimated_work_time']['breakdown']['app_remediation']} minutes")
                logger.info(f"  - Mises à jour système: {report['estimated_work_time']['breakdown']['system_updates']} minutes")
        else:
            logger.error("✗ La génération du rapport n'a pas produit de résultat valide")
            return False
    except Exception as e:
        logger.error(f"✗ Échec de la génération du rapport: {e}")
        return False
    
    # Test 5: Mode économie d'énergie
    logger.info("Test 5: Test du mode économie d'énergie...")
    try:
        # Désactiver le mode économie d'énergie pour comparer
        analyzer.set_battery_saver_mode(False)
        start_time_normal = time.time()
        normal_analysis = analyzer.analyze_installed_app(
            "BatteryTestApp", 
            "user", 
            ["INTERNET", "CAMERA", "LOCATION", "STORAGE", "CONTACTS"]
        )
        normal_time = time.time() - start_time_normal
        
        # Activer le mode économie d'énergie
        analyzer.set_battery_saver_mode(True)
        start_time_eco = time.time()
        eco_analysis = analyzer.analyze_installed_app(
            "BatteryTestApp", 
            "user", 
            ["INTERNET", "CAMERA", "LOCATION", "STORAGE", "CONTACTS"]
        )
        eco_time = time.time() - start_time_eco
        
        if eco_time < normal_time:
            logger.info(f"✓ Mode économie d'énergie efficace (Normal: {normal_time:.2f}s, Éco: {eco_time:.2f}s)")
        else:
            logger.warning(f"⚠ Mode économie d'énergie pas plus rapide (Normal: {normal_time:.2f}s, Éco: {eco_time:.2f}s)")
    except Exception as e:
        logger.error(f"✗ Échec du test du mode économie d'énergie: {e}")
    
    # Test 6: Test de la fonction rapide
    logger.info("Test 6: Test de la fonction d'analyse rapide...")
    try:
        quick_result = quick_mobile_analysis(['TestApp1', 'TestApp2'], 'wifi')
        
        if quick_result and 'overall_security_score' in quick_result:
            logger.info(f"✓ Analyse rapide réussie avec {quick_result['apps_analyzed']} applications")
        else:
            logger.error("✗ La fonction d'analyse rapide n'a pas produit de résultat valide")
            return False
    except Exception as e:
        logger.error(f"✗ Échec de la fonction d'analyse rapide: {e}")
        return False
    
    logger.info("=== TOUS LES TESTS ONT RÉUSSI ===")
    return True

if __name__ == "__main__":
    # Importation tardive pour éviter les problèmes avec les tests d'importation
    import time
    
    success = run_tests()
    sys.exit(0 if success else 1)
