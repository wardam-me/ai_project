#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test pour l'analyseur de projets Flask avec IA
"""
import os
import sys
import unittest
import tempfile
import shutil
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import du module à tester
try:
    from flask_project_analyzer import FlaskProjectAIAnalyzer
    logger.info("Module d'analyseur Flask importé avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation du module flask_project_analyzer: {e}")
    sys.exit(1)

class TestFlaskAnalyzer(unittest.TestCase):
    """Tests pour l'analyseur de projets Flask"""

    def setUp(self):
        """Création d'un projet Flask de test"""
        self.test_dir = tempfile.mkdtemp()

        # Créer une structure de projet Flask simple
        os.makedirs(os.path.join(self.test_dir, 'templates'))
        os.makedirs(os.path.join(self.test_dir, 'static'))

        # Créer app.py avec une clé secrète en dur (problème de sécurité)
        with open(os.path.join(self.test_dir, 'app.py'), 'w') as f:
            f.write("""
from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'une_cle_secrete_en_dur'  # Problème de sécurité

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)  # Mode debug en production
""")

        # Créer routes.py
        with open(os.path.join(self.test_dir, 'routes.py'), 'w') as f:
            f.write("""
from app import app
from flask import render_template

@app.route('/about')
def about():
    return render_template('about.html')
""")

        # Créer models.py
        with open(os.path.join(self.test_dir, 'models.py'), 'w') as f:
            f.write("""
from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
""")

        # Créer un template avec vulnérabilité XSS
        with open(os.path.join(self.test_dir, 'templates', 'index.html'), 'w') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Ma page Flask</title>
</head>
<body>
    <h1>Bienvenue</h1>
    <div>{{ message|safe }}</div>  <!-- Vulnérabilité XSS -->
</body>
</html>
""")

        # Créer un fichier dupliqué
        with open(os.path.join(self.test_dir, 'routes_copy.py'), 'w') as f:
            f.write("""
from app import app
from flask import render_template

@app.route('/about')
def about():
    return render_template('about.html')
""")

        logger.info(f"Projet de test créé dans {self.test_dir}")

    def tearDown(self):
        """Nettoyer les fichiers de test"""
        shutil.rmtree(self.test_dir)
        logger.info(f"Projet de test supprimé de {self.test_dir}")

    def test_full_analysis(self):
        """Test de l'analyse complète du projet"""
        analyzer = FlaskProjectAIAnalyzer(project_dir=self.test_dir)
        report = analyzer.run_full_analysis()

        # Vérifier que le rapport existe
        self.assertIsNotNone(report)

        # Vérifier les méta-informations
        self.assertEqual(report["meta"]["project_dir"], self.test_dir)

        # Vérifier la structure
        self.assertGreaterEqual(report["project"]["file_count"], 4)  # Au moins 4 fichiers
        self.assertGreaterEqual(report["project"]["dir_count"], 2)   # Au moins 2 répertoires

        # Vérifier la détection Flask
        flask_specific = report["structure"]["flask_specific"]
        self.assertEqual(flask_specific["app_file"], "app.py")

        # Vérifier les problèmes de sécurité
        security_issues = report["issues"]["security"]
        self.assertGreaterEqual(security_issues["count"], 2)  # Au moins deux problèmes de sécurité

        # Vérifier les duplications
        duplicates = report["duplicates"]
        self.assertGreaterEqual(duplicates["count"], 1)  # Au moins un groupe de duplication

        # Vérifier que le fichier de rapport a été créé
        report_file = os.path.join(self.test_dir, "flask_ai_analysis_report.json")
        self.assertTrue(os.path.exists(report_file))

        # Vérifier que le résumé a été créé
        summary_file = os.path.join(self.test_dir, "flask_ai_analysis_summary.txt")
        self.assertTrue(os.path.exists(summary_file))

        logger.info("Test d'analyse complète réussi")

    def test_security_detection(self):
        """Test de la détection des problèmes de sécurité"""
        analyzer = FlaskProjectAIAnalyzer(project_dir=self.test_dir)
        analyzer._analyze_project_structure()
        analyzer._detect_security_issues()

        security_issues = analyzer.report["issues"]["security"]

        # Vérifier la détection de la clé secrète en dur
        hardcoded_secret = any(issue["type"] == "hardcoded_secret" for issue in security_issues["items"])
        self.assertTrue(hardcoded_secret, "La clé secrète en dur n'a pas été détectée")

        # Vérifier la détection du mode debug
        debug_mode = any(issue["type"] == "debug_mode" for issue in security_issues["items"])
        self.assertTrue(debug_mode, "Le mode debug en production n'a pas été détecté")

        # Vérifier la détection de la vulnérabilité XSS
        xss_vulnerability = any(issue["type"] == "xss_vulnerability" for issue in security_issues["items"])
        self.assertTrue(xss_vulnerability, "La vulnérabilité XSS n'a pas été détectée")

        logger.info("Test de détection de sécurité réussi")

    def test_duplicate_detection(self):
        """Test de la détection des fichiers dupliqués"""
        analyzer = FlaskProjectAIAnalyzer(project_dir=self.test_dir)
        analyzer._analyze_project_structure()
        analyzer._detect_duplicate_files()

        duplicates = analyzer.report["duplicates"]

        # Vérifier qu'au moins un groupe de duplication a été détecté
        self.assertGreaterEqual(duplicates["count"], 1, "Aucun fichier dupliqué n'a été détecté")

        # Vérifier que routes.py et routes_copy.py sont détectés comme dupliqués
        routes_detected = False
        for group in duplicates["groups"]:
            files = group["files"]
            if "routes.py" in files and "routes_copy.py" in files:
                routes_detected = True
                break

        self.assertTrue(routes_detected, "La duplication entre routes.py et routes_copy.py n'a pas été détectée")

        logger.info("Test de détection de duplication réussi")


def main():
    """Fonction principale pour exécuter les tests"""
    logger.info("Démarrage des tests de l'analyseur Flask...")
    unittest.main()

if __name__ == "__main__":
    main()