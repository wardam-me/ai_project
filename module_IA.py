#!/usr/bin/env python3
"""
Module d'Intelligence Artificielle pour l'analyse de sécurité réseau
Ce module fournit des fonctionnalités avancées d'analyse et d'optimisation
"""
import os
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NetworkOptimizer:
    """Classe d'optimisation du réseau basée sur l'IA"""
    
    def __init__(self):
        """Initialisation de l'optimiseur réseau"""
        self.last_optimization = None
        self.optimization_history = []
        self.load_history()
        logger.info("NetworkOptimizer initialisé")
    
    def load_history(self):
        """Charge l'historique d'optimisation"""
        history_path = os.path.join('config', 'optimization_history.json')
        try:
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    self.optimization_history = json.load(f)
                logger.info(f"Historique d'optimisation chargé : {len(self.optimization_history)} entrées")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'historique d'optimisation : {e}")
            self.optimization_history = []
    
    def save_history(self):
        """Sauvegarde l'historique d'optimisation"""
        history_path = os.path.join('config', 'optimization_history.json')
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        try:
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.optimization_history, f, indent=2)
            logger.info("Historique d'optimisation sauvegardé")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'historique d'optimisation : {e}")
    
    def predict_network_vulnerabilities(self, network_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prédit les vulnérabilités potentielles d'un réseau en fonction des données
        
        Args:
            network_data: Données du réseau à analyser
            
        Returns:
            List[Dict]: Liste des vulnérabilités prédites avec leur probabilité
        """
        vulnerabilities = []
        
        # Analyse des appareils
        for device in network_data.get('devices', []):
            # Vérification des appareils non sécurisés
            if device.get('security_score', 100) < 50:
                vulnerabilities.append({
                    'device_mac': device.get('mac_address'),
                    'device_name': device.get('name', 'Appareil inconnu'),
                    'vulnerability_type': 'security_score_low',
                    'severity': 'high',
                    'probability': 0.9,
                    'description': f"Appareil avec un faible score de sécurité ({device.get('security_score')})",
                    'recommendation': "Vérifier et corriger les problèmes de sécurité de cet appareil"
                })
            
            # Vérification des firmwares obsolètes
            if device.get('firmware_updated') == False:
                vulnerabilities.append({
                    'device_mac': device.get('mac_address'),
                    'device_name': device.get('name', 'Appareil inconnu'),
                    'vulnerability_type': 'outdated_firmware',
                    'severity': 'medium',
                    'probability': 0.8,
                    'description': "Firmware obsolète détecté",
                    'recommendation': "Mettre à jour le firmware de l'appareil vers la dernière version"
                })
        
        # Analyse des connexions
        for connection in network_data.get('connections', []):
            # Vérification des connexions non chiffrées
            if connection.get('encrypted') == False:
                source_mac = connection.get('source')
                target_mac = connection.get('target')
                
                # Identification des appareils concernés
                source_device = next((d for d in network_data.get('devices', []) if d.get('mac_address') == source_mac), None)
                target_device = next((d for d in network_data.get('devices', []) if d.get('mac_address') == target_mac), None)
                
                source_name = source_device.get('name', 'Appareil inconnu') if source_device else 'Appareil inconnu'
                target_name = target_device.get('name', 'Appareil inconnu') if target_device else 'Appareil inconnu'
                
                vulnerabilities.append({
                    'connection_source': source_mac,
                    'connection_target': target_mac,
                    'source_name': source_name,
                    'target_name': target_name,
                    'vulnerability_type': 'unencrypted_connection',
                    'severity': 'high',
                    'probability': 0.85,
                    'description': f"Connexion non chiffrée entre {source_name} et {target_name}",
                    'recommendation': "Activer le chiffrement pour cette connexion ou utiliser un VPN"
                })
        
        # Enregistrement de l'optimisation
        self.last_optimization = {
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities_count': len(vulnerabilities),
            'network_size': len(network_data.get('devices', []))
        }
        self.optimization_history.append(self.last_optimization)
        self.save_history()
        
        return vulnerabilities
    
    def optimize_network_security(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère des recommandations pour optimiser la sécurité du réseau
        
        Args:
            network_data: Données du réseau à analyser
            
        Returns:
            Dict: Recommandations d'optimisation
        """
        # Prédiction des vulnérabilités
        vulnerabilities = self.predict_network_vulnerabilities(network_data)
        
        # Calcul des statistiques
        severity_counts = {
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'medium')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Génération du score d'optimalité
        total_devices = len(network_data.get('devices', []))
        weighted_vulns = (
            severity_counts.get('low', 0) * 1 +
            severity_counts.get('medium', 0) * 2 +
            severity_counts.get('high', 0) * 4 +
            severity_counts.get('critical', 0) * 8
        )
        
        optimality_score = max(0, 100 - (weighted_vulns / max(1, total_devices) * 10))
        
        # Classification des recommandations par priorité
        priority_recommendations = []
        medium_recommendations = []
        low_recommendations = []
        
        for vuln in vulnerabilities:
            rec = {
                'title': f"Corriger : {vuln.get('description')}",
                'description': vuln.get('recommendation'),
                'affected_devices': [vuln.get('device_name')] if 'device_name' in vuln else [vuln.get('source_name'), vuln.get('target_name')]
            }
            
            if vuln.get('severity') == 'high' or vuln.get('severity') == 'critical':
                priority_recommendations.append(rec)
            elif vuln.get('severity') == 'medium':
                medium_recommendations.append(rec)
            else:
                low_recommendations.append(rec)
        
        # Génération du résultat final
        result = {
            'optimality_score': optimality_score,
            'vulnerability_statistics': severity_counts,
            'recommendations': {
                'priority': priority_recommendations,
                'medium': medium_recommendations,
                'low': low_recommendations
            },
            'raw_vulnerabilities': vulnerabilities,
            'timestamp': datetime.now().isoformat()
        }
        
        return result

class SecurityAI:
    """Classe d'analyse de sécurité basée sur l'IA pour les réseaux WiFi"""
    
    def __init__(self):
        """Initialisation du moteur d'IA de sécurité"""
        self.network_optimizer = NetworkOptimizer()
        self.security_trends = []
        self.load_trends()
        logger.info("SecurityAI initialisé")
    
    def load_trends(self):
        """Charge les tendances de sécurité"""
        trends_path = os.path.join('config', 'security_trends.json')
        try:
            if os.path.exists(trends_path):
                with open(trends_path, 'r', encoding='utf-8') as f:
                    self.security_trends = json.load(f)
                logger.info(f"Tendances de sécurité chargées : {len(self.security_trends)} entrées")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des tendances de sécurité : {e}")
            self.security_trends = []
    
    def save_trends(self):
        """Sauvegarde les tendances de sécurité"""
        trends_path = os.path.join('config', 'security_trends.json')
        os.makedirs(os.path.dirname(trends_path), exist_ok=True)
        try:
            with open(trends_path, 'w', encoding='utf-8') as f:
                json.dump(self.security_trends, f, indent=2)
            logger.info("Tendances de sécurité sauvegardées")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des tendances de sécurité : {e}")
    
    def analyze_wifi_security(self, networks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse avancée de la sécurité des réseaux WiFi
        
        Args:
            networks: Liste des réseaux WiFi à analyser
            
        Returns:
            Dict: Résultats de l'analyse avec scores et recommandations
        """
        if not networks:
            return {
                'overall_score': 0,
                'networks_analyzed': 0,
                'security_levels': {},
                'recommendations': [],
                'timestamp': datetime.now().isoformat()
            }
        
        # Scores de sécurité par type de chiffrement
        security_scores = {
            'OPEN': 0,
            'WEP': 20,
            'WPA': 50,
            'WPA2': 80,
            'WPA2-Enterprise': 90,
            'WPA3': 95,
            'WPA3-Enterprise': 99
        }
        
        # Calculer les scores pour chaque réseau
        network_scores = []
        security_levels = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'secure': 0
        }
        
        for network in networks:
            # Extraire les informations de sécurité
            security_type = network.get('security', 'OPEN')
            encryption = network.get('encryption')
            authentication = network.get('authentication')
            
            # Déterminer le score de base
            base_score = security_scores.get(security_type, 0)
            
            # Ajustements basés sur l'encryption et l'authentification
            encryption_bonus = 0
            if encryption == 'AES' or encryption == 'CCMP':
                encryption_bonus = 10
            elif encryption == 'GCMP':
                encryption_bonus = 15
            elif encryption == 'TKIP':
                encryption_bonus = 5
            
            auth_bonus = 0
            if authentication == 'ENTERPRISE':
                auth_bonus = 10
            elif authentication == 'SAE':
                auth_bonus = 15
            elif authentication == 'OWE':
                auth_bonus = 12
            elif authentication == 'PSK':
                auth_bonus = 5
            
            # Score final (plafonné à 100)
            final_score = min(100, base_score + encryption_bonus + auth_bonus)
            
            # Déterminer le niveau de sécurité
            security_level = 'critical'
            if final_score >= 90:
                security_level = 'secure'
            elif final_score >= 70:
                security_level = 'low'
            elif final_score >= 50:
                security_level = 'medium'
            elif final_score >= 30:
                security_level = 'high'
            
            security_levels[security_level] = security_levels.get(security_level, 0) + 1
            
            # Enregistrer le score
            network_scores.append({
                'ssid': network.get('ssid', 'Réseau inconnu'),
                'bssid': network.get('bssid', '00:00:00:00:00:00'),
                'security_type': security_type,
                'encryption': encryption,
                'authentication': authentication,
                'security_score': final_score,
                'security_level': security_level
            })
        
        # Calcul du score global
        overall_score = sum(n['security_score'] for n in network_scores) / len(network_scores) if network_scores else 0
        
        # Générer des recommandations
        recommendations = self._generate_recommendations(network_scores, security_levels)
        
        # Enregistrer les tendances
        self.security_trends.append({
            'timestamp': datetime.now().isoformat(),
            'overall_score': overall_score,
            'networks_count': len(networks),
            'security_levels': security_levels
        })
        
        if len(self.security_trends) > 100:
            self.security_trends = self.security_trends[-100:]
        
        self.save_trends()
        
        # Générer les données du graphique radar
        security_dimensions = self._generate_security_dimensions(network_scores)
        
        # Résultat final
        result = {
            'overall_score': overall_score,
            'networks_analyzed': len(networks),
            'network_scores': network_scores,
            'security_levels': security_levels,
            'security_dimensions': security_dimensions,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _generate_recommendations(self, network_scores: List[Dict[str, Any]], security_levels: Dict[str, int]) -> List[Dict[str, Any]]:
        """
        Génère des recommandations basées sur l'analyse des réseaux
        
        Args:
            network_scores: Scores de sécurité des réseaux
            security_levels: Distribution des niveaux de sécurité
            
        Returns:
            List[Dict]: Liste des recommandations
        """
        recommendations = []
        
        # Recommandations pour les réseaux critiques et à haut risque
        critical_networks = [n for n in network_scores if n['security_level'] in ['critical', 'high']]
        if critical_networks:
            for network in critical_networks:
                if network['security_type'] == 'OPEN':
                    recommendations.append({
                        'priority': 'critical',
                        'title': f"Réseau ouvert : {network['ssid']}",
                        'description': "Ce réseau n'utilise aucun chiffrement. Il est fortement recommandé d'activer WPA2 ou WPA3 avec un mot de passe fort.",
                        'action_items': [
                            "Accédez à l'interface d'administration de votre routeur",
                            "Activez WPA2 ou WPA3 avec AES/CCMP",
                            "Définissez un mot de passe fort d'au moins 12 caractères"
                        ]
                    })
                elif network['security_type'] == 'WEP':
                    recommendations.append({
                        'priority': 'critical',
                        'title': f"Réseau WEP obsolète : {network['ssid']}",
                        'description': "WEP est un protocole obsolète qui peut être facilement piraté. Il est fortement recommandé de passer à WPA2 ou WPA3.",
                        'action_items': [
                            "Accédez à l'interface d'administration de votre routeur",
                            "Passez de WEP à WPA2 ou WPA3",
                            "Utilisez AES/CCMP pour le chiffrement",
                            "Définissez un nouveau mot de passe fort"
                        ]
                    })
                elif network['security_type'] == 'WPA':
                    recommendations.append({
                        'priority': 'high',
                        'title': f"Réseau WPA obsolète : {network['ssid']}",
                        'description': "WPA est un protocole vulnérable aux attaques. Il est recommandé de passer à WPA2 ou WPA3.",
                        'action_items': [
                            "Accédez à l'interface d'administration de votre routeur",
                            "Passez de WPA à WPA2 ou WPA3",
                            "Utilisez AES/CCMP au lieu de TKIP",
                            "Mettez à jour le firmware de votre routeur si possible"
                        ]
                    })
        
        # Recommandations générales basées sur la distribution des niveaux de sécurité
        if security_levels.get('critical', 0) + security_levels.get('high', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'title': "Réseaux à risque détectés",
                'description': f"Votre environnement contient {security_levels.get('critical', 0) + security_levels.get('high', 0)} réseaux à risque élevé qui nécessitent une attention immédiate.",
                'action_items': [
                    "Mettez à jour la configuration de sécurité des réseaux critiques",
                    "Envisagez d'utiliser WPA3 si votre matériel le prend en charge",
                    "Utilisez des mots de passe forts uniques pour chaque réseau"
                ]
            })
        
        if security_levels.get('medium', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'title': "Réseaux à sécurité moyenne détectés",
                'description': f"Votre environnement contient {security_levels.get('medium', 0)} réseaux à sécurité moyenne qui peuvent être améliorés.",
                'action_items': [
                    "Passez à des protocoles de sécurité plus récents",
                    "Vérifiez la force des mots de passe",
                    "Activez l'authentification à deux facteurs lorsque disponible"
                ]
            })
        
        # Recommandations pour améliorer la sécurité globale
        recommendations.append({
            'priority': 'standard',
            'title': "Bonnes pratiques de sécurité WiFi",
            'description': "Pour améliorer la sécurité générale de vos réseaux WiFi :",
            'action_items': [
                "Changez régulièrement vos mots de passe WiFi (au moins tous les 3 mois)",
                "Utilisez des SSID uniques qui ne révèlent pas d'informations personnelles",
                "Activez le filtrage MAC pour limiter l'accès aux appareils connus",
                "Désactivez WPS (WiFi Protected Setup) qui peut être vulnérable",
                "Mettez à jour régulièrement le firmware de vos routeurs et points d'accès"
            ]
        })
        
        return recommendations
    
    def _generate_security_dimensions(self, network_scores: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Génère les données pour le graphique radar des dimensions de sécurité
        
        Args:
            network_scores: Scores de sécurité des réseaux
            
        Returns:
            Dict[str, float]: Scores pour chaque dimension de sécurité
        """
        if not network_scores:
            return {
                "encryption": 0.0,
                "authentication": 0.0,
                "protocol": 0.0,
                "password": 0.0,
                "privacy": 0.0
            }
        
        # Initialisation des scores
        dimensions = {
            "encryption": 0,  # Force du chiffrement
            "authentication": 0,  # Méthodes d'authentification
            "protocol": 0,  # Version du protocole (WPA, WPA2, WPA3)
            "password": 0,  # Estimation de la robustesse des mots de passe
            "privacy": 0    # Protection de la vie privée (difussion SSID, etc.)
        }
        
        # Évaluation de l'encryption
        encryption_scores = {
            'AES': 90,
            'CCMP': 90,
            'GCMP': 95,
            'TKIP': 40,
            None: 0
        }
        
        # Évaluation de l'authentification
        auth_scores = {
            'ENTERPRISE': 90,
            'SAE': 95,
            'OWE': 85,
            'PSK': 70,
            None: 0
        }
        
        # Évaluation du protocole
        protocol_scores = {
            'OPEN': 0,
            'WEP': 10,
            'WPA': 30,
            'WPA2': 80,
            'WPA2-Enterprise': 90,
            'WPA3': 95,
            'WPA3-Enterprise': 99
        }
        
        # Calcul des scores pour chaque dimension
        for network in network_scores:
            security_type = network.get('security_type', 'OPEN')
            encryption = network.get('encryption')
            authentication = network.get('authentication')
            
            # Contribution au score d'encryption
            dimensions["encryption"] += encryption_scores.get(encryption, 0)
            
            # Contribution au score d'authentification
            dimensions["authentication"] += auth_scores.get(authentication, 0)
            
            # Contribution au score de protocole
            dimensions["protocol"] += protocol_scores.get(security_type, 0)
            
            # Estimation basique de la robustesse du mot de passe (simulation)
            # En réalité, on n'a pas accès au mot de passe
            if security_type in ['OPEN', 'WEP']:
                dimensions["password"] += 0
            elif security_type == 'WPA':
                dimensions["password"] += 50
            elif security_type == 'WPA2':
                dimensions["password"] += 70
            elif security_type == 'WPA3':
                dimensions["password"] += 90
            
            # Estimation de la confidentialité
            # Basée sur le type de réseau et le protocole
            if security_type == 'OPEN':
                dimensions["privacy"] += 0
            elif security_type == 'WEP':
                dimensions["privacy"] += 20
            elif security_type == 'WPA':
                dimensions["privacy"] += 40
            elif security_type == 'WPA2':
                dimensions["privacy"] += 70
            elif 'Enterprise' in security_type:
                dimensions["privacy"] += 90
            elif security_type == 'WPA3':
                dimensions["privacy"] += 85
        
        # Calcul des moyennes
        for dimension in dimensions:
            dimensions[dimension] = dimensions[dimension] / len(network_scores)
        
        return dimensions

# Point d'entrée pour les tests
if __name__ == "__main__":
    # Test du module
    security_ai = SecurityAI()
    network_optimizer = NetworkOptimizer()
    
    # Exemple de réseaux pour les tests
    test_networks = [
        {
            "ssid": "Réseau_Domicile",
            "bssid": "00:11:22:33:44:55",
            "security": "WPA2",
            "encryption": "AES",
            "authentication": "PSK",
            "strength": -65,
            "frequency": "2.4GHz",
            "channel": 6
        },
        {
            "ssid": "Réseau_Ancien",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "security": "WEP",
            "encryption": None,
            "authentication": None,
            "strength": -70,
            "frequency": "2.4GHz",
            "channel": 11
        }
    ]
    
    # Exemple de données de topologie pour les tests
    test_topology = {
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
            }
        ],
        "connections": [
            {
                "source": "00:11:22:33:44:55",
                "target": "AA:BB:CC:DD:EE:FF",
                "type": "wifi",
                "strength": -65,
                "encrypted": True
            }
        ]
    }
    
    # Test de l'analyse de sécurité WiFi
    wifi_analysis = security_ai.analyze_wifi_security(test_networks)
    print("Résultat de l'analyse WiFi :")
    print(f"Score global : {wifi_analysis['overall_score']:.2f}")
    print(f"Réseaux analysés : {wifi_analysis['networks_analyzed']}")
    print(f"Niveaux de sécurité : {wifi_analysis['security_levels']}")
    print(f"Recommandations : {len(wifi_analysis['recommendations'])}")
    
    # Test de l'optimisation réseau
    network_opt = network_optimizer.optimize_network_security(test_topology)
    print("\nRésultat de l'optimisation réseau :")
    print(f"Score d'optimalité : {network_opt['optimality_score']:.2f}")
    print(f"Statistiques de vulnérabilités : {network_opt['vulnerability_statistics']}")
    print(f"Recommandations prioritaires : {len(network_opt['recommendations']['priority'])}")
    
    print("\nModule d'IA testé avec succès !")