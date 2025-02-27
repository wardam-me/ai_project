from app import app, db
from models import User

def create_test_user():
    """Crée un utilisateur de test s'il n'existe pas déjà"""
    with app.app_context():
        test_email = "test@example.com"
        existing_user = User.query.filter_by(email=test_email).first()
        
        if not existing_user:
            test_user = User(username="testuser", email=test_email)
            test_user.set_password("password")
            db.session.add(test_user)
            db.session.commit()
            print(f"Utilisateur de test créé avec succès: {test_email} / password")
        else:
            print(f"Utilisateur de test existe déjà: {test_email}")

if __name__ == "__main__":
    create_test_user()