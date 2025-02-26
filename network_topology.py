"""
Module de gestion de la topologie du réseau
"""
import os
import json
import random
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class NetworkTopology:
    """Gestion de la topologie du réseau et des relations entre appareils"""
    
    def __init__(self):
        """Initialisation du gestionnaire de topologie"""
        self.topology_data = {
            'devices': [],
            'connections': [],
            'timestamp': None
        }
        self.layout_data = {}
        
        # Créer les dossiers de données si nécessaire
        os.makedirs('instance', exist_ok=True)
        
        # Chargement des données
        self.load_topology()
        self.load_layout()
        
        # Si aucune donnée n'est disponible, générer des exemples
        if not self.topology_data['devices']:
            self._generate_sample_devices()
    
    def load_topology(self):
        """Charge les données de topologie depuis le fichier, ou génère des données de test"""
        try:
            if os.path.exists('instance/topology_data.json'):
                with open('instance/topology_data.json', 'r') as f:
                    self.topology_data = json.load(f)
                logger.info("Données de topologie chargées")
            else:
                logger.info("Aucun fichier de données de topologie existant")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données de topologie: {e}")
    
    def load_layout(self):
        """Charge la disposition des appareils depuis le fichier"""
        try:
            if os.path.exists('instance/layout_data.json'):
                with open('instance/layout_data.json', 'r') as f:
                    self.layout_data = json.load(f)
                logger.info("Disposition chargée")
            else:
                logger.info("Aucun fichier de disposition existant")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la disposition: {e}")
    
    def save_topology(self):
        """Sauvegarde les données de topologie dans un fichier"""
        try:
            self.topology_data['timestamp'] = datetime.now().isoformat()
            with open('instance/topology_data.json', 'w') as f:
                json.dump(self.topology_data, f, indent=2)
            logger.info("Données de topologie sauvegardées")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données de topologie: {e}")
    
    def save_layout(self, layout_data):
        """Sauvegarde la disposition des appareils"""
        try:
            if 'mac_address' in layout_data:
                mac_address = layout_data['mac_address']
                self.layout_data[mac_address] = {
                    'x': layout_data['x'],
                    'y': layout_data['y']
                }
                
                # Mise à jour de la position dans les appareils de la topologie
                for device in self.topology_data['devices']:
                    if device['mac_address'] == mac_address:
                        device['x'] = layout_data['x']
                        device['y'] = layout_data['y']
                        break
                
                with open('instance/layout_data.json', 'w') as f:
                    json.dump(self.layout_data, f, indent=2)
                logger.info(f"Disposition mise à jour pour l'appareil {mac_address}")
            else:
                logger.warning("Données de disposition incorrectes")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la disposition: {e}")
    
    def get_topology_data(self):
        """Récupère les données de topologie avec la disposition enregistrée"""
        # Mise à jour aléatoire du statut des appareils pour la simulation
        self._update_devices_status()
        
        # Applique les positions sauvegardées
        for device in self.topology_data['devices']:
            mac_address = device['mac_address']
            if mac_address in self.layout_data:
                device['x'] = self.layout_data[mac_address]['x']
                device['y'] = self.layout_data[mac_address]['y']
        
        return self.topology_data
    
    def update_device_security(self, mac_address, security_data):
        """Met à jour les informations de sécurité d'un appareil"""
        for device in self.topology_data['devices']:
            if device['mac_address'] == mac_address:
                # Mise à jour du score de sécurité
                if 'security_score' in security_data:
                    device['security_score'] = security_data['security_score']
                
                # Mise à jour d'autres paramètres de sécurité
                if 'security_issues' in security_data:
                    device['security_issues'] = security_data['security_issues']
                
                self.save_topology()
                logger.info(f"Informations de sécurité mises à jour pour {mac_address}")
                return True
        
        logger.warning(f"Appareil non trouvé: {mac_address}")
        return False
    
    def add_device(self, device_data):
        """Ajoute un nouvel appareil à la topologie"""
        # Vérifier si l'appareil existe déjà
        for device in self.topology_data['devices']:
            if device['mac_address'] == device_data['mac_address']:
                logger.warning(f"L'appareil {device_data['mac_address']} existe déjà")
                return False
        
        # Ajout de l'appareil
        self.topology_data['devices'].append(device_data)
        self.save_topology()
        logger.info(f"Nouvel appareil ajouté: {device_data['mac_address']}")
        return True
    
    def remove_device(self, mac_address):
        """Supprime un appareil de la topologie"""
        # Supprimer l'appareil
        initial_count = len(self.topology_data['devices'])
        self.topology_data['devices'] = [d for d in self.topology_data['devices'] 
                                         if d['mac_address'] != mac_address]
        
        # Supprimer les connexions associées
        self.topology_data['connections'] = [c for c in self.topology_data['connections'] 
                                            if c['source'] != mac_address and c['target'] != mac_address]
        
        # Vérifier si l'appareil a été supprimé
        if len(self.topology_data['devices']) < initial_count:
            self.save_topology()
            
            # Supprimer également de la disposition
            if mac_address in self.layout_data:
                del self.layout_data[mac_address]
                try:
                    with open('instance/layout_data.json', 'w') as f:
                        json.dump(self.layout_data, f, indent=2)
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de la disposition: {e}")
            
            logger.info(f"Appareil supprimé: {mac_address}")
            return True
        else:
            logger.warning(f"Appareil non trouvé: {mac_address}")
            return False
    
    def _update_devices_status(self):
        """Met à jour aléatoirement le statut des appareils pour la simulation"""
        for device in self.topology_data['devices']:
            # 90% de chance que l'appareil soit en ligne
            device['online'] = random.random() < 0.9
            device['last_seen'] = datetime.now().isoformat()
            
            # Mise à jour aléatoire des données pour la simulation
            if 'signal_strength' in device:
                # Légère variation du signal
                variation = random.randint(-3, 3)
                device['signal_strength'] = max(-95, min(-30, device['signal_strength'] + variation))
    
    def _generate_sample_devices(self):
        """Génère des exemples d'appareils pour la démonstration"""
        # Appareil routeur principal
        router = {
            'mac_address': '00:11:22:33:44:55',
            'name': 'Routeur WiFi Principal',
            'device_type': 'router',
            'manufacturer': 'Netgear',
            'model': 'Nighthawk RAX50',
            'firmware_version': 'V1.0.3.80',
            'ip_address': '192.168.1.1',
            'connection_type': 'ethernet',
            'online': True,
            'signal_strength': -35,
            'security_score': 85,
            'os': 'Propriétaire',
            'last_seen': datetime.now().isoformat(),
            'x': 400,
            'y': 300
        }
        
        # Appareil ordinateur portable
        laptop = {
            'mac_address': '66:77:88:99:AA:BB',
            'name': 'Ordinateur Portable',
            'device_type': 'laptop',
            'manufacturer': 'Dell',
            'model': 'XPS 15',
            'ip_address': '192.168.1.100',
            'connection_type': 'wifi',
            'online': True,
            'signal_strength': -55,
            'security_score': 75,
            'os': 'Windows 11',
            'last_seen': datetime.now().isoformat(),
            'x': 300,
            'y': 200
        }
        
        # Appareil smartphone
        phone = {
            'mac_address': 'CC:DD:EE:FF:00:11',
            'name': 'Smartphone',
            'device_type': 'phone',
            'manufacturer': 'Samsung',
            'model': 'Galaxy S22',
            'ip_address': '192.168.1.101',
            'connection_type': 'wifi',
            'online': True,
            'signal_strength': -60,
            'security_score': 65,
            'os': 'Android 13',
            'last_seen': datetime.now().isoformat(),
            'x': 500,
            'y': 200
        }
        
        # Appareil IoT (caméra)
        camera = {
            'mac_address': '22:33:44:55:66:77',
            'name': 'Caméra IP',
            'device_type': 'iot',
            'manufacturer': 'Hikvision',
            'model': 'DS-2CD2342WD-I',
            'ip_address': '192.168.1.102',
            'connection_type': 'wifi',
            'online': True,
            'signal_strength': -65,
            'security_score': 35,
            'os': 'Propriétaire',
            'last_seen': datetime.now().isoformat(),
            'x': 600,
            'y': 400
        }
        
        # Appareil télévision intelligente
        tv = {
            'mac_address': '88:99:AA:BB:CC:DD',
            'name': 'Smart TV',
            'device_type': 'tv',
            'manufacturer': 'LG',
            'model': 'OLED C2',
            'ip_address': '192.168.1.103',
            'connection_type': 'wifi',
            'online': True,
            'signal_strength': -70,
            'security_score': 55,
            'os': 'WebOS 6.0',
            'last_seen': datetime.now().isoformat(),
            'x': 200,
            'y': 400
        }
        
        # Ajout des appareils à la topologie
        self.topology_data['devices'] = [router, laptop, phone, camera, tv]
        
        # Création des connexions entre appareils
        self.topology_data['connections'] = [
            {'source': '00:11:22:33:44:55', 'target': '66:77:88:99:AA:BB', 'connection_type': 'wifi'},
            {'source': '00:11:22:33:44:55', 'target': 'CC:DD:EE:FF:00:11', 'connection_type': 'wifi'},
            {'source': '00:11:22:33:44:55', 'target': '22:33:44:55:66:77', 'connection_type': 'wifi'},
            {'source': '00:11:22:33:44:55', 'target': '88:99:AA:BB:CC:DD', 'connection_type': 'wifi'}
        ]
        
        # Sauvegarde des données générées
        self.save_topology()
        
        # Création des données de disposition
        self.layout_data = {
            '00:11:22:33:44:55': {'x': 400, 'y': 300},
            '66:77:88:99:AA:BB': {'x': 300, 'y': 200},
            'CC:DD:EE:FF:00:11': {'x': 500, 'y': 200},
            '22:33:44:55:66:77': {'x': 600, 'y': 400},
            '88:99:AA:BB:CC:DD': {'x': 200, 'y': 400}
        }
        
        try:
            with open('instance/layout_data.json', 'w') as f:
                json.dump(self.layout_data, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la disposition: {e}")
    
    def _generate_random_mac(self):
        """Génère une adresse MAC aléatoire"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])