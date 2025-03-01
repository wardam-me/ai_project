#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module pour la génération de la roue colorée des menaces réseau
Ce module permet de générer et de manipuler les données pour la visualisation 
'Playful Network Threat Color Wheel'
"""

import json
import os
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

class ThreatColorWheel:
    """
    Classe qui gère la roue colorée des menaces réseau.
    Permet de visualiser les différentes catégories de menaces de manière ludique
    et interactive, avec des couleurs associées à chaque type de menace.
    """
    
    def __init__(self, data_file: str = 'instance/threat_wheel_data.json'):
        """
        Initialise la roue colorée des menaces
        
        Args:
            data_file: Chemin vers le fichier de données de la roue (par défaut: 'instance/threat_wheel_data.json')
        """
        self.data_file = data_file
        self.threat_categories = {
            "malware": {
                "name": "Malware",
                "color": "#FF5252",  # Rouge vif
                "icon": "bug",
                "description": "Logiciels malveillants conçus pour infiltrer, endommager ou prendre le contrôle des systèmes",
                "threats": []
            },
            "phishing": {
                "name": "Phishing",
                "color": "#FF9800",  # Orange
                "icon": "fishing",
                "description": "Tentatives d'obtenir des informations sensibles en se faisant passer pour une entité de confiance",
                "threats": []
            },
            "intrusion": {
                "name": "Intrusion",
                "color": "#FFEB3B",  # Jaune
                "icon": "door-open",
                "description": "Accès non autorisés aux systèmes, réseaux ou données",
                "threats": []
            },
            "dos": {
                "name": "Déni de service",
                "color": "#8BC34A",  # Vert clair
                "icon": "power-off",
                "description": "Attaques visant à rendre un service indisponible en surchargeant les ressources",
                "threats": []
            },
            "wifi": {
                "name": "Attaques WiFi",
                "color": "#03A9F4",  # Bleu clair
                "icon": "wifi",
                "description": "Attaques spécifiques aux réseaux sans fil comme le MITM, l'evil twin, etc.",
                "threats": []
            },
            "crypto": {
                "name": "Cryptographique",
                "color": "#673AB7",  # Violet
                "icon": "lock",
                "description": "Attaques ciblant les mécanismes de chiffrement et d'authentification",
                "threats": []
            },
            "data": {
                "name": "Vol de données",
                "color": "#E91E63",  # Rose
                "icon": "database",
                "description": "Exfiltration ou vol de données sensibles ou personnelles",
                "threats": []
            },
            "physical": {
                "name": "Physique",
                "color": "#795548",  # Marron
                "icon": "shield-alt",
                "description": "Menaces impliquant un accès physique aux appareils ou infrastructures",
                "threats": []
            }
        }
        self.load_data()
    
    def load_data(self) -> None:
        """Charge les données de la roue depuis le fichier, ou génère des données de démonstration"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Mettre à jour les catégories avec les données chargées
                for category, category_data in data.items():
                    if category in self.threat_categories:
                        self.threat_categories[category]["threats"] = category_data.get("threats", [])
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement des données: {e}")
                self._generate_demo_data()
        else:
            self._generate_demo_data()
    
    def save_data(self) -> None:
        """Sauvegarde les données de la roue dans le fichier"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.threat_categories, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde des données: {e}")
    
    def _generate_demo_data(self) -> None:
        """Génère des données de démonstration pour la roue"""
        threats_by_category = {
            "malware": [
                "Virus", "Trojan", "Ransomware", "Spyware", "Worm",
                "Adware", "Keylogger", "Rootkit", "Backdoor", "Botnet"
            ],
            "phishing": [
                "Email Phishing", "Spear Phishing", "Whaling", "Smishing", "Vishing",
                "Social Engineering", "Fake Websites", "Clone Phishing", "Pharming", "Business Email Compromise"
            ],
            "intrusion": [
                "Brute Force", "Dictionary Attack", "Password Spraying", "Credential Stuffing", "Session Hijacking",
                "MitM Attack", "SQL Injection", "XSS", "CSRF", "API Abuse"
            ],
            "dos": [
                "DDoS", "SYN Flood", "HTTP Flood", "Ping of Death", "Smurf Attack",
                "Amplification Attack", "Slowloris", "RUDY Attack", "NTP Amplification", "DNS Amplification"
            ],
            "wifi": [
                "Evil Twin", "Rogue AP", "Deauthentication", "WPA Cracking", "KRACK Attack",
                "Jamming", "WiFi Sniffing", "Karma Attack", "Wardriving", "WPS Attacks"
            ],
            "crypto": [
                "MITM", "Replay Attack", "Hash Collision", "Weak Key Attack", "Padding Oracle",
                "Side-Channel Attack", "Timing Attack", "SSL Stripping", "Certificate Spoofing", "Quantum Computing Threat"
            ],
            "data": [
                "Data Breach", "Data Exfiltration", "Espionage", "Insider Threat", "Backup Theft",
                "SIM Swapping", "Memory Scraping", "Web Scraping", "Device Theft", "Unencrypted Storage"
            ],
            "physical": [
                "Hardware Tampering", "USB Drop Attack", "Card Skimming", "Dumpster Diving", "Shoulder Surfing",
                "CCTV Blind Spots", "RAM Theft", "Physical Server Access", "Badge Copying", "Social Tailgating"
            ]
        }
        
        # Générer des menaces aléatoires pour chaque catégorie
        for category, threats in threats_by_category.items():
            self.threat_categories[category]["threats"] = []
            
            # Nombre aléatoire de menaces entre 3 et 7
            num_threats = random.randint(3, 7)
            selected_threats = random.sample(threats, num_threats)
            
            for threat in selected_threats:
                severity = random.randint(1, 10)
                frequency = random.randint(1, 100)
                last_seen_days = random.randint(0, 30)
                
                self.threat_categories[category]["threats"].append({
                    "name": threat,
                    "severity": severity,
                    "frequency": frequency,
                    "last_seen": (datetime.now().replace(microsecond=0, second=0, minute=0) \
                                  - timedelta(days=last_seen_days)).isoformat(),
                    "description": f"Description de la menace {threat}",
                    "size": 20 + (severity * frequency / 10)  # Taille du segment dans la roue
                })
        
        self.save_data()
    
    def get_wheel_data(self) -> Dict[str, Any]:
        """
        Récupère les données formatées pour la visualisation de la roue
        
        Returns:
            Dict[str, Any]: Données formatées pour la visualisation
        """
        wheel_data = {
            "categories": [],
            "threats": []
        }
        
        for category_id, category in self.threat_categories.items():
            wheel_data["categories"].append({
                "id": category_id,
                "name": category["name"],
                "color": category["color"],
                "icon": category["icon"],
                "description": category["description"]
            })
            
            for threat in category["threats"]:
                wheel_data["threats"].append({
                    "name": threat["name"],
                    "category": category_id,
                    "color": category["color"],
                    "severity": threat["severity"],
                    "frequency": threat["frequency"],
                    "size": threat["size"],
                    "description": threat.get("description", ""),
                    "lastSeen": threat.get("last_seen", "")
                })
        
        return wheel_data
    
    def add_threat(self, category_id: str, threat_data: Dict[str, Any]) -> bool:
        """
        Ajoute une nouvelle menace à une catégorie
        
        Args:
            category_id: Identifiant de la catégorie
            threat_data: Données de la menace à ajouter
            
        Returns:
            bool: True si l'ajout a réussi, False sinon
        """
        if category_id not in self.threat_categories:
            return False
        
        # Valider les données minimales requises
        required_fields = ["name", "severity", "frequency"]
        if not all(field in threat_data for field in required_fields):
            return False
        
        # Ajouter des champs par défaut si manquants
        if "last_seen" not in threat_data:
            threat_data["last_seen"] = datetime.now().isoformat()
        
        if "size" not in threat_data:
            severity = threat_data["severity"]
            frequency = threat_data["frequency"]
            threat_data["size"] = 20 + (severity * frequency / 10)
        
        # Ajouter la menace à la catégorie
        self.threat_categories[category_id]["threats"].append(threat_data)
        self.save_data()
        return True
    
    def update_threat(self, category_id: str, threat_name: str, updated_data: Dict[str, Any]) -> bool:
        """
        Met à jour une menace existante
        
        Args:
            category_id: Identifiant de la catégorie
            threat_name: Nom de la menace à mettre à jour
            updated_data: Nouvelles données pour la menace
            
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if category_id not in self.threat_categories:
            return False
        
        # Trouver la menace par son nom
        for i, threat in enumerate(self.threat_categories[category_id]["threats"]):
            if threat["name"] == threat_name:
                # Mettre à jour les données
                self.threat_categories[category_id]["threats"][i].update(updated_data)
                
                # Recalculer la taille si nécessaire
                if "severity" in updated_data or "frequency" in updated_data:
                    severity = self.threat_categories[category_id]["threats"][i]["severity"]
                    frequency = self.threat_categories[category_id]["threats"][i]["frequency"]
                    self.threat_categories[category_id]["threats"][i]["size"] = 20 + (severity * frequency / 10)
                
                self.save_data()
                return True
        
        return False
    
    def remove_threat(self, category_id: str, threat_name: str) -> bool:
        """
        Supprime une menace existante
        
        Args:
            category_id: Identifiant de la catégorie
            threat_name: Nom de la menace à supprimer
            
        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        if category_id not in self.threat_categories:
            return False
        
        # Trouver la menace par son nom
        for i, threat in enumerate(self.threat_categories[category_id]["threats"]):
            if threat["name"] == threat_name:
                # Supprimer la menace
                del self.threat_categories[category_id]["threats"][i]
                self.save_data()
                return True
        
        return False
    
    def get_threat_stats(self) -> Dict[str, Any]:
        """
        Calcule les statistiques globales des menaces
        
        Returns:
            Dict[str, Any]: Statistiques des menaces
        """
        stats = {
            "total_threats": 0,
            "avg_severity": 0,
            "max_severity": 0,
            "recent_threats": 0,  # Menaces vues au cours des 7 derniers jours
            "category_distribution": {},
            "severity_distribution": {
                "low": 0,      # 1-3
                "medium": 0,   # 4-7
                "high": 0      # 8-10
            }
        }
        
        total_severity = 0
        now = datetime.now()
        
        # Initialiser la distribution par catégorie
        for category_id in self.threat_categories:
            stats["category_distribution"][category_id] = 0
        
        # Calculer les statistiques
        for category_id, category in self.threat_categories.items():
            for threat in category["threats"]:
                stats["total_threats"] += 1
                stats["category_distribution"][category_id] += 1
                
                # Cumuler la sévérité
                severity = threat["severity"]
                total_severity += severity
                stats["max_severity"] = max(stats["max_severity"], severity)
                
                # Classifier par niveau de sévérité
                if severity <= 3:
                    stats["severity_distribution"]["low"] += 1
                elif severity <= 7:
                    stats["severity_distribution"]["medium"] += 1
                else:
                    stats["severity_distribution"]["high"] += 1
                
                # Vérifier si la menace est récente
                if "last_seen" in threat:
                    try:
                        last_seen = datetime.fromisoformat(threat["last_seen"])
                        days_ago = (now - last_seen).days
                        if days_ago <= 7:
                            stats["recent_threats"] += 1
                    except (ValueError, TypeError):
                        pass
        
        # Calculer la sévérité moyenne
        if stats["total_threats"] > 0:
            stats["avg_severity"] = round(total_severity / stats["total_threats"], 2)
        
        return stats

# Fonction pour obtenir une instance de ThreatColorWheel
def get_threat_wheel():
    """
    Récupère une instance de la roue des menaces
    
    Returns:
        ThreatColorWheel: Instance de la roue des menaces
    """
    return ThreatColorWheel()