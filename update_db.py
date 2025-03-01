#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de mise à jour de la base de données
Ce script ajoute la colonne last_seen à la table user si elle n'existe pas déjà
"""

import sqlite3
from datetime import datetime

# Chemin vers le fichier de base de données SQLite
DB_PATH = 'instance/app.db'

def add_last_seen_column():
    """Ajoute la colonne last_seen à la table user si elle n'existe pas déjà"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vérifier si la colonne existe déjà
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'last_seen' not in columns:
        print("Ajout de la colonne 'last_seen' à la table 'user'...")
        try:
            # Ajouter la colonne sans valeur par défaut
            cursor.execute("ALTER TABLE user ADD COLUMN last_seen TIMESTAMP")
            
            # Mettre à jour toutes les lignes existantes avec la date actuelle
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"UPDATE user SET last_seen = '{current_time}'")
            
            conn.commit()
            print("Colonne 'last_seen' ajoutée avec succès et valeurs mises à jour.")
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout de la colonne: {e}")
            conn.rollback()
    else:
        print("La colonne 'last_seen' existe déjà dans la table 'user'.")
    
    conn.close()

def main():
    """Fonction principale"""
    print("Mise à jour de la base de données...")
    add_last_seen_column()
    print("Mise à jour terminée.")

if __name__ == "__main__":
    main()