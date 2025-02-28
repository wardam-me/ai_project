
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'IA automatique optimisé pour les appareils mobiles
Permet l'analyse des applications et la vérification des mises à jour système
"""
import logging
import json
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration du logging optimisée pour mobile (réduit l'utilisation de la mémoire)
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import conditionnel du module principal d'IA
try:
    from module_IA import SecurityAnalysisAI
    AI_MODULE_AVAILABLE = True
    logger.info("Module SecurityAnalysisAI importé avec succès")
except ImportError:
    AI_MODULE_AVAILABLE = False
    logger.warning("Module IA principal non disponible, fonctionnement en mode dégradé")

class MobileAutoAnalyzer:
    """
    Analyseur automatique optimisé pour les appareils mobiles
    Permet d'analyser des applications et de vérifier les mises à jour système
    avec une empreinte mémoire réduite et une efficacité énergétique accrue
    """
    
    def __init__(self, cache_dir: str = 'instance/mobile_cache'):
        """
        Initialise l'analyseur automatique mobile
        
        Args:
            cache_dir: Répertoire pour le cache des analyses (optimisé pour limiter l'utilisation du stockage)
        """
        self.cache_dir = cache_dir
        self.results_file = os.path.join(cache_dir, 'mobile_analyses.json')
        self.security_ai = None
        self.last_analysis = None
        self.battery_saver_mode = False
        self.throttling_level = 0  # 0: aucun, 1: léger, 2: modéré, 3: fort
        
        # Création du répertoire de cache si nécessaire
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialisation du module d'IA principal si disponible
        if AI_MODULE_AVAILABLE:
            try:
                self.security_ai = SecurityAnalysisAI()
                logger.info("Module d'IA de sécurité initialisé pour analyse mobile")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du module IA: {e}")
        
        # Charger les résultats d'analyses précédentes
        self._load_previous_results()
    
    def _load_previous_results(self) -> None:
        """Charge les résultats d'analyses précédentes depuis le cache"""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    self.previous_results = json.load(f)
                    logger.info(f"Chargé {len(self.previous_results)} analyses précédentes")
            except Exception as e:
                logger.error(f"Erreur lors du chargement des résultats précédents: {e}")
                self.previous_results = {}
        else:
            self.previous_results = {}
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """
        Enregistre les résultats d'analyse dans le cache
        
        Args:
            results: Résultats d'analyse à sauvegarder
        """
        # Ajouter un timestamp pour le suivi
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results['timestamp'] = timestamp
        
        # Mettre à jour les résultats précédents avec les nouveaux
        analysis_id = f"analysis_{int(time.time())}"
        self.previous_results[analysis_id] = results
        
        # Limiter la taille du cache pour les appareils mobiles (garder seulement les 10 dernières analyses)
        if len(self.previous_results) > 10:
            # Trier par timestamp et supprimer les plus anciennes
            sorted_keys = sorted(self.previous_results.keys(), 
                                key=lambda k: self.previous_results[k].get('timestamp', ''))
            for old_key in sorted_keys[:-10]:
                del self.previous_results[old_key]
        
        # Sauvegarder dans le fichier
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.previous_results, f, indent=2, ensure_ascii=False)
            logger.info(f"Résultats d'analyse sauvegardés dans {self.results_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats: {e}")
    
    def set_battery_saver_mode(self, enabled: bool = True) -> None:
        """
        Active ou désactive le mode économie d'énergie
        
        Args:
            enabled: True pour activer, False pour désactiver
        """
        self.battery_saver_mode = enabled
        if enabled:
            logger.info("Mode économie d'énergie activé - Analyses réduites")
            self.throttling_level = 2
        else:
            logger.info("Mode économie d'énergie désactivé - Analyses complètes")
            self.throttling_level = 0
    
    def adjust_for_network_conditions(self, network_type: str) -> None:
        """
        Ajuste les paramètres d'analyse en fonction des conditions réseau
        
        Args:
            network_type: Type de réseau ('wifi', '4g', '3g', '2g')
        """
        if network_type == 'wifi':
            self.throttling_level = 0
        elif network_type == '4g':
            self.throttling_level = 1
        elif network_type == '3g':
            self.throttling_level = 2
        else:  # 2g ou pire
            self.throttling_level = 3
            self.battery_saver_mode = True
        
        logger.info(f"Ajustement pour réseau {network_type} - Niveau de limitation: {self.throttling_level}")
    
    def analyze_installed_app(self, app_name: str, app_type: str, 
                             permissions: List[str]) -> Dict[str, Any]:
        """
        Analyse la sécurité d'une application installée
        
        Args:
            app_name: Nom de l'application
            app_type: Type d'application ('system', 'user', 'network', 'security', etc.)
            permissions: Liste des permissions demandées par l'application
            
        Returns:
            Résultats de l'analyse
        """
        logger.info(f"Analyse de l'application {app_name} ({app_type})")
        
        # Structure de base des résultats
        results = {
            'app_name': app_name,
            'app_type': app_type,
            'permissions': permissions,
            'security_score': 0,
            'risk_level': 'unknown',
            'recommendations': [],
            'ai_insights': []
        }
        
        # Vérifier si l'application a déjà été analysée récemment
        for analysis_id, prev_result in self.previous_results.items():
            if prev_result.get('app_name') == app_name:
                # Si analyse récente (moins de 24h) et en mode éco énergie, réutiliser
                timestamp = datetime.strptime(prev_result.get('timestamp', '2000-01-01'), "%Y-%m-%d %H:%M:%S")
                time_diff = datetime.now() - timestamp
                if self.battery_saver_mode and time_diff.days < 1:
                    logger.info(f"Réutilisation de l'analyse récente pour {app_name} (mode éco énergie)")
                    return prev_result
        
        # Calculer le score de sécurité basé sur les permissions
        dangerous_permissions = [
            'CAMERA', 'MICROPHONE', 'LOCATION', 'CONTACTS', 'SMS', 
            'STORAGE', 'PHONE', 'CALENDAR', 'ACCOUNTS', 'ADMIN'
        ]
        
        # Normaliser les permissions pour la comparaison
        normalized_permissions = [p.upper() for p in permissions]
        
        # Calculer le score initial
        danger_count = sum(1 for p in normalized_permissions if any(dp in p for dp in dangerous_permissions))
        initial_score = 100 - (danger_count * 10)
        
        # Ajuster le score en fonction du type d'application
        if app_type == 'system':
            # Les applications système ont besoin de plus de permissions
            results['security_score'] = min(100, initial_score + 20)
        elif app_type == 'security':
            # Les applications de sécurité ont aussi besoin de plus de permissions
            results['security_score'] = min(100, initial_score + 10)
        else:
            results['security_score'] = initial_score
        
        # Déterminer le niveau de risque
        if results['security_score'] >= 80:
            results['risk_level'] = 'low'
        elif results['security_score'] >= 60:
            results['risk_level'] = 'medium'
        else:
            results['risk_level'] = 'high'
        
        # Générer des recommandations basiques même sans le module IA
        if 'LOCATION' in str(normalized_permissions):
            results['recommendations'].append(
                "Cette application accède à votre localisation. Vérifiez si cette permission est nécessaire."
            )
        
        if 'CAMERA' in str(normalized_permissions) or 'MICROPHONE' in str(normalized_permissions):
            results['recommendations'].append(
                "L'application peut accéder à votre caméra ou microphone. Soyez vigilant quant à son utilisation."
            )
        
        # Utiliser le module IA pour des insights plus avancés si disponible
        if self.security_ai and not self.battery_saver_mode:
            try:
                # Simulation d'un appareil pour l'analyse (puisque nous analysons une app)
                device_insight = self.security_ai.analyze_device_security(
                    app_type, app_name, results['security_score']
                )
                if device_insight:
                    results['ai_insights'].append(device_insight)
                
                # Recommandation basée sur le niveau de risque
                vuln_insight = self.security_ai.analyze_vulnerability(
                    f"app-{app_name}", 
                    f"Permissions excessives pour {app_name}", 
                    results['risk_level']
                )
                if vuln_insight:
                    results['ai_insights'].append(vuln_insight)
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse IA pour {app_name}: {e}")
        
        # Sauvegarder les résultats
        self._save_results(results)
        
        return results
    
    def check_system_updates(self) -> Dict[str, Any]:
        """
        Vérifie si des mises à jour système sont disponibles
        
        Returns:
            Statut des mises à jour et recommandations
        """
        logger.info("Vérification des mises à jour système")
        
        # En production, on utiliserait l'API du système pour vérifier les mises à jour réelles
        # Simulation pour démonstration
        update_result = {
            'update_available': random.choice([True, False]),
            'current_version': '12.0.1',
            'latest_version': '12.0.2' if random.choice([True, False]) else '12.0.1',
            'security_patches': random.randint(0, 3),
            'update_priority': 'low',
            'recommendations': [],
            'ai_insights': []
        }
        
        # Déterminer s'il y a des mises à jour de sécurité et leur priorité
        if update_result['update_available']:
            if update_result['security_patches'] > 0:
                if update_result['security_patches'] >= 3:
                    update_result['update_priority'] = 'critical'
                elif update_result['security_patches'] >= 1:
                    update_result['update_priority'] = 'high'
                
                update_result['recommendations'].append(
                    f"Une mise à jour de sécurité est disponible ({update_result['latest_version']}). "
                    f"Elle contient {update_result['security_patches']} correctifs de sécurité."
                )
            else:
                update_result['recommendations'].append(
                    f"Une mise à jour est disponible ({update_result['latest_version']}), "
                    "mais elle ne contient pas de correctifs de sécurité critiques."
                )
        else:
            update_result['recommendations'].append(
                "Votre système est à jour. Continuez à vérifier régulièrement les mises à jour."
            )
        
        # Utiliser le module IA pour des insights plus avancés si disponible
        if self.security_ai and not self.battery_saver_mode:
            try:
                # Générer une recommandation plus intelligente
                if update_result['update_available'] and update_result['security_patches'] > 0:
                    insight = self.security_ai.generate_recommendation_insight({
                        'title': 'Mise à jour du système d\'exploitation',
                        'priority': update_result['update_priority']
                    })
                    if insight:
                        update_result['ai_insights'].append(insight)
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse IA pour les mises à jour: {e}")
        
        # Sauvegarder les résultats
        self._save_results(update_result)
        
        return update_result
    
    def generate_mobile_report(self, app_analyses: List[Dict[str, Any]], 
                              update_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un rapport complet optimisé pour l'affichage mobile
        
        Args:
            app_analyses: Liste des analyses d'applications
            update_status: Statut des mises à jour système
            
        Returns:
            Rapport complet formaté pour l'affichage mobile
        """
        logger.info("Génération du rapport mobile")
        
        # Obtenir le score global de sécurité
        app_scores = [analysis.get('security_score', 0) for analysis in app_analyses]
        overall_score = sum(app_scores) / len(app_scores) if app_scores else 0
        
        # Ajuster le score en fonction du statut des mises à jour
        if update_status.get('update_available', False):
            if update_status.get('update_priority') == 'critical':
                overall_score -= 20
            elif update_status.get('update_priority') == 'high':
                overall_score -= 10
            else:
                overall_score -= 5
        
        # S'assurer que le score reste dans la plage 0-100
        overall_score = max(0, min(100, overall_score))
        
        # Trier les applications par niveau de risque
        high_risk_apps = [a for a in app_analyses if a.get('risk_level') == 'high']
        medium_risk_apps = [a for a in app_analyses if a.get('risk_level') == 'medium']
        
        # Construire le rapport complet
        report = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'overall_security_score': overall_score,
            'security_status': self._get_security_status(overall_score),
            'apps_analyzed': len(app_analyses),
            'high_risk_count': len(high_risk_apps),
            'medium_risk_count': len(medium_risk_apps),
            'system_up_to_date': not update_status.get('update_available', False),
            'critical_actions': [],
            'recommendations': [],
            'detailed_results': {
                'app_analyses': app_analyses,
                'update_status': update_status
            }
        }
        
        # Ajouter les actions critiques
        if high_risk_apps:
            report['critical_actions'].append({
                'title': f"Examiner {len(high_risk_apps)} application(s) à haut risque",
                'details': [app.get('app_name', 'App inconnue') for app in high_risk_apps]
            })
        
        if update_status.get('update_priority') in ['critical', 'high']:
            report['critical_actions'].append({
                'title': "Mettre à jour le système d'exploitation",
                'details': [f"Version actuelle: {update_status.get('current_version')}", 
                           f"Nouvelle version: {update_status.get('latest_version')}"]
            })
        
        # Utiliser le module IA pour une analyse globale si disponible
        if self.security_ai and not self.battery_saver_mode:
            try:
                network_analysis = self.security_ai.generate_network_security_analysis(
                    int(overall_score), len(app_analyses), len(report['critical_actions'])
                )
                if network_analysis:
                    report['ai_global_analysis'] = network_analysis
            except Exception as e:
                logger.error(f"Erreur lors de la génération de l'analyse globale: {e}")
        
        return report
    
    def _get_security_status(self, score: float) -> str:
        """
        Détermine le statut de sécurité global basé sur le score
        
        Args:
            score: Score de sécurité global
            
        Returns:
            Description du statut de sécurité
        """
        if score >= 90:
            return "Excellent - Votre appareil est bien protégé"
        elif score >= 75:
            return "Bon - Protection générale adéquate"
        elif score >= 60:
            return "Moyen - Des améliorations sont nécessaires"
        elif score >= 40:
            return "Faible - Risques de sécurité significatifs"
        else:
            return "Critique - Action immédiate requise"
    
    def get_battery_friendly_recommendations(self) -> List[Dict[str, Any]]:
        """
        Retourne des recommandations optimisées pour économiser la batterie
        
        Returns:
            Liste de recommandations pour économiser la batterie
        """
        recommendations = [
            {
                'title': "Désactiver les analyses automatiques",
                'description': "Limitez les analyses automatiques aux moments où l'appareil est en charge",
                'impact': "Élevé"
            },
            {
                'title': "Réduire la fréquence des analyses",
                'description': "Une analyse hebdomadaire est suffisante pour la plupart des utilisateurs",
                'impact': "Moyen"
            },
            {
                'title': "Activer le mode économie d'énergie pendant les analyses",
                'description': "Utilise des méthodes d'analyse plus légères",
                'impact': "Moyen"
            }
        ]
        
        return recommendations

# Fonction utilitaire pour exécuter une analyse rapide
def quick_mobile_analysis(app_names: List[str], network_type: str = 'wifi') -> Dict[str, Any]:
    """
    Effectue une analyse rapide des applications spécifiées
    
    Args:
        app_names: Liste des noms d'applications à analyser
        network_type: Type de connexion réseau ('wifi', '4g', '3g', '2g')
    
    Returns:
        Rapport d'analyse
    """
    analyzer = MobileAutoAnalyzer()
    
    # Configurer en fonction du réseau
    analyzer.adjust_for_network_conditions(network_type)
    
    # Simuler des analyses d'applications
    app_analyses = []
    for app_name in app_names:
        # Simulation de données d'applications pour démonstration
        app_type = random.choice(['user', 'system', 'network', 'security'])
        permissions = random.sample([
            'INTERNET', 'CAMERA', 'LOCATION', 'STORAGE', 
            'CONTACTS', 'MICROPHONE', 'CALENDAR', 'ADMIN'
        ], k=random.randint(1, 5))
        
        app_analysis = analyzer.analyze_installed_app(app_name, app_type, permissions)
        app_analyses.append(app_analysis)
    
    # Vérifier les mises à jour système
    update_status = analyzer.check_system_updates()
    
    # Générer un rapport complet
    report = analyzer.generate_mobile_report(app_analyses, update_status)
    
    return report

# Point d'entrée pour les tests
if __name__ == "__main__":
    # Exemple d'applications à analyser
    test_apps = ['Facebook', 'WhatsApp', 'Camera', 'Maps', 'SecurityApp']
    
    # Exécuter une analyse rapide
    report = quick_mobile_analysis(test_apps)
    
    # Afficher les résultats
    print(f"Score de sécurité global: {report['overall_security_score']}")
    print(f"Statut: {report['security_status']}")
    print(f"Applications analysées: {report['apps_analyzed']}")
    print(f"Applications à haut risque: {report['high_risk_count']}")
    
    if report.get('critical_actions'):
        print("\nActions critiques:")
        for action in report['critical_actions']:
            print(f"- {action['title']}")
            for detail in action['details']:
                print(f"  * {detail}")
    
    if report.get('ai_global_analysis'):
        print("\nAnalyse IA globale:")
        print(report['ai_global_analysis'])
