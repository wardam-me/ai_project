#!/usr/bin/env python3
"""
Point d'entrée principal pour NetSecure Pro - Analyse de sécurité réseau WiFi
"""
import os
import logging
from memory_monitor import MemoryMonitor
from app import app, socketio

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Point d'entrée principal
if __name__ == '__main__':
    # Log initial de l'utilisation de la mémoire au démarrage
    MemoryMonitor.log_memory_usage()
    
    # Démarrer l'application Flask avec l'extension SocketIO
    port = int(os.environ.get("PORT", 5000))
    # Si le port est déjà utilisé, essayer des ports alternatifs
    alternative_ports = [5001, 5002, 5003, 8080, 8000]
    current_port = port
    debug = True
    
    while True:
        try:
            logger.info(f"Tentative de démarrage du serveur sur le port {current_port}...")
            socketio.run(app, host="0.0.0.0", port=current_port, debug=debug, allow_unsafe_werkzeug=True)
            break  # Si le serveur démarre sans erreur, sortir de la boucle
        except OSError as e:
            if "Address already in use" in str(e):
                logger.warning(f"Port {current_port} déjà en cours d'utilisation.")
                if alternative_ports:
                    current_port = alternative_ports.pop(0)
                    logger.info(f"Essai avec le port alternatif {current_port}...")
                else:
                    logger.error("Tous les ports alternatifs sont utilisés. Impossible de démarrer le serveur.")
                    raise
            else:
                logger.error(f"Erreur lors du démarrage du serveur: {e}")
                raise