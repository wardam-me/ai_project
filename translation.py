"""
Module de gestion des traductions pour l'application d'analyse WiFi
"""
from flask import request, session
import importlib
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Langues disponibles
AVAILABLE_LANGUAGES = {
    'fr': 'Français',
    'en': 'English',
    'ar': 'العربية'
}

# Langue par défaut
DEFAULT_LANGUAGE = 'fr'

def get_user_language():
    """
    Détermine la langue de l'utilisateur à partir de la session
    ou de la requête, avec une valeur par défaut
    """
    # Vérifier si une langue est spécifiée dans la session
    lang = session.get('language')
    
    # Si aucune langue en session, essayer de récupérer de la requête
    if not lang and request.args.get('lang') in AVAILABLE_LANGUAGES:
        lang = request.args.get('lang')
        session['language'] = lang
    
    # Si toujours pas de langue, utiliser la langue par défaut
    if not lang:
        lang = DEFAULT_LANGUAGE
    
    return lang

def get_translation(key, language=None):
    """
    Récupère une traduction spécifique pour une clé donnée
    """
    if not language:
        language = get_user_language()
    
    try:
        # Importer dynamiquement le module de traduction correspondant à la langue
        translation_module = importlib.import_module(f'translations.{language}')
        return translation_module.translations.get(key, key)
    except (ImportError, AttributeError) as e:
        logger.error(f"Erreur lors du chargement des traductions pour {language}: {e}")
        
        # En cas d'erreur, essayer avec la langue par défaut
        if language != DEFAULT_LANGUAGE:
            try:
                translation_module = importlib.import_module(f'translations.{DEFAULT_LANGUAGE}')
                return translation_module.translations.get(key, key)
            except (ImportError, AttributeError):
                return key
        return key

def get_all_translations(language=None):
    """
    Récupère toutes les traductions pour une langue donnée
    """
    if not language:
        language = get_user_language()
    
    try:
        # Importer dynamiquement le module de traduction correspondant à la langue
        translation_module = importlib.import_module(f'translations.{language}')
        return translation_module.translations
    except (ImportError, AttributeError) as e:
        logger.error(f"Erreur lors du chargement des traductions pour {language}: {e}")
        
        # En cas d'erreur, utiliser la langue par défaut
        if language != DEFAULT_LANGUAGE:
            try:
                translation_module = importlib.import_module(f'translations.{DEFAULT_LANGUAGE}')
                return translation_module.translations
            except (ImportError, AttributeError):
                return {}
        return {}

def get_direction(language=None):
    """
    Détermine la direction du texte (rtl pour l'arabe, ltr pour les autres)
    """
    if not language:
        language = get_user_language()
    
    # RTL pour l'arabe
    if language == 'ar':
        return 'rtl'
    
    # LTR pour toutes les autres langues
    return 'ltr'
