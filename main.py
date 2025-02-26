import os
import json
import logging
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import emit, disconnect
from werkzeug.security import generate_password_hash
from app import app, db, socketio
from forms import LoginForm, RegistrationForm, SaveTopologyForm
from models import User, SavedTopology
from network_topology import NetworkTopology
from security_scoring import DeviceSecurityScoring
from assistant_securite import AssistantSecurite

# Configuration du logging
logger = logging.getLogger(__name__)

# Initialisation des services
network_topology = NetworkTopology()
device_security = DeviceSecurityScoring()
assistant = AssistantSecurite()

# Création du dossier instance s'il n'existe pas
os.makedirs('instance', exist_ok=True)

@app.route('/')
def accueil():
    """Page d'accueil de l'application"""
    logger.info('Page d\'accueil visitée')
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
        db.session.add(user)
        db.session.commit()
        flash('Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
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
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Échec de la connexion. Veuillez vérifier votre email et votre mot de passe.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Déconnexion de l'utilisateur"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('accueil'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord de l'utilisateur connecté"""
    return render_template('dashboard.html')

@app.route('/network_topology')
@login_required
def network_topology_view():
    """Vue de la topologie du réseau"""
    save_form = SaveTopologyForm()
    return render_template('network_topology.html', save_form=save_form)

@app.route('/save_topology', methods=['POST'])
@login_required
def save_topology():
    """Sauvegarde de la topologie réseau"""
    form = SaveTopologyForm()
    if form.validate_on_submit():
        # Récupération de la disposition actuelle
        layout_data = network_topology.get_topology_data()
        
        # Sauvegarde dans la base de données
        saved_topology = SavedTopology(
            user_id=current_user.id,
            name=form.name.data,
            layout_data=json.dumps(layout_data)
        )
        
        db.session.add(saved_topology)
        db.session.commit()
        
        flash(f'Disposition "{form.name.data}" sauvegardée avec succès!', 'success')
        return redirect(url_for('network_topology_view'))
    
    flash('Erreur lors de la sauvegarde de la disposition.', 'danger')
    return redirect(url_for('network_topology_view'))

# Routes API
@app.route('/api/topology', methods=['GET'])
@login_required
def get_topology():
    """API pour récupérer les données de topologie réseau"""
    return jsonify(network_topology.get_topology_data())

@app.route('/api/topology/update_layout', methods=['POST'])
@login_required
def update_topology_layout():
    """API pour mettre à jour la disposition des appareils"""
    data = request.json
    if not data or 'mac_address' not in data or 'x' not in data or 'y' not in data:
        return jsonify({'success': False, 'message': 'Données invalides'}), 400
    
    # Mise à jour de la disposition
    network_topology.save_layout({
        'mac_address': data['mac_address'],
        'x': data['x'],
        'y': data['y']
    })
    
    return jsonify({'success': True})

@app.route('/api/device/<mac_address>', methods=['GET'])
@login_required
def get_device_details(mac_address):
    """API pour récupérer les détails d'un appareil spécifique"""
    # Récupération des données de l'appareil depuis la topologie
    devices = network_topology.get_topology_data().get('devices', [])
    device = next((d for d in devices if d['mac_address'] == mac_address), None)
    
    if not device:
        return jsonify({'success': False, 'message': 'Appareil non trouvé'}), 404
    
    # Enrichissement avec les données de sécurité
    security_data = device_security.get_device(mac_address)
    if security_data:
        device.update(security_data)
    
    return jsonify(device)

@app.route('/api/device/<mac_address>/security', methods=['PUT'])
@login_required
def update_device_security(mac_address):
    """API pour mettre à jour les informations de sécurité d'un appareil"""
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'Données invalides'}), 400
    
    # Mise à jour des informations de sécurité
    network_topology.update_device_security(mac_address, data)
    
    return jsonify({'success': True})

# Événements WebSocket
@socketio.on('connect')
def handle_connect():
    """Gestion de la connexion WebSocket"""
    logger.debug('Client connecté au WebSocket')

@socketio.on('disconnect')
def handle_disconnect():
    """Gestion de la déconnexion WebSocket"""
    logger.debug('Client déconnecté du WebSocket')

@socketio.on('request_topology')
def handle_topology_request():
    """Envoi des données de topologie au client"""
    emit('topology_data', network_topology.get_topology_data())

@socketio.on('update_layout')
def handle_layout_update(data):
    """Mise à jour de la disposition des appareils"""
    if data and 'mac_address' in data and 'x' in data and 'y' in data:
        network_topology.save_layout(data)
        emit('topology_data', network_topology.get_topology_data(), broadcast=True)

@socketio.on('update_device_security')
def handle_device_security_update(data):
    """Mise à jour des informations de sécurité d'un appareil"""
    if data and 'mac_address' in data:
        network_topology.update_device_security(data['mac_address'], data)
        emit('topology_data', network_topology.get_topology_data(), broadcast=True)

# Gestion des erreurs
@app.errorhandler(404)
def page_non_trouvee(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def erreur_serveur(error):
    return render_template('500.html'), 500

# Exécution de l'application
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)