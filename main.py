#!/usr/bin/env python3
"""
Application principale pour NetSecure Pro - Analyse de sécurité réseau WiFi
"""
import os
import json
import logging
import random
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify,
    session, abort, current_app
)
from flask_login import (
    LoginManager, current_user, login_user, logout_user, login_required
)
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from memory_monitor import MemoryMonitor

from app import app, db, socketio, login_manager
from forms import LoginForm, RegistrationForm, SaveTopologyForm
from models import User, UserReport, SavedTopology
from network_topology import NetworkTopology
from security_scoring import DeviceSecurityScoring
from assistant_securite import AssistantSecurite
from gamification import SecurityGamification
from module_IA import SecurityAI, NetworkOptimizer, AIErrorHandler, AICloneManager, ai_clone_manager
from security_assistant import SecurityAssistant
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialiser les classes principales
network_topology = NetworkTopology()
security_scoring = DeviceSecurityScoring()
assistant_securite = AssistantSecurite()
security_ai = SecurityAI()
network_optimizer = NetworkOptimizer()
# Initialiser l'assistant intelligent
security_assistant = SecurityAssistant(security_ai, network_optimizer, assistant_securite)

# Décorateur pour vérifier si l'utilisateur est administrateur
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès refusé. Vous devez être administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Contexte global pour tous les templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Filtres personnalisés pour les templates
@app.template_filter('datetime')
def format_datetime(value, format='relative'):
    """Format une datetime en une chaîne lisible.
    
    Args:
        value: La datetime à formater (peut être une chaîne ISO ou un objet datetime)
        format: Le format de sortie ('relative' pour "il y a X minutes", ou un format strftime)
    """
    if not value:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return value
    
    if format == 'relative':
        now = datetime.now()
        diff = now - value
        
        if diff.days > 365:
            return f"il y a {diff.days // 365} ans"
        if diff.days > 30:
            return f"il y a {diff.days // 30} mois"
        if diff.days > 0:
            return f"il y a {diff.days} jours"
        if diff.seconds > 3600:
            return f"il y a {diff.seconds // 3600} heures"
        if diff.seconds > 60:
            return f"il y a {diff.seconds // 60} minutes"
        return "à l'instant"
    
    return value.strftime(format)

# Routes principales
@app.route('/')
def accueil():
    """Page d'accueil de l'application"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'inscription: {e}")
            flash('Une erreur est survenue lors de la création du compte. Veuillez réessayer.', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion d'un utilisateur existant"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Connexion réussie !', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Connexion échouée. Veuillez vérifier votre email et votre mot de passe.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Déconnexion de l'utilisateur"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('accueil'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord de l'utilisateur connecté"""
    # Récupérer les statistiques du réseau
    network_stats = security_scoring.get_network_security_status()
    
    # Récupérer tous les appareils avec leurs scores
    device_scores = security_scoring.get_all_device_scores()
    
    # Trier les appareils par score de sécurité (du plus bas au plus élevé)
    device_scores.sort(key=lambda x: x['security_score'])
    
    return render_template(
        'dashboard.html',
        network_stats=network_stats,
        device_scores=device_scores
    )

@app.route('/network-topology')
@login_required
def network_topology_view():
    """Vue de la topologie du réseau"""
    form = SaveTopologyForm()
    return render_template('network_topology.html', form=form)

