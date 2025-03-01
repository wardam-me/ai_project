
"""
Routes API sécurisées avec JWT pour l'application NetSecure Pro
"""
import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
)
from models import User
from extensions import db

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Création du Blueprint
api_secured = Blueprint('api_secured', __name__)

# ======================================================
# Routes d'authentification JWT
# ======================================================
@api_secured.route('/auth/token', methods=['POST'])
def create_token():
    """Génère un token JWT pour l'authentification API"""
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Identifiants invalides"}), 401
    
    # Créer les tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "username": user.username
    }), 200

@api_secured.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Rafraîchit le token JWT"""
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    
    return jsonify({"access_token": new_access_token}), 200

# ======================================================
# Routes API protégées
# ======================================================
@api_secured.route('/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Récupère le profil de l'utilisateur authentifié"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "last_seen": user.last_seen.isoformat() if user.last_seen else None
    }), 200

@api_secured.route('/secure-data', methods=['GET'])
@jwt_required()
def get_secure_data():
    """Exemple d'endpoint sécurisé nécessitant une authentification JWT"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Simuler des données sécurisées
    secure_data = {
        "security_reports": [
            {"id": 1, "title": "Analyse Trimestrielle", "date": "2024-01-15"},
            {"id": 2, "title": "Audit de Sécurité", "date": "2024-02-20"}
        ],
        "vulnerabilities_count": 3,
        "security_score": 85
    }
    
    return jsonify({
        "user": user.username,
        "secure_data": secure_data
    }), 200

# Fonction pour enregistrer les routes
def register_secured_api_routes(app):
    app.register_blueprint(api_secured, url_prefix='/api/v1')
