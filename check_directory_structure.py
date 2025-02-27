#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification de la structure des répertoires
Ce script vérifie que tous les répertoires et fichiers nécessaires existent
et crée les éléments manquants si nécessaire.
"""

import os
import logging
import json
import shutil
from typing import List, Dict, Tuple, Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DirectoryStructureChecker:
    """Vérificateur de structure de répertoires pour NetSecure Pro"""
    
    def __init__(self, project_root='.'):
        """
        Initialise le vérificateur de structure
        
        Args:
            project_root: Répertoire racine du projet (par défaut: '.')
        """
        self.project_root = project_root
        
        # Liste des répertoires requis
        self.required_directories = [
            'static',
            'static/css',
            'static/js',
            'static/img',
            'static/img/previews',
            'static/img/previews/network',
            'static/img/previews/protocol',
            'static/img/previews/vulnerability',
            'static/fonts',
            'static/exports',
            'static/exports/network',
            'static/exports/protocol',
            'static/exports/vulnerability',
            'static/templates',
            'templates',
            'templates/admin',
            'config',
            'instance'
        ]
        
        # Liste des fichiers requis (chemin, contenu par défaut)
        self.required_files = [
            ('config/default.py', self._get_default_config_content()),
            ('config/production.py', self._get_production_config_content()),
            ('config/development.py', self._get_development_config_content()),
            ('.flaskenv', self._get_flaskenv_content())
        ]
        
        # Structure des modules Python attendue
        self.expected_modules = {
            'app.py': 'Module principal Flask (Factory pattern)',
            'main.py': 'Point d\'entrée pour l\'application',
            'models.py': 'Modèles de données SQLAlchemy',
            'forms.py': 'Formulaires WTForms',
            'routes.py': 'Routes Flask',
            'extensions.py': 'Extensions Flask',
            'module_IA.py': 'Module d\'IA pour l\'analyse de sécurité',
            'ai_clone_manager.py': 'Gestionnaire de clones IA',
            'api_routes.py': 'Routes API',
            'network_detector.py': 'Détecteur de technologies réseau',
            'network_security.py': 'Analyseur de sécurité réseau',
            'network_topology.py': 'Gestionnaire de topologie réseau',
            'protocol_analyzer.py': 'Analyseur de protocoles de sécurité',
            'security_scoring.py': 'Système de notation de sécurité',
            'recommendations.py': 'Système de recommandations personnalisées',
            'assistant_securite.py': 'Assistant de sécurité',
            'security_assistant.py': 'Assistant intelligent d\'optimisation',
            'gamification.py': 'Système de gamification',
            'infographic_generator.py': 'Générateur d\'infographies',
            'ai_infographic_assistant.py': 'Assistant IA pour infographies',
            'translation.py': 'Gestion des traductions',
            'memory_monitor.py': 'Moniteur de mémoire'
        }
    
    def _get_default_config_content(self) -> str:
        """Contenu par défaut pour config/default.py"""
        return """\"\"\"
Configuration par défaut pour l'application NetSecure Pro
Utilisée comme base pour les autres configurations
\"\"\"

import os
from datetime import timedelta

# Configuration de base
DEBUG = False
TESTING = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-insecure')

# Configuration de la base de données
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuration de la session
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True

# Configuration des téléchargements
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

# Configuration de l'application
APP_NAME = "NetSecure Pro"
ADMIN_EMAIL = "admin@netsecure.pro"
DEFAULT_LANGUAGE = "fr"
SUPPORTED_LANGUAGES = ["fr", "en", "ar"]

# Configuration des chemins d'exportation
NETWORK_EXPORTS_PATH = "static/exports/network"
PROTOCOL_EXPORTS_PATH = "static/exports/protocol"
VULNERABILITY_EXPORTS_PATH = "static/exports/vulnerability"
"""
    
    def _get_production_config_content(self) -> str:
        """Contenu par défaut pour config/production.py"""
        return """\"\"\"
Configuration de production pour l'application NetSecure Pro
\"\"\"

from .default import *

DEBUG = False
TESTING = False

# En production, utiliser une clé secrète forte
SECRET_KEY = os.environ.get('SECRET_KEY')

# En production, utiliser le serveur PostgreSQL
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Configuration des logs
LOG_LEVEL = 'INFO'
LOG_FILE = '/var/log/netsecure/app.log'

