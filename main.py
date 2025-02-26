from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import logging
import json
import os

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
        return []

    with open(WIFI_RESULTS_FILE, "r") as file:
        try:
            data = json.load(file)
            return [net for net in data if net.get("ssid")]
        except json.JSONDecodeError:
            logger.error("Fichier JSON invalide.")
            return []

def score_network(network):
    signal_score = max(-network["rssi"], 0)
    security_score = 20 if "WPA" in network.get("ssid", "") else 0
    return signal_score + security_score

def get_best_network():
    wifi_data = load_wifi_data()
    if not wifi_data:
        return None
    return max(wifi_data, key=score_network)

@app.route('/')
def accueil():
    logger.info('Page d\'accueil visitée')
    best_network = get_best_network()
    return render_template('index.html', network=best_network)

@socketio.on('request_network_update')
def handle_network_update():
    best_network = get_best_network()
    emit('network_update', best_network)

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