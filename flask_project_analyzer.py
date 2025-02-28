
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur de projets Flask utilisant le module IA
Permet d'analyser la structure, les erreurs et les fichiers dupliqués d'un projet Flask
"""
import os
import sys
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import conditionnel du module principal d'IA
try:
    from module_IA import SecurityAnalysisAI
    AI_MODULE_AVAILABLE = True
    logger.info("Module SecurityAnalysisAI importé avec succès")
except ImportError:
    AI_MODULE_AVAILABLE = False
    logger.warning("Module IA principal non disponible, fonctionnement en mode dégradé")

# Import conditionnel du module d'IA mobile
try:
    from ia_mobile_auto_analyzer import MobileAutoAnalyzer
    MOBILE_AI_AVAILABLE = True
    logger.info("Module d'IA mobile importé avec succès")
except ImportError:
    MOBILE_AI_AVAILABLE = False
    logger.warning("Module IA mobile non disponible, fonctionnement en mode dégradé")

class FlaskProjectAIAnalyzer:
    """
    Analyseur de projets Flask utilisant l'intelligence artificielle
    pour détecter les problèmes et proposer des améliorations
    """
    
    def __init__(self, project_dir: str = '.', output_dir: str = None):
        """
        Initialise l'analyseur de projets Flask
        
        Args:
            project_dir: Répertoire du projet Flask à analyser
            output_dir: Répertoire de sortie pour les rapports (par défaut: project_dir)
        """
        self.project_dir = os.path.abspath(project_dir)
        self.output_dir = output_dir or self.project_dir
        
        # S'assurer que le répertoire de sortie existe
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialiser le module IA si disponible
        self.ai_module = None
        self.mobile_analyzer = None
        
        if AI_MODULE_AVAILABLE:
            try:
                self.ai_module = SecurityAnalysisAI()
                logger.info("Module d'IA de sécurité initialisé pour analyse Flask")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du module IA: {e}")
        
        if MOBILE_AI_AVAILABLE:
            try:
                self.mobile_analyzer = MobileAutoAnalyzer(cache_dir="instance/mobile_cache")
                logger.info("Module d'IA mobile initialisé pour analyse Flask")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du module IA mobile: {e}")
        
        # Résultats de l'analyse
        self.report = {
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "project_dir": self.project_dir,
                "ai_module_available": AI_MODULE_AVAILABLE,
                "mobile_ai_available": MOBILE_AI_AVAILABLE,
                "execution_time": 0
            },
            "project": {
                "structure": [],
                "file_count": 0,
                "dir_count": 0,
                "extensions": {}
            },
            "structure": {
                "flask_specific": {},
                "missing_elements": [],
                "best_practices": {}
            },
            "issues": {
                "security": {
                    "count": 0,
                    "items": []
                },
                "performance": {
                    "count": 0,
                    "items": []
                },
                "lsp": {
                    "count": 0, 
                    "items": []
                }
            },
            "duplicates": {
                "count": 0,
                "groups": []
            },
            "ai_analysis": {
                "score": 0,
                "highlights": [],
                "recommendations": []
            },
            "work_time": {
                "temps_total": 0,
                "details": {}
            }
        }
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Exécute l'analyse complète du projet Flask
        
        Returns:
            Dict[str, Any]: Rapport d'analyse complet
        """
        start_time = time.time()
        logger.info(f"Démarrage de l'analyse du projet Flask dans: {self.project_dir}")
        
        # Étape 1: Analyser la structure du projet
        self._analyze_project_structure()
        
        # Étape 2: Analyser les fichiers spécifiques à Flask
        self._analyze_flask_files()
        
        # Étape 3: Détecter les problèmes de sécurité
        self._detect_security_issues()
        
        # Étape 4: Détecter les problèmes de performance
        self._detect_performance_issues()
        
        # Étape 5: Détecter les erreurs LSP (Language Server Protocol)
        self._detect_lsp_errors()
        
        # Étape 6: Détecter les fichiers dupliqués
        self._detect_duplicate_files()
        
        # Étape 7: Générer l'analyse IA
        if self.ai_module is not None:
            self._generate_ai_analysis()
        
        # Étape 8: Estimer le temps de travail
        if self.mobile_analyzer is not None:
            self._estimate_work_time()
        
        # Finaliser le rapport
        execution_time = time.time() - start_time
        self.report["meta"]["execution_time"] = execution_time
        
        # Sauvegarder le rapport
        self._save_report()
        
        # Générer un résumé textuel
        self._generate_text_summary()
        
        logger.info(f"Analyse terminée en {execution_time:.2f} secondes")
        return self.report
    
    def _analyze_project_structure(self) -> None:
        """Analyse la structure du projet Flask"""
        logger.info("Analyse de la structure du projet...")
        
        structure = []
        extensions = {}
        
        # Parcourir récursivement le projet
        for root, dirs, files in os.walk(self.project_dir):
            # Ignorer les répertoires cachés et les environnements virtuels
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'venv']
            
            # Chemin relatif
            rel_path = os.path.relpath(root, self.project_dir)
            if rel_path == '.':
                rel_path = ''
            
            # Ajouter le répertoire à la structure
            if rel_path:
                structure.append({
                    "type": "directory",
                    "path": rel_path
                })
            
            # Traiter les fichiers
            for file in files:
                if file.startswith('.'):
                    continue
                
                # Chemin complet et relatif
                file_path = os.path.join(root, file)
                rel_file_path = os.path.join(rel_path, file) if rel_path else file
                
                # Obtenir l'extension
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1
                
                # Ajouter le fichier à la structure
                structure.append({
                    "type": "file",
                    "path": rel_file_path,
                    "extension": ext
                })
        
        # Mettre à jour le rapport
        self.report["project"]["structure"] = structure
        self.report["project"]["file_count"] = sum(1 for item in structure if item["type"] == "file")
        self.report["project"]["dir_count"] = sum(1 for item in structure if item["type"] == "directory")
        self.report["project"]["extensions"] = extensions
    
    def _analyze_flask_files(self) -> None:
        """Analyse les fichiers spécifiques à Flask"""
        logger.info("Analyse des fichiers spécifiques à Flask...")
        
        flask_specific = {
            "app_file": None,
            "blueprint_pattern": False,
            "sqlalchemy_used": False,
            "wtforms_used": False,
            "templates_dir": False,
            "static_dir": False,
            "config_file": False,
            "routes_file": False,
            "models_file": False,
            "forms_file": False,
            "missing_elements": []
        }
        
        # Vérifier les éléments clés d'un projet Flask
        structure = self.report["project"]["structure"]
        
        # Vérifier les répertoires essentiels
        templates_found = any(item["type"] == "directory" and item["path"] == "templates" for item in structure)
        static_found = any(item["type"] == "directory" and item["path"] == "static" for item in structure)
        
        flask_specific["templates_dir"] = templates_found
        flask_specific["static_dir"] = static_found
        
        if not templates_found:
            flask_specific["missing_elements"].append("templates_directory")
        
        if not static_found:
            flask_specific["missing_elements"].append("static_directory")
        
        # Vérifier les fichiers Python pour trouver app.py, routes.py, etc.
        app_files = ["app.py", "main.py", "wsgi.py", "__init__.py"]
        app_file_found = False
        
        for item in structure:
            if item["type"] == "file" and item["extension"] == ".py":
                file_path = os.path.join(self.project_dir, item["path"])
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Détecter l'application Flask
                        if 'Flask(' in content and not app_file_found:
                            flask_specific["app_file"] = item["path"]
                            app_file_found = True
                        
                        # Détecter les Blueprints
                        if 'Blueprint(' in content:
                            flask_specific["blueprint_pattern"] = True
                        
                        # Détecter SQLAlchemy
                        if 'SQLAlchemy(' in content or 'db.Model' in content:
                            flask_specific["sqlalchemy_used"] = True
                        
                        # Détecter WTForms
                        if 'FlaskForm' in content:
                            flask_specific["wtforms_used"] = True
                        
                        # Détecter les fichiers spécifiques
                        filename = os.path.basename(item["path"])
                        if filename == "config.py":
                            flask_specific["config_file"] = True
                        elif filename == "routes.py":
                            flask_specific["routes_file"] = True
                        elif filename == "models.py":
                            flask_specific["models_file"] = True
                        elif filename == "forms.py":
                            flask_specific["forms_file"] = True
                except Exception as e:
                    logger.warning(f"Erreur lors de la lecture de {file_path}: {e}")
        
        # Vérifier les éléments manquants
        if not app_file_found:
            flask_specific["missing_elements"].append("flask_application_file")
        
        if not flask_specific["config_file"]:
            flask_specific["missing_elements"].append("configuration_file")
        
        # Mettre à jour le rapport
        self.report["structure"]["flask_specific"] = flask_specific
        self.report["structure"]["missing_elements"] = flask_specific["missing_elements"]
    
    def _detect_security_issues(self) -> None:
        """Détecte les problèmes de sécurité dans le projet Flask"""
        logger.info("Détection des problèmes de sécurité...")
        
        security_issues = []
        
        # Parcourir les fichiers Python
        for item in self.report["project"]["structure"]:
            if item["type"] == "file" and item["extension"] == ".py":
                file_path = os.path.join(self.project_dir, item["path"])
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Vérifier les clés secrètes en dur
                        for i, line in enumerate(lines):
                            if 'SECRET_KEY' in line and ('=' in line) and ('"' in line or "'" in line):
                                security_issues.append({
                                    "severity": "high",
                                    "type": "hardcoded_secret",
                                    "file": item["path"],
                                    "line": i + 1,
                                    "description": "Clé secrète codée en dur",
                                    "snippet": line.strip()
                                })
                        
                        # Vérifier debug=True en production
                        for i, line in enumerate(lines):
                            if 'debug=True' in line and 'if __name__' not in line:
                                security_issues.append({
                                    "severity": "medium",
                                    "type": "debug_mode",
                                    "file": item["path"],
                                    "line": i + 1,
                                    "description": "Mode debug activé en production",
                                    "snippet": line.strip()
                                })
                        
                        # Vérifier l'utilisation dangereuse de eval() ou exec()
                        for i, line in enumerate(lines):
                            if ('eval(' in line or 'exec(' in line) and 'def ' not in line:
                                security_issues.append({
                                    "severity": "high",
                                    "type": "code_execution",
                                    "file": item["path"],
                                    "line": i + 1,
                                    "description": "Utilisation dangereuse de eval() ou exec()",
                                    "snippet": line.strip()
                                })
                except Exception as e:
                    logger.warning(f"Erreur lors de l'analyse de sécurité de {file_path}: {e}")
        
        # Parcourir les templates pour détecter les vulnérabilités XSS
        for item in self.report["project"]["structure"]:
            if item["type"] == "file" and item["path"].startswith("templates/") and item["extension"] == ".html":
                file_path = os.path.join(self.project_dir, item["path"])
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Vérifier l'utilisation dangereuse de |safe
                        for i, line in enumerate(lines):
                            if '{{' in line and '|safe' in line:
                                security_issues.append({
                                    "severity": "medium",
                                    "type": "xss_vulnerability",
                                    "file": item["path"],
                                    "line": i + 1,
                                    "description": "Utilisation potentiellement dangereuse de |safe",
                                    "snippet": line.strip()
                                })
                except Exception as e:
                    logger.warning(f"Erreur lors de l'analyse de sécurité de {file_path}: {e}")
        
        # Mettre à jour le rapport
        self.report["issues"]["security"]["items"] = security_issues
        self.report["issues"]["security"]["count"] = len(security_issues)
    
    def _detect_performance_issues(self) -> None:
        """Détecte les problèmes de performance dans le projet Flask"""
        logger.info("Détection des problèmes de performance...")
        
        performance_issues = []
        
        # Parcourir les fichiers Python
        for item in self.report["project"]["structure"]:
            if item["type"] == "file" and item["extension"] == ".py":
                file_path = os.path.join(self.project_dir, item["path"])
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Vérifier les requêtes N+1 potentielles
                        for i, line in enumerate(lines):
                            if 'for' in line and '.query.' in line:
                                performance_issues.append({
                                    "severity": "medium",
                                    "type": "n_plus_1_query",
                                    "file": item["path"],
                                    "line": i + 1,
                                    "description": "Requête N+1 potentielle",
                                    "snippet": line.strip()
                                })
                        
                        # Vérifier les imports globaux coûteux
                        for i, line in enumerate(lines):
                            if ('import numpy' in line or 'import pandas' in line or 'import tensorflow' in line) and 'def ' not in content:
                                performance_issues.append({
                                    "severity": "low",
                                    "type": "heavy_import",
                                    "file": item["path"],
                                    "line": i + 1,
                                    "description": "Import global coûteux",
                                    "snippet": line.strip()
                                })
                except Exception as e:
                    logger.warning(f"Erreur lors de l'analyse de performance de {file_path}: {e}")
        
        # Mettre à jour le rapport
        self.report["issues"]["performance"]["items"] = performance_issues
        self.report["issues"]["performance"]["count"] = len(performance_issues)
    
    def _detect_lsp_errors(self) -> None:
        """Détecte les erreurs LSP (Language Server Protocol) dans le projet Flask"""
        logger.info("Détection des erreurs LSP...")
        
        lsp_errors = []
        
        # Parcourir les fichiers Python
        for item in self.report["project"]["structure"]:
            if item["type"] == "file" and item["extension"] == ".py":
                file_path = os.path.join(self.project_dir, item["path"])
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Vérifier les imports non résolus
                        for i, line in enumerate(lines):
                            if line.strip().startswith(('import', 'from')) and ' import ' in line:
                                # Vérifier les imports qui pourraient ne pas exister
                                module_name = line.split(' import ')[0].replace('from ', '').strip()
                                if module_name not in ['flask', 'os', 'sys', 'json', 'datetime', 'logging', 'typing']:
                                    # Vérifier si c'est un module interne au projet
                                    is_internal = False
                                    for other_item in self.report["project"]["structure"]:
                                        if other_item["type"] == "file" and other_item["extension"] == ".py":
                                            other_path = other_item["path"].replace('.py', '').replace('/', '.')
                                            if module_name == other_path:
                                                is_internal = True
                                                break
                                    
                                    if not is_internal:
                                        lsp_errors.append({
                                            "severity": "warning",
                                            "type": "unresolved_import",
                                            "file": item["path"],
                                            "line": i + 1,
                                            "description": f"Import potentiellement non résolu: {module_name}",
                                            "snippet": line.strip()
                                        })
                        
                        # Vérifier les variables non définies
                        defined_vars = set()
                        for i, line in enumerate(lines):
                            # Ajouter les variables définies
                            if '=' in line and not line.strip().startswith('#'):
                                var_name = line.split('=')[0].strip()
                                if var_name and ' ' not in var_name:
                                    defined_vars.add(var_name)
                            
                            # Vérifier les variables utilisées
                            words = line.split()
                            for word in words:
                                if (word not in defined_vars and
                                    word not in ['if', 'for', 'while', 'def', 'class', 'return', 'import', 'from', 'as'] and
                                    not word.startswith(('self.', 'cls.', 'os.', 'sys.', 'json.', 'flask.')) and
                                    word.isalpha() and word.islower()):
                                    
                                    # Ignorer les mots communs
                                    if word not in ['in', 'and', 'or', 'not', 'is', 'None', 'True', 'False', 'print', 'app']:
                                        lsp_errors.append({
                                            "severity": "info",
                                            "type": "undefined_variable",
                                            "file": item["path"],
                                            "line": i + 1,
                                            "description": f"Variable potentiellement non définie: {word}",
                                            "snippet": line.strip()
                                        })
                                        break
                except Exception as e:
                    logger.warning(f"Erreur lors de l'analyse LSP de {file_path}: {e}")
        
        # Mettre à jour le rapport
        self.report["issues"]["lsp"]["items"] = lsp_errors
        self.report["issues"]["lsp"]["count"] = len(lsp_errors)
    
    def _detect_duplicate_files(self) -> None:
        """Détecte les fichiers dupliqués dans le projet Flask"""
        logger.info("Détection des fichiers dupliqués...")
        
        # Structures pour stocker les hachages de fichiers
        file_hashes = {}
        file_contents = {}
        duplicate_groups = []
        
        # Parcourir les fichiers
        for item in self.report["project"]["structure"]:
            if item["type"] == "file":
                file_path = os.path.join(self.project_dir, item["path"])
                
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        
                        # Calculer le hachage MD5 du contenu
                        import hashlib
                        file_hash = hashlib.md5(content).hexdigest()
                        
                        # Stocker le contenu pour l'analyse de similarité
                        if item["extension"] in ['.py', '.js', '.html', '.css']:
                            try:
                                file_contents[item["path"]] = content.decode('utf-8')
                            except:
                                pass
                        
                        # Vérifier si ce hachage existe déjà
                        if file_hash in file_hashes:
                            # Ce fichier est un duplicata exact
                            found = False
                            for group in duplicate_groups:
                                if group["type"] == "exact" and file_hashes[file_hash] in group["files"]:
                                    group["files"].append(item["path"])
                                    found = True
                                    break
                            
                            if not found:
                                duplicate_groups.append({
                                    "type": "exact",
                                    "similarity": 100,
                                    "files": [file_hashes[file_hash], item["path"]]
                                })
                        else:
                            file_hashes[file_hash] = item["path"]
                except Exception as e:
                    logger.warning(f"Erreur lors de l'analyse de duplicata de {file_path}: {e}")
        
        # Détecter les fichiers similaires (non identiques)
        processed_pairs = set()
        
        for path1, content1 in file_contents.items():
            for path2, content2 in file_contents.items():
                if path1 == path2:
                    continue
                
                # Éviter de traiter la même paire deux fois
                pair = frozenset([path1, path2])
                if pair in processed_pairs:
                    continue
                
                processed_pairs.add(pair)
                
                # Vérifier si les fichiers ont la même extension
                ext1 = os.path.splitext(path1)[1]
                ext2 = os.path.splitext(path2)[1]
                
                if ext1 == ext2:
                    # Calculer la similarité
                    similarity = self._calculate_similarity(content1, content2)
                    
                    if similarity >= 70:  # Seuil de similarité
                        # Vérifier si l'un des fichiers est déjà dans un groupe
                        found = False
                        for group in duplicate_groups:
                            if group["type"] == "similar" and (path1 in group["files"] or path2 in group["files"]):
                                # Ajouter le fichier manquant s'il n'est pas déjà dans le groupe
                                if path1 not in group["files"]:
                                    group["files"].append(path1)
                                if path2 not in group["files"]:
                                    group["files"].append(path2)
                                found = True
                                break
                        
                        if not found:
                            duplicate_groups.append({
                                "type": "similar",
                                "similarity": similarity,
                                "files": [path1, path2]
                            })
        
        # Mettre à jour le rapport
        self.report["duplicates"]["groups"] = duplicate_groups
        self.report["duplicates"]["count"] = len(duplicate_groups)
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """
        Calcule la similarité entre deux contenus textuels
        
        Args:
            content1: Premier contenu
            content2: Deuxième contenu
            
        Returns:
            float: Pourcentage de similarité (0-100)
        """
        if not content1 or not content2:
            return 0.0
        
        # Diviser en lignes pour une comparaison ligne par ligne
        lines1 = content1.split('\n')
        lines2 = content2.split('\n')
        
        # Compter les lignes identiques
        common_lines = 0
        for line in lines1:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line in lines2:
                common_lines += 1
        
        # Calculer la similarité
        total_lines = len(lines1) + len(lines2)
        if total_lines == 0:
            return 0.0
        
        similarity = (2 * common_lines / total_lines) * 100.0
        return round(similarity, 1)
    
    def _generate_ai_analysis(self) -> None:
        """Génère une analyse IA des problèmes détectés"""
        logger.info("Génération de l'analyse IA...")
        
        security_issues = self.report["issues"]["security"]["items"]
        performance_issues = self.report["issues"]["performance"]["items"]
        lsp_errors = self.report["issues"]["lsp"]["items"]
        duplicate_groups = self.report["duplicates"]["groups"]
        
        # Calculer un score basé sur les problèmes détectés
        security_penalty = len(security_issues) * 5
        perf_penalty = len(performance_issues) * 3
        lsp_penalty = len(lsp_errors) * 1
        dup_penalty = len(duplicate_groups) * 2
        
        base_score = 100
        final_score = max(0, base_score - security_penalty - perf_penalty - lsp_penalty - dup_penalty)
        
        # Générer des points forts
        highlights = []
        
        if security_issues:
            severity_counts = {}
            for issue in security_issues:
                severity = issue.get("severity", "medium")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if severity_counts.get("high", 0) > 0:
                highlights.append({
                    "type": "security",
                    "severity": "high",
                    "description": f"Détection de {severity_counts.get('high', 0)} problèmes de sécurité critiques qui nécessitent une attention immédiate."
                })
            elif severity_counts.get("medium", 0) > 0:
                highlights.append({
                    "type": "security",
                    "severity": "medium",
                    "description": f"Détection de {severity_counts.get('medium', 0)} problèmes de sécurité de gravité moyenne."
                })
        
        if duplicate_groups:
            highlights.append({
                "type": "duplication",
                "severity": "medium",
                "description": f"Détection de {len(duplicate_groups)} groupes de fichiers dupliqués ou similaires, ce qui complique la maintenance."
            })
        
        # Générer des recommandations
        recommendations = []
        
        # Recommandations de sécurité
        if any(issue["type"] == "hardcoded_secret" for issue in security_issues):
            recommendations.append({
                "priority": "high",
                "category": "security",
                "title": "Sécuriser les clés secrètes",
                "description": "Remplacer les clés secrètes en dur par des variables d'environnement ou un fichier de configuration sécurisé.",
                "ai_insight": "Les secrets codés en dur dans le code source représentent un risque majeur, surtout si le code est partagé ou hébergé sur des dépôts publics."
            })
        
        if any(issue["type"] == "debug_mode" for issue in security_issues):
            recommendations.append({
                "priority": "medium",
                "category": "security",
                "title": "Désactiver le mode debug en production",
                "description": "Configurer le mode debug pour qu'il soit actif uniquement en environnement de développement.",
                "ai_insight": "Le mode debug exposé en production peut révéler des informations sensibles sur l'application et son environnement."
            })
        
        # Recommandations de structure
        flask_specific = self.report["structure"]["flask_specific"]
        if not flask_specific.get("blueprint_pattern", False) and self.report["project"]["file_count"] > 10:
            recommendations.append({
                "priority": "medium",
                "category": "structure",
                "title": "Adopter le pattern Blueprint",
                "description": "Refactoriser l'application pour utiliser des Blueprints Flask afin d'améliorer la modularité.",
                "ai_insight": "Les Blueprints permettent une meilleure organisation du code et facilitent la maintenance d'applications de taille moyenne à grande."
            })
        
        # Recommandations de duplication
        if duplicate_groups:
            recommendations.append({
                "priority": "medium",
                "category": "duplication",
                "title": "Éliminer les fichiers dupliqués",
                "description": f"Fusionner ou refactoriser les {len(duplicate_groups)} groupes de fichiers similaires pour réduire la duplication.",
                "ai_insight": "La duplication de code augmente la complexité de maintenance et le risque d'incohérences lors des mises à jour."
            })
        
        # Utiliser le module IA pour enrichir les recommandations
        if self.ai_module:
            for i, rec in enumerate(recommendations):
                try:
                    insight = self.ai_module.generate_recommendation_insight(rec)
                    if insight:
                        recommendations[i]["ai_insight"] = insight
                except Exception as e:
                    logger.warning(f"Erreur lors de la génération d'insights IA: {e}")
        
        # Mettre à jour le rapport
        self.report["ai_analysis"]["score"] = final_score
        self.report["ai_analysis"]["highlights"] = highlights
        self.report["ai_analysis"]["recommendations"] = recommendations
    
    def _estimate_work_time(self) -> None:
        """Estime le temps de travail nécessaire pour résoudre les problèmes"""
        logger.info("Estimation du temps de travail...")
        
        # Compter les différents types de problèmes
        security_count = self.report["issues"]["security"]["count"]
        performance_count = self.report["issues"]["performance"]["count"]
        lsp_count = self.report["issues"]["lsp"]["count"]
        duplicate_count = self.report["duplicates"]["count"]
        
        # Estimer le temps de base (en minutes)
        base_time = 10
        
        # Estimer le temps pour corriger les problèmes de sécurité
        security_time = security_count * 8  # 8 minutes par problème de sécurité
        
        # Estimer le temps pour corriger les problèmes de performance
        perf_time = performance_count * 6  # 6 minutes par problème de performance
        
        # Estimer le temps pour corriger les problèmes LSP
        lsp_time = min(lsp_count * 3, 30)  # 3 minutes par problème LSP, max 30 minutes
        
        # Estimer le temps pour corriger les duplications
        dup_time = duplicate_count * 10  # 10 minutes par groupe de duplication
        
        # Calculer le temps total
        total_time = base_time + security_time + perf_time + lsp_time + dup_time
        
        # Mettre à jour le rapport
        self.report["work_time"] = {
            "temps_total": total_time,
            "details": {
                "temps_base": base_time,
                "correction_securite": security_time,
                "optimisation_performance": perf_time,
                "correction_erreurs_lsp": lsp_time,
                "elimination_duplications": dup_time
            }
        }
    
    def _save_report(self) -> None:
        """Sauvegarde le rapport d'analyse au format JSON"""
        report_file = os.path.join(self.output_dir, "flask_ai_analysis_report.json")
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.report, f, indent=2, ensure_ascii=False)
            logger.info(f"Rapport d'analyse sauvegardé dans {report_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")
    
    def _generate_text_summary(self) -> None:
        """Génère un résumé textuel de l'analyse"""
        summary_file = os.path.join(self.output_dir, "flask_ai_analysis_summary.txt")
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("RAPPORT D'ANALYSE IA DU PROJET FLASK\n")
                f.write("=" * 50 + "\n\n")
                
                # Méta-informations
                f.write(f"Date d'analyse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Répertoire analysé: {self.project_dir}\n")
                f.write(f"Temps d'exécution: {self.report['meta']['execution_time']:.2f} secondes\n\n")
                
                # Structure
                f.write("STRUCTURE DU PROJET\n")
                f.write("-" * 30 + "\n")
                f.write(f"Nombre de fichiers: {self.report['project']['file_count']}\n")
                f.write(f"Nombre de répertoires: {self.report['project']['dir_count']}\n")
                
                # Extensions
                f.write("\nExtensions de fichiers:\n")
                for ext, count in sorted(self.report['project']['extensions'].items(), key=lambda x: x[1], reverse=True)[:5]:
                    f.write(f"  - {ext}: {count}\n")
                
                # Détection Flask
                f.write("\nSTRUCTURE FLASK\n")
                f.write("-" * 30 + "\n")
                
                flask_specific = self.report["structure"]["flask_specific"]
                f.write(f"Fichier d'application: {flask_specific.get('app_file', 'Non détecté')}\n")
                f.write(f"Pattern Blueprint: {'Oui' if flask_specific.get('blueprint_pattern', False) else 'Non'}\n")
                f.write(f"SQLAlchemy utilisé: {'Oui' if flask_specific.get('sqlalchemy_used', False) else 'Non'}\n")
                f.write(f"WTForms utilisé: {'Oui' if flask_specific.get('wtforms_used', False) else 'Non'}\n")
                
                missing = self.report["structure"]["missing_elements"]
                if missing:
                    f.write("\nÉléments manquants:\n")
                    for item in missing:
                        f.write(f"  - {item}\n")
                
                # Problèmes
                f.write("\nPROBLÈMES DÉTECTÉS\n")
                f.write("-" * 30 + "\n")
                
                # Sécurité
                sec_issues = self.report["issues"]["security"]
                f.write(f"Problèmes de sécurité: {sec_issues['count']}\n")
                if sec_issues['count'] > 0:
                    high_count = sum(1 for issue in sec_issues['items'] if issue['severity'] == 'high')
                    medium_count = sum(1 for issue in sec_issues['items'] if issue['severity'] == 'medium')
                    low_count = sum(1 for issue in sec_issues['items'] if issue['severity'] == 'low')
                    
                    f.write(f"  - Critiques: {high_count}\n")
                    f.write(f"  - Moyens: {medium_count}\n")
                    f.write(f"  - Faibles: {low_count}\n")
                
                # Performance
                perf_issues = self.report["issues"]["performance"]
                f.write(f"Problèmes de performance: {perf_issues['count']}\n")
                
                # LSP
                lsp_issues = self.report["issues"]["lsp"]
                f.write(f"Erreurs LSP: {lsp_issues['count']}\n")
                
                # Duplications
                duplicates = self.report["duplicates"]
                f.write(f"Groupes de fichiers dupliqués: {duplicates['count']}\n")
                
                # Analyse IA
                f.write("\nANALYSE IA\n")
                f.write("-" * 30 + "\n")
                f.write(f"Score: {self.report['ai_analysis']['score']}/100\n")
                
                # Points forts
                highlights = self.report["ai_analysis"]["highlights"]
                if highlights:
                    f.write("\nPoints forts:\n")
                    for highlight in highlights:
                        f.write(f"  - {highlight['description']}\n")
                
                # Recommandations
                recommendations = self.report["ai_analysis"]["recommendations"]
                if recommendations:
                    f.write("\nRecommandations:\n")
                    for rec in sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority'), 3)):
                        f.write(f"  - [{rec['priority'].upper()}] {rec['title']}\n")
                        f.write(f"    {rec['description']}\n")
                
                # Temps de travail
                f.write("\nESTIMATION DU TEMPS DE TRAVAIL\n")
                f.write("-" * 30 + "\n")
                f.write(f"Temps total estimé: {self.report['work_time']['temps_total']} minutes\n")
                
                for category, time in self.report["work_time"]["details"].items():
                    f.write(f"  - {category}: {time} minutes\n")
                
                logger.info(f"Résumé textuel enregistré dans {summary_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé textuel: {e}")


def main():
    """Fonction principale"""
    analyzer = FlaskProjectAIAnalyzer()
    analyzer.run_full_analysis()
    
    logger.info("Analyse terminée. Consultez les fichiers flask_ai_analysis_report.json et flask_ai_analysis_summary.txt pour les résultats.")

if __name__ == "__main__":
    main()
