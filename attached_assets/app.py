
import subprocess
import asyncio
import os
import json

# Répertoire de configuration
CONFIG_DIR = os.path.expanduser("~/.network_detect")
NETWORK_STATUS_FILE = os.path.join(CONFIG_DIR, "network_status.json")

async def detect_Bluetooth():
    try:
        result = subprocess.check_output(['hcitool', 'scan'], timeout=5).decode('utf-8')
        return len(result.strip().split('\n')) > 1
    except Exception as e:
        print(f"Erreur Bluetooth: {e}")
        return False

def detect_LTE():
    try:
        result = subprocess.check_output(['ip', 'link']).decode('utf-8')
        if "wwan" in result:
            return True
        else:
            return False
    except Exception as e:
        print(f"Erreur LTE: {e}")
        return False

def detect_eSIM():
    try:
        # Cette vérification est simplifiée et peut ne pas fonctionner sur tous les systèmes
        result = subprocess.check_output(['mmcli', '-L'], stderr=subprocess.DEVNULL).decode('utf-8')
        return "modem" in result
    except Exception as e:
        print(f"Erreur eSIM: {e}")
        return False

def detect_WiFi():
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

def save_network_status():
    """Enregistre l'état des différentes technologies réseau"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    status = {
        "lte": detect_LTE(),
        "bluetooth": loop.run_until_complete(detect_Bluetooth()),
        "esim": detect_eSIM(),
        "wifi": detect_WiFi(),
        "timestamp": datetime.now().isoformat() if 'datetime' in globals() else None
    }
    
    with open(NETWORK_STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)
    
    return status

# Fonction principale
def main():
    status = save_network_status()
    
    print("État des technologies réseau:")
    print(f"LTE: {'Actif' if status['lte'] else 'Inactif'}")
    print(f"Bluetooth: {'Appareils détectés' if status['bluetooth'] else 'Aucun appareil détecté'}")
    print(f"eSIM: {'Actif' if status['esim'] else 'Inactif'}")
    print(f"WiFi: {'Activé' if status['wifi'] else 'Désactivé'}")

if __name__ == "__main__":
    main()
