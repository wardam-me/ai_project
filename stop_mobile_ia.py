
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour arrêter l'exécution automatique de l'IA mobile
"""
import os
import signal
import subprocess
import logging
import json
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def find_mobile_ia_process():
    """Trouve le processus d'IA mobile automatique s'il est en cours d'exécution"""
    try:
        # Rechercher les processus python qui exécutent ia_mobile_auto_analyzer.py
        result = subprocess.run(
            ['ps', 'aux'], 
            capture_output=True, 
            text=True
        )
        
        for line in result.stdout.splitlines():
            if 'ia_mobile_auto_analyzer.py' in line and 'python' in line:
                # Extraire l'ID du processus (2ème élément après découpage)
                parts = line.split()
                if len(parts) >= 2:
                    return int(parts[1])
        
        # Vérifier également les processus exécutant ia_activite_automatique.py
        for line in result.stdout.splitlines():
            if 'ia_activite_automatique.py' in line and 'python' in line:
                parts = line.split()
                if len(parts) >= 2:
                    return int(parts[1])
    
    except Exception as e:
        logger.error(f"Erreur lors de la recherche du processus IA: {e}")
    
    return None

def stop_mobile_ia_process(pid=None):
    """Arrête le processus d'IA mobile automatique"""
    if not pid:
        pid = find_mobile_ia_process()
    
    if pid:
        try:
            # Envoyer un signal SIGTERM pour arrêter proprement le processus
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Signal d'arrêt envoyé au processus IA mobile (PID: {pid})")
            
            # Vérifier si le processus est toujours en cours d'exécution après 2 secondes
            import time
            time.sleep(2)
            
            try:
                # Si os.kill ne lève pas d'exception, le processus existe toujours
                os.kill(pid, 0)
                logger.warning("Le processus est toujours en cours d'exécution, envoi d'un signal SIGKILL")
                os.kill(pid, signal.SIGKILL)
                logger.info(f"Processus IA mobile (PID: {pid}) terminé de force")
            except OSError:
                # Le processus n'existe plus
                logger.info(f"Processus IA mobile (PID: {pid}) arrêté avec succès")
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du processus IA mobile: {e}")
    else:
        logger.info("Aucun processus d'IA mobile automatique en cours d'exécution")
    
    return False

def update_status_file(status="stopped"):
    """Met à jour le fichier de statut pour indiquer que l'IA est arrêtée"""
    status_file = os.path.join("instance", "mobile_cache", "ia_status.json")
    os.makedirs(os.path.dirname(status_file), exist_ok=True)
    
    status_data = {
        "status": status,
        "timestamp": import_datetime().now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": "IA mobile automatique arrêtée par l'utilisateur"
    }
    
    try:
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Statut de l'IA mis à jour: {status}")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du fichier de statut: {e}")

def import_datetime():
    """Importe le module datetime (importation retardée pour éviter l'overhead)"""
    from datetime import datetime
    return datetime

if __name__ == "__main__":
    logger.info("Tentative d'arrêt de l'IA mobile automatique...")
    
    # Trouver et arrêter le processus d'IA mobile
    if stop_mobile_ia_process():
        # Mettre à jour le fichier de statut
        update_status_file()
        logger.info("IA mobile automatique arrêtée avec succès")
        sys.exit(0)
    else:
        logger.info("Aucun processus d'IA mobile à arrêter ou échec de l'arrêt")
        sys.exit(1)
