# Module d'analyse de sécurité réseau
import logging
import json
import os
from datetime import datetime

# Configuration du logging
logger = logging.getLogger(__name__)

# Constantes pour les niveaux de sécurité
SECURITY_LEVELS = {
    "TRÈS FAIBLE": 0,
    "FAIBLE": 1,
    "MOYEN": 2,
    "ÉLEVÉ": 3,
    "TRÈS ÉLEVÉ": 4
}

# Règles de sécurité et leurs poids
SECURITY_RULES = {
    "encryption": {
        "weight": 40,
        "options": {
            "OPEN": 0,
            "WEP": 10,
            "WPA": 25,
            "WPA2": 35,
            "WPA3": 40
        }
    },
    "signal_strength": {
        "weight": 20,
        "thresholds": {
            "very_weak": [-100, -80],
            "weak": [-79, -70],
            "medium": [-69, -60],
            "strong": [-59, -40],
            "very_strong": [-39, 0]
        }
    },
    "frequency": {
        "weight": 10,
        "options": {
            "2.4GHz": 5,
            "5GHz": 10
        }
    }
}

class NetworkSecurityAnalyzer:
    def __init__(self):
        self.reports_dir = os.path.expanduser("~/.network_detect/reports")
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def analyze_network(self, network):
        """Analyse la sécurité d'un réseau spécifique"""
        if not network:
            return None
            
        score = 0
        details = {}
        
        # Analyser le type de sécurité
        security = network.get("security", "OPEN").upper()
        encryption_score = 0
        for key, value in SECURITY_RULES["encryption"]["options"].items():
            if key in security:
                encryption_score = value
                break
                
        score += encryption_score
        encryption_percentage = (encryption_score / SECURITY_RULES["encryption"]["weight"]) * 100
        details["encryption"] = {
            "type": security,
            "score": encryption_score,
            "max": SECURITY_RULES["encryption"]["weight"],
            "percentage": encryption_percentage,
            "recommendation": self._get_encryption_recommendation(security)
        }
        
        # Analyser la force du signal
        rssi = network.get("rssi", -100)
        signal_score = 0
        signal_level = "very_weak"
        
        for level, (min_val, max_val) in SECURITY_RULES["signal_strength"]["thresholds"].items():
            if min_val <= rssi <= max_val:
                signal_level = level
                # Calculer le score proportionnel à la position dans la plage
                range_size = max_val - min_val
                position_in_range = rssi - min_val
                signal_score = int((position_in_range / range_size) * SECURITY_RULES["signal_strength"]["weight"])
                break
                
        score += signal_score
        signal_percentage = (signal_score / SECURITY_RULES["signal_strength"]["weight"]) * 100
        details["signal_strength"] = {
            "value": rssi,
            "level": signal_level,
            "score": signal_score,
            "max": SECURITY_RULES["signal_strength"]["weight"],
            "percentage": signal_percentage,
            "recommendation": self._get_signal_recommendation(signal_level)
        }
        
        # Analyser la fréquence
        frequency = network.get("frequency_mhz", 0)
        frequency_score = 0
        
        if 2400 <= frequency <= 2500:
            frequency_score = SECURITY_RULES["frequency"]["options"]["2.4GHz"]
            frequency_band = "2.4GHz"
        elif 5000 <= frequency <= 5900:
            frequency_score = SECURITY_RULES["frequency"]["options"]["5GHz"]
            frequency_band = "5GHz"
        else:
            frequency_band = "Inconnu"
            
        score += frequency_score
        frequency_percentage = (frequency_score / SECURITY_RULES["frequency"]["weight"]) * 100
        details["frequency"] = {
            "value": frequency,
            "band": frequency_band,
            "score": frequency_score,
            "max": SECURITY_RULES["frequency"]["weight"],
            "percentage": frequency_percentage,
            "recommendation": self._get_frequency_recommendation(frequency_band)
        }
        
        # Score total sur 70 (somme des poids)
        total_max = sum(rule["weight"] for rule in SECURITY_RULES.values())
        percentage = (score / total_max) * 100
        
        # Déterminer le niveau de sécurité global
        security_level = self._get_security_level(percentage)
        
        # Générer le résultat
        result = {
            "network": network,
            "score": score,
            "max_score": total_max,
            "percentage": percentage,
            "security_level": security_level,
            "details": details,
            "overall_recommendation": self._get_overall_recommendation(security_level, details),
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def analyze_all_networks(self, networks):
        """Analyse tous les réseaux et les trie par niveau de sécurité"""
        if not networks:
            return []
            
        results = []
        for network in networks:
            result = self.analyze_network(network)
            if result:
                results.append(result)
                
        # Trier par score de sécurité (du plus élevé au plus faible)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def generate_report(self, networks, report_name=None):
        """Génère un rapport complet de sécurité"""
        results = self.analyze_all_networks(networks)
        
        if not results:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = report_name or f"security_report_{timestamp}"
        
        # Statistiques globales
        total_networks = len(results)
        secure_networks = len([r for r in results if r["security_level"] in ["ÉLEVÉ", "TRÈS ÉLEVÉ"]])
        vulnerable_networks = len([r for r in results if r["security_level"] in ["TRÈS FAIBLE", "FAIBLE"]])
        
        report = {
            "report_name": report_name,
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_networks": total_networks,
                "secure_networks": secure_networks,
                "vulnerable_networks": vulnerable_networks,
                "security_distribution": self._calculate_security_distribution(results)
            },
            "network_results": results,
            "global_recommendations": self._generate_global_recommendations(results)
        }
        
        # Sauvegarder le rapport
        report_file = os.path.join(self.reports_dir, f"{report_name}.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Rapport de sécurité généré: {report_file}")
        return report
    
    def get_saved_reports(self):
        """Récupère la liste des rapports sauvegardés"""
        reports = []
        
        if not os.path.exists(self.reports_dir):
            return reports
            
        for filename in os.listdir(self.reports_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.reports_dir, filename)
                try:
                    with open(file_path, "r") as f:
                        report = json.load(f)
                        reports.append({
                            "filename": filename,
                            "report_name": report.get("report_name", filename),
                            "timestamp": report.get("timestamp", ""),
                            "total_networks": report.get("statistics", {}).get("total_networks", 0)
                        })
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture du rapport {filename}: {e}")
        
        # Trier par date (plus récent en premier)
        reports.sort(key=lambda x: x["timestamp"], reverse=True)
        return reports
    
    def get_report_by_name(self, report_name):
        """Récupère un rapport spécifique par son nom"""
        if not report_name.endswith(".json"):
            report_name += ".json"
            
        report_path = os.path.join(self.reports_dir, report_name)
        
        if not os.path.exists(report_path):
            return None
            
        try:
            with open(report_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du rapport {report_name}: {e}")
            return None
    
    def _get_security_level(self, percentage):
        """Détermine le niveau de sécurité en fonction du pourcentage du score"""
        if percentage >= 90:
            return "TRÈS ÉLEVÉ"
        elif percentage >= 70:
            return "ÉLEVÉ"
        elif percentage >= 50:
            return "MOYEN"
        elif percentage >= 30:
            return "FAIBLE"
        else:
            return "TRÈS FAIBLE"
    
    def _get_encryption_recommendation(self, security_type):
        """Génère une recommandation basée sur le type de chiffrement"""
        if "WPA3" in security_type:
            return "Le réseau utilise WPA3, le standard de sécurité le plus récent et le plus sûr. Excellente protection."
        elif "WPA2" in security_type:
            return "Le réseau utilise WPA2, un standard de sécurité solide mais plus ancien. Envisagez une mise à niveau vers WPA3 si possible."
        elif "WPA" in security_type:
            return "Le réseau utilise WPA, qui présente des vulnérabilités connues. Une mise à niveau vers WPA2 ou WPA3 est fortement recommandée."
        elif "WEP" in security_type:
            return "ATTENTION: Le réseau utilise WEP, un protocole obsolète facilement piratable. Changez immédiatement pour WPA2 ou WPA3."
        else:
            return "DANGER: Réseau ouvert sans chiffrement. N'importe qui peut intercepter vos communications. Évitez de l'utiliser pour des informations sensibles."
    
    def _get_signal_recommendation(self, signal_level):
        """Génère une recommandation basée sur la force du signal"""
        if signal_level == "very_strong":
            return "Signal excellent. Vous êtes très proche du point d'accès, ce qui est idéal pour la sécurité."
        elif signal_level == "strong":
            return "Bon signal. La connexion est stable et relativement sécurisée."
        elif signal_level == "medium":
            return "Signal moyen. La connexion peut être instable par moments, ce qui peut affecter la sécurité."
        elif signal_level == "weak":
            return "Signal faible. Rapprochez-vous du point d'accès pour améliorer la sécurité et la stabilité."
        else:
            return "Signal très faible. À cette distance, la connexion est vulnérable aux interférences et aux attaques."
    
    def _get_frequency_recommendation(self, frequency_band):
        """Génère une recommandation basée sur la bande de fréquence"""
        if frequency_band == "5GHz":
            return "La bande 5GHz offre généralement moins d'interférences et une meilleure sécurité grâce à sa portée plus limitée."
        elif frequency_band == "2.4GHz":
            return "La bande 2.4GHz a une plus grande portée mais est plus susceptible aux interférences et potentiellement moins sécurisée."
        else:
            return "Fréquence inconnue. Impossible de fournir une recommandation spécifique."
    
    def _get_overall_recommendation(self, security_level, details):
        """Génère une recommandation globale basée sur tous les facteurs"""
        recommendations = []
        
        # Ajouter les recommandations spécifiques en fonction du niveau de sécurité
        if security_level in ["TRÈS FAIBLE", "FAIBLE"]:
            if details["encryption"]["score"] < SECURITY_RULES["encryption"]["weight"] * 0.7:
                recommendations.append("Priorité: Améliorez le chiffrement de votre réseau. " + details["encryption"]["recommendation"])
                
            if details["signal_strength"]["score"] < SECURITY_RULES["signal_strength"]["weight"] * 0.5:
                recommendations.append(details["signal_strength"]["recommendation"])
        
        elif security_level == "MOYEN":
            if details["encryption"]["score"] < SECURITY_RULES["encryption"]["weight"]:
                recommendations.append(details["encryption"]["recommendation"])
                
            if details["signal_strength"]["score"] < SECURITY_RULES["signal_strength"]["weight"] * 0.7:
                recommendations.append(details["signal_strength"]["recommendation"])
        
        else:  # ÉLEVÉ ou TRÈS ÉLEVÉ
            recommendations.append("Ce réseau offre un bon niveau de sécurité. Continuez à surveiller les mises à jour de sécurité.")
            
            # Même pour les réseaux sécurisés, suggérer des améliorations si nécessaire
            if "WPA3" not in details["encryption"]["type"]:
                recommendations.append("Pour une sécurité optimale, envisagez une mise à niveau vers WPA3 lorsque c'est possible.")
        
        # Recommandations générales
        recommendations.append("Conseil général: Utilisez toujours un VPN pour les activités sensibles, même sur des réseaux sécurisés.")
        
        return recommendations
    
    def _calculate_security_distribution(self, results):
        """Calcule la distribution des niveaux de sécurité"""
        distribution = {level: 0 for level in SECURITY_LEVELS.keys()}
        
        for result in results:
            level = result["security_level"]
            distribution[level] += 1
            
        return distribution
    
    def _generate_global_recommendations(self, results):
        """Génère des recommandations globales basées sur l'ensemble des réseaux"""
        recommendations = []
        
        # Analyser les types de chiffrement
        encryption_types = [r["details"]["encryption"]["type"] for r in results]
        weak_encryption_count = sum(1 for e in encryption_types if "WPA3" not in e and "WPA2" not in e)
        
        if weak_encryption_count > 0:
            percent_weak = (weak_encryption_count / len(results)) * 100
            recommendations.append(
                f"{weak_encryption_count} réseaux ({percent_weak:.1f}%) utilisent un chiffrement faible ou inexistant. "
                "Évitez de vous connecter à ces réseaux pour des activités sensibles."
            )
        
        # Analyser les niveaux de sécurité
        security_levels = [r["security_level"] for r in results]
        low_security_count = sum(1 for s in security_levels if s in ["TRÈS FAIBLE", "FAIBLE"])
        
        if low_security_count > 0:
            percent_low = (low_security_count / len(results)) * 100
            recommendations.append(
                f"{low_security_count} réseaux ({percent_low:.1f}%) présentent un niveau de sécurité faible ou très faible. "
                "Soyez vigilant lors de la connexion aux réseaux publics."
            )
        
        # Ajouter des recommandations générales
        recommendations.append(
            "Utilisez toujours des connexions HTTPS et un VPN pour protéger vos données, "
            "particulièrement sur des réseaux publics ou inconnus."
        )
        
        recommendations.append(
            "Mettez régulièrement à jour vos appareils pour bénéficier des derniers correctifs de sécurité."
        )
        
        return recommendations
