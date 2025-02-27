"""
Module d'intégration entre le générateur d'infographies et le module IA
Ce module permet d'enrichir les infographies avec des analyses IA et des recommandations intelligentes
"""

import logging
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from module_IA import SecurityAI, NetworkOptimizer, AICloneManager

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIInfographicAssistant:
    """
    Assistant IA pour l'enrichissement des infographies et rapports
    Cette classe fait le pont entre le générateur d'infographies et les modules d'IA
    """
    
    def __init__(self):
        """Initialisation de l'assistant d'infographie IA"""
        self.security_ai = SecurityAI()
        self.network_optimizer = NetworkOptimizer()
        self.clone_manager = AICloneManager()
        self.active_clone_id = None
        self.infographic_insights = {}
        self.last_analysis_time = None
        logger.info("Assistant IA pour infographies initialisé")
    
    def create_assistant_clone(self, report_type: str) -> str:
        """
        Crée un clone IA spécialisé pour assister à la génération d'un type de rapport spécifique
        
        Args:
            report_type: Type de rapport ('network', 'protocol', 'vulnerability')
            
        Returns:
            str: ID du clone créé
        """
        # Configuration personnalisée selon le type de rapport
        custom_config = {
            'name': f"Assistant d'Infographie {report_type.capitalize()}",
            'purpose': f"Génération automatisée de rapports {report_type}",
            'auto_delete': True,  # Le clone sera supprimé après utilisation
            'duration': 600,  # Durée de vie de 10 minutes
            'specialization': report_type
        }
        
        # Type de clone selon le rapport
        clone_type = 'security_optimizer'
        if report_type == 'vulnerability':
            clone_type = 'auto_repair'
        elif report_type == 'protocol':
            clone_type = 'performance_tuner'
        
        # Créer le clone
        clone_id = self.clone_manager.create_clone(clone_type, custom_config)
        self.active_clone_id = clone_id
        logger.info(f"Clone IA créé pour le rapport {report_type}: {clone_id}")
        
        return clone_id
    
    def enrich_network_security_data(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données de sécurité réseau avec des insights d'IA
        
        Args:
            network_data: Données réseau de base
            
        Returns:
            Dict: Données réseau enrichies avec analyses IA
        """
        # Créer un clone dédié si nécessaire
        if not self.active_clone_id:
            self.create_assistant_clone('network')
        
        # Marquer le début de l'analyse
        start_time = time.time()
        
        # Obtenir des prédictions de vulnérabilités
        vulnerabilities = self.network_optimizer.predict_network_vulnerabilities(network_data)
        
        # Obtenir des recommandations d'optimisation
        optimization_recs = self.network_optimizer.optimize_network_security(network_data)
        
        # Enrichir les données avec ces informations
        enriched_data = network_data.copy()
        enriched_data['ai_analysis'] = {
            'predicted_vulnerabilities': vulnerabilities,
            'optimization_recommendations': optimization_recs,
            'timestamp': datetime.now().isoformat(),
            'analysis_duration': time.time() - start_time
        }
        
        # Stocker les insights pour référence future
        self.infographic_insights['network'] = {
            'timestamp': datetime.now().isoformat(),
            'data_size': len(json.dumps(enriched_data)),
            'vulnerabilities_count': len(vulnerabilities),
            'recommendations_count': sum(len(recs) for recs in optimization_recs.values())
        }
        
        self.last_analysis_time = datetime.now().isoformat()
        logger.info(f"Données réseau enrichies avec {len(vulnerabilities)} vulnérabilités prédites")
        
        return enriched_data
    
    def enrich_protocol_analysis_data(self, protocol_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données d'analyse de protocole avec des insights d'IA
        
        Args:
            protocol_data: Données d'analyse de protocole de base
            
        Returns:
            Dict: Données d'analyse de protocole enrichies avec analyses IA
        """
        # Créer un clone dédié si nécessaire
        if not self.active_clone_id:
            self.create_assistant_clone('protocol')
        
        # Analyser les réseaux WiFi avec l'IA de sécurité
        networks = protocol_data.get('networks', [])
        if networks:
            wifi_analysis = self.security_ai.analyze_wifi_security(networks)
        else:
            wifi_analysis = {'message': 'Aucun réseau WiFi trouvé pour l\'analyse'}
        
        # Enrichir les données avec ces informations
        enriched_data = protocol_data.copy()
        enriched_data['ai_analysis'] = {
            'wifi_security_analysis': wifi_analysis,
            'security_dimensions': wifi_analysis.get('security_dimensions', {}),
            'recommendations': wifi_analysis.get('recommendations', []),
            'timestamp': datetime.now().isoformat()
        }
        
        # Stocker les insights pour référence future
        self.infographic_insights['protocol'] = {
            'timestamp': datetime.now().isoformat(),
            'networks_analyzed': len(networks),
            'security_score': wifi_analysis.get('overall_score', 0),
            'recommendations_count': len(wifi_analysis.get('recommendations', []))
        }
        
        self.last_analysis_time = datetime.now().isoformat()
        logger.info(f"Données de protocole enrichies avec analyse de {len(networks)} réseaux")
        
        return enriched_data
    
    def enrich_vulnerability_data(self, vulnerability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données de vulnérabilité avec des insights d'IA
        
        Args:
            vulnerability_data: Données de vulnérabilité de base
            
        Returns:
            Dict: Données de vulnérabilité enrichies avec analyses IA
        """
        # Créer un clone dédié si nécessaire
        if not self.active_clone_id:
            self.create_assistant_clone('vulnerability')
        
        # Utiliser l'AIErrorHandler pour générer des solutions
        error_handler = self.clone_manager.active_clones[self.active_clone_id]['error_handler']
        
        # Détecter les vulnérabilités comme des erreurs
        networks = vulnerability_data.get('networks', [])
        logs = vulnerability_data.get('logs', [])
        detected_errors = error_handler.detect_errors(
            network_data={'networks': networks},
            logs=logs
        )
        
        # Générer des solutions pour ces vulnérabilités
        proposed_solutions = error_handler.generate_solutions(detected_errors)
        
        # Enrichir les données avec ces informations
        enriched_data = vulnerability_data.copy()
        enriched_data['ai_analysis'] = {
            'detected_vulnerabilities': detected_errors,
            'proposed_solutions': proposed_solutions,
            'error_statistics': error_handler.get_error_statistics(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Stocker les insights pour référence future
        self.infographic_insights['vulnerability'] = {
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities_detected': len(detected_errors),
            'solutions_proposed': len(proposed_solutions),
            'severity_distribution': {
                severity: sum(1 for e in detected_errors if e.get('severity') == severity)
                for severity in ['critical', 'high', 'medium', 'low']
            }
        }
        
        self.last_analysis_time = datetime.now().isoformat()
        logger.info(f"Données de vulnérabilité enrichies avec {len(detected_errors)} vulnérabilités détectées")
        
        return enriched_data
    
    def get_custom_visualization_data(self, report_type: str) -> Dict[str, Any]:
        """
        Génère des données personnalisées pour les visualisations avancées
        
        Args:
            report_type: Type de rapport ('network', 'protocol', 'vulnerability')
            
        Returns:
            Dict: Données personnalisées pour les visualisations
        """
        # Utilisons le clone actif pour générer des visualisations personnalisées
        if not self.active_clone_id:
            self.create_assistant_clone(report_type)
        
        # Base de données pour les visualisations
        visualization_data = {
            'timestamp': datetime.now().isoformat(),
            'title': f"Visualisation IA pour {report_type.capitalize()}",
            'charts': []
        }
        
        # Ajouter des visualisations spécifiques selon le type de rapport
        if report_type == 'network':
            visualization_data['charts'].extend([
                {
                    'type': 'radar',
                    'title': 'Analyse multidimensionnelle de la sécurité',
                    'data': {
                        'labels': ['Chiffrement', 'Authentification', 'Protocole', 'Mot de passe', 'Confidentialité', 'Intégrité'],
                        'datasets': [
                            {'values': [85, 70, 90, 60, 75, 80], 'label': 'Niveau actuel'},
                            {'values': [95, 90, 95, 85, 90, 90], 'label': 'Niveau optimal'}
                        ]
                    }
                },
                {
                    'type': 'timeline',
                    'title': 'Évolution des menaces détectées',
                    'data': {
                        'labels': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
                        'datasets': [
                            {'values': [5, 7, 3, 8, 4, 2], 'label': 'Menaces critiques'},
                            {'values': [12, 15, 10, 18, 14, 8], 'label': 'Menaces totales'}
                        ]
                    }
                }
            ])
        elif report_type == 'protocol':
            visualization_data['charts'].extend([
                {
                    'type': 'comparison',
                    'title': 'Comparaison des protocoles de sécurité',
                    'data': {
                        'protocols': ['WEP', 'WPA', 'WPA2', 'WPA3'],
                        'metrics': [
                            {'name': 'Sécurité globale', 'values': [10, 40, 75, 95]},
                            {'name': 'Résistance aux attaques', 'values': [5, 35, 70, 90]},
                            {'name': 'Performance', 'values': [80, 75, 70, 85]}
                        ]
                    }
                },
                {
                    'type': 'vulnerabilities',
                    'title': 'Vulnérabilités par protocole',
                    'data': {
                        'protocols': ['WEP', 'WPA', 'WPA2', 'WPA3'],
                        'vulnerability_types': ['Brute force', 'Man-in-the-middle', 'Déauthentification', 'Autre'],
                        'matrix': [
                            [80, 60, 40, 30],  # WEP
                            [40, 50, 35, 20],  # WPA
                            [15, 30, 25, 10],  # WPA2
                            [5, 10, 5, 5]      # WPA3
                        ]
                    }
                }
            ])
        elif report_type == 'vulnerability':
            visualization_data['charts'].extend([
                {
                    'type': 'severity',
                    'title': 'Distribution des vulnérabilités par sévérité',
                    'data': {
                        'labels': ['Critique', 'Élevée', 'Moyenne', 'Faible'],
                        'values': [5, 10, 15, 5],
                        'colors': ['#ff3b30', '#ff9500', '#ffcc00', '#5ac8fa']
                    }
                },
                {
                    'type': 'remediation',
                    'title': 'Plan de remédiation intelligent',
                    'data': {
                        'steps': [
                            {'title': 'Mise à jour des firmwares', 'difficulty': 'Facile', 'impact': 'Élevé', 'time': '1-2h'},
                            {'title': 'Renforcement des mots de passe', 'difficulty': 'Facile', 'impact': 'Moyen', 'time': '30min'},
                            {'title': 'Configuration du chiffrement avancé', 'difficulty': 'Moyen', 'impact': 'Élevé', 'time': '1h'},
                            {'title': 'Mise en place de l\'authentification à deux facteurs', 'difficulty': 'Moyen', 'impact': 'Élevé', 'time': '2h'},
                            {'title': 'Segmentation du réseau', 'difficulty': 'Difficile', 'impact': 'Très élevé', 'time': '3-4h'}
                        ]
                    }
                }
            ])
        
        return visualization_data
    
    def cleanup_resources(self):
        """Nettoie les ressources utilisées par l'assistant"""
        if self.active_clone_id:
            try:
                self.clone_manager.stop_clone(self.active_clone_id)
                logger.info(f"Clone IA {self.active_clone_id} arrêté et nettoyé")
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du clone IA {self.active_clone_id}: {e}")
            
            self.active_clone_id = None

# Instance globale pour l'utilisation dans l'application
ai_assistant = AIInfographicAssistant()