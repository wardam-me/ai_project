#!/bin/bash

# Configuration des couleurs ANSI
VERT="\e[32m"
JAUNE="\e[33m"
ROUGE="\e[31m"
NEUTRE="\e[0m"

# Chemin de configuration
CONFIG_DIR="$HOME/.network_detect"
CONFIG_FILE="$CONFIG_DIR/config.sh"
LOG_FILE="$CONFIG_DIR/wifi_detect.log"
EXPORT_FILE="$CONFIG_DIR/wifi_results.json"

# Vérification si Termux est utilisé
is_termux() {
    [ -d "/data/data/com.termux/files/usr" ]
}

# Installation de termux-api si nécessaire
auto_install_termux() {
    if is_termux; then
        echo -e "${JAUNE}Installation de termux-api...${NEUTRE}"
        pkg update && pkg install termux-api jq -y
    else
        echo -e "${ROUGE}Ce script est conçu pour Termux.${NEUTRE}"
        exit 1
    fi
}

# Fonction de logging avec niveaux
log_wifi() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[${timestamp}] [$level] ${message}" | tee -a "${LOG_FILE}"
}

# Scan WiFi avec Termux
scan_wifi_termux() {
    if ! is_termux; then
        log_wifi "ERROR" "Ce script ne fonctionne que sous Termux."
        exit 1
    fi

    log_wifi "INFO" "Démarrage du scan WiFi avec Termux..."
    local wifi_data=$(termux-wifi-scaninfo 2>/dev/null)
    if [ -z "$wifi_data" ]; then
        log_wifi "ERROR" "Impossible d'obtenir les informations WiFi."
        exit 1
    fi

    echo "$wifi_data" | jq '.' | tee "$EXPORT_FILE"
    log_wifi "INFO" "Résultats enregistrés dans $EXPORT_FILE"
}

# Export des résultats en CSV
export_to_csv() {
    if [ ! -f "$EXPORT_FILE" ]; then
        log_wifi "ERROR" "Aucun résultat WiFi à exporter."
        exit 1
    fi

    echo "SSID,Signal,Fréquence" > "$CONFIG_DIR/wifi_results.csv"
    jq -r '.[] | "\(.ssid),\(.rssi),\(.frequency)"' "$EXPORT_FILE" >> "$CONFIG_DIR/wifi_results.csv"
    log_wifi "INFO" "Résultats exportés en CSV : $CONFIG_DIR/wifi_results.csv"
}

# Gestion des arguments
case "$1" in
    --install)
        auto_install_termux
        ;;
    --scan)
        scan_wifi_termux
        ;;
    --export)
        export_to_csv
        ;;
    --log)
        cat "$LOG_FILE"
        ;;
    *)
        echo -e "${JAUNE}Utilisation : $0 [--install | --scan | --export | --log]${NEUTRE}"
        exit 1
        ;;
esac

