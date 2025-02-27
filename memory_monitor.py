
"""
Module de surveillance de la mémoire pour l'application NetSecure Pro
"""
import os
import psutil
import logging
from datetime import datetime

# Configuration du logging
logger = logging.getLogger(__name__)

class MemoryMonitor:
    """Classe pour surveiller l'utilisation de la mémoire de l'application"""
    
    @staticmethod
    def get_memory_usage():
        """Récupère les informations sur l'utilisation de la mémoire"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Conversion en MB pour plus de lisibilité
        rss_mb = memory_info.rss / (1024 * 1024)
        vms_mb = memory_info.vms / (1024 * 1024)
        
        # Récupérer les informations système
        system_memory = psutil.virtual_memory()
        total_mb = system_memory.total / (1024 * 1024)
        available_mb = system_memory.available / (1024 * 1024)
        used_percent = system_memory.percent
        
        return {
            'process': {
                'rss_mb': round(rss_mb, 2),
                'vms_mb': round(vms_mb, 2),
                'pid': os.getpid()
            },
            'system': {
                'total_mb': round(total_mb, 2),
                'available_mb': round(available_mb, 2),
                'used_percent': used_percent
            },
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def log_memory_usage():
        """Enregistre l'utilisation de la mémoire dans les logs"""
        memory_info = MemoryMonitor.get_memory_usage()
        process_info = memory_info['process']
        system_info = memory_info['system']
        
        logger.info(
            f"Mémoire du processus: {process_info['rss_mb']} MB (RSS), "
            f"{process_info['vms_mb']} MB (VMS) | "
            f"Système: {system_info['used_percent']}% utilisé, "
            f"{system_info['available_mb']} MB disponible"
        )
        
        return memory_info
    
    @staticmethod
    def check_memory_threshold(threshold_percent=80):
        """Vérifie si l'utilisation de la mémoire dépasse un seuil défini"""
        memory_info = MemoryMonitor.get_memory_usage()
        system_used_percent = memory_info['system']['used_percent']
        
        if system_used_percent > threshold_percent:
            logger.warning(
                f"ALERTE: Utilisation de la mémoire élevée ({system_used_percent}%), "
                f"supérieure au seuil de {threshold_percent}%"
            )
            return True
        
        return False
