"""
Extensions partagées pour l'application Flask.
Ce fichier évite les importations circulaires en initialisant les extensions.
"""

from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

# Configuration du gestionnaire de login
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'