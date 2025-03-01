#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'intégration des mises à jour IA avec l'application Flask
Ce module établit la communication entre le système de mise à jour IA et l'application
"""

import os
import json
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from ai_auto_update import AIAutoUpdater
from flask import current_app, g, jsonify

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instance/ai_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai_update_integration")

class AIUpdateIntegration:
    """
    Classe d'intégration pour connecter le système de mise à jour automatique
    avec l'application Flask et les modules IA existants
    """
    
    _instance = None
    
    def __new__(cls):
        """Implémentation du pattern Singleton"""
        if cls._instance is None:
            cls._instance = super(AIUpdateIntegration, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialisation de l'intégration des mises à jour IA"""
        if self._initialized:
            return
            
        self.updater = AIAutoUpdater()
        self.model_status = {
            "status": "inactive",
            "last_check": None,
            "version_info": None,
            "update_available": False,
            "auto_update_enabled": True
        }
        self.monitoring_thread = None
        self.is_monitoring = False
        self._health_check_interval = 300  # 5 minutes
        self._model_reload_lock = threading.Lock()
        self._initialized = True
        
        logger.info("Module d'intégration de mise à jour IA initialisé")
    
    def initialize_with_app(self, app):
        """
        Initialise l'intégration avec l'application Flask
        
        Args:
            app: Instance de l'application Flask
        """
        with app.app_context():
            # Enregistrer les routes d'API pour le système de mise à jour
            self._register_api_routes(app)
            
            # Ajouter des fonctions de gestion du cycle de vie de l'application
            @app.before_first_request
            def start_ai_update_services():
                self.start()
            
            @app.teardown_appcontext
            def cleanup_ai_update_services(exception=None):
                self.stop()
            
            logger.info("Intégration des mises à jour IA configurée avec l'application Flask")
    
    def _register_api_routes(self, app):
        """
        Enregistre les routes d'API pour l'intégration des mises à jour IA
        
        Args:
            app: Instance de l'application Flask
        """
        # Point de terminaison API pour obtenir le statut des mises à jour
        @app.route('/api/ai/updates/status', methods=['GET'])
        def get_ai_update_status():
            status = self.get_status()
            return jsonify(status)
        
        # Point de terminaison API pour forcer une mise à jour
        @app.route('/api/ai/updates/force', methods=['POST'])
        def force_ai_update():
            result = self.force_update()
            return jsonify({
                "success": result,
                "timestamp": datetime.now().isoformat(),
                "message": "Mise à jour forcée initiée" if result else "Échec de la mise à jour forcée"
            })
        
        # Point de terminaison API pour activer/désactiver les mises à jour automatiques
        @app.route('/api/ai/updates/toggle/<int:enabled>', methods=['POST'])
        def toggle_ai_auto_updates(enabled):
            self.set_auto_update(bool(enabled))
            return jsonify({
                "success": True,
                "auto_update_enabled": bool(enabled),
                "timestamp": datetime.now().isoformat()
            })
        
        # Point de terminaison API pour restaurer une version précédente
        @app.route('/api/ai/updates/rollback', methods=['POST'])
        def rollback_ai_model():
            result = self.rollback_to_previous()
            return jsonify({
                "success": result,
                "timestamp": datetime.now().isoformat(),
                "message": "Restauration réussie" if result else "Échec de la restauration"
            })
        
        # Point de terminaison API pour obtenir l'historique des mises à jour
        @app.route('/api/ai/updates/history', methods=['GET'])
        def get_ai_update_history():
            history = self.get_update_history()
            return jsonify(history)
    
    def start(self):
        """Démarre le service d'intégration des mises à jour IA"""
        if not self.is_monitoring:
            # Démarrer le gestionnaire de mise à jour automatique
            self.updater.start()
            
            # Démarrer le thread de surveillance
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_routine, daemon=True)
            self.monitoring_thread.start()
            
            logger.info("Service d'intégration des mises à jour IA démarré")
            
            # Mettre à jour le statut
            self.model_status["status"] = "active"
            self.model_status["last_check"] = datetime.now().isoformat()
    
    def stop(self):
        """Arrête le service d'intégration des mises à jour IA"""
        if self.is_monitoring:
            # Arrêter le thread de surveillance
            self.is_monitoring = False
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=10)
            
            # Arrêter le gestionnaire de mise à jour automatique
            self.updater.stop()
            
            logger.info("Service d'intégration des mises à jour IA arrêté")
            
            # Mettre à jour le statut
            self.model_status["status"] = "inactive"
    
    def _monitoring_routine(self):
        """Routine de surveillance exécutée dans un thread d'arrière-plan"""
        while self.is_monitoring:
            try:
                # Vérifier le statut du modèle et des mises à jour
                updater_status = self.updater.get_status()
                
                # Mettre à jour notre statut interne
                self.model_status["last_check"] = datetime.now().isoformat()
                self.model_status["version_info"] = self._get_model_version_info()
                
                # Vérifier si une mise à jour est disponible (simulation)
                self.model_status["update_available"] = self._check_update_availability()
                
                logger.debug(f"Statut de l'updater: {updater_status}")
                
                # Déclencher une mise à jour si nécessaire et activée
                if self.model_status["update_available"] and self.model_status["auto_update_enabled"]:
                    logger.info("Mise à jour disponible, déclenchement automatique")
                    self.force_update()
                
                # Effectuer un health check du modèle
                self._perform_model_health_check()
                
                # Attendre le prochain cycle de vérification
                for _ in range(int(self._health_check_interval / 10)):
                    if not self.is_monitoring:
                        break
                    time.sleep(10)
                    
            except Exception as e:
                logger.error(f"Erreur dans la routine de surveillance: {e}")
                time.sleep(60)  # Attendre un peu en cas d'erreur
    
    def _get_model_version_info(self) -> Dict[str, Any]:
        """
        Obtient les informations de version du modèle IA actuel
        
        Returns:
            Dict: Informations sur la version du modèle
        """
        # Dans une implémentation réelle, vous pourriez charger le modèle
        # et extraire sa version ou d'autres métadonnées
        
        # Simuler les informations de version
        model_path = "modele_ia.h5"
        
        if not os.path.exists(model_path):
            return {
                "version": "unknown",
                "creation_date": None,
                "size": 0,
                "framework": "unknown"
            }
        
        try:
            stat_info = os.stat(model_path)
            return {
                "version": f"1.{int(stat_info.st_mtime) % 100}",  # Version simulée
                "creation_date": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "size": stat_info.st_size,
                "framework": "TensorFlow 2.x"  # À adapter selon le framework réel
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention des informations du modèle: {e}")
            return {
                "version": "error",
                "creation_date": None,
                "size": 0,
                "framework": "unknown",
                "error": str(e)
            }
    
    def _check_update_availability(self) -> bool:
        """
        Vérifie si une mise à jour est disponible pour le modèle
        
        Returns:
            bool: True si une mise à jour est disponible, False sinon
        """
        # Simuler la vérification de disponibilité
        # Dans une implémentation réelle, vous interrogeriez un serveur distant
        current_minute = datetime.now().minute
        
        # Simuler une disponibilité de mise à jour toutes les 30 minutes
        return current_minute % 30 == 0
    
    def _perform_model_health_check(self):
        """Effectue une vérification de l'état du modèle IA"""
        # Vérifier si le fichier du modèle existe
        model_path = "modele_ia.h5"
        if not os.path.exists(model_path):
            logger.warning(f"Fichier modèle non trouvé: {model_path}")
            return False
        
        # Dans une implémentation réelle, vous pourriez:
        # 1. Charger le modèle et exécuter une inférence de test
        # 2. Vérifier l'empreinte mémoire et CPU
        # 3. Exécuter d'autres diagnostics
        
        logger.debug("Vérification de santé du modèle IA réussie")
        return True
    
    def reload_model(self):
        """
        Recharge le modèle IA dans les modules d'application qui l'utilisent
        Cette méthode doit être sûre pour les threads
        """
        with self._model_reload_lock:
            # Dans une implémentation réelle, vous notifieriez tous les modules
            # utilisant le modèle pour qu'ils le rechargent
            
            try:
                # Simuler un rechargement
                logger.info("Simulation du rechargement du modèle dans les modules d'application")
                time.sleep(1)  # Simuler un certain temps de chargement
                
                # Mise à jour de la date de dernier check
                self.model_status["last_check"] = datetime.now().isoformat()
                
                return True
            except Exception as e:
                logger.error(f"Erreur lors du rechargement du modèle: {e}")
                return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtient le statut actuel du système de mise à jour IA
        
        Returns:
            Dict: Statut complet du système
        """
        updater_status = self.updater.get_status()
        
        return {
            **self.model_status,
            "updater": {
                "running": updater_status["running"],
                "last_update_time": updater_status["last_update_time"],
                "total_updates": updater_status["metrics"]["total_updates"],
                "failed_updates": updater_status["metrics"]["failed_updates"],
                "available_backups": updater_status["available_backups"]
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def force_update(self) -> bool:
        """
        Force une mise à jour immédiate du modèle
        
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        update_result = self.updater.force_update()
        
        if update_result:
            # Mettre à jour le statut
            self.model_status["last_check"] = datetime.now().isoformat()
            self.model_status["update_available"] = False
            self.model_status["version_info"] = self._get_model_version_info()
            
            # Recharger le modèle dans l'application
            self.reload_model()
            
            logger.info("Mise à jour forcée réussie, modèle rechargé")
        else:
            logger.warning("Échec de la mise à jour forcée")
        
        return update_result
    
    def set_auto_update(self, enabled: bool):
        """
        Active ou désactive les mises à jour automatiques
        
        Args:
            enabled: True pour activer, False pour désactiver
        """
        self.model_status["auto_update_enabled"] = enabled
        logger.info(f"Mises à jour automatiques {'activées' if enabled else 'désactivées'}")
    
    def rollback_to_previous(self) -> bool:
        """
        Restaure le modèle à sa version précédente
        
        Returns:
            bool: True si la restauration a réussi, False sinon
        """
        rollback_result = self.updater.rollback_to_previous()
        
        if rollback_result:
            # Mettre à jour le statut
            self.model_status["last_check"] = datetime.now().isoformat()
            self.model_status["version_info"] = self._get_model_version_info()
            
            # Recharger le modèle dans l'application
            self.reload_model()
            
            logger.info("Restauration réussie, modèle rechargé")
        else:
            logger.warning("Échec de la restauration du modèle")
        
        return rollback_result
    
    def get_update_history(self) -> Dict[str, Any]:
        """
        Obtient l'historique des mises à jour
        
        Returns:
            Dict: Historique des mises à jour
        """
        updater_status = self.updater.get_status()
        
        # Formater l'historique pour l'API
        history = {
            "updates": updater_status["metrics"]["updates"],
            "total_updates": updater_status["metrics"]["total_updates"],
            "failed_updates": updater_status["metrics"]["failed_updates"],
            "current_version": self.model_status["version_info"]["version"] if self.model_status["version_info"] else "unknown"
        }
        
        return history


# Créer une instance singleton
ai_update_integration = AIUpdateIntegration()

def init_app(app):
    """
    Initialise le module d'intégration des mises à jour IA avec l'application Flask
    
    Args:
        app: Instance de l'application Flask
    """
    ai_update_integration.initialize_with_app(app)
    
    # Ajouter les routes admin
    from flask import render_template, request, redirect, url_for, flash
    
    @app.route('/admin/ai-updates')
    def admin_ai_updates():
        status = ai_update_integration.get_status()
        history = ai_update_integration.get_update_history()
        return render_template('admin/ai_updates.html', 
                               status=status, 
                               history=history)
    
    @app.route('/admin/ai-updates/toggle-auto', methods=['POST'])
    def admin_toggle_auto_updates():
        enabled = request.form.get('enabled', '0') == '1'
        ai_update_integration.set_auto_update(enabled)
        flash(f"Mises à jour automatiques {'activées' if enabled else 'désactivées'}", "success")
        return redirect(url_for('admin_ai_updates'))
    
    @app.route('/admin/ai-updates/force', methods=['POST'])
    def admin_force_update():
        result = ai_update_integration.force_update()
        if result:
            flash("Mise à jour forcée réussie", "success")
        else:
            flash("Échec de la mise à jour forcée", "danger")
        return redirect(url_for('admin_ai_updates'))
    
    @app.route('/admin/ai-updates/rollback', methods=['POST'])
    def admin_rollback():
        result = ai_update_integration.rollback_to_previous()
        if result:
            flash("Restauration réussie", "success")
        else:
            flash("Échec de la restauration", "danger")
        return redirect(url_for('admin_ai_updates'))
    
    logger.info("Routes administratives pour les mises à jour IA enregistrées")