
import subprocess
import asyncio
import os
import json
from datetime import datetime

# Répertoire de configuration
CONFIG_DIR = os.path.expanduser("~/.network_detect")
NETWORK_STATUS_FILE = os.path.join(CONFIG_DIR, "network_status.json")

class NetworkDetector:
    """Classe pour détecter les différentes technologies réseau"""
    
    @staticmethod
    async def detect_bluetooth():
        try:
            result = subprocess.check_output(['hcitool', 'scan'], timeout=5).decode('utf-8')
            return len(result.strip().split('\n')) > 1
        except Exception as e:
            print(f"Erreur Bluetooth: {e}")
            return False

    @staticmethod
    def detect_lte():
        try:
            result = subprocess.check_output(['ip', 'link']).decode('utf-8')
            if "wwan" in result:
                return True
            else:
                return False
        except Exception as e:
            print(f"Erreur LTE: {e}")
            return False

    @staticmethod
    def detect_esim():
        try:
            # Cette vérification est simplifiée
            result = subprocess.check_output(['mmcli', '-L'], stderr=subprocess.DEVNULL).decode('utf-8')
            return "modem" in result
        except Exception as e:
            print(f"Erreur eSIM: {e}")
            return False

    @staticmethod
    def detect_wifi():
        try:
            result = subprocess.check_output(['iwconfig'], stderr=subprocess.DEVNULL).decode('utf-8')
            return "ESSID" in result
        except Exception as e:
            print(f"Erreur WiFi: {e}")
            # Tentative alternative avec ip
            try:
                result = subprocess.check_output(['ip', 'link']).decode('utf-8')
                return "wlan" in result or "wlp" in result
            except Exception:
                return False
    
    @classmethod
    async def get_all_network_status(cls):
        """Récupère l'état de toutes les technologies réseau"""
        return {
            "lte": cls.detect_lte(),
            "bluetooth": await cls.detect_bluetooth(),
            "esim": cls.detect_esim(),
            "wifi": cls.detect_wifi(),
            "timestamp": datetime.now().isoformat()
        }
    
    @classmethod
    async def save_network_status(cls):
        """Enregistre l'état des différentes technologies réseau"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        status = await cls.get_all_network_status()
        
        with open(NETWORK_STATUS_FILE, 'w') as f:
            json.dump(status, f, indent=2)
        
        return status
    
    @staticmethod
    def get_saved_status():
        """Récupère le dernier état enregistré des technologies réseau"""
        if not os.path.exists(NETWORK_STATUS_FILE):
            return None
            
        try:
            with open(NETWORK_STATUS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier de statut: {e}")
            return None

# Fonction pour exécuter depuis la ligne de commande
async def main():
    status = await NetworkDetector.save_network_status()
    
    print("État des technologies réseau:")
    print(f"LTE: {'Actif' if status['lte'] else 'Inactif'}")
    print(f"Bluetooth: {'Appareils détectés' if status['bluetooth'] else 'Aucun appareil détecté'}")
    print(f"eSIM: {'Actif' if status['esim'] else 'Inactif'}")
    print(f"WiFi: {'Activé' if status['wifi'] else 'Désactivé'}")

if __name__ == "__main__":
    asyncio.run(main())
