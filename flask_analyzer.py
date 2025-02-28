
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur de projets Flask utilisant le module IA
Permet d'analyser la structure, les erreurs et les fichiers dupliqués
"""
import os
import sys
import json
import logging
import hashlib
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import conditionnel du module principal d'IA
try:
    from module_IA import SecurityAnalysisAI
    from ia_mobile_auto_analyzer import MobileAutoAnalyzer
    AI_MODULE_AVAILABLE = True
    logger.info("Module d'IA importé avec succès")
except ImportError:
    AI_MODULE_AVAILABLE = False
    logger.warning("Module IA principal non disponible, fonctionnement en mode dégradé")

class FlaskProjectAnalyzer:
    """
    Analyseur automatique pour les projets Flask
    Permet d'analyser la structure, les interactions, les erreurs et les fichiers dupliqués
    """
    
    def __init__(self, project_dir: str = '.', cache_dir: str = 'instance/flask_analyses'):
        """
        Initialise l'analyseur de projets Flask
        
        Args:
            project_dir: Répertoire racine du projet Flask
            cache_dir: Répertoire pour le cache des analyses
        """
        self.project_dir = project_dir
        self.cache_dir = cache_dir
        self.ai_module = None
        self.mobile_analyzer = None
        self.results = {
            'structure': {},
            'interactions': {},
            'errors': [],
            'duplicates': [],
            'statistics': {},
            'recommendations': []
        }
        
        # Création du répertoire de cache si nécessaire
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialisation du module d'IA principal si disponible
        if AI_MODULE_AVAILABLE:
            try:
                self.ai_module = SecurityAnalysisAI()
                self.mobile_analyzer = MobileAutoAnalyzer(cache_dir=cache_dir)
                logger.info("Module d'IA de sécurité initialisé pour analyse de projet Flask")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du module IA: {e}")
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """
        Analyse la structure du projet Flask
        
        Returns:
            Dictionnaire avec les informations sur la structure du projet
        """
        logger.info("Analyse de la structure du projet Flask...")
        
        structure = {
            'directories': [],
            'files': [],
            'file_types': defaultdict(int),
            'blueprint_modules': [],
            'templates': [],
            'static_files': [],
            'app_structure': {}
        }
        
        # Parcourir récursivement le projet
        for root, dirs, files in os.walk(self.project_dir):
            # Ignorer les répertoires cachés et virtuels
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'venv']
            
            # Traiter le chemin relatif
            rel_path = os.path.relpath(root, self.project_dir)
            if rel_path == '.':
                rel_path = ''
            
            # Ajouter le répertoire à la structure
            if rel_path:
                structure['directories'].append(rel_path)
            
            # Traiter les fichiers
            for file in files:
                if file.startswith('.'):
                    continue
                
                # Chemin complet et relatif
                file_path = os.path.join(root, file)
                rel_file_path = os.path.join(rel_path, file) if rel_path else file
                
                # Ajouter à la liste des fichiers
                structure['files'].append(rel_file_path)
                
                # Comptabiliser les types de fichiers
                file_ext = os.path.splitext(file)[1].lower()
                structure['file_types'][file_ext] += 1
                
                # Détecter les blueprints Flask
                if file_ext == '.py':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'Blueprint(' in content:
                                structure['blueprint_modules'].append(rel_file_path)
                    except Exception as e:
                        logger.warning(f"Impossible de lire le fichier {rel_file_path}: {e}")
                
                # Détecter les templates
                if root.endswith('templates') or 'templates' in root.split(os.sep):
                    structure['templates'].append(rel_file_path)
                
                # Détecter les fichiers statiques
                if root.endswith('static') or 'static' in root.split(os.sep):
                    structure['static_files'].append(rel_file_path)
        
        # Analyse de la structure de l'application principale
        self._analyze_app_structure(structure)
        
        self.results['structure'] = structure
        return structure
    
    def _analyze_app_structure(self, structure: Dict[str, Any]) -> None:
        """
        Analyse la structure de l'application Flask
        
        Args:
            structure: Dictionnaire de la structure à mettre à jour
        """
        app_files = ['app.py', 'main.py', 'wsgi.py', '__init__.py']
        app_structure = {}
        
        for app_file in app_files:
            if app_file in structure['files']:
                # Analyser le fichier principal
                file_path = os.path.join(self.project_dir, app_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Détecter la création de l'application Flask
                        if 'Flask(' in content:
                            app_structure['main_app_file'] = app_file
                            app_structure['flask_instance'] = 'Standard Flask'
                        
                        # Détecter Flask-RESTful
                        if 'Api(' in content or 'from flask_restful' in content:
                            app_structure['rest_api'] = 'Flask-RESTful'
                        
                        # Détecter SQLAlchemy
                        if 'SQLAlchemy(' in content or 'from flask_sqlalchemy' in content:
                            app_structure['database'] = 'SQLAlchemy'
                        
                        # Détecter le mode debug
                        if 'debug=True' in content:
                            app_structure['debug_mode'] = True
                        
                        # Détecter la configuration
                        if 'config.from_object' in content or 'config.from_pyfile' in content:
                            app_structure['config_method'] = 'External Configuration'
                except Exception as e:
                    logger.warning(f"Impossible d'analyser {app_file}: {e}")
        
        structure['app_structure'] = app_structure
    
    def analyze_interactions(self) -> Dict[str, Any]:
        """
        Analyse les interactions entre les fichiers du projet
        
        Returns:
            Dictionnaire avec les informations sur les interactions
        """
        logger.info("Analyse des interactions du projet Flask...")
        
        interactions = {
            'imports': defaultdict(list),
            'routes': [],
            'models': [],
            'forms': [],
            'api_endpoints': [],
            'dependencies': defaultdict(list)
        }
        
        # Parcourir les fichiers Python pour analyser les interactions
        for file_path in self.results.get('structure', {}).get('files', []):
            if not file_path.endswith('.py'):
                continue
            
            full_path = os.path.join(self.project_dir, file_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Analyser les imports
                    self._analyze_imports(file_path, content, interactions)
                    
                    # Analyser les routes
                    if '@app.route' in content or '@blueprint.route' in content:
                        routes = self._extract_routes(content)
                        for route in routes:
                            route['file'] = file_path
                            interactions['routes'].append(route)
                    
                    # Analyser les modèles SQLAlchemy
                    if 'db.Model' in content:
                        models = self._extract_models(content)
                        for model in models:
                            model['file'] = file_path
                            interactions['models'].append(model)
                    
                    # Analyser les formulaires WTForms
                    if 'FlaskForm' in content or 'Form(' in content:
                        forms = self._extract_forms(content)
                        for form in forms:
                            form['file'] = file_path
                            interactions['forms'].append(form)
                    
                    # Analyser les endpoints d'API
                    if 'Resource' in content and ('get' in content or 'post' in content):
                        api_endpoints = self._extract_api_endpoints(content)
                        for endpoint in api_endpoints:
                            endpoint['file'] = file_path
                            interactions['api_endpoints'].append(endpoint)
            except Exception as e:
                logger.warning(f"Impossible d'analyser les interactions dans {file_path}: {e}")
        
        # Construire les dépendances entre fichiers
        for file, imports in interactions['imports'].items():
            for imp in imports:
                interactions['dependencies'][imp].append(file)
        
        self.results['interactions'] = dict(interactions)
        return dict(interactions)
    
    def _analyze_imports(self, file_path: str, content: str, interactions: Dict[str, Any]) -> None:
        """
        Analyse les imports dans un fichier Python
        
        Args:
            file_path: Chemin du fichier
            content: Contenu du fichier
            interactions: Dictionnaire des interactions à mettre à jour
        """
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                interactions['imports'][file_path].append(line)
    
    def _extract_routes(self, content: str) -> List[Dict[str, Any]]:
        """
        Extrait les routes définies dans le contenu du fichier
        
        Args:
            content: Contenu du fichier
            
        Returns:
            Liste des routes extraites
        """
        routes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if '@app.route' in line or '@blueprint.route' in line:
                # Extraire le chemin de la route
                route_path = line.split('(')[1].split(')')[0].strip()
                if route_path.startswith('"') or route_path.startswith("'"):
                    route_path = route_path.strip('"\'')
                
                # Extraire les méthodes HTTP
                methods = ['GET']
                if 'methods=' in line:
                    methods_str = line.split('methods=')[1].split(']')[0].split('[')[1]
                    methods = [m.strip(' "\'') for m in methods_str.split(',')]
                
                # Trouver le nom de la fonction associée
                function_name = ''
                for j in range(i+1, min(i+5, len(lines))):
                    if 'def ' in lines[j]:
                        function_name = lines[j].split('def ')[1].split('(')[0].strip()
                        break
                
                routes.append({
                    'path': route_path,
                    'methods': methods,
                    'function': function_name
                })
        
        return routes
    
    def _extract_models(self, content: str) -> List[Dict[str, Any]]:
        """
        Extrait les modèles SQLAlchemy définis dans le contenu
        
        Args:
            content: Contenu du fichier
            
        Returns:
            Liste des modèles extraits
        """
        models = []
        lines = content.split('\n')
        
        current_model = None
        fields = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('class ') and ('(db.Model)' in line or 'db.Model' in line):
                # Nouvelle classe de modèle
                if current_model:
                    models.append({
                        'name': current_model,
                        'fields': fields
                    })
                
                current_model = line.split('class ')[1].split('(')[0].strip()
                fields = []
            
            elif current_model and ' = db.Column(' in line:
                # Champ du modèle
                field_name = line.split(' = ')[0].strip()
                fields.append(field_name)
        
        # Ajouter le dernier modèle
        if current_model:
            models.append({
                'name': current_model,
                'fields': fields
            })
        
        return models
    
    def _extract_forms(self, content: str) -> List[Dict[str, Any]]:
        """
        Extrait les formulaires WTForms définis dans le contenu
        
        Args:
            content: Contenu du fichier
            
        Returns:
            Liste des formulaires extraits
        """
        forms = []
        lines = content.split('\n')
        
        current_form = None
        fields = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('class ') and ('(FlaskForm)' in line or 'FlaskForm' in line):
                # Nouvelle classe de formulaire
                if current_form:
                    forms.append({
                        'name': current_form,
                        'fields': fields
                    })
                
                current_form = line.split('class ')[1].split('(')[0].strip()
                fields = []
            
            elif current_form and ' = ' in line and any(field in line for field in ['StringField', 'IntegerField', 'BooleanField', 'SubmitField']):
                # Champ du formulaire
                field_name = line.split(' = ')[0].strip()
                fields.append(field_name)
        
        # Ajouter le dernier formulaire
        if current_form:
            forms.append({
                'name': current_form,
                'fields': fields
            })
        
        return forms
    
    def _extract_api_endpoints(self, content: str) -> List[Dict[str, Any]]:
        """
        Extrait les endpoints d'API définis dans le contenu
        
        Args:
            content: Contenu du fichier
            
        Returns:
            Liste des endpoints extraits
        """
        api_endpoints = []
        lines = content.split('\n')
        
        current_resource = None
        methods = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if line.startswith('class ') and '(Resource)' in line:
                # Nouvelle classe de ressource
                if current_resource:
                    api_endpoints.append({
                        'resource': current_resource,
                        'methods': methods
                    })
                
                current_resource = line.split('class ')[1].split('(')[0].strip()
                methods = []
            
            elif current_resource and line.startswith('def '):
                # Méthode HTTP
                method_name = line.split('def ')[1].split('(')[0].strip()
                if method_name.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    methods.append(method_name.upper())
        
        # Ajouter la dernière ressource
        if current_resource:
            api_endpoints.append({
                'resource': current_resource,
                'methods': methods
            })
        
        return api_endpoints
    
    def detect_errors(self) -> List[Dict[str, Any]]:
        """
        Détecte les erreurs potentielles dans le code Flask
        
        Returns:
            Liste des erreurs détectées
        """
        logger.info("Détection des erreurs dans le projet Flask...")
        
        errors = []
        
        # Vérifier les routes dupliquées
        routes = self.results.get('interactions', {}).get('routes', [])
        route_paths = {}
        
        for route in routes:
            path = route.get('path', '')
            if path in route_paths:
                errors.append({
                    'type': 'duplicate_route',
                    'severity': 'warning',
                    'description': f"Route dupliquée: {path}",
                    'location': {
                        'file1': route_paths[path].get('file', ''),
                        'function1': route_paths[path].get('function', ''),
                        'file2': route.get('file', ''),
                        'function2': route.get('function', '')
                    }
                })
            else:
                route_paths[path] = route
        
        # Vérifier les fichiers Python pour les erreurs de syntaxe et les problèmes courants
        for file_path in self.results.get('structure', {}).get('files', []):
            if not file_path.endswith('.py'):
                continue
            
            full_path = os.path.join(self.project_dir, file_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Vérifier debug=True
                    if 'debug=True' in content and 'if __name__ == ' not in content:
                        errors.append({
                            'type': 'debug_mode',
                            'severity': 'warning',
                            'description': "Mode debug activé en production",
                            'location': {
                                'file': file_path,
                                'line': content.split('\n').index([l for l in content.split('\n') if 'debug=True' in l][0]) + 1
                            }
                        })
                    
                    # Vérifier les secrets hardcodés
                    if 'SECRET_KEY' in content and any(s in content for s in ["'", '"']):
                        errors.append({
                            'type': 'hardcoded_secret',
                            'severity': 'error',
                            'description': "Clé secrète en dur dans le code",
                            'location': {
                                'file': file_path
                            }
                        })
                    
                    # Vérifier les imports circulaires potentiels
                    imports = [line.strip() for line in content.split('\n') if line.strip().startswith('from ') or line.strip().startswith('import ')]
                    module_name = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                    
                    for imp in imports:
                        imported_module = imp.split(' import ')[0].replace('from ', '')
                        if imported_module.startswith('.'):
                            imported_module = module_name.rsplit('.', 1)[0] + imported_module
                        
                        # Vérifier si le module importé importe également ce module
                        for other_file in self.results.get('structure', {}).get('files', []):
                            if not other_file.endswith('.py'):
                                continue
                            
                            other_module = other_file.replace('/', '.').replace('\\', '.').replace('.py', '')
                            if other_module == imported_module:
                                try:
                                    with open(os.path.join(self.project_dir, other_file), 'r', encoding='utf-8') as other_f:
                                        other_content = other_f.read()
                                        if f'from {module_name} import' in other_content or f'import {module_name}' in other_content:
                                            errors.append({
                                                'type': 'circular_import',
                                                'severity': 'error',
                                                'description': f"Import circulaire détecté entre {module_name} et {imported_module}",
                                                'location': {
                                                    'file1': file_path,
                                                    'file2': other_file
                                                }
                                            })
                                except Exception:
                                    pass
            except Exception as e:
                errors.append({
                    'type': 'file_error',
                    'severity': 'error',
                    'description': f"Erreur lors de l'analyse du fichier: {e}",
                    'location': {
                        'file': file_path
                    }
                })
        
        # Vérifier les templates pour les erreurs potentielles
        for file_path in self.results.get('structure', {}).get('templates', []):
            full_path = os.path.join(self.project_dir, file_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Vérifier les variables non échappées (XSS)
                    if '{{' in content and '|safe' in content:
                        errors.append({
                            'type': 'xss_vulnerability',
                            'severity': 'warning',
                            'description': "Utilisation potentiellement dangereuse de |safe dans un template",
                            'location': {
                                'file': file_path
                            }
                        })
            except Exception:
                pass
        
        self.results['errors'] = errors
        return errors
    
    def find_duplicates(self) -> List[Dict[str, Any]]:
        """
        Trouve les fichiers dupliqués ou similaires dans le projet
        
        Returns:
            Liste des fichiers dupliqués
        """
        logger.info("Recherche de fichiers dupliqués...")
        
        duplicates = []
        file_hashes = {}
        
        # Parcourir les fichiers pour calculer leur hash
        for file_path in self.results.get('structure', {}).get('files', []):
            full_path = os.path.join(self.project_dir, file_path)
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()
                    file_hash = hashlib.md5(content).hexdigest()
                    
                    if file_hash in file_hashes:
                        duplicates.append({
                            'type': 'identical_files',
                            'file1': file_hashes[file_hash],
                            'file2': file_path,
                            'similarity': 100.0
                        })
                    else:
                        file_hashes[file_hash] = file_path
            except Exception:
                pass
        
        # Rechercher les fichiers Python similaires (non identiques)
        python_files = {}
        for file_path in self.results.get('structure', {}).get('files', []):
            if not file_path.endswith('.py'):
                continue
                
            full_path = os.path.join(self.project_dir, file_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Supprimer les commentaires et les espaces pour la comparaison
                    cleaned_content = self._clean_python_content(content)
                    python_files[file_path] = cleaned_content
            except Exception:
                pass
        
        # Comparer les fichiers Python entre eux
        checked_pairs = set()
        for file1, content1 in python_files.items():
            for file2, content2 in python_files.items():
                if file1 == file2 or (file1, file2) in checked_pairs or (file2, file1) in checked_pairs:
                    continue
                
                checked_pairs.add((file1, file2))
                
                similarity = self._calculate_similarity(content1, content2)
                if similarity > 70.0:  # Seuil de similarité
                    duplicates.append({
                        'type': 'similar_files',
                        'file1': file1,
                        'file2': file2,
                        'similarity': similarity
                    })
        
        self.results['duplicates'] = duplicates
        return duplicates
    
    def _clean_python_content(self, content: str) -> str:
        """
        Nettoie le contenu Python pour la comparaison
        
        Args:
            content: Contenu du fichier Python
            
        Returns:
            Contenu nettoyé
        """
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Ignorer les commentaires et les lignes vides
            if not line or line.startswith('#'):
                continue
            # Supprimer les commentaires en fin de ligne
            if '#' in line:
                line = line.split('#')[0].strip()
            # Ajouter la ligne nettoyée
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """
        Calcule la similarité entre deux contenus
        
        Args:
            content1: Premier contenu
            content2: Deuxième contenu
            
        Returns:
            Pourcentage de similarité
        """
        if not content1 or not content2:
            return 0.0
        
        # Diviser en lignes pour une comparaison ligne par ligne
        lines1 = content1.split('\n')
        lines2 = content2.split('\n')
        
        # Compter les lignes identiques
        common_lines = 0
        for line in lines1:
            if line in lines2:
                common_lines += 1
        
        # Calculer la similarité
        total_lines = len(lines1) + len(lines2)
        if total_lines == 0:
            return 0.0
        
        similarity = (2 * common_lines / total_lines) * 100.0
        return round(similarity, 2)
    
    def generate_statistics(self) -> Dict[str, Any]:
        """
        Génère des statistiques sur le projet Flask
        
        Returns:
            Dictionnaire des statistiques
        """
        logger.info("Génération des statistiques du projet...")
        
        structure = self.results.get('structure', {})
        interactions = self.results.get('interactions', {})
        errors = self.results.get('errors', [])
        duplicates = self.results.get('duplicates', [])
        
        statistics = {
            'file_count': len(structure.get('files', [])),
            'directory_count': len(structure.get('directories', [])),
            'blueprint_count': len(structure.get('blueprint_modules', [])),
            'template_count': len(structure.get('templates', [])),
            'static_file_count': len(structure.get('static_files', [])),
            'route_count': len(interactions.get('routes', [])),
            'model_count': len(interactions.get('models', [])),
            'form_count': len(interactions.get('forms', [])),
            'api_endpoint_count': len(interactions.get('api_endpoints', [])),
            'error_count': len(errors),
            'error_severity': {
                'error': sum(1 for e in errors if e.get('severity') == 'error'),
                'warning': sum(1 for e in errors if e.get('severity') == 'warning'),
                'info': sum(1 for e in errors if e.get('severity') == 'info')
            },
            'duplicate_count': len(duplicates),
            'file_types': structure.get('file_types', {}),
            'error_types': {}
        }
        
        # Compter les types d'erreurs
        for error in errors:
            error_type = error.get('type', 'unknown')
            if error_type not in statistics['error_types']:
                statistics['error_types'][error_type] = 0
            statistics['error_types'][error_type] += 1
        
        self.results['statistics'] = statistics
        return statistics
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Génère des recommandations pour améliorer le projet
        
        Returns:
            Liste des recommandations
        """
        logger.info("Génération des recommandations...")
        
        recommendations = []
        statistics = self.results.get('statistics', {})
        errors = self.results.get('errors', [])
        
        # Recommandations basées sur les erreurs
        if statistics.get('error_count', 0) > 0:
            # Recommandations pour les secrets en dur
            if statistics.get('error_types', {}).get('hardcoded_secret', 0) > 0:
                recommendations.append({
                    'priority': 'high',
                    'title': "Sécuriser les clés secrètes",
                    'description': "Utilisez des variables d'environnement ou un fichier de configuration sécurisé pour les clés secrètes.",
                    'affected_files': [e['location']['file'] for e in errors if e['type'] == 'hardcoded_secret']
                })
            
            # Recommandations pour les imports circulaires
            if statistics.get('error_types', {}).get('circular_import', 0) > 0:
                recommendations.append({
                    'priority': 'medium',
                    'title': "Résoudre les imports circulaires",
                    'description': "Restructurez le code pour éviter les imports circulaires, par exemple en déplaçant des fonctions dans un module utilitaire.",
                    'affected_files': list(set([e['location']['file1'] for e in errors if e['type'] == 'circular_import'] +
                                              [e['location']['file2'] for e in errors if e['type'] == 'circular_import']))
                })
            
            # Recommandations pour le mode debug
            if statistics.get('error_types', {}).get('debug_mode', 0) > 0:
                recommendations.append({
                    'priority': 'high',
                    'title': "Désactiver le mode debug en production",
                    'description': "Utilisez des variables d'environnement pour activer le mode debug seulement en développement.",
                    'affected_files': [e['location']['file'] for e in errors if e['type'] == 'debug_mode']
                })
            
            # Recommandations pour les vulnérabilités XSS
            if statistics.get('error_types', {}).get('xss_vulnerability', 0) > 0:
                recommendations.append({
                    'priority': 'high',
                    'title': "Prévenir les vulnérabilités XSS",
                    'description': "Évitez d'utiliser le filtre |safe dans les templates, sauf si absolument nécessaire et avec du contenu sûr.",
                    'affected_files': [e['location']['file'] for e in errors if e['type'] == 'xss_vulnerability']
                })
        
        # Recommandations basées sur la structure
        if not statistics.get('blueprint_count', 0) and statistics.get('file_count', 0) > 10:
            recommendations.append({
                'priority': 'medium',
                'title': "Utiliser des Blueprints Flask",
                'description': "Pour un projet de cette taille, les Blueprints aideraient à mieux organiser le code.",
                'affected_files': []
            })
        
        # Recommandations basées sur les fichiers dupliqués
        if statistics.get('duplicate_count', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'title': "Réduire la duplication de code",
                'description': f"Le projet contient {statistics.get('duplicate_count', 0)} fichiers dupliqués ou similaires. Considérez la refactorisation.",
                'affected_files': list(set([d['file1'] for d in self.results.get('duplicates', [])] +
                                          [d['file2'] for d in self.results.get('duplicates', [])]))
            })
        
        # Utiliser le module IA pour enrichir les recommandations
        if self.ai_module:
            try:
                for i, rec in enumerate(recommendations):
                    insight = self.ai_module.generate_recommendation_insight(rec)
                    if insight:
                        recommendations[i]['ai_insight'] = insight
            except Exception as e:
                logger.error(f"Erreur lors de l'enrichissement des recommandations par l'IA: {e}")
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def analyze_project(self) -> Dict[str, Any]:
        """
        Analyse complète du projet Flask
        
        Returns:
            Résultats complets de l'analyse
        """
        logger.info("Démarrage de l'analyse complète du projet Flask...")
        
        # Structure
        self.analyze_project_structure()
        
        # Interactions
        self.analyze_interactions()
        
        # Erreurs
        self.detect_errors()
        
        # Fichiers dupliqués
        self.find_duplicates()
        
        # Statistiques
        self.generate_statistics()
        
        # Recommandations
        self.generate_recommendations()
        
        # Estimer le temps de travail si le module mobile est disponible
        if self.mobile_analyzer:
            self.results['estimated_work'] = self._estimate_work_time()
        
        # Générer l'évaluation binaire "oui/non" pour déterminer si le projet est conforme
        self.results['is_compliant'] = self._evaluate_compliance()
        
        # Sauvegarder les résultats
        self._save_results()
        
        logger.info("Analyse du projet terminée.")
        return self.results
    
    def _estimate_work_time(self) -> Dict[str, Any]:
        """
        Estime le temps de travail nécessaire pour résoudre les problèmes
        
        Returns:
            Estimation du temps de travail
        """
        if not hasattr(self.mobile_analyzer, '_estimate_work_time'):
            return {"total_minutes": 60, "format": "1h 0min"}
        
        # Adapter les données pour le module mobile
        app_analyses = []
        for error in self.results.get('errors', []):
            app_analyses.append({
                'risk_level': 'high' if error.get('severity') == 'error' else 'medium'
            })
        
        # Simuler le statut des mises à jour
        update_status = {
            'update_available': len(self.results.get('errors', [])) > 5,
            'update_priority': 'high' if len([e for e in self.results.get('errors', []) if e.get('severity') == 'error']) > 0 else 'medium'
        }
        
        # Utiliser la méthode du module mobile
        return self.mobile_analyzer._estimate_work_time(app_analyses, update_status)
    
    def _evaluate_compliance(self) -> Dict[str, Any]:
        """
        Évalue si le projet est conforme aux normes de qualité
        
        Returns:
            Évaluation "oui" ou "non" avec justification
        """
        errors = self.results.get('errors', [])
        critical_errors = [e for e in errors if e.get('severity') == 'error']
        
        is_compliant = len(critical_errors) == 0
        
        evaluation = {
            'result': "oui" if is_compliant else "non",
            'score': 100 - (len(critical_errors) * 10) - (len(errors) - len(critical_errors)) * 3,
            'justification': []
        }
        
        # Ajouter des justifications
        if is_compliant:
            evaluation['justification'].append("Le projet ne contient pas d'erreurs critiques")
        else:
            evaluation['justification'].append(f"Le projet contient {len(critical_errors)} erreurs critiques qui doivent être corrigées")
        
        # Analyses supplémentaires
        if len(self.results.get('duplicates', [])) > 3:
            evaluation['justification'].append("Trop de duplication de code")
            evaluation['score'] -= 10
            
        if not self.results.get('structure', {}).get('blueprint_modules', []) and len(self.results.get('structure', {}).get('files', [])) > 15:
            evaluation['justification'].append("Structure de projet non modulaire pour un projet de cette taille")
            evaluation['score'] -= 5
            
        # Seuil minimum
        evaluation['score'] = max(0, evaluation['score'])
        
        return evaluation
    
    def _save_results(self) -> None:
        """Sauvegarde les résultats de l'analyse dans un fichier JSON"""
        try:
            results_path = os.path.join(self.cache_dir, 'project_analysis.json')
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            logger.info(f"Résultats d'analyse sauvegardés dans {results_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats: {e}")

# Point d'entrée pour les tests
if __name__ == "__main__":
    # Analyser le projet courant
    analyzer = FlaskProjectAnalyzer()
    results = analyzer.analyze_project()
    
    # Afficher un résumé des résultats
    print(f"\nAnalyse du projet Flask terminée")
    print(f"Fichiers analysés: {results['statistics']['file_count']}")
    print(f"Erreurs détectées: {results['statistics']['error_count']}")
    print(f"Fichiers dupliqués: {results['statistics']['duplicate_count']}")
    print(f"Recommandations: {len(results['recommendations'])}")
    
    # Afficher l'évaluation de conformité
    compliance = results['is_compliant']
    print(f"\nÉvaluation de conformité: {compliance['result'].upper()}")
    print(f"Score: {compliance['score']}/100")
    print("Justification:")
    for reason in compliance['justification']:
        print(f"- {reason}")
    
    # Afficher l'estimation du temps de travail
    if 'estimated_work' in results:
        print(f"\nTemps de travail estimé: {results['estimated_work']['format']}")
    
    print("\nConsultez le fichier project_analysis.json pour plus de détails.")
