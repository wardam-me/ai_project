#!/usr/bin/env python3
import json
import os
import random
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Dossier de configuration
CONFIG_DIR = os.path.expanduser("~/.network_detect")
WIFI_RESULTS_FILE = os.path.join(CONFIG_DIR, "wifi_results.json")

# Exemples de noms de réseaux WiFi
SAMPLE_NETWORKS = [
    {"name": "Freebox-WiFi", "security": "WPA2"},
    {"name": "Orange-Fibre", "security": "WPA2"},
    {"name": "SFR_WIFI", "security": "WPA2"},
    {"name": "Bouygues_Telecom", "security": "WPA2"},
    {"name": "WiFi_Public", "security": "Open"},
    {"name": "Cafe_WiFi", "security": "WPA"},
    {"name": "Hotel_Guest", "security": "WPA2"},
    {"name": "Bibliotheque_WiFi", "security": "WPA2"},
    {"name": "Universite_WIFI", "security": "WPA2-Enterprise"},
    {"name": "MonWiFi", "security": "WPA3"}
]

def generate_wifi_networks(count=5):
    """Génère des données de test pour les réseaux WiFi"""
    networks = []
    
    # Sélectionner un sous-ensemble aléatoire des réseaux
    selected_networks = random.sample(SAMPLE_NETWORKS, min(count, len(SAMPLE_NETWORKS)))
    
    for i, network in enumerate(selected_networks):
        # Générer un signal entre -30 (excellent) et -90 (faible)
        rssi = random.randint(-90, -30)
        
        # Fréquence (2.4GHz ou 5GHz)
        frequency = random.choice([2412 + i*5 for i in range(13)] + [5180 + i*5 for i in range(24)])
        
        networks.append({
            "ssid": network["name"],
            "rssi": rssi,
            "frequency_mhz": frequency,
            "security": network["security"]
        })
    
    return networks

def save_test_data():
    """Sauvegarde les données de test dans le fichier de résultats"""
    # Créer le répertoire s'il n'existe pas
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Générer les données
    wifi_networks = generate_wifi_networks()
    
    # Enregistrer dans le fichier
    with open(WIFI_RESULTS_FILE, 'w') as f:
        json.dump(wifi_networks, f, indent=2)
    
    logger.info(f"Données de test générées dans {WIFI_RESULTS_FILE}")
    logger.info(f"Réseaux générés: {len(wifi_networks)}")
    
    return wifi_networks

if __name__ == "__main__":
    networks = save_test_data()
    print(f"✅ {len(networks)} réseaux WiFi de test ont été générés:")
    for i, network in enumerate(networks, 1):
        print(f"{i}. {network['ssid']} ({network['rssi']} dBm, {network['frequency_mhz']} MHz, {network.get('security', 'Inconnu')})")
