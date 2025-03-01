#!/usr/bin/env python3
"""
Script pour mettre à jour la base de données avec la nouvelle table SecurityMascot
"""
import logging
from app import app, db
from models import SecurityMascot

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mascot_table():
    """Crée la table SecurityMascot dans la base de données"""
    with app.app_context():
        try:
            # Vérifier si la table existe déjà
            if not db.engine.has_table('security_mascot'):
                logger.info("Création de la table SecurityMascot...")
                SecurityMascot.__table__.create(db.engine)
                logger.info("Table SecurityMascot créée avec succès!")
            else:
                logger.info("La table SecurityMascot existe déjà.")
        except Exception as e:
            logger.error(f"Erreur lors de la création de la table: {e}")
            raise

if __name__ == "__main__":
    create_mascot_table()