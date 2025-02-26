#!/bin/bash

RESEAU="192.168.2.0/24"
PORTS="22,23,80,443,554,8080"
TEMP_FILE="scan_result.txt"

echo "[*] Scan du réseau en cours..."
nmap -p $PORTS -T4 --open $RESEAU -oG - | awk '/Up$/{print $2}' > $TEMP_FILE

echo "[*] Analyse des appareils détectés..."
while read -r IP; do
    echo "[+] Vérification de l'IP : $IP"

    # Scan des ports ouverts
    echo "  -> Scan des ports ouverts..."
    nmap -p $PORTS --open $IP | grep "open" | while read -r line; do
        echo "     $line"
    done

    # Vérifie la présence d'un serveur Web
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$IP)
    HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$IP --insecure)

    if [[ "$HTTP_STATUS" == "200" || "$HTTPS_STATUS" == "200" ]]; then
        echo "  -> Serveur Web détecté sur $IP"
    fi

done < $TEMP_FILE

echo "[*] Analyse terminée !"
