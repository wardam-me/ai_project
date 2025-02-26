"""
Module de gestion de la topologie du réseau
"""
import os
import json
import random
import time
from datetime import datetime, timedelta

class NetworkTopology:
    """Gestion de la topologie du réseau et des relations entre appareils"""
    
    def __init__(self):
        """Initialisation du gestionnaire de topologie"""
        self.topology_file = 'topology_data.json'
        self.layout_file = 'topology_layout.json'
        self.devices = []
        self.layout = {}
        self.load_topology()
        self.load_layout()
    
    def load_topology(self):
        """Charge les données de topologie depuis le fichier, ou génère des données de test"""
        if os.path.exists(self.topology_file):
            try:
                with open(self.topology_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.devices = data.get('devices', [])
            except (json.JSONDecodeError, IOError):
                # En cas d'erreur, générer des données de test
                self._generate_sample_devices()
        else:
            # Si le fichier n'existe pas, générer des données de test
            self._generate_sample_devices()
    
    def load_layout(self):
        """Charge la disposition des appareils depuis le fichier"""
        if os.path.exists(self.layout_file):
            try:
                with open(self.layout_file, 'r', encoding='utf-8') as f:
                    self.layout = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.layout = {}
    
    def save_topology(self):
        """Sauvegarde les données de topologie dans un fichier"""
        with open(self.topology_file, 'w', encoding='utf-8') as f:
            json.dump({'devices': self.devices}, f, indent=2)
    
    def save_layout(self, layout_data):
        """Sauvegarde la disposition des appareils"""
        self.layout = layout_data
        with open(self.layout_file, 'w', encoding='utf-8') as f:
            json.dump(self.layout, f, indent=2)
    
    def get_topology_data(self):
        """Récupère les données de topologie avec la disposition enregistrée"""
        self._update_devices_status()
        
        # Fusionner les informations de disposition avec les données d'appareils
        for device in self.devices:
            device_id = device.get('mac_address')
            if device_id in self.layout:
                device['position'] = self.layout[device_id]
        
        return {
            'devices': self.devices,
            'router': {
                'name': 'Router/AP',
                'connection_count': len(self.devices)
            }
        }
    
    def update_device_security(self, mac_address, security_data):
        """Met à jour les informations de sécurité d'un appareil"""
        for device in self.devices:
            if device['mac_address'] == mac_address:
                device.update(security_data)
                self.save_topology()
                return True
        return False
    
    def add_device(self, device_data):
        """Ajoute un nouvel appareil à la topologie"""
        # Vérifier si l'appareil existe déjà
        for device in self.devices:
            if device['mac_address'] == device_data['mac_address']:
                device.update(device_data)
                self.save_topology()
                return device
        
        # Ajouter le nouvel appareil
        self.devices.append(device_data)
        self.save_topology()
        return device_data
    
    def remove_device(self, mac_address):
        """Supprime un appareil de la topologie"""
        for i, device in enumerate(self.devices):
            if device['mac_address'] == mac_address:
                removed = self.devices.pop(i)
                self.save_topology()
                return removed
        return None
    
    def _update_devices_status(self):
        """Met à jour aléatoirement le statut des appareils pour la simulation"""
        for device in self.devices:
            # Mise à jour de l'activité
            if random.random() < 0.8:  # 80% de chance d'être actif
                device['status'] = 'online'
                device['last_seen'] = datetime.now().isoformat()
            else:
                device['status'] = 'offline'
                
            # Mise à jour aléatoire de la force du signal
            if random.random() < 0.1:  # 10% de chance de changer
                device['signal_strength'] = random.choice(['high', 'medium', 'low'])
    
    def _generate_sample_devices(self):
        """Génère des exemples d'appareils pour la démonstration"""
        self.devices = []
        
        # Liste d'appareils et de fabricants
        device_types = [
            {'type': 'Smartphone', 'manufacturers': ['Samsung', 'Apple', 'Xiaomi', 'Huawei']},
            {'type': 'Tablette', 'manufacturers': ['Apple', 'Samsung', 'Lenovo']},
            {'type': 'Ordinateur portable', 'manufacturers': ['Dell', 'HP', 'Lenovo', 'Apple']},
            {'type': 'Smart TV', 'manufacturers': ['Samsung', 'LG', 'Sony']},
            {'type': 'Enceinte connectée', 'manufacturers': ['Sonos', 'Google', 'Amazon']},
            {'type': 'Caméra IP', 'manufacturers': ['Nest', 'Ring', 'Arlo']},
            {'type': 'Console de jeu', 'manufacturers': ['Sony', 'Microsoft', 'Nintendo']}
        ]
        
        # Nombre d'appareils à générer (entre 6 et 12)
        num_devices = random.randint(6, 12)
        
        for i in range(num_devices):
            # Sélectionner un type d'appareil et un fabricant aléatoire
            device_info = random.choice(device_types)
            device_type = device_info['type']
            manufacturer = random.choice(device_info['manufacturers'])
            
            # Déterminer le type de connexion (80% sans fil, 20% filaire)
            connection_type = 'wireless' if random.random() < 0.8 else 'ethernet'
            
            # Générer une adresse MAC aléatoire
            mac_address = self._generate_random_mac()
            
            # Générer une adresse IP aléatoire dans le réseau 192.168.1.x
            ip_address = f'192.168.1.{random.randint(2, 254)}'
            
            # Déterminer la force du signal pour les appareils sans fil
            signal_strength = random.choice(['high', 'medium', 'low']) if connection_type == 'wireless' else 'high'
            
            # Générer une date de première détection (entre 1 et 30 jours dans le passé)
            days_ago = random.randint(1, 30)
            first_seen = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            # Générer une date de dernière activité (entre 0 et 2 jours dans le passé)
            hours_ago = random.randint(0, 48)
            last_seen = (datetime.now() - timedelta(hours=hours_ago)).isoformat()
            
            # Déterminer un score de sécurité aléatoire
            security_score = random.randint(30, 100)
            
            # Créer l'appareil
            device = {
                'device_name': f'{manufacturer} {device_type} {i+1}',
                'device_type': device_type,
                'manufacturer': manufacturer,
                'mac_address': mac_address,
                'ip_address': ip_address,
                'connection_type': connection_type,
                'signal_strength': signal_strength,
                'security_score': security_score,
                'first_seen': first_seen,
                'last_seen': last_seen,
                'status': 'online' if random.random() < 0.8 else 'offline'
            }
            
            self.devices.append(device)
        
        # Sauvegarder les appareils générés
        self.save_topology()
    
    def _generate_random_mac(self):
        """Génère une adresse MAC aléatoire"""
        mac = [random.randint(0, 255) for _ in range(6)]
        return ':'.join('{:02x}'.format(x) for x in mac)