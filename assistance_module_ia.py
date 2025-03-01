
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'assistance pour la gestion des modules IA automatiques
Fournit une interface unifiée pour gérer et contrôler les différents modules d'IA automatique
"""
import os
import logging
import json
import signal
import subprocess
import time
from datetime import datetime
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class AIModuleAssistant:
    """Gestionnaire unifié des modules d'IA automatiques"""
    
    def __init__(self):
        """Initialise l'assistant de modules IA"""
        self.modules = {
            "IA_MOBILE": {
                "name": "IA Mobile Auto Analyzer",
                "script": "ia_mobile_auto_analyzer.py",
                "stop_script": "stop_mobile_ia.py",
                "status_file": os.path.join("instance", "mobile_cache", "ia_status.json"),
                "pid_file": os.path.join("instance", "mobile_cache", "ia_mobile.pid"),
                "description": "Module optimisé pour les analyses d'appareils mobiles",
                "autostart": False
            },
            "IA_ACTIVITE": {
                "name": "IA Activité Automatique",
                "script": "ia_activite_automatique.py",
                "status_file": os.path.join("instance", "ai_reports", "ia_activite_status.json"),
                "pid_file": os.path.join("instance", "ai_reports", "ia_activite.pid"),
                "description": "Gestionnaire d'activités IA pour analyses périodiques",
                "autostart": False
            }
        }
        
        # Créer les répertoires nécessaires s'ils n'existent pas
        for module in self.modules.values():
            os.makedirs(os.path.dirname(module["status_file"]), exist_ok=True)
        
        # Vérifier l'état initial des modules
        self.update_all_statuses()
    
    def update_all_statuses(self):
        """Met à jour le statut de tous les modules IA"""
        for module_id, module in self.modules.items():
            self._update_module_status(module_id)
    
    def _update_module_status(self, module_id):
        """
        Met à jour le statut d'un module spécifique
        
        Args:
            module_id: Identifiant du module
        """
        if module_id not in self.modules:
            logger.error(f"Module inconnu: {module_id}")
            return
            
        module = self.modules[module_id]
        
        # Vérifier si le module est en cours d'exécution en recherchant le processus
        pid = self._get_module_pid(module_id)
        running = False
        
        if pid:
            # Vérifier si ce PID existe toujours
            try:
                os.kill(pid, 0)  # Signal 0 vérifie juste si le processus existe
                running = True
            except OSError:
                # Le processus n'existe plus
                running = False
                self._update_status_file(module_id, "stopped", "Le processus n'est plus en cours d'exécution")
                self._remove_pid_file(module_id)
        
        # Mettre à jour le status en fonction de l'état du processus
        if running and not self._status_file_exists(module_id):
            self._update_status_file(module_id, "running", "Le processus est en cours d'exécution")
        
        return running
    
    def _get_module_pid(self, module_id):
        """
        Récupère le PID du module à partir du fichier PID ou de la recherche de processus
        
        Args:
            module_id: Identifiant du module
            
        Returns:
            int: PID du processus ou None si non trouvé
        """
        module = self.modules[module_id]
        
        # D'abord essayer de lire le fichier PID
        if os.path.exists(module["pid_file"]):
            try:
                with open(module["pid_file"], 'r') as f:
                    pid = int(f.read().strip())
                    return pid
            except (ValueError, FileNotFoundError, IOError) as e:
                logger.error(f"Erreur lors de la lecture du fichier PID: {e}")
        
        # Si pas de fichier PID, rechercher le processus par son nom
        script_name = module["script"]
        try:
            result = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, 
                text=True
            )
            
            for line in result.stdout.splitlines():
                if script_name in line and 'python' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = int(parts[1])
                        # Mettre à jour le fichier PID
                        self._write_pid_file(module_id, pid)
                        return pid
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du processus: {e}")
        
        return None
    
    def _status_file_exists(self, module_id):
        """Vérifie si le fichier de statut existe"""
        module = self.modules[module_id]
        return os.path.exists(module["status_file"])
    
    def _update_status_file(self, module_id, status, message=""):
        """
        Met à jour le fichier de statut d'un module
        
        Args:
            module_id: Identifiant du module
            status: Statut à définir ("running", "stopped", "error")
            message: Message expliquant le statut
        """
        module = self.modules[module_id]
        status_file = module["status_file"]
        
        status_data = {
            "status": status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message or f"IA {module['name']} {status}"
        }
        
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Statut du module {module_id} mis à jour: {status}")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du fichier de statut pour {module_id}: {e}")
    
    def _write_pid_file(self, module_id, pid):
        """
        Écrit le PID dans le fichier PID
        
        Args:
            module_id: Identifiant du module
            pid: PID du processus
        """
        module = self.modules[module_id]
        pid_file = module["pid_file"]
        
        try:
            with open(pid_file, 'w') as f:
                f.write(str(pid))
            logger.debug(f"Fichier PID créé pour {module_id}: {pid}")
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture du fichier PID pour {module_id}: {e}")
    
    def _remove_pid_file(self, module_id):
        """
        Supprime le fichier PID
        
        Args:
            module_id: Identifiant du module
        """
        module = self.modules[module_id]
        pid_file = module["pid_file"]
        
        if os.path.exists(pid_file):
            try:
                os.remove(pid_file)
                logger.debug(f"Fichier PID supprimé pour {module_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la suppression du fichier PID pour {module_id}: {e}")
    
    def start_module(self, module_id, options=None):
        """
        Démarre un module IA spécifique
        
        Args:
            module_id: Identifiant du module à démarrer
            options: Options supplémentaires à passer au script (dict)
            
        Returns:
            bool: True si le démarrage a réussi, False sinon
        """
        if module_id not in self.modules:
            logger.error(f"Module inconnu: {module_id}")
            return False
            
        # Vérifier si le module est déjà en cours d'exécution
        if self._update_module_status(module_id):
            logger.info(f"Le module {module_id} est déjà en cours d'exécution")
            return True
            
        module = self.modules[module_id]
        
        # Construire la commande
        cmd = ["python", module["script"]]
        
        # Ajouter des options si spécifiées
        if options:
            for key, value in options.items():
                cmd.append(f"--{key}={value}")
        
        # Démarrer le processus
        try:
            logger.info(f"Démarrage du module {module_id}...")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre un peu pour vérifier que le processus démarre correctement
            time.sleep(2)
            
            # Vérifier si le processus est toujours en cours d'exécution
            if process.poll() is None:
                # Le processus est toujours en cours d'exécution
                self._write_pid_file(module_id, process.pid)
                self._update_status_file(module_id, "running", f"Module {module['name']} démarré avec succès")
                logger.info(f"Module {module_id} démarré avec succès (PID: {process.pid})")
                return True
            else:
                # Le processus s'est terminé
                stdout, stderr = process.communicate()
                error_msg = f"Le module n'a pas pu démarrer. Code: {process.returncode}, Erreur: {stderr}"
                self._update_status_file(module_id, "error", error_msg)
                logger.error(f"Échec du démarrage de {module_id}: {error_msg}")
                return False
                
        except Exception as e:
            error_msg = f"Erreur lors du démarrage du module: {e}"
            self._update_status_file(module_id, "error", error_msg)
            logger.error(f"Erreur lors du démarrage de {module_id}: {e}")
            return False
    
    def stop_module(self, module_id):
        """
        Arrête un module IA spécifique
        
        Args:
            module_id: Identifiant du module à arrêter
            
        Returns:
            bool: True si l'arrêt a réussi, False sinon
        """
        if module_id not in self.modules:
            logger.error(f"Module inconnu: {module_id}")
            return False
            
        # Vérifier si le module est en cours d'exécution
        if not self._update_module_status(module_id):
            logger.info(f"Le module {module_id} n'est pas en cours d'exécution")
            return True
            
        module = self.modules[module_id]
        pid = self._get_module_pid(module_id)
        
        if pid:
            try:
                # Pour l'IA mobile, utiliser le script d'arrêt spécifique si disponible
                if module_id == "IA_MOBILE" and os.path.exists(module.get("stop_script", "")):
                    logger.info(f"Arrêt du module {module_id} via script dédié...")
                    subprocess.run(["python", module["stop_script"]], check=True)
                    
                    # Vérifier si l'arrêt a réussi
                    time.sleep(1)
                    if not self._update_module_status(module_id):
                        self._update_status_file(module_id, "stopped", f"Module {module['name']} arrêté avec succès")
                        self._remove_pid_file(module_id)
                        logger.info(f"Module {module_id} arrêté avec succès")
                        return True
                
                # Si pas de script d'arrêt ou s'il a échoué, envoyer SIGTERM
                logger.info(f"Envoi du signal d'arrêt au processus {pid}...")
                os.kill(pid, signal.SIGTERM)
                
                # Attendre que le processus s'arrête
                for _ in range(10):  # Attendre jusqu'à 5 secondes
                    time.sleep(0.5)
                    try:
                        os.kill(pid, 0)  # Vérifier si le processus existe toujours
                    except OSError:
                        # Le processus n'existe plus
                        self._update_status_file(module_id, "stopped", f"Module {module['name']} arrêté avec succès")
                        self._remove_pid_file(module_id)
                        logger.info(f"Module {module_id} arrêté avec succès")
                        return True
                
                # Si le processus ne s'arrête pas, forcer l'arrêt
                logger.warning(f"Le processus {pid} ne répond pas, envoi de SIGKILL...")
                os.kill(pid, signal.SIGKILL)
                self._update_status_file(module_id, "stopped", f"Module {module['name']} arrêté de force")
                self._remove_pid_file(module_id)
                logger.info(f"Module {module_id} arrêté de force")
                return True
                
            except Exception as e:
                error_msg = f"Erreur lors de l'arrêt du module: {e}"
                self._update_status_file(module_id, "error", error_msg)
                logger.error(f"Erreur lors de l'arrêt de {module_id}: {e}")
                return False
        else:
            logger.warning(f"Aucun PID trouvé pour le module {module_id}")
            self._update_status_file(module_id, "stopped", "Aucun processus trouvé")
            return True
    
    def restart_module(self, module_id, options=None):
        """
        Redémarre un module IA spécifique
        
        Args:
            module_id: Identifiant du module à redémarrer
            options: Options supplémentaires à passer au script (dict)
            
        Returns:
            bool: True si le redémarrage a réussi, False sinon
        """
        # Arrêter le module s'il est en cours d'exécution
        if self._update_module_status(module_id):
            if not self.stop_module(module_id):
                return False
        
        # Attendre un peu pour s'assurer que l'arrêt est complet
        time.sleep(2)
        
        # Démarrer le module
        return self.start_module(module_id, options)
    
    def get_module_status(self, module_id):
        """
        Récupère le statut actuel d'un module
        
        Args:
            module_id: Identifiant du module
            
        Returns:
            dict: Statut du module ou None si le module n'existe pas
        """
        if module_id not in self.modules:
            logger.error(f"Module inconnu: {module_id}")
            return None
            
        module = self.modules[module_id]
        is_running = self._update_module_status(module_id)
        
        # Lire le fichier de statut
        status_data = {"status": "unknown"}
        if os.path.exists(module["status_file"]):
            try:
                with open(module["status_file"], 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier de statut pour {module_id}: {e}")
        
        # Mettre à jour le statut si nécessaire
        if is_running and status_data.get("status") != "running":
            self._update_status_file(module_id, "running", "Le processus est en cours d'exécution")
            status_data["status"] = "running"
            status_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_data["message"] = "Le processus est en cours d'exécution"
        elif not is_running and status_data.get("status") == "running":
            self._update_status_file(module_id, "stopped", "Le processus n'est plus en cours d'exécution")
            status_data["status"] = "stopped"
            status_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_data["message"] = "Le processus n'est plus en cours d'exécution"
        
        # Ajouter des informations supplémentaires
        result = {
            "id": module_id,
            "name": module["name"],
            "description": module["description"],
            "script": module["script"],
            "running": is_running,
            "pid": self._get_module_pid(module_id),
            **status_data
        }
        
        return result
    
    def get_all_modules_status(self):
        """
        Récupère le statut de tous les modules
        
        Returns:
            dict: Statut de tous les modules
        """
        result = {}
        for module_id in self.modules:
            result[module_id] = self.get_module_status(module_id)
        return result
    
    def set_battery_saver_mode(self, module_id, enabled=True):
        """
        Active ou désactive le mode économie d'énergie pour un module
        Actuellement, seul le module IA_MOBILE supporte cette fonctionnalité
        
        Args:
            module_id: Identifiant du module
            enabled: True pour activer, False pour désactiver
            
        Returns:
            bool: True si la configuration a réussi, False sinon
        """
        if module_id != "IA_MOBILE":
            logger.warning(f"Le mode économie d'énergie n'est pas supporté par le module {module_id}")
            return False
            
        # Vérifier si le module est en cours d'exécution
        if not self._update_module_status(module_id):
            logger.warning(f"Le module {module_id} n'est pas en cours d'exécution")
            if not self.start_module(module_id):
                return False
        
        # Pour IA_MOBILE, redémarrer avec l'option appropriée
        return self.restart_module(module_id, {"battery_saver": "true" if enabled else "false"})
    
    def configure_analysis_interval(self, module_id, interval_minutes):
        """
        Configure l'intervalle d'analyse pour un module
        Actuellement, seul le module IA_ACTIVITE supporte cette fonctionnalité
        
        Args:
            module_id: Identifiant du module
            interval_minutes: Intervalle en minutes entre les analyses
            
        Returns:
            bool: True si la configuration a réussi, False sinon
        """
        if module_id != "IA_ACTIVITE":
            logger.warning(f"La configuration de l'intervalle n'est pas supportée par le module {module_id}")
            return False
            
        # Redémarrer le module avec l'option d'intervalle
        return self.restart_module(module_id, {"interval": str(interval_minutes)})


# Interface en ligne de commande
def main():
    """Point d'entrée pour l'exécution en ligne de commande"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Assistant pour les modules IA automatiques")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"], 
                       help="Action à effectuer")
    parser.add_argument("module", nargs="?", choices=["IA_MOBILE", "IA_ACTIVITE", "all"],
                       default="all", help="Module cible (par défaut: all)")
    parser.add_argument("--battery-saver", choices=["on", "off"], 
                       help="Active ou désactive le mode économie d'énergie pour IA_MOBILE")
    parser.add_argument("--interval", type=int, 
                       help="Intervalle en minutes entre les analyses pour IA_ACTIVITE")
    
    args = parser.parse_args()
    
    assistant = AIModuleAssistant()
    
    if args.module == "all" and args.action != "status":
        modules = list(assistant.modules.keys())
    else:
        modules = [args.module] if args.module != "all" else list(assistant.modules.keys())
    
    # Traiter les options spécifiques
    if args.battery_saver:
        if "IA_MOBILE" in modules:
            assistant.set_battery_saver_mode("IA_MOBILE", args.battery_saver == "on")
        else:
            logger.warning("L'option --battery-saver ne s'applique qu'au module IA_MOBILE")
    
    if args.interval:
        if "IA_ACTIVITE" in modules:
            assistant.configure_analysis_interval("IA_ACTIVITE", args.interval)
        else:
            logger.warning("L'option --interval ne s'applique qu'au module IA_ACTIVITE")
    
    # Exécuter l'action demandée
    success = True
    if args.action == "start":
        for module_id in modules:
            if not assistant.start_module(module_id):
                success = False
    elif args.action == "stop":
        for module_id in modules:
            if not assistant.stop_module(module_id):
                success = False
    elif args.action == "restart":
        for module_id in modules:
            if not assistant.restart_module(module_id):
                success = False
    elif args.action == "status":
        if args.module == "all":
            statuses = assistant.get_all_modules_status()
            print("\nSTATUT DES MODULES IA AUTOMATIQUES\n" + "=" * 40)
            for module_id, status in statuses.items():
                running_status = "En cours d'exécution" if status["running"] else "Arrêté"
                pid_str = f" (PID: {status['pid']})" if status["pid"] else ""
                status_time = status.get("timestamp", "inconnu")
                
                print(f"\n{status['name']} ({module_id}):")
                print(f"  - État: {running_status}{pid_str}")
                print(f"  - Statut: {status.get('status', 'inconnu')} ({status_time})")
                print(f"  - Message: {status.get('message', '')}")
                print(f"  - Script: {status['script']}")
        else:
            status = assistant.get_module_status(args.module)
            if status:
                running_status = "En cours d'exécution" if status["running"] else "Arrêté"
                pid_str = f" (PID: {status['pid']})" if status["pid"] else ""
                status_time = status.get("timestamp", "inconnu")
                
                print("\nDÉTAILS DU MODULE\n" + "=" * 40)
                print(f"\n{status['name']} ({args.module}):")
                print(f"  - État: {running_status}{pid_str}")
                print(f"  - Statut: {status.get('status', 'inconnu')} ({status_time})")
                print(f"  - Message: {status.get('message', '')}")
                print(f"  - Description: {status['description']}")
                print(f"  - Script: {status['script']}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
