import json
import os

# Charger les données WiFi
CONFIG_DIR = os.path.expanduser("~/.network_detect")
WIFI_RESULTS_FILE = os.path.join(CONFIG_DIR, "wifi_results.json")

def load_wifi_data():
    if not os.path.exists(WIFI_RESULTS_FILE):
        print("Erreur: Aucun fichier de résultats WiFi trouvé.")
        return []
    
    with open(WIFI_RESULTS_FILE, "r") as file:
        try:
            data = json.load(file)
            return [net for net in data if net.get("ssid")]  # Filtrer les SSID vides
        except json.JSONDecodeError:
            print("Erreur: Fichier JSON invalide.")
            return []

def score_network(network):
    # Score basé sur RSSI et sécurité
    signal_score = max(-network["rssi"], 0)  # Plus proche de 0, meilleur est le signal
    security_score = 20 if "WPA" in network.get("ssid", "") else 0  # WPA/WPA2 est sécurisé
    
    return signal_score + security_score

def recommend_best_network(wifi_data):
    if not wifi_data:
        print("Aucun réseau à analyser.")
        return None
    
    best_network = max(wifi_data, key=score_network)
    return best_network

if __name__ == "__main__":
    wifi_data = load_wifi_data()
    best_network = recommend_best_network(wifi_data)
    
    if best_network:
        print("\n🏆 Réseau recommandé :")
        print(f"SSID : {best_network['ssid']}")
        print(f"Signal : {best_network['rssi']} dBm")
        print(f"Fréquence : {best_network['frequency_mhz']} MHz")
    else:
        print("Aucun réseau optimal trouvé.")

