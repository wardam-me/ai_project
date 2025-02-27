from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    """Modèle d'utilisateur pour l'authentification et le suivi des données utilisateur"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    reports = db.relationship('UserReport', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        """Définit le mot de passe haché pour l'utilisateur"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie si le mot de passe correspond au hash stocké"""
        return check_password_hash(self.password_hash, password)
    
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