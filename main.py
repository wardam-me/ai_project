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
    debug = True
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)