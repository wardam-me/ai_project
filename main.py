from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_socketio import SocketIO, emit
import logging
import json
import os
import subprocess
from network_security import NetworkSecurityAnalyzer
from assistant_securite import AssistantSecurite
from translation import get_user_language, get_translation, get_all_translations, get_direction, AVAILABLE_LANGUAGES

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
socketio = SocketIO(app)

# Initialiser l'analyseur de sécurité
security_analyzer = NetworkSecurityAnalyzer()

# Initialiser l'assistant de sécurité
assistant = AssistantSecurite()

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

# Route pour changer la langue
@app.route('/set-language/<language>')
def set_language(language):
    if language in AVAILABLE_LANGUAGES:
        session['language'] = language

    # Rediriger vers la page précédente ou l'accueil
    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)
    return redirect(url_for('accueil'))

@app.route('/')
def accueil():
    logger.info('Page d\'accueil visitée')
    best_network = get_best_network()
    all_networks = load_wifi_data()

    # Récupérer les traductions et la direction du texte
    lang = get_user_language()
    translations = get_all_translations(lang)
    text_direction = get_direction(lang)

    return render_template('index.html', 
                           network=best_network, 
                           all_networks=all_networks,
                           translations=translations,
                           available_languages=AVAILABLE_LANGUAGES,
                           current_language=lang,
                           text_direction=text_direction)

@app.route('/security-report')
def security_report():
    """Page principale des rapports de sécurité"""
    logger.info('Page des rapports de sécurité visitée')
    all_networks = load_wifi_data()

    # Récupérer les rapports existants
    saved_reports = security_analyzer.get_saved_reports()

    # Récupérer les traductions et la direction du texte
    lang = get_user_language()
    translations = get_all_translations(lang)
    text_direction = get_direction(lang)

    return render_template(
        'security_report.html', 
        all_networks=all_networks,
        saved_reports=saved_reports,
        translations=translations,
        available_languages=AVAILABLE_LANGUAGES,
        current_language=lang,
        text_direction=text_direction
    )

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """Génère un nouveau rapport de sécurité"""
    report_name = request.form.get('report_name', '')
    all_networks = load_wifi_data()

    if not all_networks:
        return redirect(url_for('security_report'))

    report = security_analyzer.generate_report(all_networks, report_name)

    if report:
        return redirect(url_for('view_report', report_name=report['report_name']))
    else:
        return redirect(url_for('security_report'))

@app.route('/view-report/<report_name>')
def view_report(report_name):
    """Affiche un rapport spécifique"""
    report = security_analyzer.get_report_by_name(report_name)

    if not report:
        return redirect(url_for('security_report'))

    # Récupérer les traductions et la direction du texte
    lang = get_user_language()
    translations = get_all_translations(lang)
    text_direction = get_direction(lang)

    return render_template('view_report.html', 
                          report=report,
                          translations=translations,
                          available_languages=AVAILABLE_LANGUAGES,
                          current_language=lang,
                          text_direction=text_direction)

# Routes pour l'assistant de sécurité conversationnel
@app.route('/assistant')
def assistant_page():
    """Page principale de l'assistant de sécurité"""
    logger.info('Page de l\'assistant de sécurité visitée')
    all_networks = load_wifi_data()
    conversation_id = request.args.get('conversation_id')

    # Récupérer l'historique de conversation si un ID est fourni
    conversation_history = []
    if conversation_id:
        conversation_history = assistant.get_conversation_history(conversation_id)

    # Récupérer la liste des conversations
    all_conversations = assistant.get_all_conversations()

    # Récupérer les traductions et la direction du texte
    lang = get_user_language()
    translations = get_all_translations(lang)
    text_direction = get_direction(lang)

    return render_template(
        'assistant.html', 
        all_networks=all_networks,
        conversation_history=conversation_history,
        conversation_id=conversation_id,
        all_conversations=all_conversations,
        translations=translations,
        available_languages=AVAILABLE_LANGUAGES,
        current_language=lang,
        text_direction=text_direction
    )

@app.route('/api/assistant/message', methods=['POST'])
def assistant_message():
    """API pour interagir avec l'assistant de sécurité"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Données non fournies"}), 400

    user_input = data.get('message', '')
    conversation_id = data.get('conversation_id')
    network_id = data.get('network_id')

    # Récupérer les données du réseau si un ID est fourni
    network_data = None
    if network_id is not None:
        all_networks = load_wifi_data()
        try:
            network_id = int(network_id)
            if 0 <= network_id < len(all_networks):
                network_data = all_networks[network_id]
        except (ValueError, TypeError):
            pass

    # Générer une réponse
    response = assistant.generate_response(user_input, conversation_id, network_data)

    return jsonify(response)

@app.route('/api/assistant/conversations')
def get_conversations():
    """API pour récupérer la liste des conversations"""
    conversations = assistant.get_all_conversations()
    return jsonify(conversations)

@app.route('/api/analyze-network', methods=['POST'])
def api_analyze_network():
    """API pour analyser un réseau spécifique"""
    data = request.get_json()
    network = data.get('network')

    if not network:
        return jsonify({"error": "Réseau non spécifié"}), 400

    result = security_analyzer.analyze_network(network)
    return jsonify(result)

@socketio.on('request_network_update')
def handle_network_update():
    best_network = get_best_network()
    all_networks = load_wifi_data()
    emit('network_update', {'best': best_network, 'all': all_networks})

@socketio.on('analyze_network_security')
def handle_analyze_network(data):
    """Analyser la sécurité d'un réseau spécifique via WebSocket"""
    network_id = data.get('network_id')
    all_networks = load_wifi_data()

    if not all_networks or network_id is None or network_id >= len(all_networks):
        emit('security_analysis_result', {'error': 'Réseau non trouvé'})
        return

    network = all_networks[network_id]
    result = security_analyzer.analyze_network(network)
    emit('security_analysis_result', result)

@app.errorhandler(404)
def page_non_trouvee(error):
    logger.error(f'Page non trouvée: {error}')

    # Récupérer les traductions et la direction du texte
    lang = get_user_language()
    translations = get_all_translations(lang)
    text_direction = get_direction(lang)

    return render_template('index.html', 
                          error=get_translation("error_not_found", lang),
                          translations=translations,
                          available_languages=AVAILABLE_LANGUAGES,
                          current_language=lang,
                          text_direction=text_direction), 404

@app.errorhandler(500)
def erreur_serveur(error):
    logger.error(f'Erreur serveur: {error}')

    # Récupérer les traductions et la direction du texte
    lang = get_user_language()
    translations = get_all_translations(lang)
    text_direction = get_direction(lang)

    return render_template('index.html', 
                          error=get_translation("error_server", lang),
                          translations=translations,
                          available_languages=AVAILABLE_LANGUAGES,
                          current_language=lang,
                          text_direction=text_direction), 500

# Ajouter les traductions et la direction du texte à tous les templates
@app.context_processor
def inject_translations():
    lang = get_user_language()
    return {
        't': lambda key: get_translation(key, lang),
        'translations': get_all_translations(lang),
        'available_languages': AVAILABLE_LANGUAGES,
        'current_language': lang,
        'text_direction': get_direction(lang)
    }

if __name__ == '__main__':
    os.makedirs(CONFIG_DIR, exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)