#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration de l'IA dans les rapports d'infographie
"""
import os
import json
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import des modules nécessaires
from ai_infographic_assistant import AIInfographicAssistant
from infographic_generator import InfographicGenerator

def create_test_directories():
    """Crée les répertoires nécessaires pour les tests"""
    dirs = [
        'static/exports/network',
        'static/exports/protocol',
        'static/exports/vulnerability',
        'static/img/previews/network',
        'static/img/previews/protocol',
        'static/img/previews/vulnerability',
        'static/templates',
        'config'
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        logger.info(f"Répertoire créé/vérifié: {d}")

def generate_test_vulnerability_data():
    """Génère des données de test pour un rapport de vulnérabilité"""
    return {
        "summary": {
            "total": 35,
            "critical": 5,
            "high": 10,
            "medium": 15,
            "low": 5
        },
        "critical_vulnerabilities": [
            {
                "id": "CVE-2022-12345",
                "title": "Exécution de code à distance (routeur)",
                "severity": "critical",
                "description": "Une vulnérabilité critique permet l'exécution de code arbitraire sur le routeur.",
                "affected_devices": ["Router X5", "IoT Hub"]
            },
            {
                "id": "CVE-2022-23456",
                "title": "Faille de sécurité (caméra IP)",
                "severity": "critical",
                "description": "Une faille dans le firmware de la caméra permet la récupération de flux vidéo non autorisée.",
                "affected_devices": ["IP Cam Model 3"]
            },
            {
                "id": "CVE-2022-34567",
                "title": "Authentification faible (assistant vocal)",
                "severity": "high",
                "description": "L'assistant vocal utilise une méthode d'authentification vulnérable aux attaques.",
                "affected_devices": ["Voice Assistant V2"]
            }
        ],
        "severity_distribution": {
            "critical": 5,
            "high": 10,
            "medium": 15,
            "low": 5
        },
        "discovery_timeline": [
            {
                "date": "2023-01-15",
                "vulnerabilities": 5,
                "description": "Première analyse de sécurité"
            },
            {
                "date": "2023-02-20",
                "vulnerabilities": 3,
                "description": "Scan après mise à jour du firmware"
            },
            {
                "date": "2023-03-10",
                "vulnerabilities": 8,
                "description": "Analyse approfondie suite à l'ajout de nouveaux appareils"
            },
            {
                "date": "2023-04-05",
                "vulnerabilities": 2,
                "description": "Vérification post-correction"
            }
        ],
        "remediation_plan": [
            {
                "step": 1,
                "title": "Mise à jour des firmwares",
                "description": "Mettre à jour tous les firmwares des appareils connectés, en particulier le routeur et les caméras IP.",
                "difficulty": "easy",
                "estimated_time": "1-2 heures"
            },
            {
                "step": 2,
                "title": "Renforcer les mots de passe",
                "description": "Changer tous les mots de passe par défaut et utiliser des mots de passe forts uniques pour chaque appareil.",
                "difficulty": "easy",
                "estimated_time": "30 minutes"
            },
            {
                "step": 3,
                "title": "Segmenter le réseau",
                "description": "Créer des réseaux séparés pour les appareils IoT et les ordinateurs personnels afin de limiter les risques.",
                "difficulty": "medium",
                "estimated_time": "2 heures"
            },
            {
                "step": 4,
                "title": "Configurer un pare-feu",
                "description": "Mettre en place des règles de pare-feu pour bloquer les communications non essentielles.",
                "difficulty": "hard",
                "estimated_time": "3-4 heures"
            }
        ]
    }

def generate_test_protocol_data():
    """Génère des données de test pour un rapport d'analyse de protocole"""
    return {
        "average_score": 65,
        "protocol_distribution": {
            "WPA3": 20,
            "WPA2": 45,
            "WPA": 20,
            "WEP": 10,
            "OPEN": 5
        },
        "protocols": [
            {
                "name": "WPA3",
                "security": 95,
                "encryption": "CCMP (AES)",
                "authentication": "SAE",
                "data_protection": "Très élevée",
                "known_vulnerabilities": "Très peu",
                "overall_score": 95
            },
            {
                "name": "WPA2",
                "security": 80,
                "encryption": "CCMP (AES)",
                "authentication": "PSK",
                "data_protection": "Élevée",
                "known_vulnerabilities": "Quelques-unes",
                "overall_score": 80
            },
            {
                "name": "WPA",
                "security": 60,
                "encryption": "TKIP",
                "authentication": "PSK",
                "data_protection": "Moyenne",
                "known_vulnerabilities": "Plusieurs",
                "overall_score": 60
            },
            {
                "name": "WEP",
                "security": 30,
                "encryption": "RC4",
                "authentication": "Clé partagée",
                "data_protection": "Faible",
                "known_vulnerabilities": "Nombreuses",
                "overall_score": 25
            },
            {
                "name": "OPEN",
                "security": 0,
                "encryption": "Aucun",
                "authentication": "Aucune",
                "data_protection": "Aucune",
                "known_vulnerabilities": "Toutes",
                "overall_score": 0
            }
        ],
        "vulnerability_by_protocol": {
            "WPA3": {
                "Bruteforce": 5,
                "MITM": 10,
                "Déauthentification": 15
            },
            "WPA2": {
                "Bruteforce": 20,
                "MITM": 25,
                "Déauthentification": 30
            },
            "WPA": {
                "Bruteforce": 40,
                "MITM": 45,
                "Déauthentification": 35
            },
            "WEP": {
                "Bruteforce": 80,
                "MITM": 75,
                "Déauthentification": 70
            }
        },
        "protocol_strengths": {
            "WPA3": {
                "Chiffrement": 95,
                "Authentification": 90,
                "Confidentialité": 90,
                "Intégrité": 90,
                "Disponibilité": 85
            },
            "WPA2": {
                "Chiffrement": 80,
                "Authentification": 75,
                "Confidentialité": 80,
                "Intégrité": 75,
                "Disponibilité": 80
            },
            "WPA": {
                "Chiffrement": 60,
                "Authentification": 55,
                "Confidentialité": 60,
                "Intégrité": 60,
                "Disponibilité": 75
            }
        },
        "recommendations": [
            {
                "title": "Mettre à niveau vers WPA3",
                "description": "Le protocole WPA3 offre une meilleure protection contre les attaques par force brute et une confidentialité de transfert parfaite."
            },
            {
                "title": "Remplacer les appareils utilisant WEP",
                "description": "Les appareils utilisant WEP représentent un risque majeur pour votre réseau. Remplacez-les ou isolez-les dans un réseau séparé."
            },
            {
                "title": "Activer le filtrage MAC",
                "description": "Bien que non infaillible, le filtrage MAC ajoute une couche de protection supplémentaire en limitant les appareils autorisés à se connecter."
            }
        ]
    }

