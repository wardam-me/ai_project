"""
Module de gestion des clones IA pour NetSecure Pro
Permet de créer, gérer et surveiller plusieurs instances d'IA spécialisées
"""
import json
import logging
import os
import time
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from module_IA import SecurityAnalysisAI

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable singleton pour le gestionnaire de clones
_clone_manager_instance = None

class AIClone:
    """Représente une instance clonée d'intelligence artificielle avec des paramètres spécifiques"""
    
    def __init__(self, name: str, specialization: str, learning_rate: float = 0.1, 
                 confidence_threshold: float = 0.7, clone_id: Optional[str] = None):
        """
        Initialise un clone d'IA
        
        Args:
            name: Nom du clone
            specialization: Spécialisation du clone (network, protocol, vulnerability, general)
            learning_rate: Taux d'apprentissage (0.01 à 1.0)
            confidence_threshold: Seuil de confiance pour les prédictions (0.0 à 1.0)
            clone_id: Identifiant unique (généré automatiquement si None)
        """
        self.clone_id = clone_id or str(uuid.uuid4())
        self.name = name
        self.specialization = specialization
        self.learning_rate = max(0.01, min(1.0, learning_rate))  # Limiter entre 0.01 et 1.0
        self.confidence_threshold = max(0.0, min(1.0, confidence_threshold))  # Limiter entre 0 et 1
        self.creation_date = datetime.now().isoformat()
        self.last_activity = self.creation_date
        self.status = "active"  # active, paused, training, stopped
        self.version = "1.0.0"
        self.performance_metrics = {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "requests_processed": 0,
            "average_response_time": 0.0
        }
        self.training_sessions = []
        
        # Créer l'instance de l'IA sous-jacente
        self.ai_engine = SecurityAnalysisAI()
        logger.info(f"Clone IA '{name}' créé avec ID {self.clone_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le clone en dictionnaire pour la sérialisation"""
        return {
            "clone_id": self.clone_id,
            "name": self.name,
            "specialization": self.specialization,
            "learning_rate": self.learning_rate,
            "confidence_threshold": self.confidence_threshold,
            "creation_date": self.creation_date,
            "last_activity": self.last_activity,
            "status": self.status,
            "version": self.version,
            "performance_metrics": self.performance_metrics,
            "training_sessions": self.training_sessions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIClone':
        """Crée un clone à partir d'un dictionnaire"""
        clone = cls(
            name=data["name"],
            specialization=data["specialization"],
            learning_rate=data["learning_rate"],
            confidence_threshold=data["confidence_threshold"],
            clone_id=data["clone_id"]
        )
        clone.creation_date = data["creation_date"]
        clone.last_activity = data["last_activity"]
        clone.status = data["status"]
        clone.version = data["version"]
        clone.performance_metrics = data["performance_metrics"]
        clone.training_sessions = data["training_sessions"]
        return clone
    
    def update_activity(self):
        """Met à jour le timestamp de dernière activité"""
        self.last_activity = datetime.now().isoformat()
    
    def process_request(self, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une demande et retourne les résultats
        
        Args:
            request_type: Type de demande (analyze_network, analyze_protocol, etc.)
            data: Données à analyser
            
        Returns:
            Dict: Résultats de l'analyse avec des métriques additionnelles
        """
        start_time = time.time()
        self.update_activity()
        
        # Simuler une durée de traitement
        processing_time = 0.05 + (0.1 * (1 - self.learning_rate))
        time.sleep(processing_time)
        
        # Traiter la demande selon le type
        result = self._process_by_type(request_type, data)
        
        # Mettre à jour les métriques
        elapsed_time = time.time() - start_time
        self.performance_metrics["requests_processed"] += 1
        self.performance_metrics["average_response_time"] = (
            (self.performance_metrics["average_response_time"] * 
             (self.performance_metrics["requests_processed"] - 1) + 
             elapsed_time) / self.performance_metrics["requests_processed"]
        )
        
        # Ajouter des métriques de traitement
        result_with_metrics = {
            "result": result,
            "processing_time": elapsed_time,
            "confidence": self._calculate_confidence(request_type, data),
            "clone_info": {
                "clone_id": self.clone_id,
                "name": self.name,
                "specialization": self.specialization,
                "status": self.status
            }
        }
        
        return result_with_metrics
    
    def _process_by_type(self, request_type: str, data: Dict[str, Any]) -> Any:
        """Traite une demande selon son type"""
        # Vérifier si le clone est actif
        if self.status != "active":
            return {"error": f"Clone inactif (statut: {self.status})"}
        
        # Analyse de réseau
        if request_type == "analyze_network":
            return {
                "network_analysis": self.ai_engine.generate_network_security_analysis(
                    data.get("overall_score", 50),
                    data.get("device_count", 0),
                    data.get("recommendation_count", 0)
                ),
                "highlight": self.ai_engine.generate_network_highlight(data)
            }
        
        # Analyse de protocole
        elif request_type == "analyze_protocol":
            return {
                "protocol_analysis": self.ai_engine.analyze_protocol_security(
                    data.get("protocol_name", ""),
                    data.get("security_score", 50)
                ),
                "recommendation": self.ai_engine.generate_protocol_recommendation(
                    data.get("recommendation", {})
                ),
                "highlight": self.ai_engine.generate_protocol_highlight(data)
            }
        
        # Analyse de vulnérabilité
        elif request_type == "analyze_vulnerability":
            return {
                "vulnerability_analysis": self.ai_engine.analyze_vulnerability(
                    data.get("vuln_id", ""),
                    data.get("vuln_title", ""),
                    data.get("vuln_severity", "medium")
                ),
                "remediation": self.ai_engine.generate_remediation_recommendation(
                    data.get("title", ""),
                    data.get("difficulty", "medium")
                ),
                "highlight": self.ai_engine.generate_vulnerability_highlight(data)
            }
        
        # Analyse de tendances
        elif request_type == "analyze_trends":
            return {
                "predicted_trend": self.ai_engine.predict_security_trend(
                    data.get("trend_data", [])
                )
            }
        
        # Type de demande inconnu
        else:
            return {"error": f"Type de demande non pris en charge: {request_type}"}
    
    def _calculate_confidence(self, request_type: str, data: Dict[str, Any]) -> float:
        """Calcule un niveau de confiance pour les résultats (simulé)"""
        # Base de confiance basée sur le seuil configuré
        base_confidence = self.confidence_threshold
        
        # Bonus pour la spécialisation
        specialization_match = {
            "network": ["analyze_network", "analyze_trends"],
            "protocol": ["analyze_protocol"],
            "vulnerability": ["analyze_vulnerability"],
            "general": ["analyze_network", "analyze_protocol", "analyze_vulnerability", "analyze_trends"]
        }
        
        specialization_bonus = 0.1 if request_type in specialization_match.get(self.specialization, []) else 0
        
        # Pénalité pour les données incomplètes
        data_completeness = min(1.0, len(data) / 5)  # Estimation simplifiée de la complétude
        
        # Calculer la confiance finale (limitée à 0.99)
        confidence = min(0.99, base_confidence + specialization_bonus) * data_completeness
        
        return confidence
    
    def start_training(self, training_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Démarre une session d'entraînement pour améliorer les performances
        
        Args:
            training_params: Paramètres d'entraînement
            
        Returns:
            Dict: Résultat de l'initialisation d'entraînement
        """
        if self.status == "training":
            return {"error": "Le clone est déjà en phase d'entraînement"}
        
        # Sauvegarder le statut précédent pour la restauration
        previous_status = self.status
        self.status = "training"
        self.update_activity()
        
        # Créer une nouvelle session d'entraînement
        training_session = {
            "session_id": str(uuid.uuid4()),
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "params": training_params,
            "status": "in_progress",
            "results": {}
        }
        
        self.training_sessions.append(training_session)
        
        return {
            "status": "training_started",
            "session_id": training_session["session_id"],
            "previous_status": previous_status
        }
    
    def complete_training(self, session_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Termine une session d'entraînement et applique les améliorations
        
        Args:
            session_id: ID de la session d'entraînement
            results: Résultats de l'entraînement
            
        Returns:
            Dict: Résultat de la finalisation d'entraînement
        """
        # Trouver la session d'entraînement
        for session in self.training_sessions:
            if session["session_id"] == session_id and session["status"] == "in_progress":
                session["end_time"] = datetime.now().isoformat()
                session["status"] = "completed"
                session["results"] = results
                
                # Mettre à jour les métriques de performance
                if "performance_metrics" in results:
                    for key, value in results["performance_metrics"].items():
                        if key in self.performance_metrics:
                            self.performance_metrics[key] = value
                
                # Incrémenter la version
                version_parts = self.version.split('.')
                version_parts[-1] = str(int(version_parts[-1]) + 1)
                self.version = '.'.join(version_parts)
                
                # Restaurer le statut à actif
                self.status = "active"
                self.update_activity()
                
                return {
                    "status": "training_completed",
                    "session_id": session_id,
                    "version": self.version
                }
        
        return {"error": f"Session d'entraînement non trouvée ou non active: {session_id}"}


class AICloneManager:
    """Gestionnaire de clones d'IA pour créer et administrer plusieurs instances d'IA"""
    
    def __init__(self, config_path: str = 'config/ai_clones.json'):
        """
        Initialise le gestionnaire de clones IA
        
        Args:
            config_path: Chemin vers le fichier de configuration des clones
        """
        self.config_path = config_path
        self.clones = {}  # Dictionnaire des clones par ID
        self.load_clones()
        
        # Créer un clone par défaut si aucun n'existe
        if not self.clones:
            self.create_default_clone()
    
    def load_clones(self) -> None:
        """Charge les clones depuis le fichier de configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    clones_data = json.load(f)
                    
                for clone_data in clones_data:
                    try:
                        clone = AIClone.from_dict(clone_data)
                        self.clones[clone.clone_id] = clone
                    except Exception as e:
                        logger.error(f"Erreur lors du chargement du clone: {e}")
                
                logger.info(f"{len(self.clones)} clones chargés depuis {self.config_path}")
            else:
                logger.info(f"Fichier de configuration {self.config_path} introuvable, création d'un nouveau fichier")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des clones: {e}")
    
    def save_clones(self) -> None:
        """Sauvegarde les clones dans le fichier de configuration"""
        try:
            # Créer le répertoire config s'il n'existe pas
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            clones_data = [clone.to_dict() for clone in self.clones.values()]
            
            with open(self.config_path, 'w') as f:
                json.dump(clones_data, f, indent=2)
            
            logger.info(f"{len(self.clones)} clones sauvegardés dans {self.config_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des clones: {e}")
    
    def create_default_clone(self) -> AIClone:
        """Crée un clone par défaut"""
        default_clone = AIClone(
            name="Clone IA Principal",
            specialization="general",
            learning_rate=0.5,
            confidence_threshold=0.7
        )
        self.clones[default_clone.clone_id] = default_clone
        self.save_clones()
        return default_clone
    
    def create_clone(self, name: str, specialization: str = "general", 
                    learning_rate: float = 0.5, confidence_threshold: float = 0.7) -> AIClone:
        """
        Crée un nouveau clone d'IA
        
        Args:
            name: Nom du clone
            specialization: Spécialisation du clone
            learning_rate: Taux d'apprentissage
            confidence_threshold: Seuil de confiance
            
        Returns:
            AIClone: Nouvelle instance de clone
        """
        clone = AIClone(
            name=name,
            specialization=specialization,
            learning_rate=learning_rate,
            confidence_threshold=confidence_threshold
        )
        self.clones[clone.clone_id] = clone
        self.save_clones()
        return clone
    
    def get_clone(self, clone_id: str) -> Optional[AIClone]:
        """Récupère un clone par son ID"""
        return self.clones.get(clone_id)
    
    def get_all_clones(self) -> List[Dict[str, Any]]:
        """Récupère la liste de tous les clones"""
        return [clone.to_dict() for clone in self.clones.values()]
    
    def update_clone(self, clone_id: str, updates: Dict[str, Any]) -> Optional[AIClone]:
        """
        Met à jour les propriétés d'un clone
        
        Args:
            clone_id: ID du clone à mettre à jour
            updates: Dictionnaire des propriétés à mettre à jour
            
        Returns:
            AIClone: Clone mis à jour ou None si non trouvé
        """
        clone = self.get_clone(clone_id)
        if not clone:
            return None
        
        # Mettre à jour les propriétés
        if "name" in updates:
            clone.name = updates["name"]
        
        if "learning_rate" in updates:
            clone.learning_rate = max(0.01, min(1.0, float(updates["learning_rate"])))
        
        if "confidence_threshold" in updates:
            clone.confidence_threshold = max(0.0, min(1.0, float(updates["confidence_threshold"])))
        
        if "status" in updates and updates["status"] in ["active", "paused", "stopped"]:
            clone.status = updates["status"]
        
        clone.update_activity()
        self.save_clones()
        return clone
    
    def delete_clone(self, clone_id: str) -> bool:
        """
        Supprime un clone
        
        Args:
            clone_id: ID du clone à supprimer
            
        Returns:
            bool: True si supprimé avec succès, False sinon
        """
        if clone_id in self.clones:
            del self.clones[clone_id]
            self.save_clones()
            return True
        return False
    
    def process_request(self, request_type: str, data: Dict[str, Any], 
                        clone_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Traite une demande avec un clone spécifique ou le plus approprié
        
        Args:
            request_type: Type de demande
            data: Données à analyser
            clone_id: ID du clone à utiliser (optionnel)
            
        Returns:
            Dict: Résultats de l'analyse
        """
        # Si un clone spécifique est demandé, l'utiliser
        if clone_id:
            clone = self.get_clone(clone_id)
            if not clone:
                return {"error": f"Clone non trouvé: {clone_id}"}
            return clone.process_request(request_type, data)
        
        # Sinon, trouver le clone le plus approprié
        best_clone = self._find_best_clone_for_request(request_type)
        if not best_clone:
            return {"error": "Aucun clone actif disponible"}
        
        return best_clone.process_request(request_type, data)
    
    def _find_best_clone_for_request(self, request_type: str) -> Optional[AIClone]:
        """Trouve le meilleur clone pour traiter une demande spécifique"""
        specialization_map = {
            "analyze_network": "network",
            "analyze_protocol": "protocol",
            "analyze_vulnerability": "vulnerability",
            "analyze_trends": "network"
        }
        
        target_specialization = specialization_map.get(request_type)
        
        # Chercher un clone spécialisé actif
        specialized_clones = []
        general_clones = []
        
        for clone in self.clones.values():
            if clone.status != "active":
                continue
                
            if clone.specialization == target_specialization:
                specialized_clones.append(clone)
            elif clone.specialization == "general":
                general_clones.append(clone)
        
        # Préférer un clone spécialisé
        if specialized_clones:
            # Trier par niveau de confiance
            specialized_clones.sort(key=lambda c: c.confidence_threshold, reverse=True)
            return specialized_clones[0]
        
        # Sinon utiliser un clone général
        if general_clones:
            general_clones.sort(key=lambda c: c.confidence_threshold, reverse=True)
            return general_clones[0]
        
        # En dernier recours, prendre n'importe quel clone actif
        active_clones = [c for c in self.clones.values() if c.status == "active"]
        if active_clones:
            return active_clones[0]
        
        return None
    
    def get_clone_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques globales sur tous les clones"""
        total_clones = len(self.clones)
        active_clones = sum(1 for c in self.clones.values() if c.status == "active")
        paused_clones = sum(1 for c in self.clones.values() if c.status == "paused")
        training_clones = sum(1 for c in self.clones.values() if c.status == "training")
        stopped_clones = sum(1 for c in self.clones.values() if c.status == "stopped")
        
        specializations = {}
        for clone in self.clones.values():
            specializations[clone.specialization] = specializations.get(clone.specialization, 0) + 1
        
        total_requests = sum(c.performance_metrics["requests_processed"] for c in self.clones.values())
        avg_response_time = 0
        if total_requests > 0:
            total_time = sum(c.performance_metrics["average_response_time"] * c.performance_metrics["requests_processed"] 
                           for c in self.clones.values())
            avg_response_time = total_time / total_requests
        
        return {
            "total_clones": total_clones,
            "status": {
                "active": active_clones,
                "paused": paused_clones,
                "training": training_clones,
                "stopped": stopped_clones
            },
            "specializations": specializations,
            "total_requests_processed": total_requests,
            "average_response_time": avg_response_time
        }


# Singleton pour l'accès global au gestionnaire de clones
_clone_manager_instance = None

def get_clone_manager() -> AICloneManager:
    """Récupère l'instance singleton du gestionnaire de clones"""
    global _clone_manager_instance
    if _clone_manager_instance is None:
        _clone_manager_instance = AICloneManager()
    return _clone_manager_instance