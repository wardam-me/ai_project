"""
Extensions partagées pour l'application Flask.
Ce fichier évite les importations circulaires en initialisant les extensions.
"""

from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
bcrypt = Bcrypt()
jwt = JWTManager()
talisman = Talisman()

# Configuration du gestionnaire de login
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'