# Configuration de sécurité
SESSION_COOKIE_SECURE = True
REMEMBER_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_HTTPONLY = True
"""
    
    def _get_development_config_content(self) -> str:
        """Contenu par défaut pour config/development.py"""
        return """\"\"\"
Configuration de développement pour l'application NetSecure Pro
\"\"\"

from .default import *

DEBUG = True
TESTING = False

# Configuration de la base de données pour le développement
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/development.db'

# Configuration des logs
LOG_LEVEL = 'DEBUG'
LOG_FILE = 'logs/development.log'

# Cache
CACHE_TYPE = 'simple'
"""
    
    def _get_flaskenv_content(self) -> str:
        """Contenu par défaut pour .flaskenv"""
        return """FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-key-insecure-do-not-use-in-production
"""
    
    def check_directories(self) -> Tuple[List[str], List[str]]:
        """
        Vérifie que les répertoires requis existent
        
        Returns:
            Tuple[List[str], List[str]]: (répertoires existants, répertoires manquants)
        """
        existing = []
        missing = []
        
        for directory in self.required_directories:
            dir_path = os.path.join(self.project_root, directory)
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                existing.append(directory)
            else:
                missing.append(directory)
        
        return existing, missing
    
    def check_files(self) -> Tuple[List[str], List[str]]:
        """
        Vérifie que les fichiers requis existent
        
        Returns:
            Tuple[List[str], List[str]]: (fichiers existants, fichiers manquants)
        """
        existing = []
        missing = []
        
        for file_path, _ in self.required_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                existing.append(file_path)
            else:
                missing.append(file_path)
        
        return existing, missing
    
    def check_modules(self) -> Tuple[List[str], List[str]]:
        """
        Vérifie que les modules Python attendus existent
        
        Returns:
            Tuple[List[str], List[str]]: (modules existants, modules manquants)
        """
        existing = []
        missing = []
        
        for module_file in self.expected_modules:
            full_path = os.path.join(self.project_root, module_file)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                existing.append(module_file)
            else:
                missing.append(module_file)
        
        return existing, missing
    
    def create_missing_directories(self) -> List[str]:
        """
        Crée les répertoires manquants
        
        Returns:
            List[str]: Liste des répertoires créés
        """
        _, missing = self.check_directories()
        created = []
        
        for directory in missing:
            dir_path = os.path.join(self.project_root, directory)
            try:
                os.makedirs(dir_path, exist_ok=True)
                created.append(directory)
                logger.info(f"Répertoire créé: {directory}")
            except Exception as e:
                logger.error(f"Erreur lors de la création du répertoire {directory}: {e}")
        
        return created
    
    def create_missing_files(self) -> List[str]:
        """
        Crée les fichiers manquants avec leur contenu par défaut
        
        Returns:
            List[str]: Liste des fichiers créés
        """
        _, missing = self.check_files()
        created = []
        
        for file_path, content in self.required_files:
            if file_path in missing:
                full_path = os.path.join(self.project_root, file_path)
                
                # S'assurer que le répertoire parent existe
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                try:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created.append(file_path)
                    logger.info(f"Fichier créé: {file_path}")
                except Exception as e:
                    logger.error(f"Erreur lors de la création du fichier {file_path}: {e}")
        
        return created
    
    def generate_report(self) -> Dict:
        """
        Génère un rapport sur la structure du projet
        
        Returns:
            Dict: Rapport sur la structure du projet
        """
        existing_dirs, missing_dirs = self.check_directories()
        existing_files, missing_files = self.check_files()
        existing_modules, missing_modules = self.check_modules()
        
        report = {
            "directories": {
                "existing": existing_dirs,
                "missing": missing_dirs,
                "total_existing": len(existing_dirs),
                "total_missing": len(missing_dirs)
            },
            "files": {
                "existing": existing_files,
                "missing": missing_files,
                "total_existing": len(existing_files),
                "total_missing": len(missing_files)
            },
            "modules": {
                "existing": existing_modules,
                "missing": missing_modules,
                "total_existing": len(existing_modules),
                "total_missing": len(missing_modules)
            },
            "structure_complete": len(missing_dirs) == 0 and len(missing_files) == 0,
            "core_modules_complete": len(missing_modules) == 0
        }
        
        # Enregistrer le rapport au format JSON
        report_path = os.path.join(self.project_root, 'directory_structure_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Rapport de structure enregistré dans {report_path}")
        return report
    
    def verify_and_fix_structure(self, fix_missing: bool = True) -> Dict:
        """
        Vérifie la structure et corrige les éléments manquants si demandé
        
        Args:
            fix_missing: Créer les éléments manquants si True
            
        Returns:
            Dict: Rapport sur la structure du projet et les corrections apportées
        """
        logger.info("Vérification de la structure du projet...")
        
        # Vérifier la structure actuelle
        existing_dirs, missing_dirs = self.check_directories()
        existing_files, missing_files = self.check_files()
        existing_modules, missing_modules = self.check_modules()
        
        # Corriger les éléments manquants si demandé
        created_dirs = []
        created_files = []
        
        if fix_missing:
            if missing_dirs:
                logger.info(f"Création des répertoires manquants ({len(missing_dirs)})...")
                created_dirs = self.create_missing_directories()
            
            if missing_files:
                logger.info(f"Création des fichiers manquants ({len(missing_files)})...")
                created_files = self.create_missing_files()
        
        # Générer le rapport
        report = {
            "verification": {
                "directories": {
                    "existing": existing_dirs,
                    "missing": missing_dirs,
                    "total_existing": len(existing_dirs),
                    "total_missing": len(missing_dirs)
                },
                "files": {
                    "existing": existing_files,
                    "missing": missing_files,
                    "total_existing": len(existing_files),
                    "total_missing": len(missing_files)
                },
                "modules": {
                    "existing": existing_modules,
                    "missing": missing_modules,
                    "total_existing": len(existing_modules),
                    "total_missing": len(missing_modules),
                    "missing_details": {module: self.expected_modules[module] for module in missing_modules}
                }
            },
            "corrections": {
                "directories_created": created_dirs,
                "files_created": created_files,
                "total_dirs_created": len(created_dirs),
                "total_files_created": len(created_files)
            },
            "status": {
                "structure_complete": (len(missing_dirs) - len(created_dirs)) == 0 and (len(missing_files) - len(created_files)) == 0,
                "core_modules_complete": len(missing_modules) == 0
            }
        }
        
        # Enregistrer le rapport au format JSON
        report_path = os.path.join(self.project_root, 'directory_structure_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Rapport de structure enregistré dans {report_path}")
        return report
    
    def print_summary(self, report: Optional[Dict] = None):
        """
        Affiche un résumé du rapport de structure
        
        Args:
            report: Rapport de structure (générér si None)
        """
        if report is None:
            report = self.generate_report()
        
        logger.info("=== RÉSUMÉ DE LA STRUCTURE DU PROJET ===")
        
        # Résumé des répertoires
        logger.info(f"Répertoires: {report['verification']['directories']['total_existing']} existants, "
                    f"{report['verification']['directories']['total_missing']} manquants")
        
        if report['verification']['directories']['missing']:
            logger.info("Répertoires manquants:")
            for directory in report['verification']['directories']['missing']:
                logger.info(f"  - {directory}")
        
        # Résumé des fichiers
        logger.info(f"Fichiers requis: {report['verification']['files']['total_existing']} existants, "
                    f"{report['verification']['files']['total_missing']} manquants")
        
        if report['verification']['files']['missing']:
            logger.info("Fichiers requis manquants:")
            for file_path in report['verification']['files']['missing']:
                logger.info(f"  - {file_path}")
        
        # Résumé des modules
        logger.info(f"Modules Python: {report['verification']['modules']['total_existing']} existants, "
                    f"{report['verification']['modules']['total_missing']} manquants")
        
        if report['verification']['modules']['missing']:
            logger.info("Modules Python manquants:")
            for module, description in report['verification']['modules']['missing_details'].items():
                logger.info(f"  - {module}: {description}")
        
        # Résumé des corrections
        if 'corrections' in report:
            if report['corrections']['total_dirs_created'] > 0:
                logger.info(f"Répertoires créés: {report['corrections']['total_dirs_created']}")
            
            if report['corrections']['total_files_created'] > 0:
                logger.info(f"Fichiers créés: {report['corrections']['total_files_created']}")
        
        # Statut global
        if report['status']['structure_complete']:
            logger.info("Structure de base complète: OUI")
        else:
            logger.info("Structure de base complète: NON")
        
        if report['status']['core_modules_complete']:
            logger.info("Modules essentiels complets: OUI")
        else:
            logger.info("Modules essentiels complets: NON")

def main():
    """Fonction principale"""
    checker = DirectoryStructureChecker()
    report = checker.verify_and_fix_structure(fix_missing=True)
    checker.print_summary(report)

if __name__ == "__main__":
    main()