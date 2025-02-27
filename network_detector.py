
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
        except FileNotFoundError as e:
            print(f"Commande hcitool non trouvée: {e}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de hcitool: {e}")
            return False
        except subprocess.TimeoutExpired as e:
            print(f"Délai d'attente dépassé pour la détection Bluetooth: {e}")
            return False
        except UnicodeDecodeError as e:
            print(f"Erreur de décodage de la sortie Bluetooth: {e}")
            return False
        except OSError as e:
            print(f"Erreur système lors de la détection Bluetooth: {e}")
            return False

    @staticmethod
    def detect_lte():
        try:
            result = subprocess.check_output(['ip', 'link']).decode('utf-8')
            if "wwan" in result:
                return True
            else:
                return False
        except FileNotFoundError as e:
            print(f"Commande ip non trouvée: {e}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de ip link: {e}")
            return False
        except UnicodeDecodeError as e:
            print(f"Erreur de décodage de la sortie ip: {e}")
            return False
        except OSError as e:
            print(f"Erreur système lors de la détection LTE: {e}")
            return False

    @staticmethod
    def detect_esim():
        try:
            # Cette vérification est simplifiée
            result = subprocess.check_output(['mmcli', '-L'], stderr=subprocess.DEVNULL).decode('utf-8')
            return "modem" in result
        except FileNotFoundError as e:
            print(f"Commande mmcli non trouvée: {e}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de mmcli: {e}")
            return False
        except UnicodeDecodeError as e:
            print(f"Erreur de décodage de la sortie mmcli: {e}")
            return False
        except OSError as e:
            print(f"Erreur système lors de la détection eSIM: {e}")
            return False

    @staticmethod
    def detect_wifi():
        try:
            result = subprocess.check_output(['iwconfig'], stderr=subprocess.DEVNULL).decode('utf-8')
            return "ESSID" in result
        except FileNotFoundError as e:
            print(f"Commande iwconfig non trouvée: {e}")
            # Tentative alternative avec ip
            try:
                result = subprocess.check_output(['ip', 'link']).decode('utf-8')
                return "wlan" in result or "wlp" in result
            except FileNotFoundError as e2:
                print(f"Commande ip non trouvée (alternative): {e2}")
                return False
            except subprocess.CalledProcessError as e2:
                print(f"Erreur lors de l'exécution de ip link (alternative): {e2}")
                return False
            except UnicodeDecodeError as e2:
                print(f"Erreur de décodage de la sortie ip (alternative): {e2}")
                return False
            except OSError as e2:
                print(f"Erreur système lors de la détection WiFi alternative: {e2}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de iwconfig: {e}")
            # Tentative alternative avec ip
            try:
                result = subprocess.check_output(['ip', 'link']).decode('utf-8')
                return "wlan" in result or "wlp" in result
            except Exception as e2:
                print(f"Erreur alternative WiFi: {e2}")
                return False
        except UnicodeDecodeError as e:
            print(f"Erreur de décodage de la sortie iwconfig: {e}")
            return False
        except OSError as e:
            print(f"Erreur système lors de la détection WiFi: {e}")
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
        except FileNotFoundError as e:
            print(f"Fichier de statut réseau introuvable: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Format JSON invalide dans le fichier de statut réseau: {e}")
            return None
        except PermissionError as e:
            print(f"Erreur de permission lors de la lecture du fichier de statut: {e}")
            return None
        except IOError as e:
            print(f"Erreur d'I/O lors de la lecture du fichier de statut: {e}")
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
