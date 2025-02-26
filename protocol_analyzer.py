"""
Module d'analyse avancée des protocoles de sécurité pour les réseaux WiFi.
Détecte les failles dans les protocoles et proposer des recommandations.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes pour les types de chiffrement
WEP = "WEP"
WPA = "WPA"
WPA2 = "WPA2"
WPA3 = "WPA3"
OPEN = "OPEN"

# Constantes pour les algorithmes de chiffrement
TKIP = "TKIP"
AES = "AES"
CCMP = "CCMP"
GCMP = "GCMP"

# Constantes pour les méthodes d'authentification
PSK = "PSK"
ENTERPRISE = "ENTERPRISE"
SAE = "SAE"  # WPA3 utilise SAE (Simultaneous Authentication of Equals)
OWE = "OWE"  # Opportunistic Wireless Encryption (pour les réseaux ouverts)

# Chemin du fichier pour stocker les analyses
PROTOCOL_ANALYSES_FILE = os.path.join("instance", "protocol_analyses.json")


class ProtocolAnalyzer:
    """Analyseur de protocoles de sécurité WiFi"""

    def __init__(self):
        """Initialisation de l'analyseur de protocoles"""
        self.analyses = []
        self.load_analyses()

    def load_analyses(self) -> None:
        """Charge les analyses précédentes depuis le fichier, ou initialise si nécessaire"""
        if os.path.exists(PROTOCOL_ANALYSES_FILE):
            try:
                with open(PROTOCOL_ANALYSES_FILE, "r", encoding="utf-8") as f:
                    self.analyses = json.load(f)
                    logger.info("Analyses de protocole chargées avec succès")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Erreur lors du chargement des analyses: {e}")
                self.analyses = []
        else:
            logger.info("Aucun fichier d'analyses trouvé, initialisation d'un nouveau")
            self.analyses = []

    def save_analyses(self) -> None:
        """Sauvegarde les analyses dans un fichier JSON"""
        try:
            os.makedirs(os.path.dirname(PROTOCOL_ANALYSES_FILE), exist_ok=True)
            with open(PROTOCOL_ANALYSES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.analyses, f, ensure_ascii=False, indent=2)
            logger.info("Analyses de protocole sauvegardées avec succès")
        except IOError as e:
            logger.error(f"Erreur lors de la sauvegarde des analyses: {e}")

    def analyze_network_protocol(self, network: Dict) -> Dict:
        """
        Analyse un réseau spécifique pour détecter les failles de protocole
        
        Args:
            network: Dictionnaire contenant les informations du réseau
                {
                    "ssid": str,
                    "bssid": str,
                    "security": str,
                    "encryption": Optional[str],
                    "authentication": Optional[str],
                    "strength": int,
                    "frequency": str,
                    "channel": int
                }
                
        Returns:
            Dict: Résultat de l'analyse avec les vulnérabilités et recommandations
        """
        # Extraire les informations du réseau
        ssid = network.get("ssid", "Réseau inconnu")
        security_type = network.get("security", OPEN)
        encryption = network.get("encryption")
        authentication = network.get("authentication")
        
        # Initialiser le résultat
        result = {
            "ssid": ssid,
            "timestamp": datetime.now().isoformat(),
            "security_type": security_type,
            "encryption": encryption,
            "authentication": authentication,
            "vulnerabilities": [],
            "score": 0,
            "recommendations": []
        }
        
        # Évaluer la sécurité du protocole
        vulnerabilities, score = self._evaluate_protocol_security(
            security_type, encryption, authentication
        )
        
        # Générer des recommandations
        recommendations = self._generate_protocol_recommendations(
            security_type, encryption, authentication, vulnerabilities
        )
        
        # Mettre à jour le résultat
        result["vulnerabilities"] = vulnerabilities
        result["score"] = score
        result["recommendations"] = recommendations
        
        # Sauvegarder l'analyse
        self.analyses.append(result)
        self.save_analyses()
        
        return result

    def analyze_all_networks(self, networks: List[Dict]) -> List[Dict]:
        """
        Analyse tous les réseaux pour détecter les failles de protocole
        
        Args:
            networks: Liste de dictionnaires contenant les informations des réseaux
            
        Returns:
            List[Dict]: Liste des résultats d'analyse
        """
        results = []
        for network in networks:
            result = self.analyze_network_protocol(network)
            results.append(result)
        
        return results

    def get_protocol_analysis_summary(self) -> Dict:
        """
        Génère un résumé des analyses de protocole
        
        Returns:
            Dict: Résumé des analyses
        """
        if not self.analyses:
            return {
                "total_networks": 0,
                "average_score": 0,
                "protocol_distribution": {},
                "vulnerability_types": {},
                "recommendations": []
            }
        
        # Calculer les statistiques
        total_networks = len(self.analyses)
        average_score = sum(analysis["score"] for analysis in self.analyses) / total_networks
        
        # Distribution des protocoles
        protocol_distribution = {}
        for analysis in self.analyses:
            security_type = analysis["security_type"]
            protocol_distribution[security_type] = protocol_distribution.get(security_type, 0) + 1
        
        # Types de vulnérabilités
        vulnerability_types = {}
        for analysis in self.analyses:
            for vuln in analysis["vulnerabilities"]:
                vuln_type = vuln["type"]
                vulnerability_types[vuln_type] = vulnerability_types.get(vuln_type, 0) + 1
        
        # Recommandations globales
        global_recommendations = self._generate_global_recommendations()
        
        return {
            "total_networks": total_networks,
            "average_score": round(average_score, 2),
            "protocol_distribution": protocol_distribution,
            "vulnerability_types": vulnerability_types,
            "recommendations": global_recommendations
        }

    def _evaluate_protocol_security(
        self, 
        security_type: str, 
        encryption: Optional[str] = None, 
        authentication: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """
        Évalue la sécurité d'un protocole et identifie les vulnérabilités
        
        Args:
            security_type: Type de sécurité (WEP, WPA, WPA2, WPA3, OPEN)
            encryption: Algorithme de chiffrement (TKIP, AES, CCMP, GCMP)
            authentication: Méthode d'authentification (PSK, ENTERPRISE, SAE, OWE)
            
        Returns:
            Tuple[List[Dict], int]: Liste des vulnérabilités et score de sécurité (0-100)
        """
        vulnerabilities = []
        score = 100  # Score initial parfait
        
        # Réseaux ouverts
        if security_type == OPEN:
            vulnerabilities.append({
                "type": "open_network",
                "severity": "critical",
                "description": "Réseau ouvert sans chiffrement",
                "impact": "Toutes les données transitant par ce réseau peuvent être interceptées et lues"
            })
            score -= 80  # Pénalité sévère pour un réseau ouvert
        
        # WEP (très vulnérable)
        elif security_type == WEP:
            vulnerabilities.append({
                "type": "wep_encryption",
                "severity": "critical",
                "description": "Chiffrement WEP obsolète et facilement crackable",
                "impact": "Le chiffrement peut être cassé en quelques minutes avec des outils standard"
            })
            score -= 70  # Pénalité sévère pour WEP
        
        # WPA (vulnérable)
        elif security_type == WPA:
            vulnerabilities.append({
                "type": "wpa_encryption",
                "severity": "high",
                "description": "Protocole WPA vulnérable à plusieurs attaques",
                "impact": "Peut être compromis par des attaques de type TKIP Michael MIC"
            })
            score -= 50  # Pénalité élevée pour WPA
            
            if encryption == TKIP:
                vulnerabilities.append({
                    "type": "tkip_encryption",
                    "severity": "high",
                    "description": "Chiffrement TKIP vulnérable",
                    "impact": "Exposé à des vulnérabilités connues permettant la récupération de clés"
                })
                score -= 15  # Pénalité supplémentaire pour TKIP
        
        # WPA2 (généralement sécurisé, mais avec des vulnérabilités connues)
        elif security_type == WPA2:
            if encryption == TKIP:
                vulnerabilities.append({
                    "type": "wpa2_tkip",
                    "severity": "high",
                    "description": "WPA2 avec TKIP au lieu de AES/CCMP",
                    "impact": "Vulnérable aux mêmes attaques que WPA avec TKIP"
                })
                score -= 40  # Pénalité pour WPA2 avec TKIP
            
            vulnerabilities.append({
                "type": "wpa2_krack",
                "severity": "medium",
                "description": "Vulnérable à l'attaque KRACK (Key Reinstallation Attack)",
                "impact": "Permet à un attaquant de décrypter le trafic dans certaines conditions"
            })
            score -= 20  # Pénalité pour la vulnérabilité KRACK
            
            if authentication == PSK:
                vulnerabilities.append({
                    "type": "weak_psk",
                    "severity": "medium",
                    "description": "Utilisation de clé pré-partagée (PSK)",
                    "impact": "Vulnérable aux attaques par dictionnaire et attaques pré-calculées"
                })
                score -= 10  # Pénalité pour PSK
        
        # WPA3 (le plus sécurisé)
        elif security_type == WPA3:
            # WPA3 est généralement très sécurisé, mais a quelques problèmes connus
            vulnerabilities.append({
                "type": "wpa3_dragonblood",
                "severity": "low",
                "description": "Potentiellement vulnérable aux attaques Dragonblood",
                "impact": "Possible vulnérabilité aux attaques par dictionnaire dans des conditions spécifiques"
            })
            score -= 5  # Petite pénalité pour WPA3
        
        # Cas inconnu
        else:
            vulnerabilities.append({
                "type": "unknown_security",
                "severity": "unknown",
                "description": "Type de sécurité inconnu ou non standard",
                "impact": "Impossible d'évaluer précisément la sécurité"
            })
            score -= 40  # Pénalité par défaut pour l'incertitude
        
        # S'assurer que le score ne descend pas en dessous de 0
        score = max(0, score)
        
        return vulnerabilities, score

    def _generate_protocol_recommendations(
        self, 
        security_type: str, 
        encryption: Optional[str] = None, 
        authentication: Optional[str] = None,
        vulnerabilities: List[Dict] = None
    ) -> List[Dict]:
        """
        Génère des recommandations basées sur le protocole et les vulnérabilités
        
        Args:
            security_type: Type de sécurité
            encryption: Algorithme de chiffrement
            authentication: Méthode d'authentification
            vulnerabilities: Liste des vulnérabilités détectées
            
        Returns:
            List[Dict]: Liste des recommandations
        """
        recommendations = []
        
        # Pour les réseaux ouverts
        if security_type == OPEN:
            recommendations.append({
                "priority": "critical",
                "action": "enable_encryption",
                "description": "Activer le chiffrement WPA3-SAE sur ce réseau",
                "details": "Les réseaux ouverts exposent toutes les communications à l'interception. " +
                           "Configurez votre routeur pour utiliser WPA3 avec authentification SAE pour une sécurité maximale."
            })
        
        # Pour WEP
        elif security_type == WEP:
            recommendations.append({
                "priority": "critical",
                "action": "upgrade_to_wpa3",
                "description": "Remplacer WEP par WPA3-SAE immédiatement",
                "details": "Le chiffrement WEP est cassable en minutes. " +
                           "Configurez votre routeur pour utiliser WPA3 avec authentification SAE."
            })
            recommendations.append({
                "priority": "high",
                "action": "change_router",
                "description": "Envisager le remplacement des équipements anciens",
                "details": "Si votre matériel ne prend pas en charge WPA3 ou au moins WPA2, " +
                           "il est fortement recommandé de le remplacer par des équipements modernes."
            })
        
        # Pour WPA
        elif security_type == WPA:
            recommendations.append({
                "priority": "high",
                "action": "upgrade_to_wpa3",
                "description": "Mettre à niveau vers WPA3-SAE",
                "details": "WPA est vulnérable à plusieurs types d'attaques. " +
                           "Si votre matériel le supporte, activez WPA3 avec authentification SAE."
            })
            recommendations.append({
                "priority": "medium",
                "action": "upgrade_to_wpa2",
                "description": "Alternative: passer à WPA2-AES",
                "details": "Si WPA3 n'est pas disponible, configurez au minimum WPA2 avec chiffrement AES/CCMP " +
                           "et désactivez TKIP."
            })
        
        # Pour WPA2
        elif security_type == WPA2:
            if encryption == TKIP:
                recommendations.append({
                    "priority": "high",
                    "action": "switch_to_aes",
                    "description": "Remplacer TKIP par AES/CCMP",
                    "details": "TKIP est moins sécurisé qu'AES. Configurez votre routeur pour utiliser " +
                               "exclusivement AES/CCMP avec WPA2."
                })
            
            recommendations.append({
                "priority": "medium",
                "action": "upgrade_to_wpa3",
                "description": "Mettre à niveau vers WPA3 si possible",
                "details": "WPA3 offre une protection contre les attaques KRACK et par dictionnaire. " +
                           "Si votre matériel le supporte, activez WPA3."
            })
            
            if authentication == PSK:
                recommendations.append({
                    "priority": "medium",
                    "action": "strong_password",
                    "description": "Utiliser un mot de passe fort et complexe",
                    "details": "Avec WPA2-PSK, la force de votre mot de passe est critique. " +
                               "Utilisez une phrase de passe d'au moins 12 caractères mêlant lettres, " +
                               "chiffres et caractères spéciaux."
                })
                recommendations.append({
                    "priority": "medium",
                    "action": "consider_enterprise",
                    "description": "Envisager WPA2-Enterprise pour les environnements professionnels",
                    "details": "Pour les entreprises, WPA2-Enterprise avec 802.1X offre une meilleure " +
                               "sécurité et gestion des identifiants que WPA2-PSK."
                })
        
        # Pour WPA3
        elif security_type == WPA3:
            recommendations.append({
                "priority": "low",
                "action": "firmware_updates",
                "description": "Maintenir le firmware à jour",
                "details": "Assurez-vous que votre routeur bénéficie des dernières mises à jour de firmware " +
                           "pour corriger les vulnérabilités Dragonblood et autres failles."
            })
            recommendations.append({
                "priority": "low",
                "action": "transition_mode",
                "description": "Désactiver le mode de transition WPA3-WPA2 si possible",
                "details": "Si tous vos appareils supportent WPA3, désactivez le mode de compatibilité WPA2 " +
                           "pour éviter les attaques de rétrogradation vers WPA2."
            })
        
        # Recommandations générales
        recommendations.append({
            "priority": "medium",
            "action": "disable_wps",
            "description": "Désactiver WPS (Wi-Fi Protected Setup)",
            "details": "WPS peut introduire des vulnérabilités indépendamment du protocole de sécurité choisi."
        })
        
        recommendations.append({
            "priority": "medium",
            "action": "guest_network",
            "description": "Utiliser un réseau invité séparé",
            "details": "Configurez un réseau invité distinct pour les visiteurs et les appareils IoT " +
                       "afin d'isoler les appareils potentiellement compromis."
        })
        
        return recommendations

    def _generate_global_recommendations(self) -> List[Dict]:
        """
        Génère des recommandations globales basées sur l'analyse de tous les réseaux
        
        Returns:
            List[Dict]: Liste des recommandations globales
        """
        # Compter les types de protocoles
        protocol_count = {}
        for analysis in self.analyses:
            security_type = analysis["security_type"]
            protocol_count[security_type] = protocol_count.get(security_type, 0) + 1
        
        recommendations = []
        
        # S'il y a des réseaux WEP ou ouverts
        if protocol_count.get(WEP, 0) > 0 or protocol_count.get(OPEN, 0) > 0:
            recommendations.append({
                "priority": "critical",
                "action": "replace_insecure_networks",
                "description": "Remplacer tous les réseaux non sécurisés (WEP et ouverts)",
                "details": "Plusieurs réseaux utilisent des protocoles non sécurisés (WEP ou ouverts). " +
                           "Mettez à niveau ces réseaux vers WPA3 ou au minimum WPA2-AES immédiatement."
            })
        
        # S'il y a des réseaux WPA
        if protocol_count.get(WPA, 0) > 0:
            recommendations.append({
                "priority": "high",
                "action": "upgrade_wpa_networks",
                "description": "Mettre à niveau tous les réseaux WPA vers WPA3",
                "details": "Les réseaux WPA présentent des vulnérabilités connues. " +
                           "Mettez-les à niveau vers WPA3 ou au minimum WPA2-AES."
            })
        
        # S'il y a plus de réseaux WPA2 que WPA3
        if protocol_count.get(WPA2, 0) > protocol_count.get(WPA3, 0):
            recommendations.append({
                "priority": "medium",
                "action": "prioritize_wpa3",
                "description": "Privilégier WPA3 sur tous les nouveaux appareils",
                "details": "Lors du remplacement d'équipements, choisissez des appareils compatibles WPA3. " +
                           "Pour les appareils existants, vérifiez si des mises à jour de firmware " +
                           "permettent d'activer WPA3."
            })
        
        # Recommandation générale sur la gestion des mots de passe
        recommendations.append({
            "priority": "medium",
            "action": "password_management",
            "description": "Implémenter une politique de gestion des mots de passe WiFi",
            "details": "Changez régulièrement les mots de passe WiFi (tous les 3-6 mois) et " +
                       "utilisez des phrases de passe longues et complexes. Envisagez un gestionnaire " +
                       "de mots de passe pour les stocker de manière sécurisée."
        })
        
        # Recommandation sur le monitoring
        recommendations.append({
            "priority": "medium",
            "action": "network_monitoring",
            "description": "Mettre en place une surveillance de la sécurité réseau",
            "details": "Utilisez des outils de surveillance pour détecter les tentatives d'intrusion " +
                       "et les appareils non autorisés sur votre réseau."
        })
        
        return recommendations

    def get_protocol_timeline(self) -> List[Dict]:
        """
        Obtient une chronologie des analyses de protocole
        
        Returns:
            List[Dict]: Chronologie des analyses
        """
        timeline = []
        
        for analysis in sorted(self.analyses, key=lambda x: x["timestamp"]):
            event = {
                "timestamp": analysis["timestamp"],
                "ssid": analysis["ssid"],
                "security_type": analysis["security_type"],
                "score": analysis["score"],
                "vulnerabilities_count": len(analysis["vulnerabilities"])
            }
            timeline.append(event)
        
        return timeline

    def get_protocol_comparison(self) -> Dict:
        """
        Génère une comparaison des différents protocoles de sécurité
        
        Returns:
            Dict: Comparaison des protocoles
        """
        comparison = {
            "protocols": [
                {
                    "name": "WEP",
                    "security_level": "Très faible",
                    "year_introduced": 1999,
                    "status": "Obsolète",
                    "vulnerabilities": [
                        "Clés facilement cassables",
                        "Attaques par réinjection",
                        "Déchiffrement du trafic complet"
                    ],
                    "recommendation": "À éviter complètement"
                },
                {
                    "name": "WPA",
                    "security_level": "Faible",
                    "year_introduced": 2003,
                    "status": "Déconseillé",
                    "vulnerabilities": [
                        "Vulnérabilités TKIP",
                        "Attaques sur le MIC (Message Integrity Check)"
                    ],
                    "recommendation": "Mettre à niveau vers WPA2 ou WPA3"
                },
                {
                    "name": "WPA2",
                    "security_level": "Moyen à bon",
                    "year_introduced": 2004,
                    "status": "Standard actuel",
                    "vulnerabilities": [
                        "Vulnérabilité KRACK",
                        "Attaques par dictionnaire sur PSK",
                        "Faiblesse avec TKIP"
                    ],
                    "recommendation": "Utiliser avec AES/CCMP uniquement"
                },
                {
                    "name": "WPA3",
                    "security_level": "Élevé",
                    "year_introduced": 2018,
                    "status": "Recommandé",
                    "vulnerabilities": [
                        "Vulnérabilités Dragonblood (corrigées dans les mises à jour)"
                    ],
                    "recommendation": "Solution recommandée"
                }
            ],
            "encryption_methods": [
                {
                    "name": "TKIP",
                    "security_level": "Faible",
                    "vulnerabilities": "Multiples failles cryptographiques",
                    "recommendation": "Éviter, utiliser AES/CCMP à la place"
                },
                {
                    "name": "AES/CCMP",
                    "security_level": "Élevé",
                    "vulnerabilities": "Peu de vulnérabilités connues",
                    "recommendation": "Recommandé pour WPA2"
                },
                {
                    "name": "GCMP",
                    "security_level": "Très élevé",
                    "vulnerabilities": "Peu de vulnérabilités connues",
                    "recommendation": "Recommandé pour WPA3"
                }
            ],
            "authentication_methods": [
                {
                    "name": "PSK (Pre-Shared Key)",
                    "security_level": "Moyen",
                    "vulnerabilities": "Attaques par dictionnaire",
                    "recommendation": "Utiliser des phrases de passe longues et complexes"
                },
                {
                    "name": "Enterprise (802.1X)",
                    "security_level": "Élevé",
                    "vulnerabilities": "Complexité de mise en œuvre",
                    "recommendation": "Recommandé pour les environnements professionnels"
                },
                {
                    "name": "SAE (Simultaneous Authentication of Equals)",
                    "security_level": "Très élevé",
                    "vulnerabilities": "Peu de vulnérabilités connues",
                    "recommendation": "Recommandé avec WPA3"
                }
            ]
        }
        
        return comparison


# Testing the module
if __name__ == "__main__":
    # Create an instance of the analyzer
    analyzer = ProtocolAnalyzer()
    
    # Sample networks for testing
    test_networks = [
        {
            "ssid": "HomeWiFi",
            "bssid": "00:11:22:33:44:55",
            "security": WPA2,
            "encryption": AES,
            "authentication": PSK,
            "strength": -65,
            "frequency": "2.4GHz",
            "channel": 6
        },
        {
            "ssid": "OldNetwork",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "security": WEP,
            "encryption": None,
            "authentication": None,
            "strength": -70,
            "frequency": "2.4GHz",
            "channel": 11
        },
        {
            "ssid": "ModernNetwork",
            "bssid": "11:22:33:44:55:66",
            "security": WPA3,
            "encryption": GCMP,
            "authentication": SAE,
            "strength": -60,
            "frequency": "5GHz",
            "channel": 36
        }
    ]
    
    # Analyze all networks
    results = analyzer.analyze_all_networks(test_networks)
    
    # Print the results
    for result in results:
        print(f"Réseau: {result['ssid']}")
        print(f"Score de sécurité: {result['score']}/100")
        print("Vulnérabilités:")
        for vuln in result["vulnerabilities"]:
            print(f"  - {vuln['description']} (Sévérité: {vuln['severity']})")
        print("Recommandations:")
        for rec in result["recommendations"][:3]:  # Print top 3 recommendations
            print(f"  - {rec['description']} (Priorité: {rec['priority']})")
        print("-" * 50)
    
    # Get a summary
    summary = analyzer.get_protocol_analysis_summary()
    print(f"Résumé de l'analyse de {summary['total_networks']} réseaux:")
    print(f"Score moyen: {summary['average_score']}/100")
    print("Distribution des protocoles:")
    for protocol, count in summary["protocol_distribution"].items():
        print(f"  - {protocol}: {count} réseaux")
    print("-" * 50)