def generate_test_network_data():
    """Génère des données de test pour un rapport de sécurité réseau"""
    return {
        "overall_score": 68,
        "protocol_distribution": {
            "WPA3": 20,
            "WPA2": 45,
            "WPA": 20,
            "WEP": 10,
            "OPEN": 5
        },
        "security_dimensions": {
            "Authentification": 65,
            "Chiffrement": 70,
            "Mises à jour": 50,
            "Pare-feu": 85,
            "Segmentation": 90,
            "Monitoring": 60
        },
        "devices": [
            {
                "name": "Caméra IP",
                "type": "camera",
                "security_score": 35
            },
            {
                "name": "Smart TV",
                "type": "television",
                "security_score": 55
            },
            {
                "name": "Smartphone",
                "type": "smartphone",
                "security_score": 65
            },
            {
                "name": "Routeur WiFi",
                "type": "router",
                "security_score": 75
            },
            {
                "name": "Ordinateur portable",
                "type": "computer",
                "security_score": 85
            }
        ],
        "security_trend": [
            {
                "date": "Janvier",
                "score": 54
            },
            {
                "date": "Février",
                "score": 58
            },
            {
                "date": "Mars",
                "score": 60
            },
            {
                "date": "Avril",
                "score": 65
            },
            {
                "date": "Mai",
                "score": 68
            }
        ]
    }

