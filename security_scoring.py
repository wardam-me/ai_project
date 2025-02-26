"""
Module de notation de sécurité des appareils en temps réel
"""
import os
import json
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DeviceSecurityScoring:
    """Système de notation de sécurité des appareils en temps réel"""
    
    def __init__(self):
        """Initialise le système de notation de sécurité"""
        self.devices = []
        
        # Créer le dossier de données si nécessaire
        os.makedirs('instance', exist_ok=True)
        
        # Charger les données des appareils
        self.load_devices()
        
        # Si aucune donnée n'est disponible, générer des exemples
        if not self.devices:
            self._generate_sample_devices()
    
    def load_devices(self):
        """Charge les données des appareils"""
        try:
            if os.path.exists('instance/devices_security.json'):
                with open('instance/devices_security.json', 'r') as f:
                    self.devices = json.load(f)
                logger.info("Données de sécurité des appareils chargées")
            else:
                logger.info("Aucun fichier de données d'appareils existant")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données d'appareils: {e}")
    
    def save_devices(self):
        """Sauvegarde les données des appareils"""
        try:
            with open('instance/devices_security.json', 'w') as f:
                json.dump(self.devices, f, indent=2)
            logger.info("Données de sécurité des appareils sauvegardées")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données d'appareils: {e}")
    
    def detect_devices(self):
        """
        Détecte les appareils sur le réseau
        Dans une version réelle, cela utiliserait des outils comme ARP, nmap, etc.
        Pour cette démonstration, nous générons des données d'exemple
        """
        # Simulation: 10% de chance de détecter un nouvel appareil
        if random.random() < 0.1:
            self._add_random_device()
        
        # Mise à jour aléatoire du statut des appareils existants
        for device in self.devices:
            self._update_device_status(device['mac_address'])
    
    def _generate_sample_devices(self):
        """Génère des exemples d'appareils pour la démonstration"""
        # Les données de base sont déjà générées dans network_topology.py
        # Ici nous ajoutons seulement des informations de sécurité supplémentaires
        
        # Routeur principal
        router = {
            'mac_address': '00:11:22:33:44:55',
            'security_score': 85,
            'security_issues': [
                {
                    'id': 'ISSUE-001',
                    'description': 'Firmware obsolète',
                    'severity': 'medium',
                    'solution': 'Mettre à jour le firmware vers la dernière version disponible'
                },
                {
                    'id': 'ISSUE-002',
                    'description': 'UPnP activé',
                    'severity': 'low',
                    'solution': 'Désactiver UPnP dans les paramètres du routeur'
                }
            ],
            'recommendations': [
                'Mettre à jour le firmware du routeur',
                'Désactiver UPnP pour une meilleure sécurité',
                'Activer le pare-feu intégré'
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        # Ordinateur portable
        laptop = {
            'mac_address': '66:77:88:99:AA:BB',
            'security_score': 75,
            'security_issues': [
                {
                    'id': 'ISSUE-003',
                    'description': 'Antivirus non à jour',
                    'severity': 'medium',
                    'solution': 'Mettre à jour l\'antivirus'
                }
            ],
            'recommendations': [
                'Mettre à jour les logiciels de sécurité',
                'Activer le pare-feu Windows',
                'Utiliser un VPN pour les connexions publiques'
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        # Smartphone
        phone = {
            'mac_address': 'CC:DD:EE:FF:00:11',
            'security_score': 65,
            'security_issues': [
                {
                    'id': 'ISSUE-004',
                    'description': 'Applications non mises à jour',
                    'severity': 'medium',
                    'solution': 'Mettre à jour toutes les applications'
                },
                {
                    'id': 'ISSUE-005',
                    'description': 'Connexion à des réseaux publics fréquente',
                    'severity': 'medium',
                    'solution': 'Utiliser un VPN sur les réseaux publics'
                }
            ],
            'recommendations': [
                'Activer les mises à jour automatiques',
                'Installer un gestionnaire de mots de passe',
                'Utiliser un VPN sur les réseaux publics'
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        # Caméra IP
        camera = {
            'mac_address': '22:33:44:55:66:77',
            'security_score': 35,
            'security_issues': [
                {
                    'id': 'ISSUE-006',
                    'description': 'Mot de passe par défaut non modifié',
                    'severity': 'high',
                    'solution': 'Changer le mot de passe par défaut'
                },
                {
                    'id': 'ISSUE-007',
                    'description': 'Firmware obsolète',
                    'severity': 'high',
                    'solution': 'Mettre à jour le firmware'
                },
                {
                    'id': 'ISSUE-008',
                    'description': 'Connexion non chiffrée',
                    'severity': 'high',
                    'solution': 'Activer HTTPS/TLS pour l\'accès à la caméra'
                }
            ],
            'recommendations': [
                'Changer immédiatement le mot de passe par défaut',
                'Mettre à jour le firmware',
                'Placer la caméra dans un réseau isolé',
                'Désactiver l\'accès à distance si non nécessaire'
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        # Télévision intelligente
        tv = {
            'mac_address': '88:99:AA:BB:CC:DD',
            'security_score': 55,
            'security_issues': [
                {
                    'id': 'ISSUE-009',
                    'description': 'Firmware non mis à jour',
                    'severity': 'medium',
                    'solution': 'Mettre à jour le firmware de la télévision'
                },
                {
                    'id': 'ISSUE-010',
                    'description': 'Suivi publicitaire activé',
                    'severity': 'low',
                    'solution': 'Désactiver le suivi publicitaire dans les paramètres'
                }
            ],
            'recommendations': [
                'Mettre à jour le firmware de la télévision',
                'Désactiver les fonctionnalités de suivi et de collecte de données',
                'Considérer l\'utilisation d\'un boîtier multimédia externe plus sécurisé'
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        # Ajouter les appareils à la liste
        self.devices = [router, laptop, phone, camera, tv]
        
        # Sauvegarder les données
        self.save_devices()
    
    def _add_random_device(self):
        """Ajoute un appareil aléatoire pour simuler une nouvelle détection"""
        device_types = ['printer', 'tablet', 'laptop', 'desktop', 'smartphone', 'iot']
        device_type = random.choice(device_types)
        
        mac_address = self._generate_random_mac()
        
        # Vérifier si l'appareil existe déjà
        if any(d['mac_address'] == mac_address for d in self.devices):
            return
        
        device = {
            'mac_address': mac_address,
            'security_score': random.randint(30, 90),
            'security_issues': self._generate_random_security_issues(device_type),
            'recommendations': [
                'Mettre à jour le système d\'exploitation',
                'Vérifier les paramètres de sécurité',
                'Installer un antivirus'
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        self.devices.append(device)
        self.save_devices()
        logger.info(f"Nouvel appareil détecté et ajouté: {mac_address}")
    
    def _generate_random_mac(self):
        """Génère une adresse MAC aléatoire"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    def _generate_random_security_issues(self, device_type):
        """Génère des problèmes de sécurité aléatoires basés sur le type d'appareil"""
        issues = []
        severities = ['low', 'medium', 'high']
        
        # Nombre de problèmes basé sur le type d'appareil
        if device_type == 'iot':
            num_issues = random.randint(2, 4)  # Les appareils IoT ont souvent plus de problèmes
        else:
            num_issues = random.randint(0, 2)
        
        for i in range(num_issues):
            issue_id = f"ISSUE-{random.randint(100, 999)}"
            severity = random.choice(severities)
            
            if device_type == 'iot':
                descriptions = [
                    'Mot de passe par défaut non modifié',
                    'Firmware obsolète',
                    'Connexion non chiffrée',
                    'Ports inutiles ouverts',
                    'Communications non sécurisées'
                ]
            elif device_type in ['laptop', 'desktop']:
                descriptions = [
                    'Système d\'exploitation non mis à jour',
                    'Antivirus non à jour',
                    'Pare-feu désactivé',
                    'Vulnérabilités logicielles détectées'
                ]
            else:
                descriptions = [
                    'Applications non mises à jour',
                    'Connexion à des réseaux publics fréquente',
                    'Suivi de localisation activé',
                    'Bluetooth toujours activé'
                ]
            
            description = random.choice(descriptions)
            solution = f"Résoudre le problème: {description}"
            
            issues.append({
                'id': issue_id,
                'description': description,
                'severity': severity,
                'solution': solution
            })
        
        return issues
    
    def _update_device_status(self, mac_address):
        """Met à jour aléatoirement le statut d'un appareil pour simuler des changements"""
        for device in self.devices:
            if device['mac_address'] == mac_address:
                # 5% de chance de changer le score de sécurité
                if random.random() < 0.05:
                    variation = random.randint(-5, 5)
                    device['security_score'] = max(0, min(100, device['security_score'] + variation))
                    device['last_updated'] = datetime.now().isoformat()
                    
                    # Si le score a changé, mettre à jour les recommandations
                    self._update_device_recommendations(mac_address)
                    
                    self.save_devices()
                    logger.info(f"Score de sécurité mis à jour pour {mac_address}: {device['security_score']}")
                return
    
    def calculate_device_score(self, mac_address):
        """Calcule le score de sécurité pour un appareil spécifique"""
        device = self.get_device(mac_address)
        if not device:
            return None
        
        # Dans une implémentation réelle, ce calcul serait basé sur de nombreux facteurs
        # Pour cette démo, nous utilisons simplement le score existant avec une légère variation
        score = device.get('security_score', 50)
        variation = random.randint(-3, 3)
        new_score = max(0, min(100, score + variation))
        
        # Mise à jour du score
        device['security_score'] = new_score
        device['last_updated'] = datetime.now().isoformat()
        self.save_devices()
        
        return new_score
    
    def _update_device_recommendations(self, mac_address):
        """Met à jour les recommandations de sécurité basées sur les problèmes détectés"""
        device = self.get_device(mac_address)
        if not device:
            return
        
        recommendations = []
        issues = device.get('security_issues', [])
        
        # Générer des recommandations basées sur les problèmes
        for issue in issues:
            if issue['severity'] == 'high':
                recommendations.append(f"URGENT: {issue['solution']}")
            else:
                recommendations.append(issue['solution'])
        
        # Ajouter quelques recommandations générales
        general_recommendations = [
            'Effectuer régulièrement des mises à jour de sécurité',
            'Utiliser des mots de passe forts et uniques',
            'Activer l\'authentification à deux facteurs lorsque disponible',
            'Surveiller régulièrement l\'activité réseau'
        ]
        
        # Ajouter 1-2 recommandations générales aléatoires
        for _ in range(random.randint(1, 2)):
            rec = random.choice(general_recommendations)
            if rec not in recommendations:
                recommendations.append(rec)
        
        device['recommendations'] = recommendations
    
    def get_device(self, mac_address):
        """Récupère les détails d'un appareil spécifique"""
        for device in self.devices:
            if device['mac_address'] == mac_address:
                return device
        return None
    
    def get_all_device_scores(self):
        """Récupère tous les appareils avec leurs scores de sécurité"""
        return [{
            'mac_address': device['mac_address'],
            'security_score': device['security_score'],
            'last_updated': device['last_updated']
        } for device in self.devices]
    
    def get_network_security_status(self):
        """Récupère un résumé du statut de sécurité du réseau"""
        if not self.devices:
            return {
                'overall_score': 0,
                'device_count': 0,
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'low_risk_count': 0,
                'last_updated': datetime.now().isoformat()
            }
        
        # Calcul des statistiques
        scores = [device['security_score'] for device in self.devices]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        high_risk = sum(1 for score in scores if score < 50)
        medium_risk = sum(1 for score in scores if 50 <= score < 80)
        low_risk = sum(1 for score in scores if score >= 80)
        
        return {
            'overall_score': round(overall_score, 1),
            'device_count': len(self.devices),
            'high_risk_count': high_risk,
            'medium_risk_count': medium_risk,
            'low_risk_count': low_risk,
            'last_updated': datetime.now().isoformat()
        }