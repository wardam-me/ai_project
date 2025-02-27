"""
Module de génération d'infographies pour l'export de vulnérabilités réseau.
Permet de créer des visualisations attrayantes et informatives des données de sécurité.
Intègre l'IA pour des analyses et recommandations avancées.
"""

import json
import logging
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

import matplotlib
matplotlib.use('Agg')  # Utiliser le backend non-interactif
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

# Import conditionnel pour éviter les dépendances circulaires
ai_assistant = None
try:
    from ai_infographic_assistant import ai_assistant
except ImportError:
    logger.warning("Module ai_infographic_assistant non disponible, fonctionnalités IA limitées")

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes pour les chemins de fichiers
EXPORT_DIR = os.path.join("static", "exports")
TEMPLATES_DIR = os.path.join("static", "templates")
PREVIEWS_DIR = os.path.join("static", "img", "previews")


class InfographicGenerator:
    """Générateur d'infographies pour les données de vulnérabilité réseau"""
    
    def __init__(self):
        """Initialisation du générateur d'infographies"""
        # Créer les répertoires nécessaires s'ils n'existent pas
        os.makedirs(EXPORT_DIR, exist_ok=True)
        
        # Configurer les styles de matplotlib
        plt.style.use('dark_background')
        
        # Définir les palettes de couleurs personnalisées
        self.security_cmap = LinearSegmentedColormap.from_list(
            'security', ['#ff3b30', '#ffcc00', '#34c759'], N=100
        )
        
        # Couleurs pour les différents protocoles
        self.protocol_colors = {
            'WPA3': '#34c759',  # Vert
            'WPA2': '#5ac8fa',  # Bleu
            'WPA': '#ffcc00',   # Jaune
            'WEP': '#ff9500',   # Orange
            'OPEN': '#ff3b30'   # Rouge
        }
        
        # Couleurs pour les niveaux de vulnérabilité
        self.vulnerability_colors = {
            'critical': '#ff3b30',    # Rouge
            'high': '#ff9500',        # Orange
            'medium': '#ffcc00',      # Jaune
            'low': '#5ac8fa',         # Bleu
            'info': '#34c759'         # Vert
        }
    
    def generate_network_security_infographic(
        self, 
        network_data: Dict[str, Any],
        vulnerability_data: Dict[str, Any],
        output_filename: Optional[str] = None,
        format: str = 'png',
        dpi: int = 150,
        interactive: bool = False
    ) -> str:
        """
        Génère une infographie complète de sécurité réseau
        
        Args:
            network_data: Données sur les réseaux et leur sécurité
            vulnerability_data: Données sur les vulnérabilités détectées
            output_filename: Nom du fichier de sortie (optionnel)
            format: Format de sortie (png, pdf, svg, html)
            dpi: Résolution en points par pouce (pour PNG et PDF)
            interactive: Inclure des éléments interactifs (pour PDF et HTML)
            
        Returns:
            str: Chemin vers le fichier infographique généré
        """
        # Valider le format
        format = format.lower()
        if format not in ['png', 'pdf', 'svg', 'html']:
            format = 'png'
        
        # Générer un nom de fichier basé sur la date et l'heure si non spécifié
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"network_security_{timestamp}.{format}"
        elif not output_filename.endswith(f'.{format}'):
            # Changer l'extension si nécessaire
            output_filename = f"{os.path.splitext(output_filename)[0]}.{format}"
        
        # Créer le répertoire s'il n'existe pas
        export_subdir = os.path.join(EXPORT_DIR, 'network')
        os.makedirs(export_subdir, exist_ok=True)
        
        output_path = os.path.join(export_subdir, output_filename)
        
        # Si c'est un format HTML interactif, utiliser un template préexistant
        if format == 'html' and interactive:
            # Copier un template et remplacer les données
            html_template_path = os.path.join(TEMPLATES_DIR, 'network_security_template.html')
            if os.path.exists(html_template_path):
                with open(html_template_path, 'r') as f:
                    template_content = f.read()
                
                # Remplacer les données dans le template
                template_content = template_content.replace('__DATA_PLACEHOLDER__', 
                                                          json.dumps({
                                                              'network_data': network_data,
                                                              'vulnerability_data': vulnerability_data,
                                                              'generated_at': datetime.now().strftime('%d/%m/%Y à %H:%M')
                                                          }))
                
                # Écrire le fichier HTML
                with open(output_path, 'w') as f:
                    f.write(template_content)
                
                logger.info(f"Infographie HTML interactive générée: {output_path}")
                return output_path
        
        # Pour les autres formats (png, pdf, svg) ou si le template HTML n'existe pas
        # Créer une figure avec plusieurs sous-graphiques
        fig = plt.figure(figsize=(12, 15), dpi=dpi)
        fig.suptitle("RAPPORT DE SÉCURITÉ RÉSEAU", fontsize=24, fontweight='bold', y=0.98)
        subtitle = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        fig.text(0.5, 0.96, subtitle, fontsize=14, ha='center')
        
        # Définir la mise en page des sous-graphiques
        gs = fig.add_gridspec(4, 2, height_ratios=[1, 1.5, 1.5, 1])
        
        # 1. Score de sécurité global (jauge)
        self._create_security_score_gauge(fig, gs[0, 0], network_data.get('overall_score', 0))
        
        # 2. Distribution des protocoles (camembert)
        self._create_protocol_distribution_chart(fig, gs[0, 1], network_data.get('protocol_distribution', {}))
        
        # 3. Vulnérabilités par type (graphique à barres horizontales)
        self._create_vulnerability_types_chart(fig, gs[1, 0], vulnerability_data.get('vulnerability_types', {}))
        
        # 4. Graphique radar des dimensions de sécurité
        self._create_security_dimensions_radar(fig, gs[1, 1], network_data.get('security_dimensions', {}))
        
        # 5. Top des appareils vulnérables (barres de progression)
        self._create_vulnerable_devices_chart(fig, gs[2, 0], network_data.get('devices', []))
        
        # 6. Tendance de sécurité (graphique linéaire)
        self._create_security_trend_chart(fig, gs[2, 1], network_data.get('security_trend', []))
        
        # 7. Recommandations principales (liste textuelle)
        self._create_recommendations_section(fig, gs[3, :], vulnerability_data.get('recommendations', []))
        
        # Ajuster l'espacement et sauvegarder l'image
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(output_path, bbox_inches='tight')
        plt.close(fig)
        
        logger.info(f"Infographie de sécurité réseau générée: {output_path}")
        return output_path
    
    def generate_protocol_analysis_infographic(
        self,
        protocol_data: Dict[str, Any],
        output_filename: Optional[str] = None,
        format: str = 'png',
        dpi: int = 150,
        interactive: bool = False
    ) -> str:
        """
        Génère une infographie d'analyse de protocole WiFi
        
        Args:
            protocol_data: Données d'analyse de protocole
            output_filename: Nom du fichier de sortie (optionnel)
            format: Format de sortie (png, pdf, svg, html)
            dpi: Résolution en points par pouce (pour PNG et PDF)
            interactive: Inclure des éléments interactifs (pour PDF et HTML)
            
        Returns:
            str: Chemin vers le fichier infographique généré
        """
        # Valider le format
        format = format.lower()
        if format not in ['png', 'pdf', 'svg', 'html']:
            format = 'png'
        
        # Générer un nom de fichier basé sur la date et l'heure si non spécifié
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"protocol_analysis_{timestamp}.{format}"
        elif not output_filename.endswith(f'.{format}'):
            # Changer l'extension si nécessaire
            output_filename = f"{os.path.splitext(output_filename)[0]}.{format}"
        
        # Créer le répertoire s'il n'existe pas
        export_subdir = os.path.join(EXPORT_DIR, 'protocol')
        os.makedirs(export_subdir, exist_ok=True)
        
        output_path = os.path.join(export_subdir, output_filename)
        
        # Si c'est un format HTML interactif, utiliser un template préexistant
        if format == 'html' and interactive:
            # Copier un template et remplacer les données
            html_template_path = os.path.join(TEMPLATES_DIR, 'protocol_analysis_template.html')
            if os.path.exists(html_template_path):
                with open(html_template_path, 'r') as f:
                    template_content = f.read()
                
                # Remplacer les données dans le template
                template_content = template_content.replace('__DATA_PLACEHOLDER__', 
                                                          json.dumps({
                                                              'protocol_data': protocol_data,
                                                              'generated_at': datetime.now().strftime('%d/%m/%Y à %H:%M')
                                                          }))
                
                # Écrire le fichier HTML
                with open(output_path, 'w') as f:
                    f.write(template_content)
                
                logger.info(f"Infographie HTML interactive générée: {output_path}")
                return output_path
        
        # Pour les autres formats (png, pdf, svg) ou si le template HTML n'existe pas
        # Créer une figure avec plusieurs sous-graphiques
        fig = plt.figure(figsize=(12, 16), dpi=dpi)
        fig.suptitle("ANALYSE DES PROTOCOLES WIFI", fontsize=24, fontweight='bold', y=0.98)
        subtitle = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        fig.text(0.5, 0.96, subtitle, fontsize=14, ha='center')
        
        # Définir la mise en page des sous-graphiques
        gs = fig.add_gridspec(4, 2, height_ratios=[1, 1.5, 1.5, 1.5])
        
        # 1. Score moyen des protocoles (jauge)
        self._create_security_score_gauge(fig, gs[0, 0], protocol_data.get('average_score', 0), 
                                        title="Score moyen des protocoles")
        
        # 2. Distribution des protocoles (camembert)
        self._create_protocol_distribution_chart(fig, gs[0, 1], protocol_data.get('protocol_distribution', {}))
        
        # 3. Comparaison des protocoles (tableau)
        self._create_protocol_comparison_table(fig, gs[1, :], protocol_data.get('protocols', []))
        
        # 4. Vulnérabilités par protocole (graphique à barres empilées)
        self._create_protocol_vulnerabilities_chart(fig, gs[2, 0], protocol_data.get('vulnerability_by_protocol', {}))
        
        # 5. Forces relatives des protocoles (graphique radar)
        self._create_protocol_strength_radar(fig, gs[2, 1], protocol_data.get('protocol_strengths', {}))
        
        # 6. Recommandations pour améliorer la sécurité (liste textuelle)
        self._create_recommendations_section(fig, gs[3, :], protocol_data.get('recommendations', []))
        
        # Ajuster l'espacement et sauvegarder l'image
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(output_path, bbox_inches='tight')
        plt.close(fig)
        
        logger.info(f"Infographie d'analyse de protocole générée: {output_path}")
        return output_path
    
    def generate_vulnerability_report_infographic(
        self,
        vulnerability_data: Dict[str, Any],
        output_filename: Optional[str] = None,
        format: str = 'png',
        dpi: int = 150,
        interactive: bool = False
    ) -> str:
        """
        Génère une infographie détaillée des vulnérabilités
        
        Args:
            vulnerability_data: Données sur les vulnérabilités détectées
            output_filename: Nom du fichier de sortie (optionnel)
            format: Format de sortie (png, pdf, svg, html)
            dpi: Résolution en points par pouce (pour PNG et PDF)
            interactive: Inclure des éléments interactifs (pour PDF et HTML)
            
        Returns:
            str: Chemin vers le fichier infographique généré
        """
        # Valider le format
        format = format.lower()
        if format not in ['png', 'pdf', 'svg', 'html']:
            format = 'png'
        
        # Générer un nom de fichier basé sur la date et l'heure si non spécifié
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"vulnerability_report_{timestamp}.{format}"
        elif not output_filename.endswith(f'.{format}'):
            # Changer l'extension si nécessaire
            output_filename = f"{os.path.splitext(output_filename)[0]}.{format}"
        
        # Créer le répertoire s'il n'existe pas
        export_subdir = os.path.join(EXPORT_DIR, 'vulnerability')
        os.makedirs(export_subdir, exist_ok=True)
        
        output_path = os.path.join(export_subdir, output_filename)
        
        # Si c'est un format HTML interactif, utiliser un template préexistant
        if format == 'html' and interactive:
            # Copier un template et remplacer les données
            html_template_path = os.path.join(TEMPLATES_DIR, 'vulnerability_report_template.html')
            if os.path.exists(html_template_path):
                with open(html_template_path, 'r') as f:
                    template_content = f.read()
                
                # Remplacer les données dans le template
                template_content = template_content.replace('__DATA_PLACEHOLDER__', 
                                                         json.dumps({
                                                             'vulnerability_data': vulnerability_data,
                                                             'generated_at': datetime.now().strftime('%d/%m/%Y à %H:%M')
                                                         }))
                
                # Écrire le fichier HTML
                with open(output_path, 'w') as f:
                    f.write(template_content)
                
                logger.info(f"Infographie HTML interactive générée: {output_path}")
                return output_path
        
        # Pour les autres formats (png, pdf, svg) ou si le template HTML n'existe pas
        # Créer une figure avec plusieurs sous-graphiques
        fig = plt.figure(figsize=(12, 16), dpi=dpi)
        fig.suptitle("RAPPORT DÉTAILLÉ DES VULNÉRABILITÉS", fontsize=24, fontweight='bold', y=0.98)
        subtitle = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        fig.text(0.5, 0.96, subtitle, fontsize=14, ha='center')
        
        # Définir la mise en page des sous-graphiques
        gs = fig.add_gridspec(4, 2, height_ratios=[1, 1.5, 1.5, 1.5])
        
        # 1. Résumé des vulnérabilités (compteurs)
        self._create_vulnerability_summary(fig, gs[0, :], vulnerability_data.get('summary', {}))
        
        # 2. Top 5 des vulnérabilités critiques (liste détaillée)
        self._create_top_vulnerabilities_list(fig, gs[1, :], vulnerability_data.get('critical_vulnerabilities', []))
        
        # 3. Distribution des vulnérabilités par sévérité (camembert)
        self._create_vulnerability_severity_chart(fig, gs[2, 0], vulnerability_data.get('severity_distribution', {}))
        
        # 4. Timeline de découverte des vulnérabilités (graphique linéaire)
        self._create_vulnerability_timeline(fig, gs[2, 1], vulnerability_data.get('discovery_timeline', []))
        
        # 5. Plan d'action pour remédier aux vulnérabilités (tableau)
        self._create_remediation_plan(fig, gs[3, :], vulnerability_data.get('remediation_plan', []))
        
        # Ajuster l'espacement et sauvegarder l'image
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(output_path, bbox_inches='tight')
        plt.close(fig)
        
        logger.info(f"Infographie de rapport de vulnérabilité générée: {output_path}")
        return output_path
    
    def _create_security_score_gauge(self, fig, position, score, title="Score de sécurité global"):
        """Crée une jauge pour afficher le score de sécurité"""
        ax = fig.add_subplot(position)
        
        # Déterminer la couleur en fonction du score
        if score >= 80:
            color = '#34c759'  # Vert
        elif score >= 60:
            color = '#ffcc00'  # Jaune
        elif score >= 40:
            color = '#ff9500'  # Orange
        else:
            color = '#ff3b30'  # Rouge
        
        # Créer un graphique en anneau pour la jauge
        ax.pie(
            [score, 100 - score],
            colors=[color, '#333333'],
            startangle=90,
            counterclock=False,
            wedgeprops={'width': 0.3, 'edgecolor': 'none'}
        )
        
        # Ajouter le texte du score au centre
        ax.text(0, 0, f"{score}", ha='center', va='center', fontsize=36, fontweight='bold')
        
        # Ajouter des étiquettes pour les niveaux
        ax.text(0, -0.5, title, ha='center', va='center', fontsize=14)
        
        # Catégoriser le score
        if score >= 80:
            category = "BON"
        elif score >= 60:
            category = "MOYEN"
        elif score >= 40:
            category = "PRÉOCCUPANT"
        else:
            category = "CRITIQUE"
        
        ax.text(0, -0.7, f"Niveau: {category}", ha='center', va='center', fontsize=12, color=color)
        
        # Configurer l'axes
        ax.set_aspect('equal')
        ax.axis('off')
    
    def _create_protocol_distribution_chart(self, fig, position, protocol_distribution):
        """Crée un graphique en camembert pour la distribution des protocoles"""
        ax = fig.add_subplot(position)
        
        # Préparer les données
        protocols = list(protocol_distribution.keys())
        counts = list(protocol_distribution.values())
        
        # Déterminer les couleurs en fonction des protocoles
        colors = [self.protocol_colors.get(p, '#999999') for p in protocols]
        
        # Créer le camembert
        wedges, texts, autotexts = ax.pie(
            counts,
            labels=protocols,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1}
        )
        
        # Styliser les textes
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('white')
        
        # Ajouter un titre
        ax.set_title("Distribution des protocoles", fontsize=14, pad=20)
        
        # Configurer l'axes
        ax.set_aspect('equal')
    
    def _create_vulnerability_types_chart(self, fig, position, vulnerability_types):
        """Crée un graphique à barres horizontales pour les types de vulnérabilités"""
        ax = fig.add_subplot(position)
        
        # Préparer les données
        vuln_types = list(vulnerability_types.keys())
        counts = list(vulnerability_types.values())
        
        # Inverser l'ordre pour que les barres les plus longues soient en haut
        vuln_types.reverse()
        counts.reverse()
        
        # Créer le graphique à barres horizontales
        bars = ax.barh(vuln_types, counts, color='#5ac8fa')
        
        # Ajouter les valeurs à la fin des barres
        for i, v in enumerate(counts):
            ax.text(v + 0.1, i, str(v), va='center', fontsize=10)
        
        # Configurer les axes
        ax.set_xlabel('Nombre de vulnérabilités', fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=9)
        
        # Ajouter un titre
        ax.set_title("Types de vulnérabilités détectées", fontsize=14)
        
        # Ajouter une grille
        ax.grid(axis='x', linestyle='--', alpha=0.3)
    
    def _create_security_dimensions_radar(self, fig, position, security_dimensions):
        """Crée un graphique radar pour les dimensions de sécurité"""
        ax = fig.add_subplot(position, polar=True)
        
        # Préparer les données
        categories = list(security_dimensions.keys())
        values = list(security_dimensions.values())
        
        # Nombre de variables
        N = len(categories)
        
        # Si la liste est vide, utiliser des données d'exemple
        if N == 0:
            categories = [
                'Authentification', 'Chiffrement', 'Mises à jour',
                'Pare-feu', 'Segmentation', 'Monitoring'
            ]
            values = [65, 70, 50, 85, 90, 60]
            N = len(categories)
        
        # Calculer les angles pour chaque dimension
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Fermer le polygone
        
        # Ajouter les valeurs également
        values += values[:1]
        
        # Tracer les valeurs
        ax.plot(angles, values, linewidth=2, linestyle='solid', color='#5ac8fa')
        ax.fill(angles, values, color='#5ac8fa', alpha=0.25)
        
        # Ajouter un repère à 100 (maximum)
        ax.plot(angles, [100] * (N + 1), color='#999999', linestyle='--', alpha=0.3)
        
        # Étiquettes et ticks
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=8)
        
        # Configurer les limites des axes et supprimer les étiquettes d'axes
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
        
        # Ajouter un titre
        ax.set_title("Dimensions de sécurité", fontsize=14, pad=20)
    
    def _create_vulnerable_devices_chart(self, fig, position, devices):
        """Crée un graphique à barres horizontales pour les appareils vulnérables"""
        ax = fig.add_subplot(position)
        
        # Si la liste est vide, utiliser des données d'exemple
        if not devices:
            devices = [
                {'name': 'Caméra IP', 'security_score': 35},
                {'name': 'Smart TV', 'security_score': 55},
                {'name': 'Smartphone', 'security_score': 65},
                {'name': 'Routeur WiFi', 'security_score': 75},
                {'name': 'Ordinateur portable', 'security_score': 85}
            ]
        
        # Trier les appareils par score croissant
        devices = sorted(devices, key=lambda x: x.get('security_score', 0))
        
        # Limiter aux 5 appareils les plus vulnérables
        devices = devices[:5]
        
        # Préparer les données
        names = [d.get('name', 'Inconnu') for d in devices]
        scores = [d.get('security_score', 0) for d in devices]
        
        # Créer une palette de couleurs basée sur les scores
        colors = [self.security_cmap(score / 100) for score in scores]
        
        # Créer le graphique à barres horizontales
        bars = ax.barh(names, scores, color=colors)
        
        # Ajouter les scores à la fin des barres
        for i, v in enumerate(scores):
            ax.text(v + 1, i, str(v), va='center', fontsize=10)
        
        # Configurer les axes
        ax.set_xlabel('Score de sécurité', fontsize=10)
        ax.set_xlim(0, 100)
        ax.tick_params(axis='both', which='major', labelsize=9)
        
        # Ajouter un titre
        ax.set_title("Appareils les plus vulnérables", fontsize=14)
        
        # Ajouter une grille
        ax.grid(axis='x', linestyle='--', alpha=0.3)
    
    def _create_security_trend_chart(self, fig, position, trend_data):
        """Crée un graphique linéaire pour la tendance de sécurité au fil du temps"""
        ax = fig.add_subplot(position)
        
        # Si la liste est vide, utiliser des données d'exemple
        if not trend_data:
            months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin']
            scores = [54, 58, 60, 65, 68, 72]
        else:
            months = [entry.get('date', '') for entry in trend_data]
            scores = [entry.get('score', 0) for entry in trend_data]
        
        # Créer le graphique linéaire
        ax.plot(months, scores, marker='o', linestyle='-', color='#5ac8fa', linewidth=2)
        
        # Remplir la zone sous la courbe
        ax.fill_between(months, scores, color='#5ac8fa', alpha=0.2)
        
        # Configurer les axes
        ax.set_ylim(0, 100)
        ax.set_xlabel('Période', fontsize=10)
        ax.set_ylabel('Score de sécurité', fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=9)
        
        # Ajouter un titre
        ax.set_title("Évolution du score de sécurité", fontsize=14)
        
        # Ajouter une grille
        ax.grid(linestyle='--', alpha=0.3)
    
    def _create_recommendations_section(self, fig, position, recommendations):
        """Crée une section de texte pour les recommandations principales"""
        ax = fig.add_subplot(position)
        
        # Si la liste est vide, utiliser des données d'exemple
        if not recommendations:
            recommendations = [
                {
                    'priority': 'critical',
                    'description': 'Mettre à jour le firmware du routeur',
                    'details': 'Votre routeur exécute un firmware obsolète contenant des vulnérabilités connues.'
                },
                {
                    'priority': 'high',
                    'description': 'Changer les mots de passe par défaut',
                    'details': 'Plusieurs appareils IoT utilisent encore leurs mots de passe par défaut.'
                },
                {
                    'priority': 'medium',
                    'description': 'Activer WPA3 sur votre réseau WiFi',
                    'description': 'Passer à WPA3 offre une meilleure protection contre les attaques.'
                }
            ]
        
        # Trier les recommandations par priorité
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations = sorted(recommendations, key=lambda x: priority_order.get(x.get('priority', 'low'), 999))
        
        # Limiter aux 5 recommandations les plus importantes
        recommendations = recommendations[:5]
        
        # Désactiver les axes
        ax.axis('off')
        
        # Ajouter un titre
        ax.text(0.5, 1.0, "RECOMMANDATIONS PRINCIPALES", ha='center', va='top', fontsize=14, fontweight='bold')
        
        # Ajouter chaque recommandation
        y_pos = 0.9
        for i, rec in enumerate(recommendations):
            priority = rec.get('priority', 'low')
            description = rec.get('description', '')
            details = rec.get('details', '')
            
            # Couleur basée sur la priorité
            color = self.vulnerability_colors.get(priority, '#999999')
            
            # Texte de priorité
            priority_text = priority.upper()
            
            # Ajouter la recommandation
            ax.text(0.02, y_pos, f"{i+1}.", fontsize=11, fontweight='bold')
            ax.text(0.06, y_pos, description, fontsize=11, fontweight='bold')
            ax.text(0.06, y_pos - 0.03, details, fontsize=9, wrap=True)
            ax.text(0.95, y_pos, priority_text, fontsize=9, color=color, ha='right', fontweight='bold')
            
            # Ajouter une ligne de séparation
            if i < len(recommendations) - 1:
                ax.axhline(y=y_pos - 0.07, xmin=0.02, xmax=0.98, color='#555555', alpha=0.3, linestyle='-')
            
            # Mettre à jour la position verticale
            y_pos -= 0.15
    
    def _create_protocol_comparison_table(self, fig, position, protocols_data):
        """Crée un tableau comparatif des protocoles de sécurité"""
        ax = fig.add_subplot(position)
        
        # Si la liste est vide, utiliser des données d'exemple
        if not protocols_data:
            protocols_data = [
                {
                    'name': 'WEP',
                    'security_level': 'Très faible',
                    'year_introduced': 1999,
                    'status': 'Obsolète',
                    'vulnerabilities': [
                        'Clés facilement cassables',
                        'Attaques par réinjection'
                    ],
                    'recommendation': 'À éviter complètement'
                },
                {
                    'name': 'WPA',
                    'security_level': 'Faible',
                    'year_introduced': 2003,
                    'status': 'Déconseillé',
                    'vulnerabilities': [
                        'Vulnérabilités TKIP',
                        'Attaques sur le MIC'
                    ],
                    'recommendation': 'Mettre à niveau vers WPA2/WPA3'
                },
                {
                    'name': 'WPA2',
                    'security_level': 'Moyen à bon',
                    'year_introduced': 2004,
                    'status': 'Standard actuel',
                    'vulnerabilities': [
                        'Vulnérabilité KRACK',
                        'Attaques par dictionnaire sur PSK'
                    ],
                    'recommendation': 'Utiliser avec AES/CCMP uniquement'
                },
                {
                    'name': 'WPA3',
                    'security_level': 'Élevé',
                    'year_introduced': 2018,
                    'status': 'Recommandé',
                    'vulnerabilities': [
                        'Vulnérabilités Dragonblood (corrigées)'
                    ],
                    'recommendation': 'Solution recommandée'
                }
            ]
        
        # Désactiver les axes
        ax.axis('off')
        
        # Ajouter un titre
        ax.text(0.5, 1.05, "COMPARAISON DES PROTOCOLES DE SÉCURITÉ", ha='center', va='top', fontsize=14, fontweight='bold')
        
        # Définir les colonnes
        headers = ['Protocole', 'Niveau de sécurité', 'Année', 'Statut', 'Vulnérabilités', 'Recommandation']
        column_widths = [0.10, 0.18, 0.07, 0.15, 0.25, 0.25]
        x_positions = [sum(column_widths[:i]) for i in range(len(headers))]
        
        # Ajouter les en-têtes de colonnes
        for i, header in enumerate(headers):
            ax.text(x_positions[i] + column_widths[i]/2, 0.95, header, ha='center', va='center', 
                   fontsize=10, fontweight='bold')
        
        # Ajouter une ligne sous les en-têtes
        ax.axhline(y=0.90, xmin=0, xmax=1, color='white', alpha=0.5, linestyle='-')
        
        # Ajouter les données des protocoles
        y_pos = 0.83
        for protocol in protocols_data:
            # Récupérer les données du protocole
            name = protocol.get('name', '')
            security_level = protocol.get('security_level', '')
            year = protocol.get('year_introduced', '')
            status = protocol.get('status', '')
            vulnerabilities = protocol.get('vulnerabilities', [])
            recommendation = protocol.get('recommendation', '')
            
            # Obtenir la couleur du protocole
            color = self.protocol_colors.get(name, '#999999')
            
            # Ajouter les données
            ax.text(x_positions[0] + column_widths[0]/2, y_pos, name, ha='center', va='center', 
                   fontsize=10, fontweight='bold', color=color)
            ax.text(x_positions[1] + column_widths[1]/2, y_pos, security_level, ha='center', va='center', fontsize=9)
            ax.text(x_positions[2] + column_widths[2]/2, y_pos, str(year), ha='center', va='center', fontsize=9)
            ax.text(x_positions[3] + column_widths[3]/2, y_pos, status, ha='center', va='center', fontsize=9)
            
            # Afficher les vulnérabilités
            vuln_text = "\n".join(vulnerabilities)
            ax.text(x_positions[4] + 0.01, y_pos, vuln_text, ha='left', va='center', fontsize=8)
            
            # Afficher la recommandation
            ax.text(x_positions[5] + 0.01, y_pos, recommendation, ha='left', va='center', fontsize=8)
            
            # Ajouter une ligne de séparation
            if protocol != protocols_data[-1]:
                ax.axhline(y=y_pos - 0.06, xmin=0, xmax=1, color='white', alpha=0.2, linestyle='-')
            
            # Mettre à jour la position verticale
            y_pos -= 0.13
    
    def _create_protocol_vulnerabilities_chart(self, fig, position, vulnerability_data):
        """Crée un graphique à barres empilées pour les vulnérabilités par protocole"""
        ax = fig.add_subplot(position)
        
        # Si le dictionnaire est vide, utiliser des données d'exemple
        if not vulnerability_data:
            vulnerability_data = {
                'WEP': {'critical': 5, 'high': 3, 'medium': 1, 'low': 0},
                'WPA': {'critical': 2, 'high': 4, 'medium': 2, 'low': 1},
                'WPA2': {'critical': 1, 'high': 2, 'medium': 3, 'low': 2},
                'WPA3': {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            }
        
        # Préparer les données
        protocols = list(vulnerability_data.keys())
        
        # Extraire les données pour chaque niveau de vulnérabilité
        critical_values = [vulnerability_data[p].get('critical', 0) for p in protocols]
        high_values = [vulnerability_data[p].get('high', 0) for p in protocols]
        medium_values = [vulnerability_data[p].get('medium', 0) for p in protocols]
        low_values = [vulnerability_data[p].get('low', 0) for p in protocols]
        
        # Créer le graphique à barres empilées
        bar_width = 0.6
        
        ax.bar(protocols, critical_values, bar_width, label='Critique', color=self.vulnerability_colors['critical'])
        ax.bar(protocols, high_values, bar_width, bottom=critical_values, label='Élevé', color=self.vulnerability_colors['high'])
        
        # Calcul des sommes partielles pour les barres empilées
        bottom_medium = [c + h for c, h in zip(critical_values, high_values)]
        ax.bar(protocols, medium_values, bar_width, bottom=bottom_medium, label='Moyen', color=self.vulnerability_colors['medium'])
        
        bottom_low = [c + h + m for c, h, m in zip(critical_values, high_values, medium_values)]
        ax.bar(protocols, low_values, bar_width, bottom=bottom_low, label='Faible', color=self.vulnerability_colors['low'])
        
        # Configurer les axes
        ax.set_ylabel('Nombre de vulnérabilités', fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=9)
        
        # Ajouter un titre
        ax.set_title("Vulnérabilités par protocole", fontsize=14)
        
        # Ajouter une légende
        ax.legend(fontsize=8, ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.15))
        
        # Ajouter une grille
        ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    def _create_protocol_strength_radar(self, fig, position, strength_data):
        """Crée un graphique radar pour les forces relatives des protocoles"""
        ax = fig.add_subplot(position, polar=True)
        
        # Si le dictionnaire est vide, utiliser des données d'exemple
        if not strength_data:
            strength_data = {
                'WEP': {'Chiffrement': 10, 'Authentification': 15, 'Intégrité': 20, 'Résistance aux attaques': 5, 'Gestion des clés': 10},
                'WPA': {'Chiffrement': 40, 'Authentification': 45, 'Intégrité': 50, 'Résistance aux attaques': 35, 'Gestion des clés': 40},
                'WPA2': {'Chiffrement': 75, 'Authentification': 70, 'Intégrité': 80, 'Résistance aux attaques': 65, 'Gestion des clés': 70},
                'WPA3': {'Chiffrement': 90, 'Authentification': 95, 'Intégrité': 90, 'Résistance aux attaques': 85, 'Gestion des clés': 90}
            }
        
        # Récupérer les dimensions de force
        dimensions = list(next(iter(strength_data.values())).keys())
        
        # Nombre de variables
        N = len(dimensions)
        
        # Calculer les angles pour chaque dimension
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Fermer le polygone
        
        # Préparer l'intrigue
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, fontsize=8)
        
        # Configurer les limites des axes
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
        
        # Tracer chaque protocole
        for protocol, values in strength_data.items():
            strength_values = [values[dim] for dim in dimensions]
            strength_values += strength_values[:1]  # Fermer le polygone
            
            # Tracer les valeurs avec la couleur du protocole
            color = self.protocol_colors.get(protocol, '#999999')
            ax.plot(angles, strength_values, linewidth=2, linestyle='solid', label=protocol, color=color)
            ax.fill(angles, strength_values, color=color, alpha=0.15)
        
        # Ajouter une légende
        ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1), fontsize=8)
        
        # Ajouter un titre
        ax.set_title("Forces relatives des protocoles", fontsize=14, pad=20)
    
    def _create_vulnerability_summary(self, fig, position, summary_data):
        """Crée une section résumée des vulnérabilités"""
        ax = fig.add_subplot(position)
        
        # Si le dictionnaire est vide, utiliser des données d'exemple
        if not summary_data:
            summary_data = {
                'total': 32,
                'critical': 3,
                'high': 8,
                'medium': 15,
                'low': 6,
                'cvss_avg': 7.8,
                'risk_level': 'Élevé'
            }
        
        # Désactiver les axes
        ax.axis('off')
        
        # Ajouter un titre
        ax.text(0.5, 1.05, "RÉSUMÉ DES VULNÉRABILITÉS", ha='center', va='top', fontsize=14, fontweight='bold')
        
        # Ajouter le score CVSS moyen
        cvss_avg = summary_data.get('cvss_avg', 0)
        risk_level = summary_data.get('risk_level', 'Inconnu')
        
        # Déterminer la couleur en fonction du score CVSS
        if cvss_avg >= 9.0:
            color = self.vulnerability_colors['critical']
        elif cvss_avg >= 7.0:
            color = self.vulnerability_colors['high']
        elif cvss_avg >= 4.0:
            color = self.vulnerability_colors['medium']
        else:
            color = self.vulnerability_colors['low']
        
        ax.text(0.5, 0.85, "Score CVSS moyen", ha='center', va='center', fontsize=12)
        ax.text(0.5, 0.75, f"{cvss_avg}", ha='center', va='center', fontsize=32, fontweight='bold', color=color)
        ax.text(0.5, 0.65, f"Niveau de risque: {risk_level}", ha='center', va='center', fontsize=10, color=color)
        
        # Préparer les compteurs de vulnérabilités
        total = summary_data.get('total', 0)
        critical = summary_data.get('critical', 0)
        high = summary_data.get('high', 0)
        medium = summary_data.get('medium', 0)
        low = summary_data.get('low', 0)
        
        # Ajouter les compteurs avec des icônes
        x_positions = [0.15, 0.35, 0.55, 0.75, 0.95]
        y_position = 0.35
        
        # Total
        ax.text(x_positions[0], y_position + 0.1, "Total", ha='center', va='center', fontsize=10)
        ax.text(x_positions[0], y_position, str(total), ha='center', va='center', fontsize=24, fontweight='bold')
        
        # Critique
        ax.text(x_positions[1], y_position + 0.1, "Critique", ha='center', va='center', fontsize=10)
        ax.text(x_positions[1], y_position, str(critical), ha='center', va='center', fontsize=24, 
                fontweight='bold', color=self.vulnerability_colors['critical'])
        
        # Élevé
        ax.text(x_positions[2], y_position + 0.1, "Élevé", ha='center', va='center', fontsize=10)
        ax.text(x_positions[2], y_position, str(high), ha='center', va='center', fontsize=24, 
                fontweight='bold', color=self.vulnerability_colors['high'])
        
        # Moyen
        ax.text(x_positions[3], y_position + 0.1, "Moyen", ha='center', va='center', fontsize=10)
        ax.text(x_positions[3], y_position, str(medium), ha='center', va='center', fontsize=24, 
                fontweight='bold', color=self.vulnerability_colors['medium'])
        
        # Faible
        ax.text(x_positions[4], y_position + 0.1, "Faible", ha='center', va='center', fontsize=10)
        ax.text(x_positions[4], y_position, str(low), ha='center', va='center', fontsize=24, 
                fontweight='bold', color=self.vulnerability_colors['low'])
    
    def _create_top_vulnerabilities_list(self, fig, position, vulnerabilities):
        """Crée une liste des principales vulnérabilités"""
        ax = fig.add_subplot(position)
        
        # Si la liste est vide, utiliser des données d'exemple
        if not vulnerabilities:
            vulnerabilities = [
                {
                    'cve_id': 'CVE-2022-26928',
                    'description': 'Vulnérabilité d\'exécution de code à distance dans le firmware',
                    'severity': 'critical',
                    'cvss_score': 9.8,
                    'affected_device': 'Routeur WiFi Principal',
                    'status': 'Non corrigé'
                },
                {
                    'cve_id': 'CVE-2021-37714',
                    'description': 'Identifiants par défaut exposés permettant un accès non autorisé',
                    'severity': 'critical',
                    'cvss_score': 9.6,
                    'affected_device': 'Caméra IP',
                    'status': 'Non corrigé'
                },
                {
                    'cve_id': 'CVE-2023-12345',
                    'description': 'Vulnérabilité de débordement de tampon dans le traitement des paquets réseau',
                    'severity': 'critical',
                    'cvss_score': 9.1,
                    'affected_device': 'Smart TV',
                    'status': 'Non corrigé'
                }
            ]
        
        # Désactiver les axes
        ax.axis('off')
        
        # Ajouter un titre
        ax.text(0.5, 1.05, "VULNÉRABILITÉS CRITIQUES", ha='center', va='top', fontsize=14, fontweight='bold')
        
        # Ajouter un en-tête pour le tableau
        headers = ['CVE ID', 'Description', 'Score CVSS', 'Appareil affecté', 'Statut']
        column_widths = [0.15, 0.35, 0.10, 0.20, 0.20]
        x_positions = [sum(column_widths[:i]) for i in range(len(headers))]
        
        # Ajouter les en-têtes de colonnes
        for i, header in enumerate(headers):
            ax.text(x_positions[i] + 0.01, 0.95, header, ha='left', va='center', 
                   fontsize=10, fontweight='bold')
        
        # Ajouter une ligne sous les en-têtes
        ax.axhline(y=0.90, xmin=0, xmax=1, color='white', alpha=0.5, linestyle='-')
        
        # Ajouter les données des vulnérabilités
        y_pos = 0.82
        for vuln in vulnerabilities[:5]:  # Limiter aux 5 plus critiques
            # Récupérer les données de la vulnérabilité
            cve_id = vuln.get('cve_id', '')
            description = vuln.get('description', '')
            severity = vuln.get('severity', 'low')
            cvss_score = vuln.get('cvss_score', 0)
            affected_device = vuln.get('affected_device', '')
            status = vuln.get('status', '')
            
            # Obtenir la couleur basée sur la sévérité
            color = self.vulnerability_colors.get(severity, '#999999')
            
            # Ajouter les données
            ax.text(x_positions[0] + 0.01, y_pos, cve_id, ha='left', va='center', fontsize=9)
            ax.text(x_positions[1] + 0.01, y_pos, description, ha='left', va='center', fontsize=9)
            ax.text(x_positions[2] + 0.01, y_pos, str(cvss_score), ha='left', va='center', 
                   fontsize=9, color=color, fontweight='bold')
            ax.text(x_positions[3] + 0.01, y_pos, affected_device, ha='left', va='center', fontsize=9)
            ax.text(x_positions[4] + 0.01, y_pos, status, ha='left', va='center', fontsize=9)
            
            # Ajouter une ligne de séparation
            if vuln != vulnerabilities[-1] and vulnerabilities.index(vuln) < 4:
                ax.axhline(y=y_pos - 0.06, xmin=0, xmax=1, color='white', alpha=0.2, linestyle='-')
            
            # Mettre à jour la position verticale
            y_pos -= 0.13
    
    def _create_vulnerability_severity_chart(self, fig, position, severity_distribution):
        """Crée un graphique en camembert pour la distribution des sévérités de vulnérabilités"""
        ax = fig.add_subplot(position)
        
        # Si le dictionnaire est vide, utiliser des données d'exemple
        if not severity_distribution:
            severity_distribution = {
                'critical': 3,
                'high': 8,
                'medium': 15,
                'low': 6
            }
        
        # Préparer les données
        severities = list(severity_distribution.keys())
        counts = list(severity_distribution.values())
        
        # Obtenir les couleurs pour chaque sévérité
        colors = [self.vulnerability_colors.get(sev, '#999999') for sev in severities]
        
        # Créer le camembert
        wedges, texts, autotexts = ax.pie(
            counts,
            labels=severities,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1}
        )
        
        # Styliser les textes
        for text in texts:
            text.set_fontsize(10)
            text.set_text(text.get_text().capitalize())  # Mettre en majuscule la première lettre
        
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('white')
        
        # Ajouter un titre
        ax.set_title("Distribution par sévérité", fontsize=14, pad=20)
        
        # Configurer l'axes
        ax.set_aspect('equal')
    
    def _create_vulnerability_timeline(self, fig, position, timeline_data):
        """Crée un graphique linéaire pour la chronologie de découverte des vulnérabilités"""
        ax = fig.add_subplot(position)
        
        # Si la liste est vide, utiliser des données d'exemple
        if not timeline_data:
            dates = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin']
            counts = [2, 5, 3, 8, 6, 8]
            criticals = [0, 1, 0, 2, 0, 1]
        else:
            dates = [entry.get('date', '') for entry in timeline_data]
            counts = [entry.get('total', 0) for entry in timeline_data]
            criticals = [entry.get('critical', 0) for entry in timeline_data]
        
        # Créer le graphique linéaire pour le total
        ax.plot(dates, counts, marker='o', linestyle='-', color='#5ac8fa', linewidth=2, label='Total')
        
        # Créer le graphique linéaire pour les vulnérabilités critiques
        ax.plot(dates, criticals, marker='s', linestyle='--', color=self.vulnerability_colors['critical'], 
               linewidth=2, label='Critique')
        
        # Remplir la zone sous la courbe du total
        ax.fill_between(dates, counts, color='#5ac8fa', alpha=0.1)
        
        # Configurer les axes
        ax.set_xlabel('Période', fontsize=10)
        ax.set_ylabel('Nombre de vulnérabilités', fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=9)
        
        # Ajouter un titre
        ax.set_title("Chronologie des découvertes", fontsize=14)
        
        # Ajouter une légende
        ax.legend(fontsize=9, loc='upper left')
        
        # Ajouter une grille
        ax.grid(linestyle='--', alpha=0.3)
    
    def _create_remediation_plan(self, fig, position, remediation_steps):
        """Crée une section textuelle pour le plan d'action de remédiation"""
        ax = fig.add_subplot(position)
        
        # Si la liste est vide, utiliser des données d'exemple
        if not remediation_steps:
            remediation_steps = [
                {
                    'action': 'Mettre à jour le firmware du routeur',
                    'priority': 'critical',
                    'estimated_time': '30 minutes',
                    'difficulty': 'Facile',
                    'impact': 'Élimine une vulnérabilité critique'
                },
                {
                    'action': 'Changer les mots de passe par défaut',
                    'priority': 'critical',
                    'estimated_time': '20 minutes',
                    'difficulty': 'Facile',
                    'impact': 'Sécurise les appareils IoT vulnérables'
                },
                {
                    'action': 'Activer WPA3',
                    'priority': 'high',
                    'estimated_time': '10 minutes',
                    'difficulty': 'Facile',
                    'impact': 'Renforce la sécurité du WiFi'
                },
                {
                    'action': 'Configurer un réseau invité',
                    'priority': 'medium',
                    'estimated_time': '15 minutes',
                    'difficulty': 'Moyenne',
                    'impact': 'Isole les appareils IoT du réseau principal'
                }
            ]
        
        # Désactiver les axes
        ax.axis('off')
        
        # Ajouter un titre
        ax.text(0.5, 1.05, "PLAN D'ACTION POUR REMÉDIER AUX VULNÉRABILITÉS", ha='center', va='top', 
               fontsize=14, fontweight='bold')
        
        # Ajouter un en-tête pour le tableau
        headers = ['Action', 'Priorité', 'Temps estimé', 'Difficulté', 'Impact']
        column_widths = [0.35, 0.15, 0.15, 0.15, 0.20]
        x_positions = [sum(column_widths[:i]) for i in range(len(headers))]
        
        # Ajouter les en-têtes de colonnes
        for i, header in enumerate(headers):
            ax.text(x_positions[i] + 0.01, 0.95, header, ha='left', va='center', 
                   fontsize=10, fontweight='bold')
        
        # Ajouter une ligne sous les en-têtes
        ax.axhline(y=0.90, xmin=0, xmax=1, color='white', alpha=0.5, linestyle='-')
        
        # Ajouter les données des étapes de remédiation
        y_pos = 0.82
        for step in remediation_steps:
            # Récupérer les données de l'étape
            action = step.get('action', '')
            priority = step.get('priority', 'medium')
            estimated_time = step.get('estimated_time', '')
            difficulty = step.get('difficulty', '')
            impact = step.get('impact', '')
            
            # Obtenir la couleur basée sur la priorité
            color = self.vulnerability_colors.get(priority, '#999999')
            
            # Formater le texte de priorité
            priority_text = priority.capitalize()
            
            # Ajouter les données
            ax.text(x_positions[0] + 0.01, y_pos, action, ha='left', va='center', fontsize=9, fontweight='bold')
            ax.text(x_positions[1] + 0.01, y_pos, priority_text, ha='left', va='center', 
                   fontsize=9, color=color, fontweight='bold')
            ax.text(x_positions[2] + 0.01, y_pos, estimated_time, ha='left', va='center', fontsize=9)
            ax.text(x_positions[3] + 0.01, y_pos, difficulty, ha='left', va='center', fontsize=9)
            ax.text(x_positions[4] + 0.01, y_pos, impact, ha='left', va='center', fontsize=9)
            
            # Ajouter une ligne de séparation
            if step != remediation_steps[-1]:
                ax.axhline(y=y_pos - 0.06, xmin=0, xmax=1, color='white', alpha=0.2, linestyle='-')
            
            # Mettre à jour la position verticale
            y_pos -= 0.13
            
    def generate_preview(self, report_type: str) -> str:
        """
        Génère ou renvoie un aperçu pour un type de rapport spécifique
        
        Args:
            report_type: Type de rapport ('network', 'protocol', 'vulnerability')
            
        Returns:
            str: Chemin vers l'image d'aperçu
        """
        # Vérifier si le type de rapport est valide
        if report_type not in ['network', 'protocol', 'vulnerability']:
            report_type = 'network'
        
        # Définir le chemin vers l'aperçu préexistant (SVG)
        preview_path = os.path.join(PREVIEWS_DIR, f"{report_type}", f"{report_type}_security_preview.svg")
        
        # Si l'aperçu n'existe pas, utiliser l'aperçu par défaut
        if not os.path.exists(preview_path):
            default_preview_path = os.path.join(PREVIEWS_DIR, f"{report_type}_security_preview.svg")
            
            # Si l'aperçu par défaut existe, le retourner
            if os.path.exists(default_preview_path):
                return default_preview_path
            
            # Sinon, générer un nouvel aperçu
            sample_data = self._generate_sample_data(report_type)
            
            # Créer le répertoire d'aperçus si nécessaire
            preview_dir = os.path.join(PREVIEWS_DIR, report_type)
            os.makedirs(preview_dir, exist_ok=True)
            
            # Générer un aperçu et le sauvegarder
            if report_type == 'network':
                return self.generate_network_security_infographic(
                    sample_data.get('network_data', {}),
                    sample_data.get('vulnerability_data', {}),
                    output_filename=f"{report_type}_security_preview.svg",
                    format='svg'
                )
            elif report_type == 'protocol':
                return self.generate_protocol_analysis_infographic(
                    sample_data.get('protocol_data', {}),
                    output_filename=f"{report_type}_security_preview.svg",
                    format='svg'
                )
            elif report_type == 'vulnerability':
                return self.generate_vulnerability_report_infographic(
                    sample_data.get('vulnerability_data', {}),
                    output_filename=f"{report_type}_security_preview.svg",
                    format='svg'
                )
        
        return preview_path
    
    def _generate_sample_data(self, report_type: str) -> Dict[str, Any]:
        """
        Génère des données d'exemple pour les aperçus
        
        Args:
            report_type: Type de rapport ('network', 'protocol', 'vulnerability')
            
        Returns:
            Dict: Données d'exemple pour le type de rapport spécifié
        """
        if report_type == 'network':
            return {
                'network_data': {
                    'overall_score': 72,
                    'protocol_distribution': {
                        'WPA3': 20,
                        'WPA2': 45,
                        'WPA': 20,
                        'WEP': 10,
                        'OPEN': 5
                    },
                    'security_dimensions': {
                        'Authentification': 65,
                        'Chiffrement': 70,
                        'Mises à jour': 50,
                        'Pare-feu': 85,
                        'Segmentation': 90,
                        'Monitoring': 60
                    },
                    'devices': [
                        {'name': 'Caméra IP', 'security_score': 35},
                        {'name': 'Smart TV', 'security_score': 55},
                        {'name': 'Smartphone', 'security_score': 65},
                        {'name': 'Routeur WiFi', 'security_score': 75},
                        {'name': 'Ordinateur portable', 'security_score': 85}
                    ],
                    'security_trend': [
                        {'date': 'Jan', 'score': 54},
                        {'date': 'Fév', 'score': 58},
                        {'date': 'Mar', 'score': 60},
                        {'date': 'Avr', 'score': 65},
                        {'date': 'Mai', 'score': 68},
                        {'date': 'Juin', 'score': 72}
                    ]
                },
                'vulnerability_data': {
                    'vulnerability_types': {
                        'Faible complexité de mot de passe': 12,
                        'Protocoles non sécurisés': 8,
                        'Firmware obsolète': 6,
                        'Authentification faible': 5,
                        'Ports ouverts': 4
                    },
                    'recommendations': [
                        {
                            'priority': 'critical',
                            'description': 'Mettre à jour le firmware du routeur',
                            'details': 'Votre routeur exécute un firmware obsolète contenant des vulnérabilités connues.'
                        },
                        {
                            'priority': 'high',
                            'description': 'Changer les mots de passe par défaut',
                            'details': 'Plusieurs appareils IoT utilisent encore leurs mots de passe par défaut.'
                        },
                        {
                            'priority': 'medium',
                            'description': 'Activer WPA3 sur votre réseau WiFi',
                            'details': 'Passer à WPA3 offre une meilleure protection contre les attaques.'
                        }
                    ]
                }
            }
        elif report_type == 'protocol':
            return {
                'protocol_data': {
                    'average_score': 68,
                    'protocol_distribution': {
                        'WPA3': 20,
                        'WPA2': 45,
                        'WPA': 20,
                        'WEP': 10,
                        'OPEN': 5
                    },
                    'protocols': [
                        {
                            'name': 'WPA3',
                            'security_score': 95,
                            'devices': 3,
                            'vulnerabilities': 1
                        },
                        {
                            'name': 'WPA2',
                            'security_score': 80,
                            'devices': 8,
                            'vulnerabilities': 4
                        },
                        {
                            'name': 'WPA',
                            'security_score': 60,
                            'devices': 4,
                            'vulnerabilities': 7
                        },
                        {
                            'name': 'WEP',
                            'security_score': 30,
                            'devices': 2,
                            'vulnerabilities': 9
                        },
                        {
                            'name': 'OPEN',
                            'security_score': 10,
                            'devices': 1,
                            'vulnerabilities': 12
                        }
                    ],
                    'vulnerability_by_protocol': {
                        'WPA3': {'critical': 0, 'high': 0, 'medium': 1, 'low': 0},
                        'WPA2': {'critical': 0, 'high': 1, 'medium': 2, 'low': 1},
                        'WPA': {'critical': 1, 'high': 2, 'medium': 3, 'low': 1},
                        'WEP': {'critical': 3, 'high': 3, 'medium': 2, 'low': 1},
                        'OPEN': {'critical': 5, 'high': 4, 'medium': 2, 'low': 1}
                    },
                    'protocol_strengths': {
                        'WPA3': {
                            'Authentification': 95,
                            'Chiffrement': 98,
                            'Protection contre les attaques': 90,
                            'Gestion des clés': 92,
                            'Protection vie privée': 85
                        },
                        'WPA2': {
                            'Authentification': 85,
                            'Chiffrement': 90,
                            'Protection contre les attaques': 70,
                            'Gestion des clés': 80,
                            'Protection vie privée': 65
                        }
                    },
                    'recommendations': [
                        {
                            'priority': 'critical',
                            'description': 'Migrer des réseaux WEP et ouverts vers WPA3',
                            'details': 'Les réseaux WEP et ouverts présentent des risques majeurs de sécurité.'
                        },
                        {
                            'priority': 'high',
                            'description': 'Mettre à niveau les réseaux WPA vers WPA2/WPA3',
                            'details': 'WPA contient des vulnérabilités connues et devrait être remplacé.'
                        },
                        {
                            'priority': 'medium',
                            'description': 'Activer le mode de transition WPA3 sur les réseaux WPA2',
                            'details': 'Le mode de transition permet de bénéficier des avantages de WPA3 tout en maintenant la compatibilité.'
                        }
                    ]
                }
            }
        elif report_type == 'vulnerability':
            return {
                'vulnerability_data': {
                    'summary': {
                        'total': 35,
                        'critical': 5,
                        'high': 10,
                        'medium': 15,
                        'low': 5
                    },
                    'critical_vulnerabilities': [
                        {
                            'id': 'CVE-2022-12345',
                            'title': 'Vulnérabilité d\'exécution de code à distance dans le routeur',
                            'severity': 'critical',
                            'affected_devices': 1,
                            'description': 'Permet à un attaquant d\'exécuter du code arbitraire sur le routeur WiFi.'
                        },
                        {
                            'id': 'CVE-2022-23456',
                            'title': 'Faille de sécurité dans le firmware de la caméra IP',
                            'severity': 'critical',
                            'affected_devices': 1,
                            'description': 'Permet à un attaquant d\'accéder au flux vidéo sans authentification.'
                        },
                        {
                            'id': 'CVE-2022-34567',
                            'title': 'Authentification faible sur l\'assistant vocal intelligent',
                            'severity': 'critical',
                            'affected_devices': 1,
                            'description': 'Permet à un attaquant de contourner l\'authentification et de prendre le contrôle.'
                        }
                    ],
                    'severity_distribution': {
                        'Critique': 5,
                        'Élevée': 10,
                        'Moyenne': 15,
                        'Faible': 5
                    },
                    'discovery_timeline': [
                        {'date': 'Jan', 'count': 3},
                        {'date': 'Fév', 'count': 5},
                        {'date': 'Mar', 'count': 8},
                        {'date': 'Avr', 'count': 7},
                        {'date': 'Mai', 'count': 6},
                        {'date': 'Juin', 'count': 6}
                    ],
                    'remediation_plan': [
                        {
                            'id': 'RP-001',
                            'vulnerability_id': 'CVE-2022-12345',
                            'action': 'Mettre à jour le firmware du routeur vers la version 2.1.4',
                            'difficulty': 'Facile',
                            'status': 'À faire',
                            'estimated_time': '30 minutes'
                        },
                        {
                            'id': 'RP-002',
                            'vulnerability_id': 'CVE-2022-23456',
                            'action': 'Appliquer le correctif de sécurité sur la caméra IP',
                            'difficulty': 'Moyenne',
                            'status': 'À faire',
                            'estimated_time': '1 heure'
                        }
                    ]
                }
            }
        else:
            return {}
    
    def copy_export_to_user_downloads(self, source_path: str, filename: Optional[str] = None) -> Dict[str, str]:
        """
        Copie un fichier d'export vers le répertoire de téléchargements de l'utilisateur
        et renvoie les métadonnées du fichier
        
        Args:
            source_path: Chemin vers le fichier d'export
            filename: Nom de fichier personnalisé (optionnel)
            
        Returns:
            Dict: Métadonnées du fichier (chemin, nom, taille, date)
        """
        if not os.path.exists(source_path):
            return {
                'success': False,
                'error': 'Fichier source introuvable'
            }
        
        # Obtenir le nom du fichier d'origine si aucun n'est spécifié
        if not filename:
            filename = os.path.basename(source_path)
        
        # Créer le répertoire de téléchargements s'il n'existe pas
        downloads_dir = os.path.join(EXPORT_DIR, 'downloads')
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Chemin de destination
        destination_path = os.path.join(downloads_dir, filename)
        
        # Copier le fichier
        try:
            shutil.copy2(source_path, destination_path)
            
            # Obtenir les métadonnées du fichier
            file_stats = os.stat(destination_path)
            file_size = file_stats.st_size
            file_size_readable = self._get_readable_file_size(file_size)
            modification_time = datetime.fromtimestamp(file_stats.st_mtime)
            
            return {
                'success': True,
                'path': destination_path,
                'filename': filename,
                'size': file_size_readable,
                'date': modification_time.strftime('%d/%m/%Y %H:%M'),
                'format': os.path.splitext(filename)[1][1:].upper()
            }
        except Exception as e:
            logger.error(f"Erreur lors de la copie du fichier: {str(e)}")
            return {
                'success': False,
                'error': f"Erreur lors de la copie du fichier: {str(e)}"
            }
    
    def _get_readable_file_size(self, size_in_bytes: int) -> str:
        """
        Convertit une taille en octets en une chaîne de caractères lisible
        
        Args:
            size_in_bytes: Taille en octets
            
        Returns:
            str: Taille lisible avec unité
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024.0 or unit == 'TB':
                break
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.2f} {unit}"


# Exemple d'utilisation
if __name__ == "__main__":
    generator = InfographicGenerator()
    
    # Exemple de données de réseau
    network_data = {
        'overall_score': 72,
        'protocol_distribution': {
            'WPA3': 1,
            'WPA2': 3,
            'WPA': 0,
            'WEP': 1,
            'OPEN': 1
        },
        'security_dimensions': {
            'Authentification': 65,
            'Chiffrement': 70,
            'Mises à jour': 50,
            'Pare-feu': 85,
            'Segmentation': 90,
            'Monitoring': 60
        },
        'devices': [
            {'name': 'Caméra IP', 'security_score': 35},
            {'name': 'Smart TV', 'security_score': 55},
            {'name': 'Smartphone', 'security_score': 65},
            {'name': 'Routeur WiFi', 'security_score': 75},
            {'name': 'Ordinateur portable', 'security_score': 85}
        ],
        'security_trend': [
            {'date': 'Jan', 'score': 54},
            {'date': 'Fév', 'score': 58},
            {'date': 'Mar', 'score': 60},
            {'date': 'Avr', 'score': 65},
            {'date': 'Mai', 'score': 68},
            {'date': 'Juin', 'score': 72}
        ]
    }
    
    # Exemple de données de vulnérabilité
    vulnerability_data = {
        'vulnerability_types': {
            'firmware_outdated': 8,
            'weak_password': 6,
            'open_ports': 5,
            'protocol_weakness': 5,
            'missing_updates': 4,
            'default_credentials': 4
        },
        'recommendations': [
            {
                'priority': 'critical',
                'description': 'Mettre à jour le firmware du routeur',
                'details': 'Votre routeur exécute un firmware obsolète contenant des vulnérabilités connues.'
            },
            {
                'priority': 'high',
                'description': 'Changer les mots de passe par défaut',
                'details': 'Plusieurs appareils IoT utilisent encore leurs mots de passe par défaut.'
            },
            {
                'priority': 'medium',
                'description': 'Activer WPA3 sur votre réseau WiFi',
                'details': 'Passer à WPA3 offre une meilleure protection contre les attaques.'
            }
        ]
    }
    
    # Générer une infographie
    output_path = generator.generate_network_security_infographic(
        network_data, vulnerability_data
    )
    
    print(f"Infographie générée: {output_path}")