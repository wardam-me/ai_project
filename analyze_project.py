#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'analyse de structure du projet NetSecure Pro
Ce script analyse la structure des répertoires du projet et les résultats des tests
pour identifier les erreurs et les problèmes potentiels.
"""

import os
import sys
import json
import re
import logging
from collections import defaultdict, Counter
import importlib

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectAnalyzer:
    """Analyseur de projet pour NetSecure Pro"""
    
    def __init__(self, project_root='.'):
        """
        Initialise l'analyseur de projet
        
        Args:
            project_root: Répertoire racine du projet (par défaut: '.')
        """
        self.project_root = project_root
        self.directories = []
        self.python_files = []
        self.static_files = []
        self.template_files = []
        self.config_files = []
        self.test_files = []
        self.errors = []
        self.warnings = []
        self.modules = {}
        self.test_results = {
            'success': [],
            'failure': [],
            'error': []
        }
        
    def scan_directory_structure(self):
        """Scan la structure des répertoires"""
        logger.info("Analyse de la structure des répertoires...")
        
        for root, dirs, files in os.walk(self.project_root):
            # Ignorer les répertoires cachés et ceux avec des noms spécifiques
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', '.git']]
            
            # Ajouter le répertoire à la liste
            rel_path = os.path.relpath(root, self.project_root)
            if rel_path != '.':
                self.directories.append(rel_path)
            
            # Classer les fichiers par type
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.project_root)
                
                if file.endswith('.py'):
                    if file.startswith('test_'):
                        self.test_files.append(rel_path)
                    else:
                        self.python_files.append(rel_path)
                
                elif root.endswith('static') or 'static' in root.split(os.path.sep):
                    self.static_files.append(rel_path)
                
                elif root.endswith('templates') or 'templates' in root.split(os.path.sep):
                    self.template_files.append(rel_path)
                
                elif root.endswith('config') or file in ['.flaskenv', 'pyproject.toml', 'requirements.txt']:
                    self.config_files.append(rel_path)
        
        # Analyser les statistiques
        logger.info(f"Nombre de répertoires: {len(self.directories)}")
        logger.info(f"Nombre de fichiers Python: {len(self.python_files)}")
        logger.info(f"Nombre de fichiers de test: {len(self.test_files)}")
        logger.info(f"Nombre de fichiers statiques: {len(self.static_files)}")
        logger.info(f"Nombre de templates: {len(self.template_files)}")
        logger.info(f"Nombre de fichiers de configuration: {len(self.config_files)}")
    
    def analyze_module_dependencies(self):
        """Analyse les dépendances entre les modules Python"""
        logger.info("Analyse des dépendances entre modules...")
        
        import_pattern = re.compile(r'^(?:from\s+(\S+)\s+import|\s*import\s+([^,]+))', re.MULTILINE)
        
        for py_file in self.python_files:
            module_name = os.path.splitext(os.path.basename(py_file))[0]
            self.modules[module_name] = {
                'file': py_file,
                'imports': [],
                'imported_by': []
            }
            
            try:
                with open(os.path.join(self.project_root, py_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for match in import_pattern.finditer(content):
                        imported_module = match.group(1) or match.group(2)
                        imported_module = imported_module.strip()
                        
                        # Ignorer les imports de bibliothèques standard ou externes
                        if '.' in imported_module:
                            base_module = imported_module.split('.')[0]
                        else:
                            base_module = imported_module
                        
                        # Ajouter uniquement les modules locaux
                        if base_module in self.modules or base_module in [m.split('.')[0] for m in self.modules]:
                            self.modules[module_name]['imports'].append(imported_module)
            
            except Exception as e:
                self.errors.append(f"Erreur lors de l'analyse des dépendances de {py_file}: {str(e)}")
        
        # Compléter les relations 'imported_by'
        for module_name, info in self.modules.items():
            for imported_module in info['imports']:
                # Gérer les modules avec des points (ex: 'package.module')
                base_module = imported_module.split('.')[0]
                if base_module in self.modules:
                    if module_name not in self.modules[base_module]['imported_by']:
                        self.modules[base_module]['imported_by'].append(module_name)
    
    def analyze_test_results(self):
        """Analyse les résultats des tests"""
        logger.info("Analyse des résultats des tests...")
        
        for test_file in self.test_files:
            file_path = os.path.join(self.project_root, test_file)
            
            try:
                # Extraire le module de test
                module_name = os.path.splitext(test_file)[0].replace(os.path.sep, '.')
                
                # Tenter d'importer le module pour voir s'il y a des erreurs de syntaxe
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    self.test_results['success'].append(f"Module {module_name} importé avec succès")
                except Exception as e:
                    self.test_results['error'].append(f"Erreur lors de l'import du module {module_name}: {str(e)}")
                
                # Lire le contenu du fichier pour extraire les messages de test
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Rechercher les messages de test positifs
                    success_pattern = re.compile(r'(?:assert|self\.assert\w+|INFO:.*?:)\s*(.+?succès|réussi|passed|success)', re.IGNORECASE)
                    for match in success_pattern.finditer(content):
                        self.test_results['success'].append(f"{test_file}: {match.group(0)}")
                    
                    # Rechercher les messages d'échec potentiels
                    failure_pattern = re.compile(r'(?:assert\s+\w+\s*[!=><]=|self\.assert\w+|raise\s+\w+Error|ERROR:.*?:)\s*(.+?)', re.IGNORECASE)
                    for match in failure_pattern.finditer(content):
                        if not any(positive in match.group(0).lower() for positive in ['success', 'succès', 'réussi', 'passed']):
                            self.test_results['failure'].append(f"{test_file}: {match.group(0)}")
            
            except Exception as e:
                self.errors.append(f"Erreur lors de l'analyse des résultats de test pour {test_file}: {str(e)}")
    
    def analyze_lsp_errors(self):
        """Analyse les erreurs du Language Server Protocol (LSP)"""
        logger.info("Analyse des erreurs LSP...")
        
        lsp_errors = defaultdict(list)
        
        for py_file in self.python_files + self.test_files:
            file_path = os.path.join(self.project_root, py_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Analyser les imports manquants, les variables non définies, etc.
                    import_error_pattern = re.compile(r'import\s+([^,\s]+)', re.MULTILINE)
                    for match in import_error_pattern.finditer(content):
                        module_name = match.group(1)
                        try:
                            importlib.import_module(module_name)
                        except ImportError:
                            lsp_errors[py_file].append(f"Import could not be resolved: {module_name}")
                    
                    # Rechercher les variables potentiellement non définies
                    # Cette analyse est simplifiée et peut produire des faux positifs
                    undefined_var_pattern = re.compile(r'(?<!\bdef\s)(?<!\bclass\s)(?<!\bfrom\s)(?<!\bimport\s)(?<!\bfor\s)(?<!\bas\s)\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=[.,\(\[\]=])')
                    variables = set()
                    assignments = set()
                    
                    # Collecter les affectations
                    assignment_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=')
                    for match in assignment_pattern.finditer(content):
                        assignments.add(match.group(1))
                    
                    # Collecter les utilisations de variables
                    for match in undefined_var_pattern.finditer(content):
                        var_name = match.group(1)
                        if var_name not in ['self', 'cls', 'True', 'False', 'None', 'print', 'len', 'range']:
                            variables.add(var_name)
                    
                    # Variables utilisées mais jamais affectées (simplification)
                    for var in variables:
                        if var not in assignments and not any(var in imported for imported in lsp_errors[py_file]):
                            if not re.search(r'\bdef\s+' + var + r'\b|\bclass\s+' + var + r'\b', content):
                                lsp_errors[py_file].append(f"Variable potentiellement non définie: {var}")
            
            except Exception as e:
                self.errors.append(f"Erreur lors de l'analyse LSP pour {py_file}: {str(e)}")
        
        self.lsp_errors = lsp_errors
    
    def generate_report(self):
        """Génère un rapport d'analyse"""
        logger.info("Génération du rapport d'analyse...")
        
        report = {
            "structure": {
                "directories": self.directories,
                "python_files": self.python_files,
                "test_files": self.test_files,
                "static_files": len(self.static_files),
                "template_files": len(self.template_files),
                "config_files": len(self.config_files)
            },
            "modules": {
                "total": len(self.modules),
                "details": self.modules
            },
            "test_results": {
                "success": len(self.test_results['success']),
                "failure": len(self.test_results['failure']),
                "error": len(self.test_results['error']),
                "success_details": self.test_results['success'][:10],  # Limiter pour la lisibilité
                "failure_details": self.test_results['failure'],
                "error_details": self.test_results['error']
            },
            "lsp_errors": {
                "total": sum(len(errors) for errors in self.lsp_errors.values()),
                "files_with_errors": len(self.lsp_errors),
                "details": dict(self.lsp_errors)
            },
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        # Enregistrer le rapport au format JSON
        report_path = os.path.join(self.project_root, 'project_analysis_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Rapport d'analyse enregistré dans {report_path}")
        return report
    
    def analyze_project(self):
        """Exécute l'analyse complète du projet"""
        logger.info("Début de l'analyse du projet...")
        
        self.scan_directory_structure()
        self.analyze_module_dependencies()
        self.analyze_test_results()
        self.analyze_lsp_errors()
        
        return self.generate_report()
    
    def print_summary(self):
        """Imprime un résumé de l'analyse"""
        logger.info("=== RÉSUMÉ DE L'ANALYSE DU PROJET ===")
        logger.info(f"Structure du projet:")
        logger.info(f"  - {len(self.directories)} répertoires")
        logger.info(f"  - {len(self.python_files)} fichiers Python")
        logger.info(f"  - {len(self.test_files)} fichiers de test")
        logger.info(f"  - {len(self.static_files)} fichiers statiques")
        logger.info(f"  - {len(self.template_files)} templates")
        
        logger.info(f"Modules:")
        top_imported = Counter()
        for module_name, info in self.modules.items():
            top_imported[module_name] = len(info['imported_by'])
        
        logger.info(f"  - Modules les plus importés:")
        for module, count in top_imported.most_common(5):
            logger.info(f"    * {module}: {count} imports")
        
        logger.info(f"Résultats des tests:")
        logger.info(f"  - {len(self.test_results['success'])} succès")
        logger.info(f"  - {len(self.test_results['failure'])} échecs potentiels")
        logger.info(f"  - {len(self.test_results['error'])} erreurs")
        
        if self.test_results['failure']:
            logger.info(f"  - Échecs potentiels:")
            for failure in self.test_results['failure'][:5]:
                logger.info(f"    * {failure}")
        
        if self.test_results['error']:
            logger.info(f"  - Erreurs:")
            for error in self.test_results['error']:
                logger.info(f"    * {error}")
        
        logger.info(f"Erreurs LSP:")
        logger.info(f"  - {sum(len(errors) for errors in self.lsp_errors.values())} erreurs potentielles dans {len(self.lsp_errors)} fichiers")
        
        if self.lsp_errors:
            top_errors = Counter()
            for file, errors in self.lsp_errors.items():
                top_errors[file] = len(errors)
            
            logger.info(f"  - Fichiers avec le plus d'erreurs:")
            for file, count in top_errors.most_common(5):
                logger.info(f"    * {file}: {count} erreurs")
        
        if self.errors:
            logger.info(f"Erreurs d'analyse:")
            for error in self.errors:
                logger.info(f"  - {error}")
        
        if self.warnings:
            logger.info(f"Avertissements:")
            for warning in self.warnings:
                logger.info(f"  - {warning}")

def main():
    """Fonction principale"""
    analyzer = ProjectAnalyzer()
    analyzer.analyze_project()
    analyzer.print_summary()

if __name__ == "__main__":
    main()