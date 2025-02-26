"""
Module de recommandations personnalisées basé sur l'historique d'analyse
pour l'application d'analyse de réseaux WiFi.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
import random

logger = logging.getLogger(__name__)

# Configuration du stockage
CONFIG_DIR = os.path.expanduser("~/.network_detect")
HISTORY_FILE = os.path.join(CONFIG_DIR, "analysis_history.json")
RECOMMENDATIONS_FILE = os.path.join(CONFIG_DIR, "personalized_recommendations.json")

class RecommendationSystem:
    """Système de recommandations personnalisées basé sur l'historique d'analyse"""

    def __init__(self):
        """Initialise le système de recommandations"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.load_history()

    def load_history(self):
        """Charge l'historique d'analyse"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as file:
                    self.history = json.load(file)
            except json.JSONDecodeError:
                logger.error("Fichier d'historique corrompu, création d'un nouveau fichier")
                self.history = {"user_actions": [], "generated_reports": [], "consulted_networks": []}
        else:
            self.history = {"user_actions": [], "generated_reports": [], "consulted_networks": []}

    def save_history(self):
        """Sauvegarde l'historique d'analyse"""
        with open(HISTORY_FILE, "w") as file:
            json.dump(self.history, file, indent=2)

    def add_action(self, action_type, action_data):
        """Ajoute une action à l'historique

        Args:
            action_type (str): Type d'action ('report_generated', 'network_analyzed', 'assistant_query')
            action_data (dict): Données associées à l'action
        """
        action = {
            "type": action_type,
            "data": action_data,
            "timestamp": datetime.now().isoformat()
        }

        # Ajouter l'action à la catégorie appropriée
        if action_type == "report_generated":
            self.history["generated_reports"].append(action)
        elif action_type == "network_analyzed":
            self.history["consulted_networks"].append(action)

        # Ajouter à la liste générale d'actions
        self.history["user_actions"].append(action)

        # Sauvegarder l'historique après chaque action
        self.save_history()

        # Générer de nouvelles recommandations
        self.generate_recommendations()

    def add_report_generation(self, report_name, networks_count, security_levels):
        """Ajoute une génération de rapport à l'historique"""
        self.add_action("report_generated", {
            "report_name": report_name,
            "networks_count": networks_count,
            "security_levels": security_levels
        })

    def add_network_analysis(self, network_ssid, security_level, recommendations):
        """Ajoute une analyse de réseau à l'historique"""
        self.add_action("network_analyzed", {
            "ssid": network_ssid,
            "security_level": security_level,
            "recommendations": recommendations
        })

    def generate_recommendations(self):
        """Génère des recommandations personnalisées basées sur l'historique"""
        recommendations = {
            "security_focus": self._get_security_focus(),
            "network_preferences": self._get_network_preferences(),
            "recommended_actions": self._get_recommended_actions(),
            "last_updated": datetime.now().isoformat()
        }

        # Sauvegarder les recommandations
        with open(RECOMMENDATIONS_FILE, "w") as file:
            json.dump(recommendations, file, indent=2)

        return recommendations

    def get_recommendations(self):
        """Récupère les recommandations personnalisées"""
        if os.path.exists(RECOMMENDATIONS_FILE):
            try:
                with open(RECOMMENDATIONS_FILE, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                logger.error("Fichier de recommandations corrompu")
                return self.generate_recommendations()
        else:
            return self.generate_recommendations()

    def _get_security_focus(self):
        """Détermine le focus de sécurité de l'utilisateur"""
        # Analyser les réseaux consultés pour déterminer le focus
        security_concerns = {
            "encryption": 0,
            "signal_strength": 0,
            "frequency": 0
        }

        # Parcourir l'historique des réseaux consultés
        for action in self.history["consulted_networks"]:
            if "recommendations" in action["data"]:
                for rec in action["data"]["recommendations"]:
                    if "chiffrement" in rec.lower() or "encryption" in rec.lower():
                        security_concerns["encryption"] += 1
                    elif "signal" in rec.lower():
                        security_concerns["signal_strength"] += 1
                    elif "fréquence" in rec.lower() or "frequency" in rec.lower():
                        security_concerns["frequency"] += 1

        # Déterminer le focus principal
        if not security_concerns or max(security_concerns.values()) == 0:
            return "general"

        # Correction: utiliser items() pour obtenir les paires clé-valeur
        return max(security_concerns.items(), key=lambda item: item[1])[0]

    def _get_network_preferences(self):
        """Détermine les préférences de réseau de l'utilisateur"""
        # Analyser les réseaux consultés fréquemment
        ssid_counts = {}
        security_preference = {"WPA3": 0, "WPA2": 0, "WPA": 0, "WEP": 0, "OPEN": 0}

        for action in self.history["consulted_networks"]:
            ssid = action["data"].get("ssid", "")
            if ssid:
                ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1

            security = action["data"].get("security_level", "").upper()
            for sec_type in security_preference:
                if sec_type in security:
                    security_preference[sec_type] += 1

        # Déterminer la préférence de sécurité
        preferred_security = "WPA2"  # Par défaut
        if security_preference and max(security_preference.values()) > 0:
            # Correction: utiliser items() pour obtenir les paires clé-valeur
            preferred_security = max(security_preference.items(), key=lambda item: item[1])[0]

        # Déterminer les réseaux préférés
        preferred_networks = sorted(ssid_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "preferred_security": preferred_security,
            "frequently_accessed": [net for net, _ in preferred_networks[:3] if net]
        }

    def _get_recommended_actions(self):
        """Génère des actions recommandées basées sur l'historique"""
        recommended_actions = []

        # Si peu de rapports générés, suggérer d'en créer
        if len(self.history["generated_reports"]) < 2:
            recommended_actions.append({
                "type": "report_generation",
                "description": {
                    "fr": "Générer un rapport complet de sécurité pour tous vos réseaux",
                    "en": "Generate a comprehensive security report for all your networks",
                    "ar": "إنشاء تقرير أمان شامل لجميع شبكاتك"
                },
                "priority": "high"
            })

        # Analyser les niveaux de sécurité des réseaux consultés
        low_security_networks = []
        for action in self.history["consulted_networks"]:
            if action["data"].get("security_level", "").upper() in ["FAIBLE", "TRÈS FAIBLE", "LOW", "VERY LOW"]:
                low_security_networks.append(action["data"].get("ssid", ""))

        # Recommander d'améliorer la sécurité des réseaux vulnérables
        if low_security_networks:
            # Correction: convertir le set en liste avant de le trancher
            unique_networks = list(set(low_security_networks))
            for network in unique_networks[:2]:  # Limiter à 2 recommandations
                recommended_actions.append({
                    "type": "improve_security",
                    "network": network,
                    "description": {
                        "fr": f"Améliorer la sécurité du réseau '{network}'",
                        "en": f"Improve the security of the '{network}' network",
                        "ar": f"تحسين أمان شبكة '{network}'"
                    },
                    "priority": "medium"
                })

        # Si peu d'actions au total, suggérer d'explorer l'assistant
        if len(self.history["user_actions"]) < 5:
            recommended_actions.append({
                "type": "explore_assistant",
                "description": {
                    "fr": "Consulter l'assistant de sécurité pour des conseils personnalisés",
                    "en": "Consult the security assistant for personalized advice",
                    "ar": "استشر مساعد الأمان للحصول على نصائح مخصصة"
                },
                "priority": "low"
            })

        # Si l'historique est vide, ajouter des recommandations par défaut
        if not recommended_actions:
            recommended_actions = [
                {
                    "type": "update_scan",
                    "description": {
                        "fr": "Effectuer une nouvelle analyse des réseaux disponibles",
                        "en": "Perform a new scan of available networks",
                        "ar": "إجراء مسح جديد للشبكات المتاحة"
                    },
                    "priority": "medium"
                },
                {
                    "type": "security_check",
                    "description": {
                        "fr": "Vérifier la sécurité de vos réseaux fréquemment utilisés",
                        "en": "Check the security of your frequently used networks",
                        "ar": "تحقق من أمان الشبكات التي تستخدمها بشكل متكرر"
                    },
                    "priority": "high"
                }
            ]

        return recommended_actions

# Instance globale du système de recommandations
recommendation_system = RecommendationSystem()