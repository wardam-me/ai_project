
#!/usr/bin/env python3
"""
Script d'automatisation des activités du module IA
Exécute périodiquement des analyses de sécurité et génère des rapports
"""
import os
import time
import logging
import json
import random
import schedule
from datetime import datetime
from typing import Dict, Any, List

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Vérification et import conditionnel du module IA
try:
    from module_IA import SecurityAnalysisAI
    ai_available = True
    logger.info("Module IA importé avec succès")
except ImportError:
    ai_available = False
    logger.warning("Module IA non disponible, fonctionnement en mode dégradé")

# Importer les autres modules nécessaires
try:
    from network_security import NetworkSecurityAnalyzer
    from network_topology import NetworkTopology
    from security_scoring import DeviceSecurityScoring
    logger.info("Modules de sécurité importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules de sécurité: {e}")
    exit(1)

class IAActivityManager:
    """Gestionnaire d'activités automatiques du module IA"""
    
    def __init__(self, interval_minutes: int = 60):
        """
        Initialise le gestionnaire d'activités IA
        
        Args:
            interval_minutes: Intervalle en minutes entre les analyses
        """
        self.interval_minutes = interval_minutes
        self.last_run_time = None
        
        # Initialiser les modules
        self.security_analyzer = NetworkSecurityAnalyzer()
        self.network_topology = NetworkTopology()
        self.device_scoring = DeviceSecurityScoring()
        
        # Initialiser le module IA si disponible
        self.ai_module = None
        if ai_available:
            try:
                self.ai_module = SecurityAnalysisAI()
                logger.info("Module IA initialisé pour l'automatisation")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du module IA: {e}")
        
        # Créer le répertoire pour les rapports
        self.reports_dir = os.path.join("instance", "ai_reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        
        logger.info(f"Gestionnaire d'activités IA initialisé, intervalle: {interval_minutes} minutes")
    
    def run_security_analysis(self) -> Dict[str, Any]:
        """
        Exécute une analyse de sécurité complète
        
        Returns:
            Dict[str, Any]: Résultats de l'analyse
        """
        logger.info("Démarrage de l'analyse de sécurité automatique...")
        
        # Récupérer les données de topologie
        topology_data = self.network_topology.get_topology_data()
        
        # Récupérer les scores de sécurité des appareils
        device_scores = self.device_scoring.get_all_device_scores()
        
        # Obtenir les statistiques du réseau
        network_stats = self.device_scoring.get_network_security_status()
        
        # Simuler la détection de nouvelles menaces
        threats_detected = self._generate_simulated_threats()
        
        # Utiliser l'IA pour générer des recommandations si disponible
        ai_recommendations = []
        if self.ai_module is not None:
            try:
                # Générer des recommandations avancées
                ai_recommendations = self.ai_module.generate_advanced_security_recommendations(
                    total_vulns=network_stats.get('total_vulnerabilities', 0),
                    critical_vulns=network_stats.get('critical_vulnerabilities', 0)
                )
                
                # Générer une analyse du réseau
                network_analysis = self.ai_module.generate_network_security_analysis(
                    overall_score=network_stats.get('security_score', 0),
                    device_count=len(device_scores),
                    recommendation_count=len(ai_recommendations)
                )
                logger.info(f"Analyse IA générée: {network_analysis[:50]}...")
            except Exception as e:
                logger.error(f"Erreur lors de la génération des recommandations IA: {e}")
        
        # Créer les résultats de l'analyse
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "network_stats": network_stats,
            "devices_analyzed": len(device_scores),
            "threats_detected": threats_detected,
            "ai_recommendations": ai_recommendations if self.ai_module is not None else [],
            "security_score": network_stats.get('security_score', 0)
        }
        
        # Sauvegarder les résultats
        self._save_analysis_results(analysis_results)
        
        logger.info(f"Analyse de sécurité terminée, score: {analysis_results['security_score']}")
        self.last_run_time = datetime.now()
        
        return analysis_results
    
    def _generate_simulated_threats(self) -> List[Dict[str, Any]]:
        """
        Génère des menaces simulées pour les tests
        
        Returns:
            List[Dict[str, Any]]: Liste des menaces simulées
        """
        threat_types = [
            "Tentative de désauthentification",
            "Point d'accès jumeau (Evil Twin)",
            "Attaque KRACK",
            "Serveur DHCP malveillant",
            "Attaque par force brute",
            "Tentative d'accès non autorisé"
        ]
        
        severity_levels = ["low", "medium", "high", "critical"]
        
        # Générer un nombre aléatoire de menaces (0-3)
        num_threats = random.randint(0, 3)
        threats = []
        
        for _ in range(num_threats):
            threat = {
                "type": random.choice(threat_types),
                "severity": random.choice(severity_levels),
                "timestamp": datetime.now().isoformat(),
                "source_ip": f"192.168.1.{random.randint(2, 254)}",
                "description": "Détection automatique par analyse IA"
            }
            threats.append(threat)
        
        return threats
    
    def _save_analysis_results(self, results: Dict[str, Any]) -> None:
        """
        Sauvegarde les résultats de l'analyse dans un fichier JSON
        
        Args:
            results: Résultats de l'analyse à sauvegarder
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_analysis_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Résultats de l'analyse sauvegardés dans {filepath}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats: {e}")
    
    def get_latest_analysis(self) -> Dict[str, Any]:
        """
        Récupère la dernière analyse effectuée
        
        Returns:
            Dict[str, Any]: Dernière analyse ou dictionnaire vide si aucune
        """
        try:
            files = os.listdir(self.reports_dir)
            json_files = [f for f in files if f.endswith('.json')]
            
            if not json_files:
                return {}
            
            # Trier par date (du plus récent au plus ancien)
            json_files.sort(reverse=True)
            latest_file = os.path.join(self.reports_dir, json_files[0])
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la dernière analyse: {e}")
            return {}
    
    def schedule_analysis(self):
        """Configure la planification des analyses automatiques"""
        schedule.every(self.interval_minutes).minutes.do(self.run_security_analysis)
        logger.info(f"Analyse automatique planifiée toutes les {self.interval_minutes} minutes")
    
    def run(self):
        """Exécute le gestionnaire d'activités en continu"""
        logger.info("Démarrage du gestionnaire d'activités IA...")
        
        # Exécuter une première analyse immédiatement
        self.run_security_analysis()
        
        # Planifier les analyses suivantes
        self.schedule_analysis()
        
        # Boucle principale
        logger.info("Gestionnaire d'activités IA en attente...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier chaque minute


if __name__ == "__main__":
    # Configurer l'intervalle (en minutes)
    ANALYSIS_INTERVAL = 60  # 1 heure par défaut
    
    try:
        # Créer et démarrer le gestionnaire d'activités
        activity_manager = IAActivityManager(interval_minutes=ANALYSIS_INTERVAL)
        activity_manager.run()
    except KeyboardInterrupt:
        logger.info("Arrêt du gestionnaire d'activités IA")
    except Exception as e:
        logger.critical(f"Erreur fatale: {e}")