def test_ai_infographic_assistant():
    """Teste l'assistant d'infographie IA"""
    logger.info("Test de l'assistant d'infographie IA...")
    
    # Créer une instance de l'assistant
    ai_assistant = AIInfographicAssistant(use_cache=True)
    
    # Vérifier si l'IA est disponible
    if ai_assistant.is_available():
        logger.info("L'assistant IA est disponible et fonctionnel")
    else:
        logger.warning("L'assistant IA n'est pas disponible, utilisation de la version simulée")
    
    # Générer des données de test
    vuln_data = generate_test_vulnerability_data()
    protocol_data = generate_test_protocol_data()
    network_data = generate_test_network_data()
    
    # Enrichir les données avec l'IA
    vuln_data_enriched = ai_assistant.enrich_vulnerability_data(vuln_data)
    protocol_data_enriched = ai_assistant.enrich_protocol_analysis_data(protocol_data)
    network_data_enriched = ai_assistant.enrich_network_security_data(network_data)
    
    # Vérifier les différences dans les données
    logger.info("Vérification des enrichissements IA...")
    
    # Vérifier l'enrichissement des vulnérabilités
    if 'ai_advanced_recommendations' in vuln_data_enriched:
        logger.info("Enrichissement des vulnérabilités réussi")
        logger.info(f"Nombre de recommandations avancées: {len(vuln_data_enriched['ai_advanced_recommendations'])}")
    
    # Vérifier l'enrichissement des protocoles
    if 'ai_protocol_comparison' in protocol_data_enriched:
        logger.info("Enrichissement des protocoles réussi")
        logger.info(f"Analyse comparative des protocoles: {protocol_data_enriched['ai_protocol_comparison']['summary']}")
    
    # Vérifier l'enrichissement du réseau
    if 'ai_analysis' in network_data_enriched:
        logger.info("Enrichissement du réseau réussi")
        logger.info(f"Analyse du réseau: {network_data_enriched['ai_analysis']}")
    
    return vuln_data_enriched, protocol_data_enriched, network_data_enriched

def test_infographic_generator(vuln_data, protocol_data, network_data):
    """Teste le générateur d'infographie avec les données enrichies par l'IA"""
    logger.info("Test du générateur d'infographie...")
    
    # Créer une instance du générateur
    generator = InfographicGenerator()
    
    # Générer des infographies
    logger.info("Génération des infographies...")
    
    # Infographie de vulnérabilité
    vuln_path_svg = generator.generate_vulnerability_report_infographic(
        vuln_data,
        output_filename="vulnerability_report_test.svg",
        format="svg",
        use_ai=True
    )
    
    # Infographie de protocole
    protocol_path_png = generator.generate_protocol_analysis_infographic(
        protocol_data,
        output_filename="protocol_analysis_test.png",
        format="png",
        use_ai=True
    )
    
    # Infographie de réseau
    try:
        network_path_html = generator.generate_network_security_infographic(
            network_data,
            vuln_data,
            output_filename="network_security_test.html",
            format="html",
            interactive=True,
            use_ai=True
        )
    except Exception as e:
        logger.warning(f"Erreur lors de la génération du format HTML: {e}")
        # Essayer à la place le format PNG
        network_path_html = generator.generate_network_security_infographic(
            network_data,
            vuln_data,
            output_filename="network_security_test.png",
            format="png",
            use_ai=True
        )
    
    logger.info(f"Infographie de vulnérabilité générée: {vuln_path_svg}")
    logger.info(f"Infographie de protocole générée: {protocol_path_png}")
    logger.info(f"Infographie de réseau générée: {network_path_html}")
    
    return vuln_path_svg, protocol_path_png, network_path_html

def main():
    """Fonction principale"""
    logger.info("Démarrage des tests d'intégration IA...")
    
    # Créer les répertoires nécessaires
    create_test_directories()
    
    # Tester l'assistant d'infographie IA
    vuln_data, protocol_data, network_data = test_ai_infographic_assistant()
    
    # Tester le générateur d'infographie
    try:
        vuln_path, protocol_path, network_path = test_infographic_generator(vuln_data, protocol_data, network_data)
        logger.info("Tests complétés avec succès!")
        logger.info("Fichiers générés:")
        logger.info(f" - {vuln_path}")
        logger.info(f" - {protocol_path}")
        logger.info(f" - {network_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la génération des infographies: {e}")
    
if __name__ == "__main__":
    main()