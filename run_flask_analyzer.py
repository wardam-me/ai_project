
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour exécuter l'analyseur IA de projet Flask
"""

import os
import json
import logging
import argparse
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RunFlaskAnalyzer")

def print_report_summary(report_file):
    """
    Affiche un résumé du rapport d'analyse
    
    Args:
        report_file: Chemin vers le fichier de rapport JSON
    """
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print("\n=== RÉSUMÉ DU RAPPORT D'ANALYSE IA ===")
        
        # Méta-informations
        print(f"\nTemps d'exécution de l'analyse: {report['meta']['execution_time']:.2f} secondes")
        
        # Statistiques du projet
        print("\n[Structure du projet]")
        print(f"Extensions de fichiers: {', '.join(f'{ext} ({count})' for ext, count in list(report['project']['extensions'].items())[:5])}")
        
        # Structure Flask
        print("\n[Structure Flask]")
        if 'missing_elements' in report['structure']['flask_specific']:
            print(f"Éléments manquants: {', '.join(report['structure']['flask_specific'].get('missing_elements', []))}")
        print(f"Utilisation de Blueprints: {'Oui' if report['structure']['flask_specific'].get('blueprint_pattern', False) else 'Non'}")
        print(f"Utilisation de SQLAlchemy: {'Oui' if report['structure']['flask_specific'].get('sqlalchemy_used', False) else 'Non'}")
        
        # Problèmes
        security_count = report['issues']['security']['count']
        performance_count = report['issues']['performance']['count']
        lsp_count = report['issues']['lsp']['count']
        duplicate_count = report['duplicates']['count']
        
        print("\n[Problèmes détectés]")
        print(f"Problèmes de sécurité: {security_count}")
        print(f"Problèmes de performance: {performance_count}")
        print(f"Erreurs LSP: {lsp_count}")
        print(f"Groupes de fichiers dupliqués: {duplicate_count}")
        
        # Estimation du temps de travail
        print("\n[Estimation du temps de travail]")
        print(f"Temps total estimé: {report['work_time']['temps_total']} minutes")
        for category, minutes in report['work_time']['details'].items():
            if minutes > 0:
                print(f"  - {category}: {minutes} minutes")
        
        # Actions recommandées
        print("\n[Actions recommandées]")
        
        if security_count > 0:
            print("1. Résoudre les problèmes de sécurité critiques")
            
        if duplicate_count > 0:
            print("2. Éliminer les fichiers dupliqués pour simplifier la maintenance")
            
        if performance_count > 0:
            print("3. Optimiser les points chauds de performance")
            
        if lsp_count > 0:
            print("4. Corriger les erreurs de syntaxe et les imports")
        
        print("\nPour plus de détails, consultez les fichiers:")
        print(f"  - {report_file}")
        print(f"  - flask_ai_analysis_summary.txt")
        
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du rapport: {e}")
        print("Erreur lors de la lecture du rapport. Vérifiez le fichier flask_ai_analysis_report.json")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Exécute l'analyseur IA de projet Flask")
    parser.add_argument('--path', default='.', help="Chemin vers le répertoire racine du projet (par défaut: répertoire courant)")
    args = parser.parse_args()
    
    project_path = os.path.abspath(args.path)
    
    logger.info(f"Démarrage de l'analyse IA du projet Flask dans: {project_path}")
    start_time = time.time()
    
    try:
        # Importer et exécuter l'analyseur
        from flask_project_analyzer import FlaskProjectAIAnalyzer
        
        analyzer = FlaskProjectAIAnalyzer(project_path)
        analyzer.run_full_analysis()
        
        # Afficher le résumé
        report_file = os.path.join(project_path, 'flask_ai_analysis_report.json')
        print_report_summary(report_file)
        
    except ImportError:
        logger.error("Erreur: Module flask_project_analyzer introuvable")
        print("Erreur: Le module flask_project_analyzer n'a pas pu être importé.")
        print("Assurez-vous que le fichier flask_project_analyzer.py existe dans le répertoire courant.")
        return
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'analyse: {e}")
        print(f"Erreur lors de l'exécution de l'analyse: {e}")
        return
    
    total_time = time.time() - start_time
    logger.info(f"Analyse terminée en {total_time:.2f} secondes")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'exécution de l'analyseur de projets Flask
"""
import os
import sys
import json
import argparse
import logging
from flask_analyzer import FlaskProjectAnalyzer

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def parse_args():
    """
    Parse les arguments en ligne de commande
    
    Returns:
        Arguments parsés
    """
    parser = argparse.ArgumentParser(description='Analyseur de projets Flask')
    parser.add_argument('--project-dir', '-p', default='.', help='Répertoire du projet Flask à analyser')
    parser.add_argument('--output', '-o', default='project_analysis.json', help='Fichier de sortie pour les résultats')
    parser.add_argument('--summary', '-s', action='store_true', help='Afficher uniquement le résumé')
    parser.add_argument('--errors-only', '-e', action='store_true', help='Afficher uniquement les erreurs')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='text', help='Format de sortie')
    return parser.parse_args()

