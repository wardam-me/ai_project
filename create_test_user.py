"""
Script pour créer un utilisateur de test pour NetSecure Pro
"""
import os
import sys
from werkzeug.security import generate_password_hash
from app import app, db
from models import User

def create_test_user(username, email, password, is_admin=False):
    """Crée un utilisateur de test"""
    with app.app_context():
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            print(f"Utilisateur existe déjà: {existing_user.username} ({existing_user.email})")
            return existing_user

        # Créer le nouvel utilisateur
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=is_admin
        )
        
        # Ajouter à la base de données
        db.session.add(user)
        db.session.commit()
        
        print(f"Utilisateur créé: {user.username} ({user.email}), Admin: {user.is_admin}")
        return user

if __name__ == "__main__":
    # Créer un utilisateur de test régulier
    create_test_user('testuser', 'test@example.com', 'password123')
    
    # Créer un utilisateur administrateur
    create_test_user('admin', 'admin@netsecure.pro', 'admin123', is_admin=True)