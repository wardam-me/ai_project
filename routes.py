"""
Routes principales pour l'application NetSecure Pro
"""
import json
import logging
import random
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    render_template, request, redirect, url_for, flash, jsonify,
    session, abort, current_app
)
from flask_login import (
    current_user, login_user, logout_user, login_required
)
from flask_socketio import emit

from extensions import db, socketio
from forms import LoginForm, RegistrationForm, SaveTopologyForm
from models import User, UserReport, SavedTopology
from network_topology import NetworkTopology
from security_scoring import DeviceSecurityScoring
from assistant_securite import AssistantSecurite
from protocol_analyzer import ProtocolAnalyzer
from infographic_generator import InfographicGenerator
from ai_infographic_assistant import AIInfographicAssistant
from recommendations import RecommendationSystem

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialiser les classes principales
network_topology = NetworkTopology()
security_scoring = DeviceSecurityScoring()
assistant_securite = AssistantSecurite()
protocol_analyzer = ProtocolAnalyzer()
infographic_generator = InfographicGenerator()
ai_assistant = AIInfographicAssistant()
recommendation_system = RecommendationSystem()

# Décorateur pour vérifier si l'utilisateur est administrateur
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès refusé. Vous devez être administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def register_routes(app):
    """
    Enregistre toutes les routes de l'application
    """
    # Contexte global pour tous les templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Filtres personnalisés pour les templates
    @app.template_filter('datetime')
    def format_datetime(value, format='relative'):
        """Format une datetime en une chaîne lisible."""
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
    
    # ======================================================
    # Routes principales
    # ======================================================
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
    
    # ======================================================
    # Routes pour la topologie réseau
    # ======================================================
    @app.route('/network-topology')
    @login_required
    def network_topology_view():
        """Affiche la visualisation de la topologie réseau"""
        form = SaveTopologyForm()
        saved_topologies = SavedTopology.query.filter_by(user_id=current_user.id).all()
        
        return render_template(
            'network_topology.html',
            form=form,
            saved_topologies=saved_topologies
        )
    
    @app.route('/api/topology-data')
    @login_required
    def get_topology_data():
        """API: Récupère les données de topologie en JSON"""
        data = network_topology.get_topology_data()
        return jsonify(data)
    
    @app.route('/api/save-topology', methods=['POST'])
    @login_required
    def save_topology():
        """API: Sauvegarde une disposition de topologie"""
        form = SaveTopologyForm()
        
        if form.validate_on_submit():
            layout_data = request.json.get('layout')
            
            if not layout_data:
                return jsonify({'success': False, 'error': 'Données de disposition manquantes'})
            
            # Créer une nouvelle sauvegarde
            new_topology = SavedTopology(
                user_id=current_user.id,
                name=form.name.data,
                layout_data=json.dumps(layout_data)
            )
            
            try:
                db.session.add(new_topology)
                db.session.commit()
                return jsonify({'success': True, 'id': new_topology.id})
            except Exception as e:
                db.session.rollback()
                logger.error(f"Erreur lors de la sauvegarde de la topologie: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        return jsonify({'success': False, 'error': 'Formulaire invalide'})
    
    # ======================================================
    # Routes pour l'analyse de sécurité
    # ======================================================
    @app.route('/vulnerability-analysis')
    @login_required
    def vulnerability_analysis():
        """Page d'analyse des vulnérabilités"""
        # Récupérer les appareils vulnérables
        device_scores = security_scoring.get_all_device_scores()
        vulnerable_devices = sorted(
            [d for d in device_scores if d['security_score'] < 70],
            key=lambda d: d['security_score']
        )
        
        return render_template(
            'vulnerability_analysis.html',
            devices=vulnerable_devices
        )
    
    @app.route('/protocol-analysis')
    @login_required
    def protocol_analysis():
        """Page d'analyse des protocoles"""
        # Charger les données d'analyse de protocole
        with open('attached_assets/wifi_results.json', 'r') as f:
            wifi_data = json.load(f)
        
        # Analyser les protocoles de sécurité
        protocol_results = protocol_analyzer.analyze_all_networks(wifi_data)
        protocol_summary = protocol_analyzer.get_protocol_analysis_summary()
        
        return render_template(
            'protocol_analysis.html',
            protocols=protocol_results,
            summary=protocol_summary
        )
    
    @app.route('/security-report')
    @login_required
    def security_report():
        """Page de rapport de sécurité"""
        network_stats = security_scoring.get_network_security_status()
        device_scores = security_scoring.get_all_device_scores()
        
        return render_template(
            'security_report.html',
            network_stats=network_stats,
            device_scores=device_scores
        )
    
    # ======================================================
    # Routes pour l'assistant IA
    # ======================================================
    @app.route('/chatbot')
    @login_required
    def chatbot():
        """Page de l'assistant IA"""
        conversations = assistant_securite.get_all_conversations()
        
        return render_template(
            'chatbot.html',
            conversations=conversations
        )
    
    @app.route('/api/assistant/query', methods=['POST'])
    @login_required
    def assistant_query():
        """API: Interroger l'assistant IA (route maintenue pour compatibilité)"""
        return chatbot_query()
        
    @app.route('/api/chatbot', methods=['POST'])
    @login_required
    def chatbot_query():
        """API: Interroger le chatbot d'assistant de cyberdéfense"""
        user_input = request.json.get('query') or request.json.get('message')
        conversation_id = request.json.get('conversation_id')
        
        if not user_input:
            return jsonify({'error': 'Query is required'})
        
        # Récupérer les données réseau actuelles
        try:
            with open('attached_assets/wifi_results.json', 'r') as f:
                network_data = json.load(f)
        except Exception as e:
            app.logger.error(f"Erreur lors de la lecture des données réseau: {e}")
            network_data = {}
        
        # Générer une réponse
        response = assistant_securite.generate_response(
            user_input, 
            conversation_id=conversation_id,
            network_data=network_data
        )
        
        return jsonify(response)
        
    @app.route('/api/chatbot/history', methods=['GET'])
    @login_required
    def chatbot_history():
        """API: Récupérer l'historique des conversations"""
        conversations = assistant_securite.get_all_conversations()
        return jsonify(conversations)
        
    @app.route('/api/chatbot/conversation/<conversation_id>', methods=['GET'])
    @login_required
    def chatbot_conversation(conversation_id):
        """API: Récupérer une conversation spécifique"""
        conversation = assistant_securite.get_conversation_history(conversation_id)
        return jsonify(conversation)
    
    # ======================================================
    # Routes pour l'analyse IA
    # ======================================================
    @app.route('/ai-analysis')
    @login_required
    def ai_analysis():
        """Page d'analyse IA avancée"""
        # Générer des données de simulation pour la démo
        optimization_results = {
            'optimality_score': 78.5,
            'vulnerability_statistics': {
                'critical': 1,
                'high': 3,
                'medium': 7,
                'low': 12
            },
            'recommendations': {
                'priority': [
                    {
                        'title': 'Mettre à jour le firmware du routeur',
                        'description': 'Une vulnérabilité critique a été détectée dans la version actuelle du firmware.',
                        'affected_devices': ['Routeur principal']
                    }
                ],
                'medium': [
                    {
                        'title': 'Modifier les mots de passe par défaut',
                        'description': 'Plusieurs appareils IoT utilisent encore leurs mots de passe par défaut.',
                        'affected_devices': ['Caméra salon', 'Thermostat']
                    },
                    {
                        'title': 'Isoler les appareils IoT',
                        'description': 'Créer un réseau séparé pour les appareils IoT améliorerait la sécurité.',
                        'affected_devices': ['Tous les appareils IoT']
                    }
                ]
            },
            'raw_vulnerabilities': [
                {
                    'vulnerability_type': 'Firmware obsolète',
                    'severity': 'critical',
                    'probability': 0.95,
                    'description': 'Firmware du routeur vulnérable à l\'exploit CVE-2023-XXXX',
                    'recommendation': 'Mettre à jour vers la dernière version du firmware'
                },
                {
                    'vulnerability_type': 'Authentification faible',
                    'severity': 'high',
                    'probability': 0.85,
                    'description': 'Mots de passe par défaut sur plusieurs appareils',
                    'recommendation': 'Changer tous les mots de passe par défaut'
                }
            ]
        }
        
        wifi_analysis = {
            'overall_score': 65.3,
            'networks_analyzed': 7,
            'security_levels': {
                'secure': 2,
                'medium': 3,
                'vulnerable': 2
            },
            'recommendations': [
                {
                    'title': 'Migrer vers WPA3',
                    'priority': 'high',
                    'description': 'WPA2 est vulnérable à diverses attaques. La migration vers WPA3 est recommandée.',
                    'action_items': [
                        'Vérifier la compatibilité des appareils avec WPA3',
                        'Mettre à jour le firmware du routeur',
                        'Reconfigurer le réseau avec WPA3-Personal'
                    ]
                },
                {
                    'title': 'Renforcer la robustesse des mots de passe',
                    'priority': 'medium',
                    'description': 'Les mots de passe WiFi doivent être complexes et longs (min. 12 caractères).',
                    'action_items': [
                        'Créer un mot de passe avec majuscules, minuscules, chiffres et symboles',
                        'Longueur minimale de 12 caractères'
                    ]
                }
            ],
            'network_scores': [
                {
                    'ssid': 'Maison_Principal',
                    'security_type': 'WPA2',
                    'encryption': 'AES',
                    'security_score': 75,
                    'security_level': 'medium'
                },
                {
                    'ssid': 'Maison_Invités',
                    'security_type': 'WPA3',
                    'encryption': 'AES',
                    'security_score': 92,
                    'security_level': 'secure'
                },
                {
                    'ssid': 'IoT_Network',
                    'security_type': 'WPA2',
                    'encryption': 'TKIP',
                    'security_score': 45,
                    'security_level': 'vulnerable'
                }
            ]
        }
        
        return render_template('ai_analysis.html', 
                              optimization_results=optimization_results,
                              wifi_analysis=wifi_analysis)
    
    # ======================================================
    # Routes pour la génération d'infographies
    # ======================================================
    @app.route('/infographic-export-hub')
    @login_required
    def infographic_export_hub():
        """Hub central pour l'exportation des infographies"""
        # Obtenir des aperçus pour chaque type de rapport
        network_preview = infographic_generator.generate_preview('network')
        protocol_preview = infographic_generator.generate_preview('protocol')
        vulnerability_preview = infographic_generator.generate_preview('vulnerability')
        
        return render_template(
            'infographic_export_hub.html',
            network_preview=network_preview,
            protocol_preview=protocol_preview,
            vulnerability_preview=vulnerability_preview
        )
    
    @app.route('/generate-infographic', methods=['POST'])
    @login_required
    def generate_infographic():
        """Génère une infographie selon les paramètres spécifiés"""
        report_type = request.form.get('report_type')
        export_format = request.form.get('format', 'png')
        use_ai = request.form.get('use_ai', 'true') == 'true'
        
        # Validation des entrées
        if report_type not in ['network', 'protocol', 'vulnerability']:
            flash('Type de rapport invalide.', 'danger')
            return redirect(url_for('infographic_export_hub'))
        
        if export_format not in ['png', 'pdf', 'svg']:
            flash('Format d\'export invalide.', 'danger')
            return redirect(url_for('infographic_export_hub'))
        
        try:
            return generate_report(report_type, export_format, use_ai)
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'infographie: {e}")
            flash(f"Erreur lors de la génération de l'infographie: {str(e)}", 'danger')
            return redirect(url_for('infographic_export_hub'))
    
    @app.route('/one-click-export/<report_type>')
    @login_required
    def one_click_export(report_type):
        """Génère une infographie avec un seul clic en utilisant les paramètres par défaut"""
        # Paramètres par défaut
        export_format = 'pdf'  # Format par défaut (plus professionnel)
        use_ai = True  # Toujours utiliser l'IA pour enrichir les données
        
        # Validation des entrées
        if report_type not in ['network', 'protocol', 'vulnerability']:
            flash('Type de rapport invalide.', 'danger')
            return redirect(url_for('dashboard'))
        
        logger.info(f"Génération d'un rapport One-Click pour {report_type} (format: {export_format})")
        
        try:
            return generate_report(report_type, export_format, use_ai, one_click=True)
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport One-Click: {e}")
            flash(f"Erreur lors de la génération du rapport rapide: {str(e)}", 'danger')
            return redirect(url_for('dashboard'))
    
    def generate_report(report_type, export_format, use_ai, one_click=False):
        """Fonction utilitaire pour générer un rapport d'infographie"""
        
        if export_format not in ['png', 'pdf', 'svg']:
            flash('Format d\'export invalide.', 'danger')
            return redirect(url_for('infographic_export_hub'))
        
        try:
            # Générer l'infographie
            if report_type == 'network':
                # Récupérer les données pour le rapport réseau
                network_stats = security_scoring.get_network_security_status()
                device_scores = security_scoring.get_all_device_scores()
                
                # Préparer les données pour l'infographie
                network_data = {
                    'security_score': network_stats['security_score'],
                    'total_devices': network_stats['total_devices'],
                    'vulnerable_devices': network_stats['vulnerable_devices'],
                    'secure_devices': network_stats['secure_devices'],
                    'device_types': network_stats['device_types'],
                    'security_distribution': network_stats['security_distribution'],
                    'devices': device_scores
                }
                
                # Obtenir les données de vulnérabilité simplifiées
                vulnerability_data = {
                    'total_vulnerabilities': sum(d['issues_count'] for d in device_scores),
                    'critical_vulnerabilities': sum(1 for d in device_scores if d['security_score'] < 50),
                    'severity_distribution': {
                        'critical': sum(1 for d in device_scores if d['security_score'] < 30),
                        'high': sum(1 for d in device_scores if 30 <= d['security_score'] < 50),
                        'medium': sum(1 for d in device_scores if 50 <= d['security_score'] < 70),
                        'low': sum(1 for d in device_scores if 70 <= d['security_score'])
                    }
                }
                
                # Générer l'infographie
                output_file = infographic_generator.generate_network_security_infographic(
                    network_data=network_data,
                    vulnerability_data=vulnerability_data,
                    format=export_format,
                    use_ai=use_ai
                )
            
            elif report_type == 'protocol':
                # Charger les données de protocole
                with open('attached_assets/wifi_results.json', 'r') as f:
                    wifi_data = json.load(f)
                
                # Analyser les protocoles de sécurité
                protocol_results = protocol_analyzer.analyze_all_networks(wifi_data)
                protocol_summary = protocol_analyzer.get_protocol_analysis_summary()
                
                # Préparer les données pour l'infographie
                protocol_data = {
                    'networks': protocol_results,
                    'summary': protocol_summary,
                    'comparison': protocol_analyzer.get_protocol_comparison(),
                    'timeline': protocol_analyzer.get_protocol_timeline()
                }
                
                # Générer l'infographie
                output_file = infographic_generator.generate_protocol_analysis_infographic(
                    protocol_data=protocol_data,
                    format=export_format,
                    use_ai=use_ai
                )
            
            else:  # vulnerability
                # Récupérer les appareils vulnérables
                device_scores = security_scoring.get_all_device_scores()
                vulnerable_devices = [d for d in device_scores if d['security_score'] < 70]
                
                # Préparer les données pour l'infographie
                vulnerability_data = {
                    'vulnerable_devices': vulnerable_devices,
                    'total_vulnerabilities': sum(d['issues_count'] for d in vulnerable_devices),
                    'critical_vulnerabilities': sum(1 for d in vulnerable_devices if d['security_score'] < 50),
                    'severity_distribution': {
                        'critical': sum(1 for d in vulnerable_devices if d['security_score'] < 30),
                        'high': sum(1 for d in vulnerable_devices if 30 <= d['security_score'] < 50),
                        'medium': sum(1 for d in vulnerable_devices if 50 <= d['security_score'] < 70),
                        'low': 0  # Par définition, les appareils avec score >= 70 ne sont pas vulnérables
                    },
                    'vulnerability_types': {
                        'configuration': sum(1 for d in vulnerable_devices if any('config' in issue.lower() for issue in d['security_issues'])),
                        'patch': sum(1 for d in vulnerable_devices if any('patch' in issue.lower() for issue in d['security_issues'])),
                        'authentication': sum(1 for d in vulnerable_devices if any('auth' in issue.lower() for issue in d['security_issues'])),
                        'encryption': sum(1 for d in vulnerable_devices if any('crypt' in issue.lower() for issue in d['security_issues'])),
                        'other': sum(1 for d in vulnerable_devices if not any(keyword in ' '.join(d['security_issues']).lower() for keyword in ['config', 'patch', 'auth', 'crypt']))
                    }
                }
                
                # Générer l'infographie
                output_file = infographic_generator.generate_vulnerability_report_infographic(
                    vulnerability_data=vulnerability_data,
                    format=export_format,
                    use_ai=use_ai
                )
            
            # Préparer les métadonnées pour l'affichage
            file_info = infographic_generator.copy_export_to_user_downloads(output_file)
            
            return render_template(
                'export_success.html',
                file_info=file_info,
                report_type=report_type
            )
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'infographie: {e}")
            flash(f"Erreur lors de la génération de l'infographie: {str(e)}", 'danger')
            return redirect(url_for('infographic_export_hub'))
    
    # ======================================================
    # Routes pour la gamification
    # ======================================================
    @app.route('/security-game')
    @login_required
    def security_game():
        """Page de gamification de la sécurité"""
        return render_template('security_game.html')
    
    # ======================================================
    # Routes pour le radar de sécurité
    # ======================================================
    @app.route('/security-radar')
    @login_required
    def security_radar():
        """Page de visualisation du radar de sécurité"""
        return render_template('security_radar.html')
    
    # ======================================================
    # Routes pour l'administration
    # ======================================================
    @app.route('/admin/dashboard')
    @login_required
    @admin_required
    def admin_dashboard():
        """Tableau de bord administrateur"""
        users = User.query.all()
        
        return render_template(
            'admin/dashboard.html',
            users=users
        )
    
    @app.route('/admin/ai-management')
    @login_required
    @admin_required
    def admin_ai_management():
        """Page de gestion de l'IA et des clones IA"""
        # Récupérer le gestionnaire de clones
        from ai_clone_manager import get_clone_manager
        
        clone_manager = get_clone_manager()
        clones = clone_manager.get_all_clones()
        statistics = clone_manager.get_clone_statistics()
        
        return render_template(
            'admin/ai_management.html',
            clones=clones,
            statistics=statistics
        )
    
    @app.route('/admin/security')
    @login_required
    @admin_required
    def admin_security():
        """Page d'administration de la sécurité"""
        return render_template('admin/security.html')
    
    @app.route('/admin/users')
    @login_required
    @admin_required
    def admin_users():
        """Page de gestion des utilisateurs"""
        users = User.query.all()
        
        return render_template(
            'admin/users.html',
            users=users
        )
    
    @app.route('/admin/system')
    @login_required
    @admin_required
    def admin_system():
        """Page d'administration système"""
        return render_template('admin/system.html')
    
    # ======================================================
    # Routes pour les erreurs
    # ======================================================
    @app.errorhandler(404)
    def page_non_trouvee(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def erreur_serveur(error):
        return render_template('500.html'), 500
    
    # ======================================================
    # Gestionnaires WebSocket
    # ======================================================
    @socketio.on('connect')
    def handle_connect():
        """Gestion de la connexion WebSocket"""
        logger.info(f"Nouvelle connexion WebSocket: {request.sid}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Gestion de la déconnexion WebSocket"""
        logger.info(f"Déconnexion WebSocket: {request.sid}")
    
    @socketio.on('request_network_update')
    def handle_network_update():
        """Envoie une mise à jour des données réseau"""
        # Simuler une détection de nouvel appareil
        security_scoring._add_random_device()
        
        # Obtenir les données mises à jour
        network_stats = security_scoring.get_network_security_status()
        device_scores = security_scoring.get_all_device_scores()
        
        # Émettre les données mises à jour
        emit('network_status_update', {
            'stats': network_stats,
            'devices': device_scores
        })
    
    @socketio.on('request_topology_update')
    def handle_topology_update():
        """Envoie une mise à jour des données de topologie"""
        # Mettre à jour aléatoirement le statut des appareils
        network_topology._update_devices_status()
        
        # Obtenir les données mises à jour
        topology_data = network_topology.get_topology_data()
        
        # Émettre les données mises à jour
        emit('topology_update', topology_data)
    
    # Retourner l'application configurée
    return app