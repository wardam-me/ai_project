#!/usr/bin/env python3
"""
Module de gestion des traductions pour NetSecure Pro
Utilise Flask-Babel pour la gestion des langues
"""
from flask import request, session
from flask_babel import Babel

# Langues supportées
LANGUAGES = {
    'en': 'English',
    'fr': 'Français'
}

def setup_babel(app):
    """Configure Babel pour l'application Flask"""
    babel = Babel(app)
    
    @babel.localeselector
    def get_locale():
        """Détermine la langue à utiliser"""
        # Si l'utilisateur a explicitement choisi une langue, utiliser celle-ci
        if 'language' in session:
            return session['language']
        
        # Sinon, essayer de deviner la langue à partir des en-têtes HTTP
        return request.accept_languages.best_match(LANGUAGES.keys())
    
    return babel

def switch_language(lang):
    """Change la langue active de l'utilisateur"""
    if lang in LANGUAGES:
        session['language'] = lang
        return True
    return False

def get_language_info():
    """Retourne les informations sur les langues disponibles"""
    current_lang = 'fr'  # Langue par défaut
    
    if 'language' in session:
        current_lang = session['language']
    
    return {
        'current': current_lang,
        'available': LANGUAGES
    }

def get_translation(key, **kwargs):
    """Fonction d'aide pour obtenir une traduction
    Wrapper autour de gettext pour plus de flexibilité"""
    from flask_babel import gettext as _
    return _(key, **kwargs)