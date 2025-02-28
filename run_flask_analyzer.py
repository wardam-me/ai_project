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