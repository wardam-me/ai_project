from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import logging
import json
import os
import subprocess

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)

# Configuration de l'analyseur WiFi
CONFIG_DIR = os.path.expanduser("~/.network_detect")
WIFI_RESULTS_FILE = os.path.join(CONFIG_DIR, "wifi_results.json")

def load_wifi_data():
    if not os.path.exists(WIFI_RESULTS_FILE):
        logger.warning("Aucun fichier de résultats WiFi trouvé.")
        # Essayer de générer des données de test
        try:
            logger.info("Génération de données de test...")
            subprocess.run(["python", "generate_test_data.py"], check=True)
            if os.path.exists(WIFI_RESULTS_FILE):
                logger.info("Données de test générées avec succès.")
            else:
                logger.warning("Échec de génération des données de test.")
                return []
        except Exception as e:
            logger.error(f"Erreur lors de la génération des données de test: {e}")
            return []

    with open(WIFI_RESULTS_FILE, "r") as file:
        try:
            data = json.load(file)
            return [net for net in data if net.get("ssid")]
        except json.JSONDecodeError:
            logger.error("Fichier JSON invalide.")
            return []

def score_network(network):
    # Score basé sur la puissance du signal et le type de sécurité
    signal_score = max(-network["rssi"], 0)  # Plus le RSSI est proche de 0, meilleur est le signal

    # Bonus pour la sécurité (WPA2/WPA3 est meilleur)
    security = network.get("security", "").upper()
    security_score = 0
    if "WPA3" in security:
        security_score = 30
    elif "WPA2" in security:
        security_score = 20
    elif "WPA" in security:
        security_score = 10

    # Score total (plus petit = meilleur)
    return signal_score - security_score

def get_best_network():
    wifi_data = load_wifi_data()
    if not wifi_data:
        return None
    # Le meilleur réseau a le score le plus bas
    return min(wifi_data, key=score_network)

@app.route('/')
def accueil():
    logger.info('Page d\'accueil visitée')
    best_network = get_best_network()
    all_networks = load_wifi_data()
    return render_template('index.html', network=best_network, all_networks=all_networks)

@socketio.on('request_network_update')
def handle_network_update():
    best_network = get_best_network()
    all_networks = load_wifi_data()
    emit('network_update', {'best': best_network, 'all': all_networks})

@app.errorhandler(404)
def page_non_trouvee(error):
    logger.error(f'Page non trouvée: {error}')
    return render_template('index.html', 
                         error="Page non trouvée. Retournez à l'accueil."), 404

@app.errorhandler(500)
def erreur_serveur(error):
    logger.error(f'Erreur serveur: {error}')
    return render_template('index.html', 
                         error="Erreur serveur. Veuillez réessayer plus tard."), 500

if __name__ == '__main__':
    os.makedirs(CONFIG_DIR, exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)