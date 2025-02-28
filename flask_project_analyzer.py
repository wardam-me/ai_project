
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module IA automatique pour analyser et évaluer les fichiers du projet Flask Server
Ce script analyse la structure, les erreurs, les doublons et les interactions dans le projet
"""

import os
import sys
import re
import json
import logging
import hashlib
import time
from collections import defaultdict, Counter
import importlib

# Importation des modules existants
try:
    from analyze_project import ProjectAnalyzer
    from check_directory_structure import DirectoryStructureChecker
    from list_errors import extract_errors_from_log, analyze_python_errors
except ImportError as e:
    print(f"Erreur lors de l'importation des modules existants: {e}")
    print("Assurez-vous que les modules analyze_project.py, check_directory_structure.py et list_errors.py sont présents.")
    sys.exit(1)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("IA-FlaskAnalyzer")

class FlaskProjectAIAnalyzer:
    """Analyseur IA pour projets Flask"""
    
    def __init__(self, project_root='.'):
        """
        Initialise l'analyseur de projet Flask
        
        Args:
            project_root: Répertoire racine du projet (par défaut: '.')
        """
        self.project_root = project_root
        self.start_time = time.time()
        
        # Initialiser les analyseurs existants
        self.project_analyzer = ProjectAnalyzer(project_root)
        self.structure_checker = DirectoryStructureChecker(project_root)
        
        # Résultats d'analyse
        self.duplicate_files = {}
        self.file_interactions = {}
        self.flask_specific_issues = {}
        self.performance_issues = []
        self.security_issues = []
        self.file_hashes = {}
        self.file_extensions = Counter()
        self.largest_files = []
        self.estimated_work_time = 0
        
    def compute_file_hash(self, file_path):
        """
        Calcule le hash SHA-256 d'un fichier
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            str: Hash du fichier
        """
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"Erreur lors du calcul du hash pour {file_path}: {e}")
            return None
    
    def find_duplicate_files(self):
        """
        Trouve les fichiers dupliqués en comparant leurs hashes
        """
        logger.info("Recherche des fichiers dupliqués...")
        
        # Dictionnaire pour stocker les hashes de fichiers
        hash_to_files = defaultdict(list)
        
        # Parcourir tous les fichiers
        for root, _, files in os.walk(self.project_root):
            for file in files:
                # Ignorer les répertoires spécifiques
                if any(ignore in root for ignore in ['.git', '__pycache__', '.pytest_cache', '.venv']):
                    continue
                
                # Ignorer certains types de fichiers
                if file.endswith(('.pyc', '.pyo', '.pyd', '.so', '.obj')):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                
                # Collecter les statistiques sur les extensions
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    self.file_extensions[ext] += 1
                
                # Calculer le hash du fichier
                file_hash = self.compute_file_hash(file_path)
                if file_hash:
                    hash_to_files[file_hash].append(rel_path)
                    self.file_hashes[rel_path] = file_hash
        
        # Identifier les fichiers dupliqués
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                self.duplicate_files[file_hash] = files
        
        logger.info(f"Trouvé {len(self.duplicate_files)} groupes de fichiers dupliqués")
        
        # Identifier les 10 plus gros fichiers
        files_with_size = []
        for root, _, files in os.walk(self.project_root):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    rel_path = os.path.relpath(file_path, self.project_root)
                    files_with_size.append((rel_path, size))
                except Exception:
                    pass
        
        self.largest_files = sorted(files_with_size, key=lambda x: x[1], reverse=True)[:10]
    
    def analyze_flask_structure(self):
        """
        Analyse la structure d'un projet Flask
        """
        logger.info("Analyse de la structure Flask...")
        
        # Éléments attendus dans un projet Flask
        expected_flask_elements = {
            'app.py': False,
            'main.py': False,
            'routes.py': False,
            'models.py': False,
            'forms.py': False,
            'templates': False,
            'static': False,
            'config': False,
        }
        
        # Vérifier si les éléments attendus existent
        for root, dirs, files in os.walk(self.project_root):
            for directory in dirs:
                if directory in expected_flask_elements:
                    expected_flask_elements[directory] = True
            
            for file in files:
                if file in expected_flask_elements:
                    expected_flask_elements[file] = True
        
        # Identifier les problèmes spécifiques à Flask
        missing_elements = [element for element, exists in expected_flask_elements.items() if not exists]
        
        if missing_elements:
            self.flask_specific_issues['missing_elements'] = missing_elements
            logger.info(f"Éléments manquants dans la structure Flask: {', '.join(missing_elements)}")
        
        # Vérifier si le blueprint pattern est utilisé
        blueprint_pattern = False
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'Blueprint' in content:
                                blueprint_pattern = True
                                break
                    except Exception:
                        pass
            
            if blueprint_pattern:
                break
        
        self.flask_specific_issues['blueprint_pattern'] = blueprint_pattern
        
        # Vérifier l'utilisation de SQLAlchemy
        sqlalchemy_used = False
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'SQLAlchemy' in content or 'db.Model' in content:
                                sqlalchemy_used = True
                                break
                    except Exception:
                        pass
            
            if sqlalchemy_used:
                break
        
        self.flask_specific_issues['sqlalchemy_used'] = sqlalchemy_used
    
    def analyze_file_interactions(self):
        """
        Analyse les interactions entre les fichiers du projet
        """
        logger.info("Analyse des interactions entre fichiers...")
        
        # Dictionnaire pour stocker les interactions (fichier -> fichiers importés)
        interactions = defaultdict(set)
        
        # Parcourir tous les fichiers Python
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_root)
                    
                    # Analyser les imports
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Rechercher les imports
                            import_pattern = re.compile(r'^(?:from\s+(\S+)\s+import|\s*import\s+([^,]+))', re.MULTILINE)
                            
                            for match in import_pattern.finditer(content):
                                imported_module = match.group(1) or match.group(2)
                                imported_module = imported_module.strip()
                                
                                # Ajouter l'interaction
                                interactions[rel_path].add(imported_module)
                    except Exception as e:
                        logger.error(f"Erreur lors de l'analyse des interactions pour {rel_path}: {e}")
        
        # Convertir les sets en listes pour la sérialisation JSON
        self.file_interactions = {k: list(v) for k, v in interactions.items()}
    
    def analyze_security_issues(self):
        """
        Analyse les problèmes de sécurité potentiels
        """
        logger.info("Analyse des problèmes de sécurité...")
        
        security_patterns = [
            (r'SECRET_KEY\s*=\s*[\'"](.*?)[\'"]', "Clé secrète hardcodée"),
            (r'password\s*=\s*[\'"](.*?)[\'"]', "Mot de passe hardcodé"),
            (r'@app\.route.*methods=\s*\[[\'"]POST[\'"]\).*?def\s+\w+.*?(?!csrf)', "Route POST sans protection CSRF"),
            (r'cursor\.execute\([\'"].*?\s+(?:WHERE|INSERT|UPDATE|DELETE).*?%s', "Potentielle vulnérabilité d'injection SQL"),
            (r'eval\(', "Utilisation dangereuse de eval()"),
            (r'exec\(', "Utilisation dangereuse de exec()"),
            (r'subprocess\.call\(.*?shell\s*=\s*True', "Exécution de commande shell avec vulnérabilité d'injection"),
            (r'CORS\(.*?origins\s*=\s*[\'"]\*[\'"]', "Configuration CORS trop permissive"),
            (r'app\.debug\s*=\s*True', "Mode debug activé en production"),
            (r'request\.args\.get\(.*?\)', "Utilisation de paramètres GET sans validation"),
        ]
        
        # Parcourir tous les fichiers Python
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_root)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Rechercher les patterns de sécurité
                            for pattern, description in security_patterns:
                                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                                
                                for match in matches:
                                    line_number = content[:match.start()].count('\n') + 1
                                    self.security_issues.append({
                                        'file': rel_path,
                                        'line': line_number,
                                        'description': description,
                                        'match': match.group(0)[:50] + ('...' if len(match.group(0)) > 50 else '')
                                    })
                    except Exception as e:
                        logger.error(f"Erreur lors de l'analyse de sécurité pour {rel_path}: {e}")
    
    def analyze_performance_issues(self):
        """
        Analyse les problèmes de performance potentiels
        """
        logger.info("Analyse des problèmes de performance...")
        
        performance_patterns = [
            (r'for\s+.*?\s+in\s+.*?:\s*\n\s*for\s+.*?\s+in\s+.*?:', "Boucles imbriquées potentiellement inefficaces"),
            (r'session\s*\.\s*query\s*\(.*?\)\s*\.\s*all\s*\(\)', "Chargement de tous les enregistrements sans limite"),
            (r'\.sleep\s*\(\s*\d+\s*\)', "Utilisation de sleep explicite"),
            (r'\.filter\s*\(.*?\)\s*\.\s*filter\s*\(', "Multiples opérations de filtrage séquentielles"),
            (r'[\'"]SELECT.*?FROM.*?JOIN.*?[\'"]', "Requête SQL potentiellement complexe"),
            (r'with\s+open\(.*?\)\s+as\s+.*?:\s*\n\s*lines\s*=\s*f\.readlines\(\)', "Lecture en mémoire de fichiers potentiellement volumineux"),
            (r'json\.loads\(.*?open\(.*?\)\.read\(\)\)', "Chargement complet de fichiers JSON en mémoire"),
            (r'@app\.route\(.*?\)\s*\n\s*def\s+\w+\s*\(.*?\):\s*\n\s*(?!.*?cache)', "Routes sans mise en cache"),
        ]
        
        # Parcourir tous les fichiers Python
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_root)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Rechercher les patterns de performance
                            for pattern, description in performance_patterns:
                                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                                
                                for match in matches:
                                    line_number = content[:match.start()].count('\n') + 1
                                    self.performance_issues.append({
                                        'file': rel_path,
                                        'line': line_number,
                                        'description': description,
                                        'match': match.group(0)[:50] + ('...' if len(match.group(0)) > 50 else '')
                                    })
                    except Exception as e:
                        logger.error(f"Erreur lors de l'analyse de performance pour {rel_path}: {e}")
    
    def estimate_work_time(self):
        """
        Estime le temps de travail nécessaire pour résoudre les problèmes identifiés
        """
        logger.info("Estimation du temps de travail nécessaire...")
        
        # Base de temps (en minutes)
        base_time = 30
        
        # Ajouter du temps pour les problèmes de structure
        if hasattr(self.structure_checker, 'verification'):
            missing_dirs = len(self.structure_checker.verification['directories']['missing'])
            missing_files = len(self.structure_checker.verification['files']['missing'])
            missing_modules = len(self.structure_checker.verification['modules']['missing'])
            
            structure_time = (missing_dirs * 5) + (missing_files * 10) + (missing_modules * 20)
        else:
            # Faire une vérification rapide
            _, missing_dirs = self.structure_checker.check_directories()
            _, missing_files = self.structure_checker.check_files()
            _, missing_modules = self.structure_checker.check_modules()
            
            structure_time = (len(missing_dirs) * 5) + (len(missing_files) * 10) + (len(missing_modules) * 20)
        
        # Ajouter du temps pour les problèmes LSP
        lsp_issues_count = sum(len(errors) for errors in self.project_analyzer.lsp_errors.values()) if hasattr(self.project_analyzer, 'lsp_errors') else 0
        lsp_time = lsp_issues_count * 3  # 3 minutes par erreur
        
        # Ajouter du temps pour les doublons
        duplicate_time = len(self.duplicate_files) * 15  # 15 minutes par groupe de doublons
        
        # Ajouter du temps pour les problèmes de sécurité
        security_time = len(self.security_issues) * 10  # 10 minutes par problème de sécurité
        
        # Ajouter du temps pour les problèmes de performance
        performance_time = len(self.performance_issues) * 8  # 8 minutes par problème de performance
        
        # Calculer le temps total
        total_time = base_time + structure_time + lsp_time + duplicate_time + security_time + performance_time
        
        # Limiter à une journée de travail maximum (8 heures)
        total_time = min(total_time, 480)
        
        self.estimated_work_time = total_time
        logger.info(f"Temps de travail estimé: {total_time} minutes")
        
        return {
            "temps_total": total_time,
            "details": {
                "temps_base": base_time,
                "temps_structure": structure_time,
                "temps_lsp": lsp_time,
                "temps_doublons": duplicate_time,
                "temps_securite": security_time,
                "temps_performance": performance_time
            }
        }
    
    def run_full_analysis(self):
        """
        Exécute l'analyse complète du projet
        """
        logger.info("Début de l'analyse complète du projet Flask...")
        
        # Exécuter l'analyse de projet existante
        self.project_analyzer.analyze_project()
        
        # Vérifier la structure du projet
        self.structure_checker.verify_and_fix_structure(fix_missing=False)
        
        # Trouver les fichiers dupliqués
        self.find_duplicate_files()
        
        # Analyser la structure Flask
        self.analyze_flask_structure()
        
        # Analyser les interactions entre fichiers
        self.analyze_file_interactions()
        
        # Analyser les problèmes de sécurité
        self.analyze_security_issues()
        
        # Analyser les problèmes de performance
        self.analyze_performance_issues()
        
        # Estimer le temps de travail
        work_time_details = self.estimate_work_time()
        
        # Calculer le temps d'exécution
        execution_time = time.time() - self.start_time
        
        # Générer le rapport
        return self.generate_report(execution_time, work_time_details)
    
    def generate_report(self, execution_time, work_time_details):
        """
        Génère un rapport d'analyse complet
        
        Args:
            execution_time: Temps d'exécution de l'analyse
            work_time_details: Détails sur l'estimation du temps de travail
            
        Returns:
            dict: Rapport d'analyse
        """
        logger.info("Génération du rapport d'analyse...")
        
        report = {
            "meta": {
                "execution_time": execution_time,
                "timestamp": time.time(),
                "analyzer_version": "1.0.0"
            },
            "project": {
                "root": self.project_root,
                "extensions": dict(self.file_extensions),
                "largest_files": self.largest_files
            },
            "structure": {
                "project_analyzer_report": os.path.join(self.project_root, 'project_analysis_report.json'),
                "structure_report": os.path.join(self.project_root, 'directory_structure_report.json'),
                "flask_specific": self.flask_specific_issues
            },
            "duplicates": {
                "count": len(self.duplicate_files),
                "groups": self.duplicate_files
            },
            "interactions": {
                "count": len(self.file_interactions),
                "details": self.file_interactions
            },
            "issues": {
                "security": {
                    "count": len(self.security_issues),
                    "details": self.security_issues
                },
                "performance": {
                    "count": len(self.performance_issues),
                    "details": self.performance_issues
                },
                "lsp": {
                    "count": sum(len(errors) for errors in self.project_analyzer.lsp_errors.values()) if hasattr(self.project_analyzer, 'lsp_errors') else 0,
                    "report": "Voir project_analysis_report.json pour plus de détails"
                }
            },
            "work_time": work_time_details
        }
        
        # Enregistrer le rapport au format JSON
        report_file = os.path.join(self.project_root, 'flask_ai_analysis_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Rapport d'analyse enregistré dans {report_file}")
        
        # Générer un résumé textuel
        self.generate_text_summary(report, report_file)
        
        return report
    
    def generate_text_summary(self, report, report_file):
        """
        Génère un résumé textuel du rapport
        
        Args:
            report: Rapport d'analyse
            report_file: Chemin vers le fichier de rapport JSON
        """
        summary_file = os.path.join(self.project_root, 'flask_ai_analysis_summary.txt')
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=== RAPPORT D'ANALYSE IA DU PROJET FLASK ===\n\n")
            
            f.write(f"Temps d'exécution: {report['meta']['execution_time']:.2f} secondes\n")
            f.write(f"Rapport complet: {report_file}\n\n")
            
            f.write("=== STRUCTURE DU PROJET ===\n")
            f.write(f"Extensions de fichiers: {', '.join(f'{ext} ({count})' for ext, count in report['project']['extensions'].items())}\n")
            f.write("Top 5 des plus gros fichiers:\n")
            for i, (file, size) in enumerate(report['project']['largest_files'][:5], 1):
                f.write(f"  {i}. {file}: {size / 1024:.1f} Ko\n")
            
            f.write("\n=== PROBLÈMES DÉTECTÉS ===\n")
            total_issues = (
                report['issues']['security']['count'] + 
                report['issues']['performance']['count'] + 
                report['issues']['lsp']['count'] + 
                report['duplicates']['count']
            )
            f.write(f"Total: {total_issues} problèmes\n")
            f.write(f"Sécurité: {report['issues']['security']['count']} problèmes\n")
            f.write(f"Performance: {report['issues']['performance']['count']} problèmes\n")
            f.write(f"Erreurs LSP: {report['issues']['lsp']['count']} problèmes\n")
            f.write(f"Fichiers dupliqués: {report['duplicates']['count']} groupes\n")
            
            if report['issues']['security']['count'] > 0:
                f.write("\nTop problèmes de sécurité:\n")
                for i, issue in enumerate(report['issues']['security']['details'][:3], 1):
                    f.write(f"  {i}. {issue['file']} (ligne {issue['line']}): {issue['description']}\n")
            
            if report['issues']['performance']['count'] > 0:
                f.write("\nTop problèmes de performance:\n")
                for i, issue in enumerate(report['issues']['performance']['details'][:3], 1):
                    f.write(f"  {i}. {issue['file']} (ligne {issue['line']}): {issue['description']}\n")
            
            if report['duplicates']['count'] > 0:
                f.write("\nTop groupes de fichiers dupliqués:\n")
                for i, (_, files) in enumerate(list(report['duplicates']['groups'].items())[:3], 1):
                    f.write(f"  {i}. {len(files)} fichiers dupliqués: {', '.join(files[:2])}{'...' if len(files) > 2 else ''}\n")
            
            f.write("\n=== ESTIMATION DU TEMPS DE TRAVAIL ===\n")
            f.write(f"Temps total estimé: {report['work_time']['temps_total']} minutes\n")
            f.write(f"Détails:\n")
            for category, time in report['work_time']['details'].items():
                f.write(f"  - {category}: {time} minutes\n")
        
        logger.info(f"Résumé textuel enregistré dans {summary_file}")


def main():
    """Fonction principale"""
    analyzer = FlaskProjectAIAnalyzer()
    analyzer.run_full_analysis()
    
    logger.info("Analyse terminée. Consultez flask_ai_analysis_report.json et flask_ai_analysis_summary.txt pour les résultats.")

if __name__ == "__main__":
    main()
