import os
import logging
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_socketio import SocketIO
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from urllib.parse import urlparse as url_parse
from models import db, User, UserReport, SavedTopology
from forms import RegistrationForm, LoginForm, SaveTopologyForm
from translation import get_user_language, get_translation, get_all_translations

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Création de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SESSION_SECRET", "dev_key_for_testing")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données
db.init_app(app)

# Initialisation de Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration du gestionnaire de connexion
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Création des tables de la base de données
with app.app_context():
    db.create_all()