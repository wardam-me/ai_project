#!/usr/bin/env python3
"""
Script pour créer les dossiers nécessaires aux drapeaux et générer des images simples
"""
import os
import logging
from PIL import Image, ImageDraw

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_directories():
    """Crée les répertoires pour les drapeaux"""
    flag_dir = os.path.join('static', 'img', 'flags')
    
    # Créer le dossier img s'il n'existe pas
    if not os.path.exists(os.path.join('static', 'img')):
        os.makedirs(os.path.join('static', 'img'))
        logger.info(f"Répertoire créé: {os.path.join('static', 'img')}")
    
    # Créer le dossier flags s'il n'existe pas
    if not os.path.exists(flag_dir):
        os.makedirs(flag_dir)
        logger.info(f"Répertoire créé: {flag_dir}")
    
    return flag_dir

def create_french_flag(directory):
    """Crée un drapeau français simple"""
    width, height = 30, 20
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Dessiner les bandes verticales - format corrigé pour draw.rectangle
    draw.rectangle((0, 0, width//3, height), fill=(0, 35, 149))  # Bleu
    draw.rectangle((2*width//3, 0, width, height), fill=(237, 41, 57))  # Rouge
    
    # Sauvegarder l'image
    img.save(os.path.join(directory, 'fr.png'))
    logger.info(f"Drapeau français créé: {os.path.join(directory, 'fr.png')}")

def create_english_flag(directory):
    """Crée un drapeau britannique simple"""
    width, height = 30, 20
    img = Image.new('RGB', (width, height), color=(1, 33, 105))  # Bleu marine
    draw = ImageDraw.Draw(img)
    
    # Croix blanche de Saint André
    draw.line(((0, 0), (width, height)), fill=(255, 255, 255), width=3)
    draw.line(((0, height), (width, 0)), fill=(255, 255, 255), width=3)
    
    # Croix de Saint Georges
    draw.rectangle((width//3, 0, 2*width//3, height), fill=(255, 255, 255))
    draw.rectangle((0, height//3, width, 2*height//3), fill=(255, 255, 255))
    
    # Croix de Saint Patrick
    draw.line(((0, 0), (width, height)), fill=(207, 20, 43), width=1)
    draw.line(((0, height), (width, 0)), fill=(207, 20, 43), width=1)
    
    # Croix de Saint Georges (en rouge)
    draw.rectangle((width//3 + 2, height//3, 2*width//3 - 2, 2*height//3), fill=(207, 20, 43))
    draw.rectangle((width//3, height//3 + 2, 2*width//3, 2*height//3 - 2), fill=(207, 20, 43))
    
    # Sauvegarder l'image
    img.save(os.path.join(directory, 'en.png'))
    logger.info(f"Drapeau anglais créé: {os.path.join(directory, 'en.png')}")

if __name__ == "__main__":
    try:
        # Créer les répertoires
        flag_dir = create_directories()
        
        # Créer les drapeaux
        create_french_flag(flag_dir)
        create_english_flag(flag_dir)
        
        logger.info("Création des drapeaux terminée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la création des drapeaux: {e}")