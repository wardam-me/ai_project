"""
Module de notation de sécurité des appareils en temps réel
"""
import os
import json
import logging
import time
import random
from datetime import datetime

# Configuration
CONFIG_DIR = os.path.expanduser("~/.network_detect")
DEVICE_DATA_FILE = os.path.join(CONFIG_DIR, 'devices.json')

# Logging
logger = logging.getLogger(__name__)

class DeviceSecurityScoring:
    """Système de notation de sécurité des appareils en temps réel"""
    
    def __init__(self):
        """Initialise le système de notation de sécurité"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.devices = {}
        self.load_devices()
    
    def load_devices(self):
        """Charge les données des appareils"""
        if os.path.exists(DEVICE_DATA_FILE):
            try:
                with open(DEVICE_DATA_FILE, 'r') as file:
                    self.devices = json.load(file)
                logger.info(f"Données de {len(self.devices)} appareils chargées")
            except Exception as e:
                logger.error(f"Erreur lors du chargement des données d'appareils: {e}")
                self.devices = {}
        else:
            logger.info("Aucun fichier de données d'appareils existant")
            self.devices = {}
    
    def save_devices(self):
        """Sauvegarde les données des appareils"""
        try:
            with open(DEVICE_DATA_FILE, 'w') as file:
                json.dump(self.devices, file, indent=2)
            logger.info(f"Données de {len(self.devices)} appareils sauvegardées")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données d'appareils: {e}")
    
    def detect_devices(self):
        """
        Détecte les appareils sur le réseau
        Dans une version réelle, cela utiliserait des outils comme ARP, nmap, etc.
        Pour cette démonstration, nous générons des données d'exemple
        """
        # Pour la démonstration, créons quelques appareils simulés si aucun n'existe
        if not self.devices:
            self._generate_sample_devices()
        else:
            # Simuler la détection de nouveaux appareils (1 chance sur 5)
            if random.random() < 0.2:
                self._add_random_device()
            
            # Simuler la mise à jour des appareils existants
            for mac_address in list(self.devices.keys()):
                device = self.devices[mac_address]
                device['last_seen'] = datetime.now().isoformat()
                
                # Simuler des changements aléatoires de statut pour certains appareils
                if random.random() < 0.3:
                    self._update_device_status(mac_address)
        
        self.save_devices()
        return list(self.devices.values())
    
    def _generate_sample_devices(self):
        """Génère des exemples d'appareils pour la démonstration"""
        device_types = ["Smartphone", "Laptop", "Smart TV", "IoT Device", "Router", "Tablet"]
        manufacturers = ["Samsung", "Apple", "Huawei", "Sony", "LG", "TP-Link", "Xiaomi"]
        
        for i in range(5):
            mac_address = self._generate_random_mac()
            device_type = random.choice(device_types)
            manufacturer = random.choice(manufacturers)
            
            self.devices[mac_address] = {
                'mac_address': mac_address,
                'ip_address': f"192.168.1.{random.randint(10, 250)}",
                'device_type': device_type,
                'manufacturer': manufacturer,
                'hostname': f"{manufacturer.lower()}-{device_type.lower()}-{random.randint(1, 999)}",
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'security_score': random.randint(30, 95),
                'security_issues': self._generate_random_security_issues(device_type),
                'recommendations': []
            }
            
            # Ajouter des recommandations basées sur les problèmes de sécurité
            self._update_device_recommendations(mac_address)
    
    def _add_random_device(self):
        """Ajoute un appareil aléatoire pour simuler une nouvelle détection"""
        device_types = ["Smartphone", "Laptop", "Smart TV", "IoT Device", "Router", "Tablet"]
        manufacturers = ["Samsung", "Apple", "Huawei", "Sony", "LG", "TP-Link", "Xiaomi"]
        
        mac_address = self._generate_random_mac()
        
        # Ne pas ajouter si ce MAC existe déjà
        if mac_address in self.devices:
            return
        
        device_type = random.choice(device_types)
        manufacturer = random.choice(manufacturers)
        
        self.devices[mac_address] = {
            'mac_address': mac_address,
            'ip_address': f"192.168.1.{random.randint(10, 250)}",
            'device_type': device_type,
            'manufacturer': manufacturer,
            'hostname': f"{manufacturer.lower()}-{device_type.lower()}-{random.randint(1, 999)}",
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'security_score': random.randint(30, 95),
            'security_issues': self._generate_random_security_issues(device_type),
            'recommendations': []
        }
        
        # Ajouter des recommandations basées sur les problèmes de sécurité
        self._update_device_recommendations(mac_address)
        
        logger.info(f"Nouvel appareil détecté: {manufacturer} {device_type}")
    
    def _generate_random_mac(self):
        """Génère une adresse MAC aléatoire"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    def _generate_random_security_issues(self, device_type):
        """Génère des problèmes de sécurité aléatoires basés sur le type d'appareil"""
        issues = []
        
        # Problèmes potentiels basés sur le type d'appareil
        potential_issues = {
            'firmware_version': {
                'status': random.choice(['up_to_date', 'outdated', 'very_outdated', 'unknown']),
                'impact': random.choice(['low', 'medium', 'high'])
            },
            'update_status': {
                'status': random.choice(['enabled', 'disabled', 'unknown']),
                'impact': random.choice(['low', 'medium', 'high'])
            },
            'vulnerabilities': {
                'status': random.choice(['none', 'some', 'many', 'unknown']),
                'impact': random.choice(['low', 'medium', 'high'])
            }
        }
        
        # Ajouter des problèmes spécifiques au type d'appareil
        if device_type == "Router":
            potential_issues['open_ports'] = {
                'status': random.choice(['few', 'many', 'too_many']),
                'impact': random.choice(['medium', 'high'])
            }
            potential_issues['encryption'] = {
                'status': random.choice(['strong', 'medium', 'weak', 'none']),
                'impact': 'high'
            }
        
        elif device_type in ["Smartphone", "Tablet", "Laptop"]:
            potential_issues['password_protection'] = {
                'status': random.choice(['enabled', 'disabled', 'weak', 'unknown']),
                'impact': random.choice(['medium', 'high'])
            }
            potential_issues['encryption'] = {
                'status': random.choice(['enabled', 'partial', 'disabled']),
                'impact': random.choice(['medium', 'high'])
            }
        
        elif device_type == "IoT Device":
            potential_issues['default_password'] = {
                'status': random.choice(['changed', 'not_changed', 'unknown']),
                'impact': 'high'
            }
            potential_issues['firmware_version'] = {
                'status': 'very_outdated',  # Les IoT ont souvent un firmware obsolète
                'impact': 'high'
            }
        
        # Ajouter des problèmes génériques
        potential_issues['firewall'] = {
            'status': random.choice(['enabled', 'disabled', 'partial', 'unknown']),
            'impact': random.choice(['medium', 'high'])
        }
        
        potential_issues['suspicious_activity'] = {
            'status': random.choice(['none', 'detected', 'unknown']),
            'impact': random.choice(['medium', 'high'])
        }
        
        # Convertir le dictionnaire en liste d'objets pour l'API
        for issue_type, details in potential_issues.items():
            issues.append({
                'type': issue_type,
                'status': details['status'],
                'impact': details['impact']
            })
        
        return issues
    
    def _update_device_status(self, mac_address):
        """Met à jour aléatoirement le statut d'un appareil pour simuler des changements"""
        if mac_address not in self.devices:
            return
        
        device = self.devices[mac_address]
        
        # Chance de changer un problème de sécurité existant
        if device['security_issues'] and random.random() < 0.5:
            issue_index = random.randint(0, len(device['security_issues']) - 1)
            issue = device['security_issues'][issue_index]
            
            # Possibilité d'amélioration ou de dégradation
            if issue['type'] == 'firmware_version':
                issue['status'] = random.choice(['up_to_date', 'outdated', 'very_outdated'])
            elif issue['type'] == 'update_status':
                issue['status'] = random.choice(['enabled', 'disabled'])
            elif issue['type'] == 'encryption':
                issue['status'] = random.choice(['strong', 'medium', 'weak', 'none'])
            elif issue['type'] == 'password_protection':
                issue['status'] = random.choice(['enabled', 'disabled', 'weak'])
            elif issue['type'] == 'suspicious_activity':
                issue['status'] = random.choice(['none', 'detected'])
        
        # Recalculer le score de sécurité
        self.calculate_device_score(mac_address)
        
        # Mettre à jour les recommandations
        self._update_device_recommendations(mac_address)
    
    def calculate_device_score(self, mac_address):
        """Calcule le score de sécurité pour un appareil spécifique"""
        if mac_address not in self.devices:
            return
        
        device = self.devices[mac_address]
        base_score = 100
        
        # Réduire le score en fonction des problèmes de sécurité
        for issue in device['security_issues']:
            penalty = 0
            
            # Pénalité en fonction du type et du statut du problème
            if issue['type'] == 'firmware_version':
                if issue['status'] == 'outdated':
                    penalty = 10
                elif issue['status'] == 'very_outdated':
                    penalty = 20
                elif issue['status'] == 'unknown':
                    penalty = 5
            
            elif issue['type'] == 'update_status':
                if issue['status'] == 'disabled':
                    penalty = 15
                elif issue['status'] == 'unknown':
                    penalty = 5
            
            elif issue['type'] == 'vulnerabilities':
                if issue['status'] == 'some':
                    penalty = 15
                elif issue['status'] == 'many':
                    penalty = 30
                elif issue['status'] == 'unknown':
                    penalty = 10
            
            elif issue['type'] == 'open_ports':
                if issue['status'] == 'many':
                    penalty = 15
                elif issue['status'] == 'too_many':
                    penalty = 25
            
            elif issue['type'] == 'encryption':
                if issue['status'] == 'medium':
                    penalty = 15
                elif issue['status'] == 'weak':
                    penalty = 25
                elif issue['status'] == 'none':
                    penalty = 40
                elif issue['status'] == 'partial':
                    penalty = 20
            
            elif issue['type'] == 'password_protection':
                if issue['status'] == 'disabled':
                    penalty = 30
                elif issue['status'] == 'weak':
                    penalty = 20
                elif issue['status'] == 'unknown':
                    penalty = 15
            
            elif issue['type'] == 'default_password':
                if issue['status'] == 'not_changed':
                    penalty = 40
                elif issue['status'] == 'unknown':
                    penalty = 20
            
            elif issue['type'] == 'firewall':
                if issue['status'] == 'disabled':
                    penalty = 25
                elif issue['status'] == 'partial':
                    penalty = 10
                elif issue['status'] == 'unknown':
                    penalty = 15
            
            elif issue['type'] == 'suspicious_activity':
                if issue['status'] == 'detected':
                    penalty = 35
                elif issue['status'] == 'unknown':
                    penalty = 10
            
            # Ajuster la pénalité en fonction de l'impact
            if issue['impact'] == 'low':
                penalty = max(1, int(penalty * 0.7))
            elif issue['impact'] == 'high':
                penalty = int(penalty * 1.3)
            
            base_score -= penalty
        
        # S'assurer que le score est dans la plage [0, 100]
        device['security_score'] = max(0, min(100, base_score))
        
        logger.debug(f"Score de sécurité calculé pour {mac_address}: {device['security_score']}")
        return device['security_score']
    
    def _update_device_recommendations(self, mac_address):
        """Met à jour les recommandations de sécurité basées sur les problèmes détectés"""
        if mac_address not in self.devices:
            return
        
        device = self.devices[mac_address]
        recommendations = []
        
        # Générer des recommandations basées sur les problèmes
        for issue in device['security_issues']:
            if issue['type'] == 'firmware_version' and issue['status'] in ['outdated', 'very_outdated']:
                recommendations.append('rec_update_firmware')
            
            elif issue['type'] == 'update_status' and issue['status'] == 'disabled':
                recommendations.append('rec_install_updates')
            
            elif issue['type'] == 'vulnerabilities' and issue['status'] in ['some', 'many']:
                recommendations.append('rec_address_vulnerabilities')
            
            elif issue['type'] == 'open_ports' and issue['status'] in ['many', 'too_many']:
                recommendations.append('rec_close_ports')
            
            elif issue['type'] == 'encryption' and issue['status'] in ['medium', 'weak', 'none', 'partial']:
                recommendations.append('rec_improve_encryption')
            
            elif issue['type'] == 'password_protection' and issue['status'] in ['disabled', 'weak']:
                recommendations.append('rec_enable_password')
            
            elif issue['type'] == 'default_password' and issue['status'] == 'not_changed':
                recommendations.append('rec_enable_password')
            
            elif issue['type'] == 'firewall' and issue['status'] in ['disabled', 'partial']:
                recommendations.append('rec_enable_firewall')
            
            elif issue['type'] == 'suspicious_activity' and issue['status'] == 'detected':
                recommendations.append('rec_check_suspicious')
        
        # Si aucun problème grave n'est détecté, ajouter une recommandation positive
        if device['security_score'] >= 80:
            recommendations.append('rec_device_secure')
        
        # Éliminer les doublons
        device['recommendations'] = list(set(recommendations))
    
    def get_device(self, mac_address):
        """Récupère les détails d'un appareil spécifique"""
        return self.devices.get(mac_address)
    
    def get_all_device_scores(self):
        """Récupère tous les appareils avec leurs scores de sécurité"""
        # Mettre à jour les appareils avant de les retourner
        self.detect_devices()
        
        return [
            {
                'mac_address': device['mac_address'],
                'hostname': device['hostname'],
                'device_type': device['device_type'],
                'manufacturer': device['manufacturer'],
                'ip_address': device['ip_address'],
                'security_score': device['security_score'],
                'last_seen': device['last_seen']
            }
            for mac_address, device in self.devices.items()
        ]
    
    def get_network_security_status(self):
        """Récupère un résumé du statut de sécurité du réseau"""
        devices = list(self.devices.values())
        
        if not devices:
            return {
                'global_score': 0,
                'critical_devices': 0,
                'warning_devices': 0,
                'secure_devices': 0,
                'security_distribution': {
                    'critical': 0,
                    'warning': 0,
                    'secure': 0
                }
            }
        
        # Compter les appareils par catégorie de score
        critical = sum(1 for d in devices if d['security_score'] < 50)
        warning = sum(1 for d in devices if 50 <= d['security_score'] < 80)
        secure = sum(1 for d in devices if d['security_score'] >= 80)
        
        # Calculer le score global du réseau
        if devices:
            global_score = sum(d['security_score'] for d in devices) / len(devices)
        else:
            global_score = 0
        
        return {
            'global_score': round(global_score),
            'critical_devices': critical,
            'warning_devices': warning,
            'secure_devices': secure,
            'security_distribution': {
                'critical': critical,
                'warning': warning,
                'secure': secure
            }
        }

# Instance globale du système de notation de sécurité
security_scoring = DeviceSecurityScoring()