def format_error(error):
    """
    Formate une erreur pour l'affichage texte
    
    Args:
        error: Erreur à formater
        
    Returns:
        Texte formaté
    """
    severity_markers = {
        'error': '[ERREUR]',
        'warning': '[AVERT]',
        'info': '[INFO]'
    }
    
    marker = severity_markers.get(error.get('severity', 'info'), '[???]')
    desc = error.get('description', 'Erreur inconnue')
    
    location_info = ''
    if 'location' in error:
        loc = error['location']
        if isinstance(loc, dict):
            if 'file' in loc:
                location_info = f" - Fichier: {loc['file']}"
                if 'line' in loc:
                    location_info += f", Ligne: {loc['line']}"
            elif 'file1' in loc and 'file2' in loc:
                location_info = f" - Fichiers: {loc['file1']} et {loc['file2']}"
    
    return f"{marker} {desc}{location_info}"

def print_results(results, args):
    """
    Affiche les résultats de l'analyse
    
    Args:
        results: Résultats de l'analyse
        args: Arguments de la ligne de commande
    """
    if args.format == 'json':
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return
    
    if args.errors_only:
        errors = results.get('errors', [])
        print(f"\nERREURS DÉTECTÉES ({len(errors)}):")
        if errors:
            for error in errors:
                print(format_error(error))
        else:
            print("Aucune erreur détectée.")
        return
    
    if args.summary:
        stats = results.get('statistics', {})
        print("\nRÉSUMÉ DE L'ANALYSE:")
        print(f"- {stats.get('file_count', 0)} fichiers analysés")
        print(f"  - {stats.get('template_count', 0)} templates")
        print(f"  - {stats.get('static_file_count', 0)} fichiers statiques")
        print(f"  - {stats.get('blueprint_count', 0)} blueprints")
        print(f"- {stats.get('route_count', 0)} routes")
        print(f"- {stats.get('model_count', 0)} modèles")
        print(f"- {stats.get('form_count', 0)} formulaires")
        print(f"- {stats.get('error_count', 0)} erreurs détectées")
        print(f"- {stats.get('duplicate_count', 0)} fichiers dupliqués")
        
        # Afficher le résultat binaire
        compliance = results.get('is_compliant', {})
        print("\nÉVALUATION BINAIRE:")
        print(f"Résultat: {compliance.get('result', 'inconnu').upper()}")
        print(f"Score: {compliance.get('score', 0)}/100")
        for reason in compliance.get('justification', []):
            print(f"- {reason}")
            
        if 'estimated_work' in results:
            print(f"\nTemps de travail estimé: {results['estimated_work'].get('format', 'inconnu')}")
        return
    
    # Affichage complet
    print("\n" + "=" * 80)
    print("ANALYSE DU PROJET FLASK")
    print("=" * 80)
    
    # Structure
    structure = results.get('structure', {})
    print(f"\nSTRUCTURE DU PROJET:")
    print(f"- {len(structure.get('directories', []))} répertoires")
    print(f"- {len(structure.get('files', []))} fichiers")
    print(f"- {len(structure.get('blueprint_modules', []))} blueprints")
    print(f"- {len(structure.get('templates', []))} templates")
    print(f"- {len(structure.get('static_files', []))} fichiers statiques")
    
    # Types de fichiers
    file_types = structure.get('file_types', {})
    print("\nTYPES DE FICHIERS:")
    for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"- {ext}: {count} fichiers")
    
    # Interactions
    interactions = results.get('interactions', {})
    print(f"\nINTERACTIONS:")
    print(f"- {len(interactions.get('routes', []))} routes")
    print(f"- {len(interactions.get('models', []))} modèles")
    print(f"- {len(interactions.get('forms', []))} formulaires")
    print(f"- {len(interactions.get('api_endpoints', []))} endpoints d'API")
    
    # Erreurs
    errors = results.get('errors', [])
    print(f"\nERREURS DÉTECTÉES ({len(errors)}):")
    if errors:
        for error in sorted(errors, key=lambda x: x.get('severity', ''), reverse=True)[:10]:
            print(format_error(error))
        if len(errors) > 10:
            print(f"... et {len(errors) - 10} autres erreurs (voir le fichier de résultats complet)")
    else:
        print("Aucune erreur détectée.")
    
    # Fichiers dupliqués
    duplicates = results.get('duplicates', [])
    print(f"\nFICHIERS DUPLIQUÉS ({len(duplicates)}):")
    if duplicates:
        for dup in sorted(duplicates, key=lambda x: x.get('similarity', 0), reverse=True)[:5]:
            print(f"- {dup['file1']} et {dup['file2']} (similarité: {dup['similarity']}%)")
        if len(duplicates) > 5:
            print(f"... et {len(duplicates) - 5} autres doublons (voir le fichier de résultats complet)")
    else:
        print("Aucun fichier dupliqué détecté.")
    
    # Recommandations
    recommendations = results.get('recommendations', [])
    print(f"\nRECOMMANDATIONS ({len(recommendations)}):")
    if recommendations:
        for rec in sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority'), 3)):
            print(f"- [{rec.get('priority', 'medium').upper()}] {rec.get('title', 'Recommandation')}")
            print(f"  {rec.get('description', '')}")
            if 'ai_insight' in rec:
                print(f"  IA: {rec['ai_insight']}")
    else:
        print("Aucune recommandation générée.")
    
    # Évaluation binaire
    compliance = results.get('is_compliant', {})
    print("\nÉVALUATION BINAIRE:")
    print(f"Résultat: {compliance.get('result', 'inconnu').upper()}")
    print(f"Score: {compliance.get('score', 0)}/100")
    for reason in compliance.get('justification', []):
        print(f"- {reason}")
    
    # Temps de travail
    if 'estimated_work' in results:
        work = results['estimated_work']
        print(f"\nTEMPS DE TRAVAIL ESTIMÉ: {work.get('format', 'inconnu')}")
        if 'breakdown' in work:
            breakdown = work['breakdown']
            print(f"- Temps de base: {breakdown.get('base_time', 0)} minutes")
            print(f"- Correction des erreurs: {breakdown.get('app_remediation', 0)} minutes")
            print(f"- Améliorations générales: {breakdown.get('system_updates', 0)} minutes")

def main():
    """Point d'entrée principal"""
    args = parse_args()
    
    # Vérifier si le répertoire existe
    if not os.path.isdir(args.project_dir):
        logger.error(f"Le répertoire '{args.project_dir}' n'existe pas.")
        return 1
    
    # Créer l'analyseur
    analyzer = FlaskProjectAnalyzer(project_dir=args.project_dir)
    
    # Analyser le projet
    logger.info(f"Analyse du projet dans '{args.project_dir}'...")
    results = analyzer.analyze_project()
    
    # Sauvegarder les résultats
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Résultats d'analyse sauvegardés dans '{args.output}'")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des résultats: {e}")
    
    # Afficher les résultats
    print_results(results, args)
    
    # Retourner le code de sortie basé sur la conformité
    is_compliant = results.get('is_compliant', {}).get('result', '') == 'oui'
    return 0 if is_compliant else 1

if __name__ == "__main__":
    sys.exit(main())
