import os
import logging
from flask import Flask
from urllib.parse import urlparse
from extensions import db, login_manager, socketio

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    """
    Fonction Factory pour créer l'application Flask
    Cela permet d'éviter les importations circulaires
    """
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
        # Import ici pour éviter les importations circulaires
        from models import User, UserReport, SavedTopology
        db.create_all()
        
        # Importation des routes
        from routes import register_routes
        register_routes(app)
    
    return app

# Importation de la fonction de chargement d'utilisateur pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Création de l'application
app = create_app()