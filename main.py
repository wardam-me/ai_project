#!/usr/bin/env python3
"""
Application principale pour NetSecure Pro - Analyse de sécurité réseau WiFi
"""
import os
import json
import logging
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

from app import app, db, socketio, login_manager
from forms import LoginForm, RegistrationForm, SaveTopologyForm
from models import User, UserReport, SavedTopology
from network_topology import NetworkTopology
from security_scoring import DeviceSecurityScoring
from assistant_securite import AssistantSecurite

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialiser les classes principales
network_topology = NetworkTopology()
security_scoring = DeviceSecurityScoring()
assistant_securite = AssistantSecurite()

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
    """Page de l'assistant de sécurité"""
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

# Gestionnaires d'erreurs
@app.errorhandler(404)
def page_non_trouvee(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def erreur_serveur(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Point d'entrée principal
if __name__ == '__main__':
    # Démarrer l'application avec Socket.IO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)