import logging
import json
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, current_user, logout_user, login_required
from urllib.parse import urlparse
from app import app, db, socketio
from models import User, UserReport, SavedTopology
from forms import RegistrationForm, LoginForm, SaveTopologyForm
from network_topology import NetworkTopology
from network_security import NetworkSecurityAnalyzer
from network_detector import NetworkDetector
from assistant_securite import AssistantSecurite
from security_scoring import DeviceSecurityScoring
from recommendations import RecommendationSystem
from translation import get_user_language, get_translation, get_all_translations

# Configuration du logging
logger = logging.getLogger(__name__)

# Initialisation des services
network_topology = NetworkTopology()
network_security = NetworkSecurityAnalyzer()
security_scoring = DeviceSecurityScoring()
recommendations = RecommendationSystem()
assistant = AssistantSecurite()

@app.route('/')
def accueil():
    logger.info("Page d'accueil visitée")
    return render_template('index.html', title='Accueil')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Inscription', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Échec de connexion. Vérifiez votre email et mot de passe.', 'danger')
    
    return render_template('login.html', title='Connexion', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('accueil'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Tableau de Bord', user=current_user)

@app.route('/network_topology')
@login_required
def network_topology_view():
    form = SaveTopologyForm()
    topology_data = network_topology.get_topology_data()
    saved_topologies = SavedTopology.query.filter_by(user_id=current_user.id).all()
    return render_template('network_topology.html', 
                           title='Topologie du Réseau', 
                           topology_data=json.dumps(topology_data),
                           form=form,
                           saved_topologies=saved_topologies)

@app.route('/save_topology', methods=['POST'])
@login_required
def save_topology():
    form = SaveTopologyForm()
    if form.validate_on_submit():
        layout_data = request.form.get('layout_data')
        if layout_data:
            topology = SavedTopology(
                user_id=current_user.id,
                name=form.name.data,
                layout_data=layout_data
            )
            db.session.add(topology)
            db.session.commit()
            flash('Disposition sauvegardée avec succès!', 'success')
        else:
            flash('Erreur: Données de disposition non trouvées.', 'danger')
    else:
        flash('Erreur: Formulaire invalide.', 'danger')
    
    return redirect(url_for('network_topology_view'))

@socketio.on('connect')
def handle_connect():
    logger.debug('Client connecté au WebSocket')

@socketio.on('disconnect')
def handle_disconnect():
    logger.debug('Client déconnecté du WebSocket')

@socketio.on('request_topology')
def handle_topology_request():
    logger.debug('Demande de données de topologie reçue')
    topology_data = network_topology.get_topology_data()
    socketio.emit('topology_data', topology_data)

@socketio.on('update_layout')
def handle_layout_update(data):
    logger.debug('Mise à jour de la disposition reçue')
    network_topology.save_layout(data)
    socketio.emit('layout_updated', {'status': 'success'})

@socketio.on('update_device_security')
def handle_device_security_update(data):
    logger.debug(f'Mise à jour de la sécurité pour appareil: {data["mac_address"]}')
    network_topology.update_device_security(data["mac_address"], data["security_data"])
    socketio.emit('device_updated', {'status': 'success', 'mac_address': data["mac_address"]})

@app.route('/api/topology', methods=['GET'])
def get_topology():
    topology_data = network_topology.get_topology_data()
    return jsonify(topology_data)

@app.route('/api/topology/layout', methods=['POST'])
@login_required
def update_topology_layout():
    data = request.json
    network_topology.save_layout(data)
    return jsonify({'status': 'success'})

@app.route('/api/devices/<mac_address>', methods=['GET'])
def get_device_details(mac_address):
    topology_data = network_topology.get_topology_data()
    device = next((d for d in topology_data['devices'] if d['mac_address'] == mac_address), None)
    if device:
        return jsonify(device)
    return jsonify({'error': 'Appareil non trouvé'}), 404

@app.route('/api/devices/<mac_address>/security', methods=['PUT'])
@login_required
def update_device_security(mac_address):
    data = request.json
    network_topology.update_device_security(mac_address, data)
    return jsonify({'status': 'success'})

@app.errorhandler(404)
def page_non_trouvee(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def erreur_serveur(error):
    return render_template('500.html'), 500

@app.context_processor
def inject_translations():
    lang = get_user_language()
    return dict(
        get_translation=lambda key: get_translation(key, lang),
        translations=get_all_translations(lang),
        current_language=lang
    )

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)