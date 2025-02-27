#!/usr/bin/env python3
"""
Assistant Intelligent d'Optimisation de Sécurité
Ce module combine le module IA avec l'assistant de sécurité pour offrir des
recommandations de sécurité personnalisées et intelligentes.
"""
import os
import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SecurityAssistant:
    """Assistant Intelligent d'Optimisation de Sécurité"""
    
    def __init__(self, security_ai, network_optimizer, assistant_securite):
        """
        Initialisation de l'assistant intelligent
        
        Args:
            security_ai: Instance de SecurityAI
            network_optimizer: Instance de NetworkOptimizer
            assistant_securite: Instance de AssistantSecurite
        """
        self.security_ai = security_ai
        self.network_optimizer = network_optimizer
        self.assistant_securite = assistant_securite
        self.optimization_history = []
        self.load_history()
        logger.info("SecurityAssistant initialisé")
    
    def load_history(self):
        """Charge l'historique des optimisations"""
        history_path = os.path.join('config', 'security_assistant_history.json')
        try:
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    self.optimization_history = json.load(f)
                logger.info(f"Historique de l'assistant chargé : {len(self.optimization_history)} entrées")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'historique de l'assistant : {e}")
            self.optimization_history = []
    
    def save_history(self):
        """Sauvegarde l'historique des optimisations"""
        history_path = os.path.join('config', 'security_assistant_history.json')
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        try:
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.optimization_history, f, indent=2)
            logger.info("Historique de l'assistant sauvegardé")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'historique de l'assistant : {e}")
    
    def generate_security_assessment(self, network_data: Dict[str, Any], wifi_networks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère une évaluation complète de la sécurité du réseau
        
        Args:
            network_data: Données du réseau (topologie, appareils, connexions)
            wifi_networks: Liste des réseaux WiFi détectés
            
        Returns:
            Dict: Évaluation complète de la sécurité
        """
        # Analyser le réseau avec NetworkOptimizer
        network_optimization = self.network_optimizer.optimize_network_security(network_data)
        
        # Analyser les réseaux WiFi avec SecurityAI
        wifi_analysis = self.security_ai.analyze_wifi_security(wifi_networks)
        
        # Calculer un score global combinant les deux analyses
        network_score = network_optimization.get('optimality_score', 0)
        wifi_score = wifi_analysis.get('overall_score', 0)
        
        # Pondération: 60% pour le réseau, 40% pour le WiFi
        global_score = (network_score * 0.6) + (wifi_score * 0.4)
        
        # Fusionner et prioriser les recommandations
        priority_recommendations = self._merge_prioritize_recommendations(
            network_optimization.get('recommendations', {}),
            wifi_analysis.get('recommendations', [])
        )
        
        # Générer un plan d'action en étapes
        action_plan = self._generate_action_plan(priority_recommendations)
        
        # Sauvegarder dans l'historique
        assessment_record = {
            'timestamp': datetime.now().isoformat(),
            'global_score': global_score,
            'network_score': network_score,
            'wifi_score': wifi_score,
            'devices_count': len(network_data.get('devices', [])),
            'networks_count': len(wifi_networks)
        }
        self.optimization_history.append(assessment_record)
        self.save_history()
        
        # Résultat final
        return {
            'timestamp': datetime.now().isoformat(),
            'global_score': global_score,
            'network_optimization': network_optimization,
            'wifi_analysis': wifi_analysis,
            'priority_recommendations': priority_recommendations,
            'action_plan': action_plan,
            'security_status': self._determine_security_status(global_score)
        }
    
    def _merge_prioritize_recommendations(self, network_recommendations: Dict[str, List], wifi_recommendations: List[Dict]) -> List[Dict]:
        """
        Fusionne et priorise les recommandations de sécurité
        
        Args:
            network_recommendations: Recommandations du NetworkOptimizer
            wifi_recommendations: Recommandations du SecurityAI
            
        Returns:
            List[Dict]: Liste fusionnée et priorisée des recommandations
        """
        all_recommendations = []
        
        # Ajouter les recommandations prioritaires du réseau
        if 'priority' in network_recommendations:
            for rec in network_recommendations['priority']:
                all_recommendations.append({
                    'source': 'network',
                    'priority': 'critical',
                    'title': rec.get('title', ''),
                    'description': rec.get('description', ''),
                    'action_items': [],
                    'affected_items': rec.get('affected_devices', [])
                })
        
        # Ajouter les recommandations moyennes du réseau
        if 'medium' in network_recommendations:
            for rec in network_recommendations['medium']:
                all_recommendations.append({
                    'source': 'network',
                    'priority': 'high',
                    'title': rec.get('title', ''),
                    'description': rec.get('description', ''),
                    'action_items': [],
                    'affected_items': rec.get('affected_devices', [])
                })
        
        # Ajouter les recommandations WiFi
        for rec in wifi_recommendations:
            all_recommendations.append({
                'source': 'wifi',
                'priority': rec.get('priority', 'medium'),
                'title': rec.get('title', ''),
                'description': rec.get('description', ''),
                'action_items': rec.get('action_items', []),
                'affected_items': []
            })
        
        # Trier par priorité (critical > high > medium > low)
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_recommendations = sorted(
            all_recommendations,
            key=lambda x: priority_order.get(x['priority'], 4)
        )
        
        return sorted_recommendations
    
    def _generate_action_plan(self, recommendations: List[Dict]) -> List[Dict]:
        """
        Génère un plan d'action étape par étape basé sur les recommandations
        
        Args:
            recommendations: Liste des recommandations priorisées
            
        Returns:
            List[Dict]: Plan d'action avec étapes ordonnées
        """
        action_plan = []
        step_number = 1
        
        # Regrouper les actions par priorité
        for priority in ['critical', 'high', 'medium', 'low']:
            priority_recs = [r for r in recommendations if r['priority'] == priority]
            
            for rec in priority_recs:
                # Si la recommandation a des actions spécifiques, les utiliser
                if rec['action_items']:
                    for action in rec['action_items']:
                        action_plan.append({
                            'step': step_number,
                            'priority': rec['priority'],
                            'action': action,
                            'context': rec['title'],
                            'estimated_time': self._estimate_action_time(action, rec['priority']),
                            'completion_impact': self._calculate_impact_score(rec['priority'])
                        })
                        step_number += 1
                # Sinon, créer une action basée sur la description
                else:
                    action_plan.append({
                        'step': step_number,
                        'priority': rec['priority'],
                        'action': f"Résoudre : {rec['title']}",
                        'context': rec['description'],
                        'estimated_time': self._estimate_action_time(rec['title'], rec['priority']),
                        'completion_impact': self._calculate_impact_score(rec['priority'])
                    })
                    step_number += 1
        
        return action_plan
    
    def _estimate_action_time(self, action: str, priority: str) -> str:
        """
        Estime le temps nécessaire pour compléter une action
        
        Args:
            action: Description de l'action
            priority: Priorité de l'action
            
        Returns:
            str: Estimation du temps (ex: "5-10 minutes")
        """
        # Estimation simplifiée basée sur la priorité et la longueur de l'action
        if priority == 'critical':
            base_time = 15
        elif priority == 'high':
            base_time = 10
        else:
            base_time = 5
        
        # Ajuster en fonction de la complexité apparente (longueur de la description)
        complexity_factor = min(3, max(1, len(action) // 50))
        min_time = base_time * complexity_factor
        max_time = min_time * 2
        
        # Formater l'estimation
        if min_time < 60:
            return f"{min_time}-{max_time} minutes"
        else:
            return f"{min_time // 60}-{max_time // 60} heures"
    
    def _calculate_impact_score(self, priority: str) -> int:
        """
        Calcule l'impact estimé de la résolution d'une action sur le score global
        
        Args:
            priority: Priorité de l'action
            
        Returns:
            int: Points d'impact estimés
        """
        if priority == 'critical':
            return random.randint(8, 15)
        elif priority == 'high':
            return random.randint(5, 10)
        elif priority == 'medium':
            return random.randint(3, 6)
        else:
            return random.randint(1, 3)
    
    def _determine_security_status(self, global_score: float) -> Dict[str, Any]:
        """
        Détermine le statut de sécurité global et génère un message d'état
        
        Args:
            global_score: Score global de sécurité
            
        Returns:
            Dict: Statut de sécurité avec niveau et message
        """
        if global_score >= 90:
            level = "excellent"
            message = "Votre réseau est très bien sécurisé. Continuez à maintenir ce niveau de sécurité."
            icon = "shield-check"
            color = "success"
        elif global_score >= 75:
            level = "bon"
            message = "Votre réseau a un bon niveau de sécurité. Quelques améliorations mineures sont recommandées."
            icon = "shield-plus"
            color = "info"
        elif global_score >= 60:
            level = "moyen"
            message = "Votre réseau présente quelques vulnérabilités. Des améliorations sont nécessaires."
            icon = "shield-exclamation"
            color = "warning"
        elif global_score >= 40:
            level = "faible"
            message = "Votre réseau présente des vulnérabilités importantes. Des actions urgentes sont nécessaires."
            icon = "shield-x"
            color = "danger"
        else:
            level = "critique"
            message = "Votre réseau présente des vulnérabilités critiques. Une action immédiate est requise."
            icon = "exclamation-triangle"
            color = "danger"
        
        return {
            'level': level,
            'message': message,
            'icon': icon,
            'color': color
        }
    
    def generate_chatbot_response(self, query: str, network_data: Dict[str, Any], wifi_networks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère une réponse personnalisée du chatbot intégrant l'IA
        
        Args:
            query: Question ou requête de l'utilisateur
            network_data: Données du réseau
            wifi_networks: Liste des réseaux WiFi
            
        Returns:
            Dict: Réponse du chatbot avec recommandations personnalisées
        """
        # Obtenir une réponse de base de l'assistant de sécurité
        base_response = self.assistant_securite.generate_response(query)
        
        # Analyser la requête pour déterminer si elle est liée à la sécurité
        security_related = any(keyword in query.lower() for keyword in 
                            ['sécurité', 'vulnérabilité', 'protection', 'danger', 
                             'menace', 'wifi', 'réseau', 'appareil', 'optimiser'])
        
        # Si la requête est liée à la sécurité, enrichir la réponse avec l'IA
        if security_related:
            # Obtenir une évaluation rapide
            network_score = self.network_optimizer.optimize_network_security(network_data).get('optimality_score', 0)
            wifi_score = self.security_ai.analyze_wifi_security(wifi_networks).get('overall_score', 0)
            global_score = (network_score * 0.6) + (wifi_score * 0.4)
            
            # Ajouter des informations personnalisées
            enriched_response = {
                'text': base_response,
                'security_assessment': {
                    'global_score': global_score,
                    'network_score': network_score,
                    'wifi_score': wifi_score,
                    'security_status': self._determine_security_status(global_score)
                },
                'has_enrichment': True
            }
            
            # Ajouter une recommandation prioritaire si disponible
            network_recs = self.network_optimizer.optimize_network_security(network_data).get('recommendations', {})
            wifi_recs = self.security_ai.analyze_wifi_security(wifi_networks).get('recommendations', [])
            
            priority_recs = self._merge_prioritize_recommendations(network_recs, wifi_recs)
            if priority_recs:
                enriched_response['top_recommendation'] = priority_recs[0]
            
            return enriched_response
        else:
            # Réponse standard sans enrichissement
            return {
                'text': base_response,
                'has_enrichment': False
            }
    
    def get_historical_trends(self) -> Dict[str, Any]:
        """
        Analyse les tendances historiques de sécurité
        
        Returns:
            Dict: Analyse des tendances avec évolution du score global
        """
        if not self.optimization_history or len(self.optimization_history) < 2:
            return {
                'has_enough_data': False,
                'message': "Pas assez de données historiques pour analyser les tendances."
            }
        
        # Extraire les scores et dates
        scores = []
        dates = []
        for entry in self.optimization_history:
            if 'global_score' in entry and 'timestamp' in entry:
                scores.append(entry['global_score'])
                try:
                    date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    dates.append(date.strftime('%d/%m/%Y'))
                except:
                    dates.append('Date inconnue')
        
        # Calculer l'évolution
        score_evolution = scores[-1] - scores[0]
        
        # Déterminer la tendance
        if score_evolution > 5:
            trend = "positive"
            message = "Votre sécurité s'améliore significativement au fil du temps."
        elif score_evolution > 0:
            trend = "slightly_positive"
            message = "Votre sécurité s'améliore légèrement au fil du temps."
        elif score_evolution > -5:
            trend = "stable"
            message = "Votre niveau de sécurité est relativement stable."
        else:
            trend = "negative"
            message = "Votre niveau de sécurité se dégrade. Action requise."
        
        return {
            'has_enough_data': True,
            'scores': scores,
            'dates': dates,
            'score_evolution': score_evolution,
            'trend': trend,
            'message': message
        }