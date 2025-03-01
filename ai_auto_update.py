#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de mise à jour automatique du module IA pour NetSecure Pro
Ce script surveille et met à jour le modèle IA sans interrompre la production
"""

import os
import sys
import time
import json
import logging
import hashlib
import threading
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instance/ai_auto_update.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai_auto_update")

class AIAutoUpdater:
    """
    Gestionnaire de mise à jour automatique pour le module IA
    Fonctionne en arrière-plan sans interrompre la production
    """
    
    # Chemins
    MODEL_PATH = "modele_ia.h5"
    MODEL_BACKUP_DIR = "instance/backups"
    METRICS_FILE = "instance/ai_update_metrics.json"
    
    # Paramètres
    UPDATE_INTERVAL = 3600  # 1 heure entre les vérifications de mise à jour
    MAX_BACKUPS = 5  # Nombre maximum de sauvegardes à conserver
    
    def __init__(self):
        """
        Initialisation du gestionnaire de mise à jour
        """
        # Créer les répertoires s'ils n'existent pas
        os.makedirs(self.MODEL_BACKUP_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(self.METRICS_FILE), exist_ok=True)
        
        # Initialiser les variables d'état
        self.running = False
        self.update_thread = None
        self.last_update_time = None
        
        # Charger ou initialiser les métriques
        self.metrics = self._load_metrics()
        
        logger.info("Gestionnaire de mise à jour IA initialisé")
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Charge les métriques de mise à jour précédentes"""
        if os.path.exists(self.METRICS_FILE):
            try:
                with open(self.METRICS_FILE, 'r') as f:
                    metrics = json.load(f)
                logger.debug(f"Métriques chargées depuis {self.METRICS_FILE}")
                return metrics
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Erreur lors du chargement des métriques: {e}")
        
        # Métriques par défaut
        default_metrics = {
            "total_updates": 0,
            "failed_updates": 0,
            "last_update": None,
            "updates": [],
            "model_performance": {
                "accuracy": 0.85,  # Simulé
                "recall": 0.78,    # Simulé
                "f1_score": 0.81   # Simulé
            }
        }
        logger.debug("Métriques par défaut initialisées")
        return default_metrics
    
    def _save_metrics(self):
        """Sauvegarde les métriques de mise à jour"""
        try:
            with open(self.METRICS_FILE, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            logger.debug(f"Métriques sauvegardées dans {self.METRICS_FILE}")
        except IOError as e:
            logger.error(f"Erreur lors de la sauvegarde des métriques: {e}")
    
    def _get_model_hash(self, file_path: str) -> str:
        """
        Calcule le hash MD5 du fichier modèle
        
        Args:
            file_path: Chemin vers le fichier modèle
            
        Returns:
            Hash MD5 du fichier
        """
        if not os.path.exists(file_path):
            logger.warning(f"Fichier inexistant: {file_path}")
            return ""
            
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
            return file_hash.hexdigest()
        except IOError as e:
            logger.error(f"Erreur lors du calcul du hash: {e}")
            return ""
    
    def _backup_current_model(self) -> bool:
        """
        Crée une sauvegarde du modèle actuel
        
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        if not os.path.exists(self.MODEL_PATH):
            logger.warning(f"Modèle inexistant, impossible de faire une sauvegarde: {self.MODEL_PATH}")
            return False
            
        try:
            # Générer un nom de fichier basé sur la date
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"model_backup_{timestamp}.h5"
            backup_path = os.path.join(self.MODEL_BACKUP_DIR, backup_filename)
            
            # Copier le fichier
            shutil.copy2(self.MODEL_PATH, backup_path)
            logger.info(f"Sauvegarde créée: {backup_path}")
            
            # Nettoyer les anciennes sauvegardes
            self._cleanup_old_backups()
            
            return True
        except IOError as e:
            logger.error(f"Erreur lors de la sauvegarde du modèle: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Nettoie les anciennes sauvegardes pour ne garder que les MAX_BACKUPS plus récentes"""
        try:
            # Lister tous les fichiers de sauvegarde
            backup_files = [os.path.join(self.MODEL_BACKUP_DIR, f) 
                          for f in os.listdir(self.MODEL_BACKUP_DIR) 
                          if f.startswith("model_backup_") and f.endswith(".h5")]
            
            # Trier par date de modification (plus récent en premier)
            backup_files.sort(key=os.path.getmtime, reverse=True)
            
            # Supprimer les fichiers excédentaires
            for old_file in backup_files[self.MAX_BACKUPS:]:
                os.remove(old_file)
                logger.debug(f"Ancienne sauvegarde supprimée: {old_file}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des anciennes sauvegardes: {e}")
    
    def _download_latest_model(self) -> Optional[str]:
        """
        Télécharge le dernier modèle depuis le serveur ou le système de stockage
        
        Returns:
            str: Chemin vers le modèle téléchargé, ou None si échec
        """
        # Dans une implémentation réelle, vous téléchargeriez le modèle depuis un serveur
        # Par exemple:
        # - Une API REST
        # - Un système de stockage (S3, GCS, etc.)
        # - Un dépôt Git
        
        try:
            # Pour cette simulation, nous allons simplement créer un modèle factice
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_path = f"instance/temp_model_{timestamp}.h5"
            
            # Simuler un téléchargement (créer un fichier factice)
            with open(temp_path, 'wb') as f:
                # Écrire des données aléatoires
                f.write(b'MODEL_DATA_' + timestamp.encode() + b'_' * 1024)
            
            logger.info(f"Nouveau modèle téléchargé vers: {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement du modèle: {e}")
            return None
    
    def _verify_model_integrity(self, model_path: str) -> bool:
        """
        Vérifie l'intégrité du modèle téléchargé
        
        Args:
            model_path: Chemin vers le modèle à vérifier
            
        Returns:
            bool: True si le modèle est valide, False sinon
        """
        if not os.path.exists(model_path):
            logger.error(f"Impossible de vérifier le modèle: fichier inexistant {model_path}")
            return False
            
        try:
            # Dans une implémentation réelle, vous pourriez:
            # 1. Vérifier la signature du fichier
            # 2. Valider le format du modèle
            # 3. Exécuter des tests de chargement et d'inférence
            
            # Pour cette simulation, nous vérifions simplement la taille du fichier
            file_size = os.path.getsize(model_path)
            if file_size < 100:  # Taille minimale attendue
                logger.warning(f"Modèle suspect (taille: {file_size} octets)")
                return False
                
            logger.debug(f"Intégrité du modèle vérifiée (taille: {file_size} octets)")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du modèle: {e}")
            return False
    
    def _apply_update(self, new_model_path: str) -> bool:
        """
        Applique la mise à jour en remplaçant l'ancien modèle par le nouveau
        
        Args:
            new_model_path: Chemin vers le nouveau modèle
            
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if not os.path.exists(new_model_path):
            logger.error(f"Impossible d'appliquer la mise à jour: fichier inexistant {new_model_path}")
            return False
            
        try:
            # Calculer les hash pour les journaux
            old_hash = self._get_model_hash(self.MODEL_PATH) if os.path.exists(self.MODEL_PATH) else "initial"
            new_hash = self._get_model_hash(new_model_path)
            
            # Sauvegarder l'ancien modèle
            backup_success = True
            if os.path.exists(self.MODEL_PATH):
                backup_success = self._backup_current_model()
                if not backup_success:
                    logger.warning("Impossible de créer une sauvegarde, mais tentative de mise à jour quand même")
            
            # Remplacer l'ancien modèle par le nouveau
            if os.path.exists(self.MODEL_PATH):
                os.remove(self.MODEL_PATH)
            shutil.copy2(new_model_path, self.MODEL_PATH)
            
            # Nettoyer le fichier temporaire
            os.remove(new_model_path)
            
            # Mettre à jour les métriques
            self.metrics["total_updates"] += 1
            self.metrics["last_update"] = datetime.now().isoformat()
            
            # Ajouter l'entrée de mise à jour à l'historique
            update_entry = {
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "old_hash": old_hash,
                "new_hash": new_hash,
                "backed_up": backup_success
            }
            self.metrics["updates"].append(update_entry)
            
            # Sauvegarder les métriques
            self._save_metrics()
            
            logger.info(f"Mise à jour appliquée avec succès: {old_hash} -> {new_hash}")
            return True
        except Exception as e:
            # Mettre à jour les statistiques d'échec
            self.metrics["failed_updates"] += 1
            
            # Ajouter l'entrée d'échec à l'historique
            update_entry = {
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }
            self.metrics["updates"].append(update_entry)
            
            # Sauvegarder les métriques
            self._save_metrics()
            
            logger.error(f"Erreur lors de l'application de la mise à jour: {e}")
            return False
    
    def _evaluate_model_performance(self) -> Dict[str, float]:
        """
        Évalue les performances du modèle mis à jour
        
        Returns:
            Dict: Métriques de performance du modèle
        """
        # Dans une implémentation réelle, vous évalueriez le modèle sur un ensemble de test
        
        # Pour cette simulation, nous générons des métriques aléatoires
        import random
        
        # Petites variations aléatoires de performance
        accuracy = round(0.85 + random.uniform(-0.05, 0.05), 3)
        recall = round(0.78 + random.uniform(-0.05, 0.05), 3)
        f1_score = round(0.81 + random.uniform(-0.05, 0.05), 3)
        
        # Mettre à jour les métriques dans le modèle
        performance = {
            "accuracy": accuracy,
            "recall": recall,
            "f1_score": f1_score
        }
        
        # Sauvegarder dans les métriques globales
        self.metrics["model_performance"] = performance
        self._save_metrics()
        
        logger.info(f"Performances modèle évaluées: {performance}")
        return performance
    
    def _update_process(self):
        """Processus principal de mise à jour en arrière-plan"""
        while self.running:
            try:
                logger.debug("Vérification des mises à jour...")
                
                # 1. Télécharger le dernier modèle
                new_model_path = self._download_latest_model()
                if not new_model_path:
                    logger.warning("Échec du téléchargement, report de la mise à jour")
                    time.sleep(self.UPDATE_INTERVAL)
                    continue
                    
                # 2. Vérifier l'intégrité du modèle
                if not self._verify_model_integrity(new_model_path):
                    logger.warning("Modèle invalide, report de la mise à jour")
                    # Nettoyer le fichier temporaire
                    if os.path.exists(new_model_path):
                        os.remove(new_model_path)
                    time.sleep(self.UPDATE_INTERVAL)
                    continue
                
                # 3. Vérifier si le modèle est différent du modèle actuel
                current_hash = self._get_model_hash(self.MODEL_PATH) if os.path.exists(self.MODEL_PATH) else ""
                new_hash = self._get_model_hash(new_model_path)
                
                if current_hash and current_hash == new_hash:
                    logger.info("Le modèle téléchargé est identique au modèle actuel, mise à jour ignorée")
                    # Nettoyer le fichier temporaire
                    os.remove(new_model_path)
                    time.sleep(self.UPDATE_INTERVAL)
                    continue
                
                # 4. Appliquer la mise à jour
                update_success = self._apply_update(new_model_path)
                
                if update_success:
                    # 5. Évaluer les performances du modèle mis à jour
                    self._evaluate_model_performance()
                    
                    # Mettre à jour l'horodatage de la dernière mise à jour
                    self.last_update_time = datetime.now().isoformat()
                
                # Attendre l'intervalle avant la prochaine vérification
                time.sleep(self.UPDATE_INTERVAL)
                
            except Exception as e:
                logger.error(f"Erreur dans le processus de mise à jour: {e}")
                time.sleep(300)  # Attendre 5 minutes en cas d'erreur
    
    def start(self):
        """Démarre le processus de mise à jour automatique en arrière-plan"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._update_process, daemon=True)
            self.update_thread.start()
            logger.info("Processus de mise à jour automatique démarré")
    
    def stop(self):
        """Arrête le processus de mise à jour automatique"""
        if self.running:
            self.running = False
            logger.info("Arrêt du processus de mise à jour automatique")
            
            # Attendre la fin du thread (si nécessaire)
            if self.update_thread and self.update_thread.is_alive():
                self.update_thread.join(timeout=10)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtient le statut actuel du gestionnaire de mise à jour
        
        Returns:
            Dict: Informations sur le statut actuel
        """
        # Obtenir la liste des sauvegardes disponibles
        backup_files = []
        if os.path.exists(self.MODEL_BACKUP_DIR):
            backup_files = [f for f in os.listdir(self.MODEL_BACKUP_DIR) 
                          if f.startswith("model_backup_") and f.endswith(".h5")]
        
        return {
            "running": self.running,
            "last_update_time": self.last_update_time,
            "metrics": self.metrics,
            "available_backups": len(backup_files)
        }
    
    def force_update(self) -> bool:
        """
        Force une mise à jour immédiate du modèle
        
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            # 1. Télécharger le dernier modèle
            new_model_path = self._download_latest_model()
            if not new_model_path:
                logger.error("Échec du téléchargement lors de la mise à jour forcée")
                return False
                
            # 2. Vérifier l'intégrité du modèle
            if not self._verify_model_integrity(new_model_path):
                logger.error("Modèle invalide lors de la mise à jour forcée")
                if os.path.exists(new_model_path):
                    os.remove(new_model_path)
                return False
            
            # 3. Appliquer la mise à jour
            update_success = self._apply_update(new_model_path)
            
            if update_success:
                # 4. Évaluer les performances du modèle mis à jour
                self._evaluate_model_performance()
                
                # Mettre à jour l'horodatage de la dernière mise à jour
                self.last_update_time = datetime.now().isoformat()
            
            return update_success
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour forcée: {e}")
            return False
    
    def rollback_to_previous(self) -> bool:
        """
        Restaure le modèle à sa version précédente
        
        Returns:
            bool: True si la restauration a réussi, False sinon
        """
        try:
            # Trouver le dernier fichier de sauvegarde
            if not os.path.exists(self.MODEL_BACKUP_DIR):
                logger.error(f"Répertoire de sauvegarde inexistant: {self.MODEL_BACKUP_DIR}")
                return False
                
            backup_files = [f for f in os.listdir(self.MODEL_BACKUP_DIR) 
                          if f.startswith("model_backup_") and f.endswith(".h5")]
            
            if not backup_files:
                logger.error("Aucune sauvegarde disponible pour la restauration")
                return False
                
            # Trier par date de modification (plus récent en premier)
            backup_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.MODEL_BACKUP_DIR, f)), 
                            reverse=True)
            
            last_backup = os.path.join(self.MODEL_BACKUP_DIR, backup_files[0])
            
            # Calculer les hash pour les journaux
            old_hash = self._get_model_hash(self.MODEL_PATH) if os.path.exists(self.MODEL_PATH) else "unknown"
            backup_hash = self._get_model_hash(last_backup)
            
            # Créer une sauvegarde du modèle actuel pour pouvoir revenir en avant si nécessaire
            if os.path.exists(self.MODEL_PATH):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                rollback_backup = os.path.join(self.MODEL_BACKUP_DIR, f"pre_rollback_{timestamp}.h5")
                shutil.copy2(self.MODEL_PATH, rollback_backup)
                logger.info(f"Modèle actuel sauvegardé avant restauration: {rollback_backup}")
            
            # Restaurer depuis la sauvegarde
            if os.path.exists(self.MODEL_PATH):
                os.remove(self.MODEL_PATH)
            shutil.copy2(last_backup, self.MODEL_PATH)
            
            # Mettre à jour les métriques
            update_entry = {
                "timestamp": datetime.now().isoformat(),
                "status": "rollback",
                "old_hash": old_hash,
                "new_hash": backup_hash,
                "rollback_to": os.path.basename(last_backup)
            }
            self.metrics["updates"].append(update_entry)
            
            # Sauvegarder les métriques
            self._save_metrics()
            
            logger.info(f"Restauration réussie vers: {last_backup}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la restauration: {e}")
            return False

def main():
    """Fonction principale pour exécution directe"""
    # Créer une instance du gestionnaire
    updater = AIAutoUpdater()
    
    # Démarrer le gestionnaire
    updater.start()
    
    try:
        # Garder le processus principal en vie
        while True:
            time.sleep(60)
            status = updater.get_status()
            logger.info(f"Statut: {status['running']}, Dernière mise à jour: {status['last_update_time']}")
    except KeyboardInterrupt:
        # Arrêter proprement sur Ctrl+C
        logger.info("Arrêt du programme")
        updater.stop()
    except Exception as e:
        logger.error(f"Erreur dans la fonction principale: {e}")
        updater.stop()

if __name__ == "__main__":
    main()