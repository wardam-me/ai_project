import subprocess

def detect_LTE():
    try:
        result = subprocess.check_output(['ip', 'link']).decode('utf-8')
        if "wwan" in result:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")

# Fonction principale
def main():
    if detect_LTE():
        print("LTE is active")
    else:
        print("LTE is not active")

    loop = asyncio.get_event_loop()
    if loop.run_until_complete(detect_Bluetooth()):
        print("Bluetooth devices detected")
    else:
        print("No Bluetooth devices detected")

    if detect_eSIM():
        print("eSIM is active")
    else:
        print("eSIM is not active")

    if detect_WiFi():
        print("WiFi is enabled")
    else:
        print("WiFi is not enabled")

if __name__ == "__main__":
    main()
