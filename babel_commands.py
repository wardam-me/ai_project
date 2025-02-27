#!/usr/bin/env python3
"""
Script utilitaire pour gérer les traductions avec Flask-Babel
Usage:
    1. Extraire les messages: python babel_commands.py extract
    2. Initialiser une nouvelle langue: python babel_commands.py init LANG
    3. Mettre à jour les messages: python babel_commands.py update
    4. Compiler les messages: python babel_commands.py compile
"""
import os
import sys
import subprocess
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chemins des fichiers
BABEL_CFG = 'babel.cfg'
MESSAGES_POT = 'messages.pot'
TRANSLATIONS_DIR = 'translations'

def extract_messages():
    """Extraire les messages à traduire depuis le code source"""
    logger.info("Extraction des messages...")
    cmd = f"pybabel extract -F {BABEL_CFG} -o {MESSAGES_POT} ."
    subprocess.run(cmd, shell=True)
    logger.info("Extraction terminée.")

def init_language(lang):
    """Initialiser une nouvelle langue"""
    if not os.path.exists(MESSAGES_POT):
        logger.error(f"Le fichier {MESSAGES_POT} n'existe pas. Exécutez d'abord 'extract'.")
        return
    
    logger.info(f"Initialisation de la langue '{lang}'...")
    cmd = f"pybabel init -i {MESSAGES_POT} -d {TRANSLATIONS_DIR} -l {lang}"
    subprocess.run(cmd, shell=True)
    logger.info(f"Initialisation de la langue '{lang}' terminée.")

def update_translations():
    """Mettre à jour les traductions existantes"""
    if not os.path.exists(MESSAGES_POT):
        logger.error(f"Le fichier {MESSAGES_POT} n'existe pas. Exécutez d'abord 'extract'.")
        return
    
    logger.info("Mise à jour des traductions...")
    cmd = f"pybabel update -i {MESSAGES_POT} -d {TRANSLATIONS_DIR}"
    subprocess.run(cmd, shell=True)
    logger.info("Mise à jour terminée.")

def compile_translations():
    """Compiler les traductions"""
    logger.info("Compilation des traductions...")
    cmd = f"pybabel compile -d {TRANSLATIONS_DIR}"
    subprocess.run(cmd, shell=True)
    logger.info("Compilation terminée.")

def create_translations_dir():
    """Créer le répertoire des traductions s'il n'existe pas"""
    if not os.path.exists(TRANSLATIONS_DIR):
        os.makedirs(TRANSLATIONS_DIR)
        logger.info(f"Répertoire '{TRANSLATIONS_DIR}' créé.")

def main():
    """Point d'entrée du script"""
    if len(sys.argv) < 2:
        print("Usage: python babel_commands.py COMMAND [ARGS]")
        print("Commands:")
        print("  extract               - Extraire les messages à traduire")
        print("  init LANG             - Initialiser une nouvelle langue (ex: fr, en)")
        print("  update                - Mettre à jour les traductions existantes")
        print("  compile               - Compiler les traductions")
        return

    # Créer le répertoire des traductions si nécessaire
    create_translations_dir()

    command = sys.argv[1]
    
    if command == "extract":
        extract_messages()
    elif command == "init" and len(sys.argv) > 2:
        lang = sys.argv[2]
        init_language(lang)
    elif command == "update":
        update_translations()
    elif command == "compile":
        compile_translations()
    else:
        print("Commande non reconnue ou arguments manquants.")
        print("Utilisez 'python babel_commands.py' sans arguments pour voir l'aide.")

if __name__ == "__main__":
    main()