from datetime import datetime
import json
from flask_login import UserMixin
from extensions import db, bcrypt

class User(UserMixin, db.Model):
    """Modèle d'utilisateur pour l'authentification et le suivi des données utilisateur"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    reports = db.relationship('UserReport', backref='author', lazy='dynamic')
    mascots = db.relationship('SecurityMascot', backref='owner', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Définit le mot de passe haché pour l'utilisateur"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Vérifie si le mot de passe correspond au hash stocké"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class UserReport(db.Model):
    """Modèle pour les rapports générés par les utilisateurs"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Report {self.title}>'

class SavedTopology(db.Model):
    """Modèle pour les dispositions de topologie sauvegardées par les utilisateurs"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    layout_data = db.Column(db.Text, nullable=False)  # JSON data avec les positions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('topologies', lazy='dynamic'))

    def __repr__(self):
        return f'<SavedTopology {self.name}>'

class SecurityMascot(db.Model):
    """Modèle pour les mascottes de cybersécurité personnalisées des utilisateurs"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Éléments de la mascotte
    base = db.Column(db.String(50), nullable=False, default='penguin')
    hat = db.Column(db.String(50), nullable=True)
    accessory = db.Column(db.String(50), nullable=True)
    outfit = db.Column(db.String(50), nullable=True)
    background = db.Column(db.String(50), nullable=True)
    
    # Personnalisation
    colors = db.Column(db.Text, nullable=False, default='{"primary":"#3498db","secondary":"#2ecc71","accent":"#e74c3c"}')
    personality = db.Column(db.String(50), nullable=False, default='friendly')
    security_score = db.Column(db.Integer, nullable=False, default=50)
    
    def get_colors(self):
        """Récupère les couleurs de la mascotte sous forme de dictionnaire"""
        return json.loads(self.colors)
    
    def set_colors(self, colors_dict):
        """Définit les couleurs de la mascotte à partir d'un dictionnaire"""
        self.colors = json.dumps(colors_dict)
    
    def get_security_level(self):
        """Détermine le niveau de sécurité basé sur le score"""
        if self.security_score >= 90:
            return "expert"
        elif self.security_score >= 75:
            return "advanced"
        elif self.security_score >= 60:
            return "intermediate"
        elif self.security_score >= 40:
            return "basic"
        else:
            return "novice"
    
    def get_security_title(self):
        """Récupère le titre de sécurité basé sur le niveau"""
        levels = {
            "expert": "Expert en cybersécurité",
            "advanced": "Gardien avancé",
            "intermediate": "Protecteur confirmé",
            "basic": "Défenseur en formation",
            "novice": "Apprenti en sécurité"
        }
        return levels.get(self.get_security_level(), "Défenseur en formation")
    
    def __repr__(self):
        return f'<SecurityMascot {self.name} ({self.get_security_level()})>'