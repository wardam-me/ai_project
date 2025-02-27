#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour lister les erreurs dans les résultats des tests
Ce script analyse les fichiers de logs et les sorties des tests pour identifier les erreurs.
"""

import os
import re
import glob
import logging
from collections import defaultdict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_errors_from_log(log_file):
    """
    Extrait les erreurs d'un fichier de log
    
    Args:
        log_file: Chemin vers le fichier de log
        
    Returns:
        List[str]: Liste des erreurs trouvées
    """
    errors = []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Rechercher les messages d'erreur et d'exception
            error_pattern = re.compile(r'(ERROR:.*?$|Traceback \(most recent call last\):|[Ee]xception|[Ee]rreur|[Ff]ailed|[Ff]ail|\b[Ee]rror:)', re.MULTILINE)
            
            prev_line = ""
            current_error = None
            in_traceback = False
            
            for line in content.split('\n'):
                # Détecter le début d'un traceback
                if "Traceback (most recent call last):" in line:
                    current_error = [line]
                    in_traceback = True
                    continue
                
                # Si on est dans un traceback, continuer à collecter les lignes
                if in_traceback and current_error is not None:
                    current_error.append(line)
                    
                    # Détecter la fin d'un traceback
                    if re.search(r'^\w+Error:', line) or re.search(r'^\w+Exception:', line):
                        if current_error is not None:
                            errors.append('\n'.join(current_error))
                        current_error = None
                        in_traceback = False
                    continue
                
                # Rechercher des messages d'erreur individuels
                match = error_pattern.search(line)
                if match and "Entrée de niveau ERROR" not in line:
                    context = prev_line + '\n' if prev_line else ''
                    errors.append(context + line)
                
                prev_line = line
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du fichier {log_file}: {e}")
    
    return errors

def analyze_test_directories():
    """
    Analyse les répertoires de test pour y trouver des journaux
    
    Returns:
        Dict[str, List[str]]: Dictionnaire des erreurs par fichier
    """
    errors_by_file = defaultdict(list)
    
    # Lister tous les fichiers .log
    log_files = []
    for pattern in ['*.log', '**/*.log']:
        log_files.extend(glob.glob(pattern, recursive=True))
    
    for log_file in log_files:
        errors = extract_errors_from_log(log_file)
        if errors:
            errors_by_file[log_file] = errors
    
    return errors_by_file

def analyze_python_errors():
    """
    Analyse les erreurs dans les fichiers Python en examinant les imports et syntaxe
    
    Returns:
        Dict[str, List[str]]: Dictionnaire des erreurs par fichier
    """
    errors_by_file = defaultdict(list)
    python_files = []
    
    # Lister tous les fichiers Python
    for pattern in ['*.py', '**/*.py']:
        python_files.extend(glob.glob(pattern, recursive=True))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Rechercher les commentaires indiquant des problèmes
                todo_pattern = re.compile(r'#\s*TODO:?(.+)$', re.MULTILINE | re.IGNORECASE)
                fixme_pattern = re.compile(r'#\s*FIXME:?(.+)$', re.MULTILINE | re.IGNORECASE)
                
                for match in todo_pattern.finditer(content):
                    errors_by_file[py_file].append(f"TODO: {match.group(1).strip()}")
                
                for match in fixme_pattern.finditer(content):
                    errors_by_file[py_file].append(f"FIXME: {match.group(1).strip()}")
                
                # Rechercher les erreurs courantes de types
                type_errors = [
                    (r'(\w+)\s*=\s*None.*?\1\s*\+\s*\d+', "Possible TypeError: opération sur None"),
                    (r'for\s+\w+\s+in\s+(\w+).*?if\s+not\s+\1:', "Possible TypeError: test sur un itérateur qui pourrait être None"),
                    (r'except\s*:', "Except trop général, devrait capturer des exceptions spécifiques"),
                    (r'except\s+Exception\s*:', "Except trop général, devrait capturer des exceptions spécifiques")
                ]
                
                for pattern, message in type_errors:
                    if re.search(pattern, content):
                        errors_by_file[py_file].append(message)
        
        except Exception as e:
            errors_by_file[py_file].append(f"Erreur lors de l'analyse: {str(e)}")
    
    return errors_by_file

def analyze_test_results():
    """
    Analyse les résultats des tests en examinant les fichiers de test
    
    Returns:
        Dict[str, List[str]]: Dictionnaire des erreurs par fichier de test
    """
    errors_by_file = defaultdict(list)
    test_files = []
    
    # Lister tous les fichiers de test
    for pattern in ['test_*.py', '**/test_*.py']:
        test_files.extend(glob.glob(pattern, recursive=True))
    
    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Rechercher les assertions avec des messages d'échec
                if 'assert' in content:
                    assertion_pattern = re.compile(r'assert\s+.+?,\s*[\'"](.*?)[\'"]', re.MULTILINE)
                    for match in assertion_pattern.finditer(content):
                        errors_by_file[test_file].append(f"Assertion message: {match.group(1)}")
                
                # Rechercher les blocs try/except qui pourraient masquer des erreurs
                if 'try:' in content and 'except' in content:
                    try_except_pattern = re.compile(r'try:.*?except\s+\w+.*?:(.*?)(?:finally:|$)', re.DOTALL)
                    for match in try_except_pattern.finditer(content):
                        except_block = match.group(1)
                        if 'pass' in except_block and not re.search(r'#.*?ignore', except_block, re.IGNORECASE):
                            errors_by_file[test_file].append("Exception silencieuse (except: pass) sans commentaire explicatif")
        
        except Exception as e:
            errors_by_file[test_file].append(f"Erreur lors de l'analyse: {str(e)}")
    
    return errors_by_file

def main():
    """Fonction principale"""
    logger.info("Recherche des erreurs dans les journaux...")
    log_errors = analyze_test_directories()
    
    logger.info("Analyse des erreurs dans les fichiers Python...")
    python_errors = analyze_python_errors()
    
    logger.info("Analyse des résultats de tests...")
    test_errors = analyze_test_results()
    
    # Fusionner tous les résultats
    all_errors = defaultdict(list)
    for d in [log_errors, python_errors, test_errors]:
        for file_path, errors in d.items():
            all_errors[file_path].extend(errors)
    
    # Afficher les résultats
    logger.info("=== RÉSUMÉ DES ERREURS DÉTECTÉES ===")
    if all_errors:
        total_errors = sum(len(errors) for errors in all_errors.values())
        logger.info(f"Total: {total_errors} erreurs potentielles dans {len(all_errors)} fichiers")
        
        for file_path, errors in sorted(all_errors.items()):
            logger.info(f"\n{file_path} ({len(errors)} erreurs):")
            for i, error in enumerate(errors, 1):
                logger.info(f"  {i}. {error}")
    else:
        logger.info("Aucune erreur détectée")
    
    # Enregistrer les résultats dans un fichier
    with open('error_analysis_results.txt', 'w', encoding='utf-8') as f:
        f.write("=== RÉSUMÉ DES ERREURS DÉTECTÉES ===\n")
        if all_errors:
            total_errors = sum(len(errors) for errors in all_errors.values())
            f.write(f"Total: {total_errors} erreurs potentielles dans {len(all_errors)} fichiers\n\n")
            
            for file_path, errors in sorted(all_errors.items()):
                f.write(f"{file_path} ({len(errors)} erreurs):\n")
                for i, error in enumerate(errors, 1):
                    f.write(f"  {i}. {error}\n")
        else:
            f.write("Aucune erreur détectée\n")
    
    logger.info(f"Résultats enregistrés dans error_analysis_results.txt")

if __name__ == "__main__":
    main()