import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from urllib.parse import urlparse
from flask_socketio import SocketIO

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)

# Création de la base de données
class Base:
    pass

db = SQLAlchemy(model_class=Base)

# Initialisation de SocketIO
socketio = SocketIO()

# Initialisation du gestionnaire de login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

# Création de l'application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or 'clef-secrete-temporaire'

# Configuration de la base de données
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or 'sqlite:///app.db'
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialisation des extensions
db.init_app(app)
login_manager.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")

# Import des modèles et création des tables
with app.app_context():
    from models import User, UserReport, SavedTopology
    db.create_all()

# Importation de la fonction de chargement d'utilisateur pour Flask-Login
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))