import os
import logging
from flask import Flask
from urllib.parse import urlparse
from extensions import db, login_manager, socketio, bcrypt, jwt, talisman

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
    
    # Configuration des clés secrètes depuis les variables d'environnement
    app.secret_key = os.environ.get("SESSION_SECRET") or 'clef-secrete-temporaire'
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY") or app.secret_key
    
    # Configuration de la base de données
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or 'sqlite:///app.db'
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Configuration JWT
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 heure
    
    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Politique CSP (Content Security Policy)
    csp = {
        'default-src': ['\'self\''],
        'script-src': ['\'self\'', '\'unsafe-inline\'', 'cdn.jsdelivr.net', 'code.jquery.com'],
        'style-src': ['\'self\'', '\'unsafe-inline\'', 'cdn.jsdelivr.net', 'fonts.googleapis.com'],
        'font-src': ['\'self\'', 'fonts.gstatic.com'],
        'img-src': ['\'self\'', 'data:', 'cdn.pixabay.com', 'randomuser.me'],
        'connect-src': ['\'self\'']
    }
    
    # Initialiser Talisman avec les paramètres CSP, mais désactiver en développement
    talisman.init_app(
        app,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        force_https=os.environ.get("FLASK_ENV") == "production",
        session_cookie_secure=os.environ.get("FLASK_ENV") == "production",
        session_cookie_http_only=True
    )
    
    # Import des modèles et création des tables
    with app.app_context():
        # Import ici pour éviter les importations circulaires
        from models import User, UserReport, SavedTopology
        db.create_all()
        
        # Importation des routes principales
        from routes import register_routes
        register_routes(app)
        
        # Importation des routes API
        from api_routes import register_api_routes
        register_api_routes(app)
        
        # Importation des routes API sécurisées JWT
        from api_secured_routes import register_secured_api_routes
        register_secured_api_routes(app)
        
        # Initialisation du système de mise à jour automatique IA
        try:
            from ai_update_integration import init_app as init_ai_updates
            init_ai_updates(app)
            logger.info("Système de mise à jour automatique IA initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du système de mise à jour IA: {e}")
    
    return app

# Importation de la fonction de chargement d'utilisateur pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Création de l'application
app = create_app()