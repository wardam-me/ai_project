"""
Module d'assistance IA pour enrichir les données des infographies de sécurité
"""
import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import conditionnel du module IA si disponible
AI_MODULE_AVAILABLE = False
SecurityAnalysisAI = None

try:
    from module_IA import SecurityAnalysisAI
    AI_MODULE_AVAILABLE = True
    logger.info("Module SecurityAnalysisAI importé avec succès")
except ImportError:
    # Classe simulée pour éviter les erreurs
    class SecurityAnalysisAI:
        def __init__(self):
            logger.warning("Utilisation d'une classe SecurityAnalysisAI simulée")
        
        def is_available(self):
            return False
        
        # Méthodes simulées pour éviter les erreurs
        def generate_recommendation_insight(self, rec):
            return "Insight simulé pour les recommandations de sécurité"
            
        def analyze_device_security(self, device_type, device_name, security_score):
            return f"Analyse simulée pour l'appareil {device_name}"
            
        def predict_security_trend(self, trend_data):
            return [{"date": "Futur", "score": 75, "predicted": True}]
            
        def generate_network_security_analysis(self, overall_score, device_count, rec_count):
            return "Analyse simulée du réseau"
            
        def analyze_protocol_security(self, protocol_name, security_score):
            return f"Analyse simulée du protocole {protocol_name}"
            
        def generate_protocol_recommendation(self, rec):
            return "Recommandation simulée pour les protocoles"
            
        def generate_protocol_comparison(self, protocol_names):
            return {"summary": "Comparaison simulée", "protocols": {}}
            
        def analyze_vulnerability(self, vuln_id, vuln_title, vuln_severity):
            return f"Analyse simulée de la vulnérabilité {vuln_id}"
            
        def generate_remediation_recommendation(self, title, difficulty):
            return "Recommandation simulée pour la remédiation"
            
        def analyze_vulnerability_trend(self, date, count, description):
            return "Analyse simulée des tendances de vulnérabilité"
            
        def generate_advanced_security_recommendations(self, total_vulns, critical_vulns):
            return [{"title": "Recommandation simulée", "description": "Description", "ai_confidence": 90}]
            
        def generate_network_highlight(self, data):
            return "Point fort simulé pour le réseau"
            
        def generate_protocol_highlight(self, data):
            return "Point fort simulé pour les protocoles"
            
        def generate_vulnerability_highlight(self, data):
            return "Point fort simulé pour les vulnérabilités"
    
    logger.warning("Module module_IA non disponible, utilisation d'une version simulée")

