#!/usr/bin/env python3
"""
Script pour créer les répertoires nécessaires pour l'application
"""
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_directories():
    """Crée les répertoires nécessaires pour l'application"""
    directories = [
        "instance",
        "instance/ai_reports",
        "instance/backups",
        "instance/conversations",
        "instance/echo_data",       # Répertoire pour les données d'écho brutes
        "instance/echo_reports",    # Répertoire pour les rapports d'analyse d'écho
        "instance/flask_analyses",
        "instance/mobile_cache",
        "config",
        "static/exports",
        "static/css",
        "static/js",
        "static/img",
        "static/fonts",
        'static/img/previews',  # Dossier pour les prévisualisations d'infographies
        'static/img/previews/network',  # Dossier pour les prévisualisations d'infographies réseau 
        'static/img/previews/protocol',  # Dossier pour les prévisualisations d'infographies de protocole
        'static/img/previews/vulnerability',  # Dossier pour les prévisualisations d'infographies de vulnérabilité
        'static/exports/network',  # Dossier pour les infographies réseau exportées
        'static/exports/protocol',  # Dossier pour les infographies de protocole exportées
        'static/exports/vulnerability',  # Dossier pour les infographies de vulnérabilité exportées
        'static/templates', # Dossier pour les templates d'infographie
        'templates',
        'templates/admin',  # Dossier pour les templates d'administration

    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Répertoire créé ou existant: {directory}")

if __name__ == "__main__":
    try:
        create_directories()
        logger.info("Tous les répertoires ont été créés avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors de la création des répertoires: {e}")