@app.route('/topology/save', methods=['POST'])
@login_required
def save_topology():
    """Sauvegarde de la topologie réseau"""
    form = SaveTopologyForm()
    
    if form.validate_on_submit():
        try:
            # Récupérer les données de disposition des appareils
            layout_data = json.loads(request.form.get('layout_data', '{}'))
            
            # Créer une nouvelle topologie sauvegardée
            topology = SavedTopology(
                user_id=current_user.id,
                name=form.name.data,
                layout_data=json.dumps(layout_data)
            )
            
            db.session.add(topology)
            db.session.commit()
            
            flash('Disposition sauvegardée avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la sauvegarde de la topologie: {e}")
            flash('Une erreur est survenue lors de la sauvegarde.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('network_topology_view'))

# Routes API
@app.route('/api/topology')
@login_required
def get_topology():
    """API pour récupérer les données de topologie réseau"""
    topology_data = network_topology.get_topology_data()
    return jsonify(topology_data)

@app.route('/api/topology/layout', methods=['POST'])
@login_required
def update_topology_layout():
    """API pour mettre à jour la disposition des appareils"""
    data = request.json
    
    if not data or 'mac_address' not in data or 'x' not in data or 'y' not in data:
        return jsonify({'success': False, 'error': 'Données invalides'})
    
    try:
        network_topology.save_layout(data)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la disposition: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/topology/layout/save', methods=['POST'])
@login_required
def save_topology_layout():
    """API pour sauvegarder une disposition de topologie"""
    data = request.json
    
    if not data or 'name' not in data or 'layout' not in data:
        return jsonify({'success': False, 'error': 'Données invalides'})
    
    try:
        # Créer une nouvelle topologie sauvegardée
        topology = SavedTopology(
            user_id=current_user.id,
            name=data['name'],
            layout_data=json.dumps(data['layout'])
        )
        
        db.session.add(topology)
        db.session.commit()
        
        return jsonify({'success': True, 'id': topology.id})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la sauvegarde de la disposition: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/device/<mac_address>')
@login_required
def get_device_details(mac_address):
    """API pour récupérer les détails d'un appareil spécifique"""
    device = None
    
    # Rechercher dans les données de topologie
    for d in network_topology.topology_data['devices']:
        if d['mac_address'] == mac_address:
            device = d
            break
    
    if not device:
        return jsonify({'success': False, 'error': 'Appareil non trouvé'})
    
    # Ajouter les données de sécurité
    security_info = security_scoring.get_device(mac_address)
    if security_info:
        device.update({
            'security_issues': security_info.get('security_issues', []),
            'recommendations': security_info.get('recommendations', [])
        })
    
    return jsonify({'success': True, 'device': device})

@app.route('/api/device/<mac_address>/security', methods=['GET'])
@login_required
def update_device_security(mac_address):
    """API pour mettre à jour les informations de sécurité d'un appareil"""
    # Calculer un nouveau score de sécurité pour l'appareil
    new_score = security_scoring.calculate_device_score(mac_address)
    
    if new_score is None:
        return jsonify({'success': False, 'error': 'Appareil non trouvé'})
    
    # Mettre à jour les données de topologie
    device_data = security_scoring.get_device(mac_address)
    if device_data:
        network_topology.update_device_security(mac_address, {
            'security_score': device_data['security_score'],
            'security_issues': device_data.get('security_issues', [])
        })
    
    # Émettre une mise à jour via Socket.IO
    socketio.emit('device_update', {
        'mac_address': mac_address,
        'security_score': new_score,
        'last_updated': datetime.now().isoformat()
    })
    
    return jsonify({'success': True, 'new_score': new_score})

# Routes pour l'assistant de sécurité
@app.route('/assistant', methods=['GET', 'POST'])
@login_required
def assistant():
    """Page de l'assistant de sécurité (ancienne version)"""
    if request.method == 'POST':
        user_input = request.form.get('question', '')
        if user_input:
            # Récupérer les données de topologie pour le contexte
            network_data = network_topology.get_topology_data()
            
            # Générer une réponse
            response = assistant_securite.generate_response(
                user_input, 
                conversation_id=current_user.id,
                network_data=network_data
            )
            
            return jsonify({'success': True, 'response': response})
        else:
            return jsonify({'success': False, 'error': 'Question vide'})
    
    # Récupérer l'historique des conversations
    conversations = assistant_securite.get_conversation_history(current_user.id)
    
    return render_template('assistant.html', conversations=conversations)

@app.route('/chatbot')
@login_required
def chatbot():
    """Page du chatbot de sécurité (nouvelle version)"""
    return render_template('chatbot.html')

@app.route('/api/chatbot', methods=['POST'])
@login_required
def api_chatbot():
    """API pour l'interaction avec le chatbot"""
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Message manquant'}), 400
    
    user_input = data['message']
    conversation_id = data.get('conversation_id', None)
    
    # Si aucun ID de conversation n'est fourni, en créer un nouveau basé sur l'ID utilisateur et l'horodatage
    if not conversation_id:
        conversation_id = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Récupérer les données de topologie pour le contexte
    network_data = network_topology.get_topology_data()
    
    # Générer une réponse
    result = assistant_securite.generate_response(
        user_input, 
        conversation_id=conversation_id,
        network_data=network_data
    )
    
    return jsonify(result)

@app.route('/api/chatbot/history')
@login_required
def api_chatbot_history():
    """API pour récupérer l'historique des conversations"""
    conversations = assistant_securite.get_all_conversations()
    return jsonify(conversations)

@app.route('/api/chatbot/conversation/<conversation_id>')
@login_required
def api_chatbot_conversation(conversation_id):
    """API pour récupérer une conversation spécifique"""
    conversation = assistant_securite.get_conversation_history(conversation_id)
    return jsonify(conversation)

@app.route('/vulnerability-analysis')
@login_required
def vulnerability_analysis():
    """Page d'analyse des vulnérabilités"""
    return render_template('vulnerability_analysis.html')

@app.route('/security-report')
@login_required
def security_report():
    """Page de rapport détaillé de sécurité"""
    return render_template('security_report.html')

@app.route('/protocol-analysis')
@login_required
def protocol_analysis():
    """Page d'analyse des protocoles de sécurité WiFi"""
    from protocol_analyzer import ProtocolAnalyzer
    
    # Initialiser l'analyseur de protocoles
    analyzer = ProtocolAnalyzer()
    
    # Récupérer les données d'exemple pour la démonstration
    # Dans une implémentation réelle, ces données viendraient d'une analyse réseau
    test_networks = [
        {
            "ssid": "Réseau_Domicile",
            "bssid": "00:11:22:33:44:55",
            "security": "WPA2",
            "encryption": "AES",
            "authentication": "PSK",
            "strength": -65,
            "frequency": "2.4GHz",
            "channel": 6
        },
        {
            "ssid": "Réseau_Ancien",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "security": "WEP",
            "encryption": None,
            "authentication": None,
            "strength": -70,
            "frequency": "2.4GHz",
            "channel": 11
        },
        {
            "ssid": "Réseau_Invité",
            "bssid": "11:22:33:44:55:66",
            "security": "OPEN",
            "encryption": None,
            "authentication": None,
            "strength": -60,
            "frequency": "2.4GHz",
            "channel": 1
        },
        {
            "ssid": "Réseau_Enterprise",
            "bssid": "22:33:44:55:66:77",
            "security": "WPA2",
            "encryption": "AES",
            "authentication": "ENTERPRISE",
            "strength": -55,
            "frequency": "5GHz",
            "channel": 36
        },
        {
            "ssid": "Réseau_Moderne",
            "bssid": "33:44:55:66:77:88",
            "security": "WPA3",
            "encryption": "GCMP",
            "authentication": "SAE",
            "strength": -50,
            "frequency": "5GHz",
            "channel": 48
        }
    ]
    
    # Analyser les réseaux
    analysis_results = analyzer.analyze_all_networks(test_networks)
    
    # Récupérer le résumé global
    summary = analyzer.get_protocol_analysis_summary()
    
    # Récupérer la comparaison des protocoles
    protocol_comparison = analyzer.get_protocol_comparison()
    
    # Récupérer la chronologie des analyses
    timeline = analyzer.get_protocol_timeline()
    
    return render_template(
        'protocol_analysis.html',
        analysis_results=analysis_results,
        summary=summary,
        protocol_comparison=protocol_comparison,
        timeline=timeline
    )

@app.route('/export-infographic/<report_type>')
@login_required
def export_infographic(report_type):
    """Génère et exporte une infographie basée sur le type de rapport"""
    from infographic_generator import InfographicGenerator
    from protocol_analyzer import ProtocolAnalyzer
    
    # Initialiser le générateur d'infographies
    generator = InfographicGenerator()
    
    # Chemin du fichier infographique généré
    output_path = None
    
    # Selon le type de rapport, générer l'infographie appropriée
    if report_type == 'network_security':
        # Exemple de données de réseau pour la démonstration
        network_data = {
            'overall_score': 72,
            'protocol_distribution': {
                'WPA3': 1,
                'WPA2': 3,
                'WPA': 0,
                'WEP': 1,
                'OPEN': 1
            },
            'security_dimensions': {
                'Authentification': 65,
                'Chiffrement': 70,
                'Mises à jour': 50,
                'Pare-feu': 85,
                'Segmentation': 90,
                'Monitoring': 60
            },
            'devices': [
                {'name': 'Caméra IP', 'security_score': 35},
                {'name': 'Smart TV', 'security_score': 55},
                {'name': 'Smartphone', 'security_score': 65},
                {'name': 'Routeur WiFi', 'security_score': 75},
                {'name': 'Ordinateur portable', 'security_score': 85}
            ],
            'security_trend': [
                {'date': 'Jan', 'score': 54},
                {'date': 'Fév', 'score': 58},
                {'date': 'Mar', 'score': 60},
                {'date': 'Avr', 'score': 65},
                {'date': 'Mai', 'score': 68},
                {'date': 'Juin', 'score': 72}
            ]
        }
        
        # Exemple de données de vulnérabilité
        vulnerability_data = {
            'vulnerability_types': {
                'firmware_outdated': 8,
                'weak_password': 6,
                'open_ports': 5,
                'protocol_weakness': 5,
                'missing_updates': 4,
                'default_credentials': 4
            },
            'recommendations': [
                {
                    'priority': 'critical',
                    'description': 'Mettre à jour le firmware du routeur',
                    'details': 'Votre routeur exécute un firmware obsolète contenant des vulnérabilités connues.'
                },
                {
                    'priority': 'high',
                    'description': 'Changer les mots de passe par défaut',
                    'details': 'Plusieurs appareils IoT utilisent encore leurs mots de passe par défaut.'
                },
                {
                    'priority': 'medium',
                    'description': 'Activer WPA3 sur votre réseau WiFi',
                    'details': 'Passer à WPA3 offre une meilleure protection contre les attaques.'
                }
            ]
        }
        
        # Générer l'infographie
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"network_security_{timestamp}.png"
        output_path = generator.generate_network_security_infographic(
            network_data, vulnerability_data, output_filename=filename
        )
    
    elif report_type == 'protocol_analysis':
        # Initialiser l'analyseur de protocoles
        analyzer = ProtocolAnalyzer()
        
        # Récupérer les données d'exemple
        test_networks = [
            {
                "ssid": "Réseau_Domicile",
                "bssid": "00:11:22:33:44:55",
                "security": "WPA2",
                "encryption": "AES",
                "authentication": "PSK",
                "strength": -65,
                "frequency": "2.4GHz",
                "channel": 6
            },
            {
                "ssid": "Réseau_Ancien",
                "bssid": "AA:BB:CC:DD:EE:FF",
                "security": "WEP",
                "encryption": None,
                "authentication": None,
                "strength": -70,
                "frequency": "2.4GHz",
                "channel": 11
            },
            {
                "ssid": "Réseau_Moderne",
                "bssid": "33:44:55:66:77:88",
                "security": "WPA3",
                "encryption": "GCMP",
                "authentication": "SAE",
                "strength": -50,
                "frequency": "5GHz",
                "channel": 48
            }
        ]
        
        # Analyser les réseaux
        analyzer.analyze_all_networks(test_networks)
        
        # Préparer les données pour l'infographie
        protocol_data = {
            'average_score': analyzer.get_protocol_analysis_summary().get('average_score', 0),
            'protocol_distribution': analyzer.get_protocol_analysis_summary().get('protocol_distribution', {}),
            'protocols': analyzer.get_protocol_comparison().get('protocols', []),
            'vulnerability_by_protocol': {
                'WEP': {'critical': 5, 'high': 3, 'medium': 1, 'low': 0},
                'WPA': {'critical': 2, 'high': 4, 'medium': 2, 'low': 1},
                'WPA2': {'critical': 1, 'high': 2, 'medium': 3, 'low': 2},
                'WPA3': {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            },
            'protocol_strengths': {
                'WEP': {'Chiffrement': 10, 'Authentification': 15, 'Intégrité': 20, 'Résistance aux attaques': 5, 'Gestion des clés': 10},
                'WPA': {'Chiffrement': 40, 'Authentification': 45, 'Intégrité': 50, 'Résistance aux attaques': 35, 'Gestion des clés': 40},
                'WPA2': {'Chiffrement': 75, 'Authentification': 70, 'Intégrité': 80, 'Résistance aux attaques': 65, 'Gestion des clés': 70},
                'WPA3': {'Chiffrement': 90, 'Authentification': 95, 'Intégrité': 90, 'Résistance aux attaques': 85, 'Gestion des clés': 90}
            },
            'recommendations': analyzer.get_protocol_analysis_summary().get('recommendations', [])
        }
        
        # Générer l'infographie
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"protocol_analysis_{timestamp}.png"
        output_path = generator.generate_protocol_analysis_infographic(
            protocol_data, output_filename=filename
        )
    
    elif report_type == 'vulnerability_report':
        # Exemple de données de vulnérabilité
        vulnerability_data = {
            'summary': {
                'total': 32,
                'critical': 3,
                'high': 8,
                'medium': 15,
                'low': 6,
                'cvss_avg': 7.8,
                'risk_level': 'Élevé'
            },
            'critical_vulnerabilities': [
                {
                    'cve_id': 'CVE-2022-26928',
                    'description': 'Vulnérabilité d\'exécution de code à distance dans le firmware',
                    'severity': 'critical',
                    'cvss_score': 9.8,
                    'affected_device': 'Routeur WiFi Principal',
                    'status': 'Non corrigé'
                },
                {
                    'cve_id': 'CVE-2021-37714',
                    'description': 'Identifiants par défaut exposés permettant un accès non autorisé',
                    'severity': 'critical',
                    'cvss_score': 9.6,
                    'affected_device': 'Caméra IP',
                    'status': 'Non corrigé'
                },
                {
                    'cve_id': 'CVE-2023-12345',
                    'description': 'Vulnérabilité de débordement de tampon dans le traitement des paquets réseau',
                    'severity': 'critical',
                    'cvss_score': 9.1,
                    'affected_device': 'Smart TV',
                    'status': 'Non corrigé'
                }
            ],
            'severity_distribution': {
                'critical': 3,
                'high': 8,
                'medium': 15,
                'low': 6
            },
            'discovery_timeline': [
                {'date': 'Jan', 'total': 2, 'critical': 0},
                {'date': 'Fév', 'total': 5, 'critical': 1},
                {'date': 'Mar', 'total': 3, 'critical': 0},
                {'date': 'Avr', 'total': 8, 'critical': 2},
                {'date': 'Mai', 'total': 6, 'critical': 0},
                {'date': 'Juin', 'total': 8, 'critical': 1}
            ],
            'remediation_plan': [
                {
                    'action': 'Mettre à jour le firmware du routeur',
                    'priority': 'critical',
                    'estimated_time': '30 minutes',
                    'difficulty': 'Facile',
                    'impact': 'Élimine une vulnérabilité critique'
                },
                {
                    'action': 'Changer les mots de passe par défaut',
                    'priority': 'critical',
                    'estimated_time': '20 minutes',
                    'difficulty': 'Facile',
                    'impact': 'Sécurise les appareils IoT vulnérables'
                },
                {
                    'action': 'Activer WPA3',
                    'priority': 'high',
                    'estimated_time': '10 minutes',
                    'difficulty': 'Facile',
                    'impact': 'Renforce la sécurité du WiFi'
                },
                {
                    'action': 'Configurer un réseau invité',
                    'priority': 'medium',
                    'estimated_time': '15 minutes',
                    'difficulty': 'Moyenne',
                    'impact': 'Isole les appareils IoT du réseau principal'
                }
            ]
        }
        
        # Générer l'infographie
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vulnerability_report_{timestamp}.png"
        output_path = generator.generate_vulnerability_report_infographic(
            vulnerability_data, output_filename=filename
        )
    
    else:
        # Type de rapport non pris en charge
        flash('Type de rapport non pris en charge', 'danger')
        return redirect(url_for('dashboard'))
    
    # Vérifier si l'infographie a été générée
    if not output_path or not os.path.exists(output_path):
        flash('Erreur lors de la génération de l\'infographie', 'danger')
        return redirect(url_for('dashboard'))
    
    # Retourner le chemin relatif pour servir le fichier
    relative_path = output_path.replace('static/', '')
    
    # Enregistrer le téléchargement dans l'historique de l'utilisateur
    # Cette partie serait implémentée dans une version complète
    
    # Rediriger vers la page de visualisation avec un message de succès
    flash('Infographie générée avec succès', 'success')
    return render_template('export_success.html', image_path=relative_path)


@app.route('/api/export-infographic/<report_type>', methods=['POST'])
@login_required
def api_export_infographic(report_type):
    """API pour générer une infographie et retourner son URL"""
    # Cette route est appelée par AJAX pour générer l'infographie en arrière-plan
    
    try:
        # Rediriger vers la route normale qui génère l'infographie
        response_url = url_for('export_infographic', report_type=report_type)
        
        return jsonify({
            'success': True,
            'message': 'Génération de l\'infographie en cours...',
            'redirect_url': response_url
        })
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'infographie: {e}")
        return jsonify({
            'success': False,
            'message': f"Erreur lors de la génération: {str(e)}"
        }), 500

# Gestionnaires d'événements Socket.IO
@socketio.on('connect')
def handle_connect():
    """Gestion de la connexion WebSocket"""
    logger.info(f"Client connecté: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Gestion de la déconnexion WebSocket"""
    logger.info(f"Client déconnecté: {request.sid}")

@socketio.on('request_topology')
def handle_topology_request():
    """Envoi des données de topologie au client"""
    topology_data = network_topology.get_topology_data()
    emit('topology_data', topology_data)

@socketio.on('update_layout')
def handle_layout_update(data):
    """Mise à jour de la disposition des appareils"""
    if 'mac_address' in data and 'x' in data and 'y' in data:
        try:
            network_topology.save_layout(data)
            # Émettre la mise à jour à tous les clients
            emit('layout_update', {data['mac_address']: {'x': data['x'], 'y': data['y']}}, broadcast=True)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la disposition: {e}")

@socketio.on('update_device_security')
def handle_device_security_update(data):
    """Mise à jour des informations de sécurité d'un appareil"""
    if 'mac_address' in data:
        mac_address = data['mac_address']
        # Calculer un nouveau score de sécurité
        new_score = security_scoring.calculate_device_score(mac_address)
        
        if new_score is not None:
            # Mettre à jour les données de topologie
            device_data = security_scoring.get_device(mac_address)
            if device_data:
                network_topology.update_device_security(mac_address, {
                    'security_score': device_data['security_score'],
                    'security_issues': device_data.get('security_issues', [])
                })
            
            # Émettre la mise à jour à tous les clients
            emit('device_update', {
                'mac_address': mac_address,
                'security_score': new_score,
                'last_updated': datetime.now().isoformat()
            }, broadcast=True)

# Initialiser le système de gamification
gamification = SecurityGamification()

# Routes pour le tableau de bord de sécurité gamifié
@app.route('/security-game')
@login_required
def security_game():
    """Tableau de bord de sécurité gamifié avec système de points et récompenses"""
    # Récupérer les statistiques du réseau
    network_stats = security_scoring.get_network_security_status()
    
    # Initialiser l'utilisateur dans le système de gamification s'il ne l'est pas déjà
    gamification.initialize_user(current_user.id)
    
    # Mettre à jour le score de l'utilisateur en fonction des statistiques de sécurité
    progress_data = gamification.update_score_from_security(current_user.id, network_stats)
    
    # Récupérer toutes les données de gamification de l'utilisateur
    user_data = gamification.get_user_gamification_data(current_user.id)
    
    # Obtenir le classement
    leaderboard = gamification.get_leaderboard(limit=5)
    
    # Récupérer les noms d'utilisateur pour le classement
    leaderboard_users = {}
    for entry in leaderboard:
        try:
            user = User.query.get(int(entry['user_id']))
            if user:
                leaderboard_users[entry['user_id']] = user.username
            else:
                leaderboard_users[entry['user_id']] = f"Utilisateur {entry['user_id']}"
        except:
            leaderboard_users[entry['user_id']] = f"Utilisateur {entry['user_id']}"
    
    # Déterminer les titres basés sur les scores
    level = user_data['scores']['level']
    if level >= 20:
        user_title = "Légende de la Sécurité"
    elif level >= 15:
        user_title = "Expert en Cyber-Sécurité"
    elif level >= 10:
        user_title = "Maître des Défenses"
    elif level >= 5:
        user_title = "Protecteur du Réseau"
    else:
        user_title = "Gardien Novice"
    
    overall_score = network_stats['overall_score']
    if overall_score >= 90:
        score_title = "Sécurité Exemplaire"
    elif overall_score >= 80:
        score_title = "Très Bonne Sécurité"
    elif overall_score >= 70:
        score_title = "Bonne Sécurité"
    elif overall_score >= 50:
        score_title = "Sécurité Moyenne"
    else:
        score_title = "Sécurité à Risque"
    
    # Définir un filtre pour convertir les chaînes ISO en objets datetime
    @app.template_filter('from_isoformat')
    def from_isoformat(value):
        if not value:
            return datetime.now()
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return datetime.now()
    
    return render_template(
        'security_game.html',
        network_stats=network_stats,
        user_data=user_data,
        xp_gain=progress_data.get('xp_gain', 0),
        level_up=progress_data.get('level_up'),
        new_achievements=progress_data.get('new_achievements', []),
        challenge_progress=progress_data.get('challenge_progress', []),
        leaderboard=leaderboard,
        leaderboard_users=leaderboard_users,
        user_title=user_title,
        score_title=score_title
    )

@app.route('/perform-network-scan')
@login_required
def perform_network_scan():
    """Effectue une analyse du réseau et attribue des points d'expérience"""
    # Simuler une détection de réseau
    security_scoring.detect_devices()
    
    # Récupérer les statistiques du réseau après l'analyse
    network_stats = security_scoring.get_network_security_status()
    
    # Mettre à jour le score de l'utilisateur avec des points bonus pour l'analyse
    fixed_issues = []  # Simulation de problèmes résolus
    progress_data = gamification.update_score_from_security(current_user.id, network_stats, fixed_issues)
    
    # Ajouter des points supplémentaires pour l'action d'analyse
    gamification._add_xp(str(current_user.id), 30)
    
    flash('Analyse du réseau effectuée avec succès ! +30 XP', 'success')
    return redirect(url_for('security_game'))

@app.route('/fix-security-issues')
@login_required
def fix_security_issues():
    """Simule la correction de problèmes de sécurité et attribue des récompenses"""
    # Récupérer tous les appareils avec leurs scores
    device_scores = security_scoring.get_all_device_scores()
    
    # Filtrer les appareils avec des scores de sécurité faibles
    low_security_devices = [d for d in device_scores if d['security_score'] < 60]
    
    fixed_issues = []
    xp_gained = 0
    
    # Pour chaque appareil à faible sécurité, simuler une amélioration
    for device in low_security_devices[:min(3, len(low_security_devices))]:
        # Récupérer les détails de l'appareil
        device_data = security_scoring.get_device(device['mac_address'])
        
        if device_data and device_data.get('security_issues'):
            # Simuler la résolution d'un problème de sécurité aléatoire
            issue_to_fix = random.choice(device_data['security_issues'])
            fixed_issues.append(issue_to_fix)
            
            # Attribuer des points selon la sévérité
            if issue_to_fix['severity'] == 'high':
                xp_gained += 50
            elif issue_to_fix['severity'] == 'medium':
                xp_gained += 25
            else:
                xp_gained += 10
            
            # Augmenter le score de sécurité de l'appareil
            new_score = min(100, device_data['security_score'] + random.randint(5, 15))
            device_data['security_score'] = new_score
            
            # Mettre à jour les problèmes de sécurité (supprimer celui qui a été résolu)
            device_data['security_issues'] = [issue for issue in device_data['security_issues'] if issue['id'] != issue_to_fix['id']]
            
            # Mettre à jour les données de topologie
            network_topology.update_device_security(device['mac_address'], {
                'security_score': new_score,
                'security_issues': device_data['security_issues']
            })
    
    # Sauvegarder les modifications
    security_scoring.save_devices()
    
    # Mettre à jour les statistiques du réseau après les corrections
    network_stats = security_scoring.get_network_security_status()
    
    # Mettre à jour le score de l'utilisateur avec les problèmes résolus
    progress_data = gamification.update_score_from_security(current_user.id, network_stats, fixed_issues)
    
    if fixed_issues:
        flash(f'{len(fixed_issues)} problèmes de sécurité corrigés ! +{xp_gained} XP', 'success')
    else:
        flash('Aucun problème de sécurité critique à corriger.', 'info')
    
    return redirect(url_for('security_game'))

@app.route('/api/gamification/user-data')
@login_required
def api_gamification_user_data():
    """API pour récupérer les données de gamification de l'utilisateur"""
    user_data = gamification.get_user_gamification_data(current_user.id)
    return jsonify(user_data)

@app.route('/api/gamification/leaderboard')
@login_required
def api_gamification_leaderboard():
    """API pour récupérer le classement"""
    leaderboard = gamification.get_leaderboard()
    
    # Récupérer les noms d'utilisateur pour le classement
    for entry in leaderboard:
        try:
            user = User.query.get(int(entry['user_id']))
            if user:
                entry['username'] = user.username
            else:
                entry['username'] = f"Utilisateur {entry['user_id']}"
        except:
            entry['username'] = f"Utilisateur {entry['user_id']}"
    
    return jsonify(leaderboard)

# Gestionnaires d'erreurs
@app.errorhandler(404)
def page_non_trouvee(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def erreur_serveur(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Route pour obtenir les statistiques mémoire
@app.route('/api/memory-stats')
@login_required
def memory_stats():
    """Récupère les statistiques d'utilisation de la mémoire"""
    memory_info = MemoryMonitor.log_memory_usage()
    return jsonify(memory_info)

# Nouvelle route pour l'analyse IA
@app.route('/ai-analysis')
@login_required
def ai_analysis():
    """Page d'analyse avancée avec Intelligence Artificielle"""
    # Récupérer les données de topologie pour l'analyse
    topology_data = network_topology.get_topology_data()
    
    # Utiliser le module d'IA pour l'analyse et l'optimisation
    optimization_results = network_optimizer.optimize_network_security(topology_data)
    
    # Récupérer des données wifi de test
    test_networks = [
        {
            "ssid": "Réseau_Domicile",
            "bssid": "00:11:22:33:44:55",
            "security": "WPA2",
            "encryption": "AES",
            "authentication": "PSK",
            "strength": -65,
            "frequency": "2.4GHz",
            "channel": 6
        },
        {
            "ssid": "Réseau_Ancien",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "security": "WEP",
            "encryption": None,
            "authentication": None,
            "strength": -70,
            "frequency": "2.4GHz",
            "channel": 11
        },
        {
            "ssid": "Réseau_Invité",
            "bssid": "11:22:33:44:55:66",
            "security": "OPEN",
            "encryption": None,
            "authentication": None,
            "strength": -60,
            "frequency": "2.4GHz",
            "channel": 1
        }
    ]
    
    # Analyser les réseaux WiFi
    wifi_analysis = security_ai.analyze_wifi_security(test_networks)
    
    return render_template(
        'ai_analysis.html',
        optimization_results=optimization_results,
        wifi_analysis=wifi_analysis
    )

# Nouvelle route pour l'assistant intelligent d'optimisation de sécurité
@app.route('/security-assistant')
@login_required
def intelligent_security_assistant():
    """Assistant Intelligent d'Optimisation de Sécurité"""
    # Récupérer les données de topologie pour l'analyse
    topology_data = network_topology.get_topology_data()
    
    # Récupérer des données wifi de test
    test_networks = [
        {
            "ssid": "Réseau_Domicile",
            "bssid": "00:11:22:33:44:55",
            "security": "WPA2",
            "encryption": "AES",
            "authentication": "PSK",
            "strength": -65,
            "frequency": "2.4GHz",
            "channel": 6
        },
        {
            "ssid": "Réseau_Ancien",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "security": "WEP",
            "encryption": None,
            "authentication": None,
            "strength": -70,
            "frequency": "2.4GHz",
            "channel": 11
        },
        {
            "ssid": "Réseau_Invité",
            "bssid": "11:22:33:44:55:66",
            "security": "OPEN",
            "encryption": None,
            "authentication": None,
            "strength": -60,
            "frequency": "2.4GHz",
            "channel": 1
        }
    ]
    
    # Générer une évaluation complète de la sécurité
    assessment_results = security_assistant.generate_security_assessment(topology_data, test_networks)
    
    # Récupérer les tendances historiques si disponibles
    historical_trends = security_assistant.get_historical_trends()
    
    return render_template(
        'security_assistant.html',
        assessment_results=assessment_results,
        historical_trends=historical_trends
    )

@app.route('/api/optimize-network')
@login_required
def api_optimize_network():
    """API pour obtenir des recommandations d'optimisation du réseau"""
    # Récupérer les données de topologie
    topology_data = network_topology.get_topology_data()
    
    # Analyser et optimiser la sécurité du réseau
    optimization_results = network_optimizer.optimize_network_security(topology_data)
    
    return jsonify(optimization_results)

@app.route('/api/analyze-wifi')
@login_required
def api_analyze_wifi():
    """API pour analyser la sécurité des réseaux WiFi"""
    # Dans une implémentation réelle, ces données viendraient d'une analyse réseau
    # Pour la démonstration, utiliser des données d'exemple
    test_networks = [
        {
            "ssid": "Réseau_Domicile",
            "bssid": "00:11:22:33:44:55",
            "security": "WPA2",
            "encryption": "AES",
            "authentication": "PSK",
            "strength": -65,
            "frequency": "2.4GHz",
            "channel": 6
        },
        {
            "ssid": "Réseau_Ancien",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "security": "WEP",
            "encryption": None,
            "authentication": None,
            "strength": -70,
            "frequency": "2.4GHz",
            "channel": 11
        }
    ]
    
    # Analyser les réseaux WiFi
    wifi_analysis = security_ai.analyze_wifi_security(test_networks)
    
    return jsonify(wifi_analysis)

@app.route('/security-radar')
@login_required
def security_radar():
    """Visualisation interactive du radar de sécurité"""
    # Récupérer les données de topologie pour l'analyse
    topology_data = network_topology.get_topology_data()
    
    # Récupérer des données wifi de test
    test_networks = [
        {
            "ssid": "Réseau_Domicile",
            "bssid": "00:11:22:33:44:55",
            "security": "WPA2",
            "encryption": "AES",
            "authentication": "PSK",
            "strength": -65,
            "frequency": "2.4GHz",
            "channel": 6
        },
        {
            "ssid": "Réseau_Ancien",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "security": "WEP",
            "encryption": None,
            "authentication": None,
            "strength": -70,
            "frequency": "2.4GHz",
            "channel": 11
        },
        {
            "ssid": "Réseau_Entreprise",
            "bssid": "22:33:44:55:66:77",
            "security": "WPA2-Enterprise",
            "encryption": "AES",
            "authentication": "ENTERPRISE",
            "strength": -55,
            "frequency": "5GHz",
            "channel": 36
        },
        {
            "ssid": "Réseau_Public",
            "bssid": "11:22:33:44:55:66",
            "security": "OPEN",
            "encryption": None,
            "authentication": None,
            "strength": -60,
            "frequency": "2.4GHz",
            "channel": 1
        },
        {
            "ssid": "Réseau_Moderne",
            "bssid": "33:44:55:66:77:88",
            "security": "WPA3",
            "encryption": "GCMP",
            "authentication": "SAE",
            "strength": -50,
            "frequency": "5GHz",
            "channel": 48
        }
    ]
    
    # Analyser les réseaux WiFi
    wifi_analysis = security_ai.analyze_wifi_security(test_networks)
    
    # Analyser l'optimisation du réseau
    optimization_results = network_optimizer.optimize_network_security(topology_data)
    
    # Générer des données de comparaison historiques pour démonstration
    historical_data = [
        {
            "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "dimensions": {
                "protocol": 65.0,
                "encryption": 70.0,
                "authentication": 60.0,
                "password": 55.0,
                "privacy": 50.0
            }
        },
        {
            "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            "dimensions": {
                "protocol": 70.0,
                "encryption": 75.0,
                "authentication": 65.0,
                "password": 60.0,
                "privacy": 55.0
            }
        },
        {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "dimensions": wifi_analysis.get('security_dimensions', {})
        }
    ]
    
    return render_template(
        'security_radar.html',
        wifi_analysis=wifi_analysis,
        optimization_results=optimization_results,
        historical_data=historical_data,
        networks=test_networks
    )

# Ajout d'une route API pour notre assistant intelligent
@app.route('/api/security-assistant/assessment', methods=['POST'])
@login_required
def api_security_assessment():
    """API pour obtenir une évaluation complète de la sécurité"""
    # Récupérer les données de topologie
    topology_data = network_topology.get_topology_data()
    
    # Dans une implémentation réelle, ces données viendraient d'une analyse réseau
    # Pour la démonstration, utiliser des données d'exemple
    test_networks = [
        {
            "ssid": "Réseau_Domicile",
            "bssid": "00:11:22:33:44:55",
            "security": "WPA2",
            "encryption": "AES",
            "authentication": "PSK",
            "strength": -65,
            "frequency": "2.4GHz",
            "channel": 6
        },
        {
            "ssid": "Réseau_Ancien",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "security": "WEP",
            "encryption": None,
            "authentication": None,
            "strength": -70,
            "frequency": "2.4GHz",
            "channel": 11
        },
        {
            "ssid": "Réseau_Invité",
            "bssid": "11:22:33:44:55:66",
            "security": "OPEN",
            "encryption": None,
            "authentication": None,
            "strength": -60,
            "frequency": "2.4GHz",
            "channel": 1
        }
    ]
    
    # Générer une évaluation complète de la sécurité
    assessment_results = security_assistant.generate_security_assessment(topology_data, test_networks)
    
    return jsonify(assessment_results)

@app.route('/api/security-assistant/trends')
@login_required
def api_security_trends():
    """API pour obtenir les tendances historiques de sécurité"""
    historical_trends = security_assistant.get_historical_trends()
    return jsonify(historical_trends)

@app.route('/api/security-assistant/chatbot', methods=['POST'])
@login_required
def api_security_assistant_chatbot():
    """API pour interagir avec le chatbot de l'assistant intelligent"""
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Message manquant'}), 400
    
    user_input = data['message']
    
    # Récupérer les données de topologie pour le contexte
    topology_data = network_topology.get_topology_data()
    
    # Récupérer des données wifi de test
    test_networks = [
        {
            "ssid": "Réseau_Domicile",
            "bssid": "00:11:22:33:44:55",
            "security": "WPA2",
            "encryption": "AES",
            "authentication": "PSK",
            "strength": -65,
            "frequency": "2.4GHz",
            "channel": 6
        },
        {
            "ssid": "Réseau_Ancien",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "security": "WEP",
            "encryption": None,
            "authentication": None,
            "strength": -70,
            "frequency": "2.4GHz",
            "channel": 11
        }
    ]
    
    # Générer une réponse enrichie avec l'IA
    response = security_assistant.generate_chatbot_response(user_input, topology_data, test_networks)
    
    return jsonify({
        'success': True,
        'response': response
    })

# Routes pour le système de détection et correction auto IA
@app.route('/ai-error-detection')
@login_required
def ai_error_detection():
    """Page de détection automatique des erreurs réseau par IA"""
    # Récupérer les clones actifs
    clones = ai_clone_manager.get_all_clones()
    
    # Récupérer les données de topologie pour l'analyse
    topology_data = network_topology.get_topology_data()
    
    # Initialiser l'AIErrorHandler pour la détection manuelle des erreurs
    error_handler = AIErrorHandler()
    detected_errors = error_handler.detect_errors(topology_data)
    
    # Générer des solutions pour les erreurs détectées
    solutions = error_handler.generate_solutions(detected_errors)
    
    # Statistiques des erreurs - s'assurer que error_stats a la structure attendue
    error_stats = error_handler.get_error_statistics()
    
    # Si error_stats n'a pas la structure attendue, initialiser avec des valeurs par défaut
    if not error_stats:
        error_stats = {
            'types': {'connectivity': 2, 'security': 3, 'performance': 1, 'configuration': 1},
            'severity': {'high': 2, 'medium': 3, 'low': 2},
            'unresolved': 5,
            'fixed': 2
        }
    
    # S'assurer que les clés nécessaires existent
    if 'types' not in error_stats:
        error_stats['types'] = {'connectivity': 2, 'security': 3, 'performance': 1, 'configuration': 1}
    if 'severity' not in error_stats:
        error_stats['severity'] = {'high': 2, 'medium': 3, 'low': 2}
    if 'unresolved' not in error_stats:
        error_stats['unresolved'] = 5
    if 'fixed' not in error_stats:
        error_stats['fixed'] = 2
    
    return render_template(
        'ai_error_detection.html',
        clones=clones,
        detected_errors=detected_errors,
        solutions=solutions,
        error_stats=error_stats
    )

@app.route('/api/ai-error-detection', methods=['POST'])
@login_required
def api_ai_error_detection():
    """API pour la détection d'erreurs réseau"""
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'error': 'Données manquantes'}), 400
    
    # Récupérer les données de topologie
    topology_data = network_topology.get_topology_data()
    
    # Récupérer les logs si fournis
    logs = data.get('logs', [])
    
    # Initialiser l'AIErrorHandler
    error_handler = AIErrorHandler()
    
    # Détecter les erreurs
    detected_errors = error_handler.detect_errors(topology_data, logs)
    
    # Générer des solutions
    solutions = error_handler.generate_solutions(detected_errors)
    
    return jsonify({
        'success': True,
        'detected_errors': detected_errors,
        'solutions': solutions,
        'error_count': len(detected_errors)
    })

@app.route('/api/ai-clone/create', methods=['POST'])
@login_required
def api_create_ai_clone():
    """API pour créer un nouveau clone IA"""
    data = request.json
    
    if not data or 'clone_type' not in data:
        return jsonify({'success': False, 'error': 'Type de clone manquant'}), 400
    
    clone_type = data.get('clone_type')
    custom_config = data.get('custom_config')
    
    # Créer le clone
    clone_id = ai_clone_manager.create_clone(clone_type, custom_config)
    
    # Récupérer les informations du clone
    clone_status = ai_clone_manager.get_clone_status(clone_id)
    
    return jsonify({
        'success': True,
        'clone_id': clone_id,
        'status': clone_status
    })

@app.route('/api/ai-clone/<clone_id>/status')
@login_required
def api_get_ai_clone_status(clone_id):
    """API pour récupérer le statut d'un clone IA"""
    clone_status = ai_clone_manager.get_clone_status(clone_id)
    
    if not clone_status:
        return jsonify({'success': False, 'error': f"Clone {clone_id} non trouvé"}), 404
    
    return jsonify({
        'success': True,
        'status': clone_status
    })

@app.route('/api/ai-clone/<clone_id>/stop', methods=['POST'])
@login_required
def api_stop_ai_clone(clone_id):
    """API pour arrêter un clone IA"""
    success = ai_clone_manager.stop_clone(clone_id)
    
    return jsonify({
        'success': success,
        'message': f"Clone {clone_id} arrêté avec succès" if success else f"Erreur lors de l'arrêt du clone {clone_id}"
    })

@app.route('/api/ai-clone/<clone_id>/auto-correct', methods=['POST'])
@login_required
def api_auto_correct_with_clone(clone_id):
    """API pour appliquer des corrections automatiques avec un clone IA"""
    # Récupérer les données de topologie
    topology_data = network_topology.get_topology_data()
    
    # Appliquer les corrections automatiques
    correction_result = ai_clone_manager.apply_auto_corrections(clone_id, topology_data)
    
    if correction_result.get('success'):
        # Si des modifications ont été appliquées, mettre à jour les données de topologie
        modified_data = correction_result.get('modified_data')
        if modified_data:
            # Dans une implémentation réelle, on sauvegarderait ces modifications
            # dans la base de données ou le système de stockage approprié
            
            # Émettre un événement pour notifier les clients des modifications
            socketio.emit('topology_updated', {
                'message': correction_result.get('message'),
                'changes_count': len(correction_result.get('changes', []))
            })
    
    return jsonify(correction_result)

@app.route('/ai-clones')
@login_required
def ai_clones_dashboard():
    """Tableau de bord des clones IA"""
    # Récupérer tous les clones
    clones = ai_clone_manager.get_all_clones()
    
    # Récupérer les configurations disponibles
    clone_configs = ai_clone_manager._load_clone_configs()
    
    return render_template(
        'ai_clones.html',
        clones=clones,
        clone_configs=clone_configs
    )

# Route d'administration centrale
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Interface d'administration centrale avec accès complet au système"""
    # Récupérer les statistiques du système
    memory_stats = MemoryMonitor.get_memory_usage()
    
    # Récupérer les données IA
    clones = ai_clone_manager.get_all_clones()
    
    # Récupérer les statistiques réseau
    network_stats = security_scoring.get_network_security_status()
    
    # Récupérer les données de tous les utilisateurs
    users = User.query.all()
    
    # Créer un jeu de données d'erreurs pour la démonstration
    error_stats = AIErrorHandler().get_error_statistics()
    
    return render_template(
        'admin/dashboard.html',
        memory_stats=memory_stats,
        clones=clones,
        network_stats=network_stats,
        users=users,
        error_stats=error_stats
    )

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Gestion des utilisateurs"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin_status(user_id):
    """Active ou désactive le statut administrateur d'un utilisateur"""
    user = User.query.get_or_404(user_id)
    
    # Ne pas permettre à un admin de se rétrograder lui-même
    if user.id == current_user.id:
        flash('Vous ne pouvez pas modifier votre propre statut administrateur.', 'danger')
        return redirect(url_for('admin_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    action = "activé" if user.is_admin else "désactivé"
    flash(f'Le statut administrateur de {user.username} a été {action}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/system')
@login_required
@admin_required
def admin_system():
    """Gestion du système et surveillance des performances"""
    memory_stats = MemoryMonitor.get_memory_usage()
    return render_template('admin/system.html', memory_stats=memory_stats)

@app.route('/admin/ai-management')
@login_required
@admin_required
def admin_ai_management():
    """Gestion avancée des modules d'intelligence artificielle"""
    clones = ai_clone_manager.get_all_clones()
    clone_configs = ai_clone_manager._load_clone_configs()
    
    return render_template(
        'admin/ai_management.html',
        clones=clones,
        clone_configs=clone_configs
    )

@app.route('/admin/security')
@login_required
@admin_required
def admin_security():
    """Surveillance avancée de la sécurité et gestion des vulnérabilités"""
    # Récupérer les statistiques réseau
    network_stats = security_scoring.get_network_security_status()
    
    # Récupérer tous les appareils avec leurs scores
    device_scores = security_scoring.get_all_device_scores()
    
    return render_template(
        'admin/security.html',
        network_stats=network_stats,
        device_scores=device_scores
    )

# Point d'entrée principal
if __name__ == '__main__':
    # Log initial de l'utilisation de la mémoire au démarrage
    MemoryMonitor.log_memory_usage()
    
    # Créer un clone IA par défaut pour la détection et correction automatique
    default_clone_id = ai_clone_manager.create_clone('auto_repair')
    logger.info(f"Clone IA par défaut créé : {default_clone_id}")
    
    # Démarrer l'application Flask avec l'extension SocketIO
    # Utilisation du port 5000 au lieu de 8080 pour respecter les directives de développement de Replit
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)