class AIInfographicAssistant:
    """
    Assistant d'infographie alimenté par l'IA pour enrichir les données
    et améliorer les rapports de sécurité
    """
    
    def __init__(self, use_cache: bool = True, cache_dir: str = 'config'):
        """
        Initialise l'assistant d'infographie IA
        
        Args:
            use_cache: Utiliser le cache pour les requêtes fréquentes (par défaut: True)
            cache_dir: Répertoire où stocker les données en cache
        """
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, 'ai_insights_cache.json')
        self.security_ai = None
        self.cache = {}
        
        # Initialiser le module IA si disponible
        if AI_MODULE_AVAILABLE:
            try:
                self.security_ai = SecurityAnalysisAI()
                logger.info("Module IA chargé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du module IA: {e}")
        else:
            logger.warning("Module IA non disponible, fonctionnant en mode dégradé")
        
        # Charger le cache si existant et demandé
        if use_cache:
            self._load_cache()
    
    def _load_cache(self) -> None:
        """Charge le cache depuis le fichier"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"Cache chargé depuis {self.cache_file}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du cache: {e}")
                self.cache = {}
    
    def _save_cache(self) -> None:
        """Enregistre le cache dans le fichier"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            logger.info(f"Cache enregistré dans {self.cache_file}")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du cache: {e}")
    
    def _get_cache_key(self, data_type: str, data_hash: str) -> str:
        """
        Génère une clé de cache unique pour les données
        
        Args:
            data_type: Type de données (network, protocol, vulnerability)
            data_hash: Hash ou identifiant unique des données
            
        Returns:
            str: Clé de cache
        """
        return f"{data_type}_{data_hash}"
    
    def _generate_data_hash(self, data: Dict[str, Any]) -> str:
        """
        Génère un hash simple pour les données
        
        Args:
            data: Données à hasher
            
        Returns:
            str: Hash des données (simplifié)
        """
        # Version simplifiée, en production utiliser un hash plus robuste
        try:
            # Utiliser uniquement quelques champs clés pour le hash
            key_items = []
            
            if 'report_id' in data:
                key_items.append(f"id:{data['report_id']}")
            
            if 'generated_at' in data:
                key_items.append(f"date:{data['generated_at']}")
            
            if 'devices' in data and isinstance(data['devices'], list):
                key_items.append(f"devices:{len(data['devices'])}")
            
            if 'vulnerabilities' in data and isinstance(data['vulnerabilities'], list):
                key_items.append(f"vulns:{len(data['vulnerabilities'])}")
            
            # Si aucune clé spécifique n'est trouvée, utiliser un timestamp
            if not key_items:
                key_items.append(f"ts:{datetime.now().timestamp()}")
            
            return "_".join(key_items)
        except Exception as e:
            logger.error(f"Erreur lors de la génération du hash: {e}")
            return f"fallback_{datetime.now().timestamp()}"
    
    def is_available(self) -> bool:
        """
        Vérifie si l'assistant IA est disponible et fonctionnel
        
        Returns:
            bool: True si l'assistant est disponible, False sinon
        """
        return self.security_ai is not None and AI_MODULE_AVAILABLE
    
    def enrich_network_security_data(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données de sécurité réseau avec des insights IA
        
        Args:
            network_data: Données de sécurité réseau
            
        Returns:
            Dict[str, Any]: Données enrichies
        """
        if not self.is_available():
            logger.warning("Module IA non disponible, données non enrichies")
            return network_data
        
        try:
            # Vérifier le cache
            data_hash = self._generate_data_hash(network_data)
            cache_key = self._get_cache_key('network', data_hash)
            
            if self.use_cache and cache_key in self.cache:
                logger.info(f"Utilisation des données en cache pour {cache_key}")
                return self.cache[cache_key]
            
            # Créer une copie pour ne pas modifier l'original
            enriched_data = network_data.copy()
            
            # Enrichir les recommandations
            if 'recommendations' in enriched_data and isinstance(enriched_data['recommendations'], list):
                for i, rec in enumerate(enriched_data['recommendations']):
                    if i < len(enriched_data['recommendations']):
                        ai_insight = self.security_ai.generate_recommendation_insight(rec)
                        if ai_insight:
                            enriched_data['recommendations'][i]['ai_insight'] = ai_insight
            
            # Enrichir les données des appareils
            if 'devices' in enriched_data and isinstance(enriched_data['devices'], list):
                for i, device in enumerate(enriched_data['devices']):
                    if i < len(enriched_data['devices']):
                        device_type = device.get('type', '')
                        device_name = device.get('name', '')
                        security_score = device.get('security_score', 0)
                        
                        ai_insight = self.security_ai.analyze_device_security(
                            device_type, device_name, security_score
                        )
                        
                        if ai_insight:
                            enriched_data['devices'][i]['ai_security_analysis'] = ai_insight
            
            # Ajouter des tendances de sécurité prédictives
            if 'security_trend' in enriched_data:
                predictive_trend = self.security_ai.predict_security_trend(enriched_data['security_trend'])
                if predictive_trend:
                    enriched_data['predictive_security_trend'] = predictive_trend
            
            # Ajouter une analyse globale
            enriched_data['ai_analysis'] = self.security_ai.generate_network_security_analysis(
                enriched_data.get('overall_score', 0),
                len(enriched_data.get('devices', [])),
                len(enriched_data.get('recommendations', []))
            )
            
            # Sauvegarder dans le cache
            if self.use_cache:
                self.cache[cache_key] = enriched_data
                self._save_cache()
            
            logger.info("Données de sécurité réseau enrichies avec succès")
            return enriched_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enrichissement des données réseau: {e}")
            return network_data
    
    def enrich_protocol_analysis_data(self, protocol_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données d'analyse de protocole avec des insights IA
        
        Args:
            protocol_data: Données d'analyse de protocole
            
        Returns:
            Dict[str, Any]: Données enrichies
        """
        if not self.is_available():
            logger.warning("Module IA non disponible, données non enrichies")
            return protocol_data
        
        try:
            # Vérifier le cache
            data_hash = self._generate_data_hash(protocol_data)
            cache_key = self._get_cache_key('protocol', data_hash)
            
            if self.use_cache and cache_key in self.cache:
                logger.info(f"Utilisation des données en cache pour {cache_key}")
                return self.cache[cache_key]
            
            # Créer une copie pour ne pas modifier l'original
            enriched_data = protocol_data.copy()
            
            # Enrichir les protocoles
            if 'protocols' in enriched_data and isinstance(enriched_data['protocols'], list):
                for i, protocol in enumerate(enriched_data['protocols']):
                    if i < len(enriched_data['protocols']):
                        protocol_name = protocol.get('name', '')
                        security_score = protocol.get('security', 0)
                        
                        ai_insight = self.security_ai.analyze_protocol_security(
                            protocol_name, security_score
                        )
                        
                        if ai_insight:
                            enriched_data['protocols'][i]['ai_security_analysis'] = ai_insight
            
            # Enrichir les recommandations
            if 'recommendations' in enriched_data and isinstance(enriched_data['recommendations'], list):
                for i, rec in enumerate(enriched_data['recommendations']):
                    if i < len(enriched_data['recommendations']):
                        ai_insight = self.security_ai.generate_protocol_recommendation(rec)
                        if ai_insight:
                            enriched_data['recommendations'][i]['ai_insight'] = ai_insight
            
            # Ajouter une analyse comparative des protocoles
            if 'protocols' in enriched_data and isinstance(enriched_data['protocols'], list):
                protocol_comparison = self.security_ai.generate_protocol_comparison(
                    [p.get('name', '') for p in enriched_data['protocols']]
                )
                if protocol_comparison:
                    enriched_data['ai_protocol_comparison'] = protocol_comparison
            
            # Sauvegarder dans le cache
            if self.use_cache:
                self.cache[cache_key] = enriched_data
                self._save_cache()
            
            logger.info("Données d'analyse de protocole enrichies avec succès")
            return enriched_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enrichissement des données de protocole: {e}")
            return protocol_data
    
    def enrich_vulnerability_data(self, vulnerability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données de vulnérabilité avec des insights IA
        
        Args:
            vulnerability_data: Données de vulnérabilité
            
        Returns:
            Dict[str, Any]: Données enrichies
        """
        if not self.is_available():
            logger.warning("Module IA non disponible, données non enrichies")
            return vulnerability_data
        
        try:
            # Vérifier le cache
            data_hash = self._generate_data_hash(vulnerability_data)
            cache_key = self._get_cache_key('vulnerability', data_hash)
            
            if self.use_cache and cache_key in self.cache:
                logger.info(f"Utilisation des données en cache pour {cache_key}")
                return self.cache[cache_key]
            
            # Créer une copie pour ne pas modifier l'original
            enriched_data = vulnerability_data.copy()
            
            # Enrichir les vulnérabilités critiques
            if 'critical_vulnerabilities' in enriched_data and isinstance(enriched_data['critical_vulnerabilities'], list):
                for i, vuln in enumerate(enriched_data['critical_vulnerabilities']):
                    if i < len(enriched_data['critical_vulnerabilities']):
                        vuln_id = vuln.get('id', '')
                        vuln_title = vuln.get('title', '')
                        vuln_severity = vuln.get('severity', 'medium')
                        
                        ai_insights = self.security_ai.analyze_vulnerability(
                            vuln_id, vuln_title, vuln_severity
                        )
                        
                        if ai_insights:
                            enriched_data['critical_vulnerabilities'][i]['ai_insights'] = ai_insights
            
            # Enrichir le plan de remédiation
            if 'remediation_plan' in enriched_data and isinstance(enriched_data['remediation_plan'], list):
                for i, step in enumerate(enriched_data['remediation_plan']):
                    if i < len(enriched_data['remediation_plan']):
                        title = step.get('title', '')
                        difficulty = step.get('difficulty', 'medium')
                        
                        ai_recommendation = self.security_ai.generate_remediation_recommendation(
                            title, difficulty
                        )
                        
                        if ai_recommendation:
                            enriched_data['remediation_plan'][i]['ai_recommendation'] = ai_recommendation
            
            # Enrichir la chronologie de découverte
            if 'discovery_timeline' in enriched_data and isinstance(enriched_data['discovery_timeline'], list):
                for i, entry in enumerate(enriched_data['discovery_timeline']):
                    if i < len(enriched_data['discovery_timeline']) and i % 2 == 0:  # Une entrée sur deux pour limiter
                        date = entry.get('date', '')
                        count = entry.get('vulnerabilities', 0)
                        description = entry.get('description', '')
                        
                        ai_insights = self.security_ai.analyze_vulnerability_trend(
                            date, count, description
                        )
                        
                        if ai_insights:
                            enriched_data['discovery_timeline'][i]['ai_insights'] = ai_insights
            
            # Ajouter des recommandations avancées
            enriched_data['ai_advanced_recommendations'] = self.security_ai.generate_advanced_security_recommendations(
                enriched_data.get('summary', {}).get('total', 0),
                enriched_data.get('summary', {}).get('critical', 0)
            )
            
            # Sauvegarder dans le cache
            if self.use_cache:
                self.cache[cache_key] = enriched_data
                self._save_cache()
            
            logger.info("Données de vulnérabilité enrichies avec succès")
            return enriched_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enrichissement des données de vulnérabilité: {e}")
            return vulnerability_data
    
    def generate_ai_highlight(self, data_type: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Génère un point fort/insight principal sur les données pour mettre en avant
        
        Args:
            data_type: Type de données (network, protocol, vulnerability)
            data: Données à analyser
            
        Returns:
            Optional[str]: Insight principal ou None si non disponible
        """
        if not self.is_available():
            return None
        
        try:
            if data_type == 'network':
                return self.security_ai.generate_network_highlight(data)
            elif data_type == 'protocol':
                return self.security_ai.generate_protocol_highlight(data)
            elif data_type == 'vulnerability':
                return self.security_ai.generate_vulnerability_highlight(data)
            else:
                logger.warning(f"Type de données non pris en charge: {data_type}")
                return None
        except Exception as e:
            logger.error(f"Erreur lors de la génération du point fort: {e}")
            return None
    
    def clear_cache(self) -> bool:
        """
        Efface le cache d'insights IA
        
        Returns:
            bool: True si le cache a été effacé avec succès, False sinon
        """
        try:
            self.cache = {}
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            logger.info("Cache effacé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'effacement du cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Renvoie des statistiques sur le cache
        
        Returns:
            Dict[str, Any]: Statistiques du cache
        """
        stats = {
            'cache_size': len(self.cache),
            'cache_file_exists': os.path.exists(self.cache_file),
            'cache_types': {}
        }
        
        # Compter les types de données en cache
        for key in self.cache.keys():
            data_type = key.split('_')[0] if '_' in key else 'unknown'
            if data_type in stats['cache_types']:
                stats['cache_types'][data_type] += 1
            else:
                stats['cache_types'][data_type] = 1
        
        return stats