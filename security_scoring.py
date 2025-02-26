"""
Module de notation de sécurité des appareils en temps réel
pour l'application d'analyse de réseaux WiFi.
"""

import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path
import random
import uuid

logger = logging.getLogger(__name__)

# Configuration du stockage
CONFIG_DIR = os.path.expanduser("~/.network_detect")
DEVICES_FILE = os.path.join(CONFIG_DIR, "connected_devices.json")
SCORES_FILE = os.path.join(CONFIG_DIR, "security_scores.json")

class SecurityScoring:
    """Système de notation de sécurité des appareils en temps réel"""
    
    def __init__(self):
        """Initialise le système de notation de sécurité"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.load_devices()
        self.load_scores()
        
    def load_devices(self):
        """Charge la liste des appareils connectés"""
        if os.path.exists(DEVICES_FILE):
            try:
                with open(DEVICES_FILE, "r") as file:
                    self.devices = json.load(file)
            except json.JSONDecodeError:
                logger.error("Fichier d'appareils corrompu, création d'un nouveau fichier")
                self.devices = []
                self.save_devices()
        else:
            self.devices = []
            self.save_devices()
            
    def save_devices(self):
        """Sauvegarde la liste des appareils connectés"""
        with open(DEVICES_FILE, "w") as file:
            json.dump(self.devices, file, indent=2)
            
    def load_scores(self):
        """Charge les scores de sécurité des appareils"""
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, "r") as file:
                    self.scores = json.load(file)
            except json.JSONDecodeError:
                logger.error("Fichier de scores corrompu, création d'un nouveau fichier")
                self.scores = {}
                self.save_scores()
        else:
            self.scores = {}
            self.save_scores()
            
    def save_scores(self):
        """Sauvegarde les scores de sécurité des appareils"""
        with open(SCORES_FILE, "w") as file:
            json.dump(self.scores, file, indent=2)
    
    def detect_devices(self, network_data=None):
        """
        Détecte les appareils connectés au réseau
        
        Pour l'instant, cette fonction génère des données de test, 
        mais elle pourrait être connectée à une API réseau réelle.
        """
        # Dans une implémentation réelle, on utiliserait des outils comme nmap, 
        # arp-scan, ou des API de routeurs pour détecter les appareils
        
        # Conserver les appareils existants et en ajouter de nouveaux si nécessaire
        existing_mac_addresses = {device["mac_address"] for device in self.devices}
        
        # Dans une version de démonstration, générer quelques appareils aléatoires
        if not self.devices or random.random() < 0.3:  # 30% de chance d'ajouter un nouvel appareil
            new_device = self._generate_test_device(existing_mac_addresses)
            if new_device:
                self.devices.append(new_device)
                # Initialiser le score pour ce nouvel appareil
                self.calculate_device_score(new_device["mac_address"])
        
        # Mettre à jour les informations des appareils existants
        for device in self.devices:
            # Simuler des changements dans les valeurs de sécurité
            if random.random() < 0.2:  # 20% de chance de mise à jour
                self._update_test_device(device)
                # Recalculer le score après la mise à jour
                self.calculate_device_score(device["mac_address"])
        
        # Sauvegarder les modifications
        self.save_devices()
        self.save_scores()
        
        return self.devices
    
    def _generate_test_device(self, existing_mac_addresses):
        """Génère un appareil de test avec des valeurs aléatoires"""
        # Types d'appareils possibles
        device_types = [
            "Smartphone", "Laptop", "Tablet", "Smart TV", "IoT Device", 
            "Security Camera", "Gaming Console", "Smart Speaker"
        ]
        
        # Fabricants d'appareils possibles
        manufacturers = [
            "Apple", "Samsung", "Google", "Sony", "Microsoft", 
            "Huawei", "Xiaomi", "LG", "Amazon", "Lenovo"
        ]
        
        # Systèmes d'exploitation possibles
        os_types = [
            "iOS", "Android", "Windows", "macOS", "Linux", 
            "Custom Firmware", "RTOS", "Other"
        ]
        
        # Versions de firmware possibles
        firmware_versions = [
            "Latest", "Outdated", "Very Outdated", "Unknown"
        ]
        
        # Statuts de mise à jour possibles
        update_statuses = [
            "Up to date", "Updates available", "Critical updates needed", "Unknown"
        ]
        
        # Vulnérabilités connues possibles
        known_vulnerabilities = [
            "None detected", "Outdated SSL", "Open ports", "Default credentials",
            "Unpatched CVE", "Weak encryption", "Multiple vulnerabilities"
        ]
        
        # Génération d'adresse MAC aléatoire
        while True:
            mac_parts = ["%02x" % random.randint(0, 255) for _ in range(6)]
            mac_address = ":".join(mac_parts).upper()
            if mac_address not in existing_mac_addresses:
                break
        
        # Déterminer le nom d'appareil basé sur le type et le fabricant
        device_type = random.choice(device_types)
        manufacturer = random.choice(manufacturers)
        device_name = f"{manufacturer} {device_type}"
        
        # Valeurs de sécurité
        firmware_version = random.choice(firmware_versions)
        update_status = random.choice(update_statuses)
        vulnerability = random.choice(known_vulnerabilities)
        
        # Autres détails de l'appareil
        ip_parts = [str(random.randint(1, 254)) for _ in range(4)]
        ip_address = ".".join(ip_parts)
        
        # Détails de connexion
        first_seen = datetime.now().isoformat()
        
        # Créer l'appareil
        device = {
            "mac_address": mac_address,
            "device_name": device_name,
            "device_type": device_type,
            "manufacturer": manufacturer,
            "os_type": random.choice(os_types),
            "ip_address": ip_address,
            "first_seen": first_seen,
            "last_seen": first_seen,
            "security_details": {
                "firmware_version": firmware_version,
                "update_status": update_status,
                "known_vulnerabilities": vulnerability,
                "open_ports": random.randint(0, 5),
                "encryption_level": random.choice(["Strong", "Medium", "Weak", "None"]),
                "password_protected": random.choice([True, False]),
                "firewall_enabled": random.choice([True, False]),
                "suspicious_activity": random.choice([True, False]),
            }
        }
        
        return device
    
    def _update_test_device(self, device):
        """Met à jour les valeurs de sécurité d'un appareil de test"""
        # Mettre à jour la dernière date de visualisation
        device["last_seen"] = datetime.now().isoformat()
        
        # Mettre à jour aléatoirement certaines valeurs de sécurité
        security = device["security_details"]
        
        # Choisir aléatoirement une valeur à modifier
        update_field = random.choice([
            "firmware_version", "update_status", "known_vulnerabilities",
            "open_ports", "encryption_level", "password_protected",
            "firewall_enabled", "suspicious_activity"
        ])
        
        if update_field == "firmware_version":
            security["firmware_version"] = random.choice([
                "Latest", "Outdated", "Very Outdated", "Unknown"
            ])
        elif update_field == "update_status":
            security["update_status"] = random.choice([
                "Up to date", "Updates available", "Critical updates needed", "Unknown"
            ])
        elif update_field == "known_vulnerabilities":
            security["known_vulnerabilities"] = random.choice([
                "None detected", "Outdated SSL", "Open ports", "Default credentials",
                "Unpatched CVE", "Weak encryption", "Multiple vulnerabilities"
            ])
        elif update_field == "open_ports":
            security["open_ports"] = max(0, security["open_ports"] + random.choice([-1, 0, 1, 2]))
        elif update_field == "encryption_level":
            security["encryption_level"] = random.choice(["Strong", "Medium", "Weak", "None"])
        elif update_field == "password_protected":
            security["password_protected"] = not security["password_protected"]
        elif update_field == "firewall_enabled":
            security["firewall_enabled"] = not security["firewall_enabled"]
        elif update_field == "suspicious_activity":
            security["suspicious_activity"] = not security["suspicious_activity"]
    
    def calculate_device_score(self, mac_address):
        """
        Calcule le score de sécurité pour un appareil spécifique
        
        Le score est sur 100, où 100 est le plus sécurisé
        """
        # Trouver l'appareil par adresse MAC
        device = next((d for d in self.devices if d["mac_address"] == mac_address), None)
        if not device:
            return None
        
        # Base du score
        score = 100
        security = device["security_details"]
        
        # Déductions basées sur le firmware
        if security["firmware_version"] == "Outdated":
            score -= 10
        elif security["firmware_version"] == "Very Outdated":
            score -= 25
        elif security["firmware_version"] == "Unknown":
            score -= 15
        
        # Déductions basées sur le statut de mise à jour
        if security["update_status"] == "Updates available":
            score -= 5
        elif security["update_status"] == "Critical updates needed":
            score -= 20
        elif security["update_status"] == "Unknown":
            score -= 10
        
        # Déductions basées sur les vulnérabilités connues
        if security["known_vulnerabilities"] != "None detected":
            if security["known_vulnerabilities"] == "Multiple vulnerabilities":
                score -= 30
            elif security["known_vulnerabilities"] in ["Unpatched CVE", "Default credentials", "Weak encryption"]:
                score -= 25
            else:
                score -= 15
        
        # Déductions basées sur les ports ouverts
        score -= security["open_ports"] * 5
        
        # Déductions basées sur le niveau de chiffrement
        if security["encryption_level"] == "Medium":
            score -= 10
        elif security["encryption_level"] == "Weak":
            score -= 25
        elif security["encryption_level"] == "None":
            score -= 40
        
        # Déductions si pas de protection par mot de passe
        if not security["password_protected"]:
            score -= 20
        
        # Déductions si pas de pare-feu
        if not security["firewall_enabled"]:
            score -= 15
        
        # Déductions pour activité suspecte
        if security["suspicious_activity"]:
            score -= 25
        
        # Limiter le score entre 0 et 100
        score = max(0, min(100, score))
        
        # Stocker le score avec un timestamp
        self.scores[mac_address] = {
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "history": self.scores.get(mac_address, {}).get("history", []) + [{
                "score": score,
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        # Limiter l'historique à 50 entrées
        if len(self.scores[mac_address]["history"]) > 50:
            self.scores[mac_address]["history"] = self.scores[mac_address]["history"][-50:]
        
        # Sauvegarder les scores
        self.save_scores()
        
        return score
    
    def get_device_score(self, mac_address):
        """Récupère le score de sécurité pour un appareil spécifique"""
        return self.scores.get(mac_address, {}).get("score", 0)
    
    def get_all_device_scores(self):
        """Récupère tous les scores de sécurité des appareils"""
        # Mettre à jour les scores pour s'assurer qu'ils sont à jour
        for device in self.devices:
            self.calculate_device_score(device["mac_address"])
        
        # Récupérer les données d'appareil avec leurs scores
        devices_with_scores = []
        for device in self.devices:
            mac = device["mac_address"]
            device_copy = device.copy()
            device_copy["security_score"] = self.scores.get(mac, {}).get("score", 0)
            device_copy["score_timestamp"] = self.scores.get(mac, {}).get("timestamp", "")
            device_copy["score_history"] = self.scores.get(mac, {}).get("history", [])
            devices_with_scores.append(device_copy)
        
        return devices_with_scores
    
    def get_network_security_status(self):
        """
        Récupère l'état de sécurité global du réseau
        
        Retourne un dictionnaire avec:
        - score_global: Score moyen de tous les appareils
        - appareils_critiques: Nombre d'appareils avec un score < 50
        - appareils_attention: Nombre d'appareils avec un score entre 50 et 70
        - appareils_securises: Nombre d'appareils avec un score > 70
        - derniere_mise_a_jour: Timestamp de la dernière mise à jour
        """
        devices_with_scores = self.get_all_device_scores()
        
        if not devices_with_scores:
            return {
                "score_global": 0,
                "appareils_critiques": 0,
                "appareils_attention": 0,
                "appareils_securises": 0,
                "derniere_mise_a_jour": datetime.now().isoformat(),
                "total_appareils": 0
            }
        
        # Calculer les statistiques
        scores = [device["security_score"] for device in devices_with_scores]
        global_score = sum(scores) / len(scores) if scores else 0
        
        # Compter les appareils par niveau de sécurité
        critical_devices = sum(1 for score in scores if score < 50)
        warning_devices = sum(1 for score in scores if 50 <= score <= 70)
        secure_devices = sum(1 for score in scores if score > 70)
        
        return {
            "score_global": round(global_score, 1),
            "appareils_critiques": critical_devices,
            "appareils_attention": warning_devices,
            "appareils_securises": secure_devices,
            "derniere_mise_a_jour": datetime.now().isoformat(),
            "total_appareils": len(devices_with_scores)
        }

# Instance globale du système de notation de sécurité
security_scoring = SecurityScoring()
