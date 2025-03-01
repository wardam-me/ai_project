#!/usr/bin/env python3
"""
Module de création de mascottes de cybersécurité personnalisées pour NetSecure Pro
Ce module permet aux utilisateurs de créer des mascottes personnalisées
basées sur leur profil de sécurité et leurs préférences.
"""
import os
import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MascotCreator:
    """
    Créateur de mascottes de cybersécurité personnalisées
    Permet de générer des mascottes basées sur le profil de sécurité et les préférences
    """
    
    def __init__(self, data_dir: str = 'instance'):
        """
        Initialise le créateur de mascottes
        
        Args:
            data_dir: Répertoire pour les données des mascottes (par défaut: 'instance')
        """
        self.data_dir = data_dir
        self.mascots_file = os.path.join(data_dir, 'user_mascots.json')
        self.elements_file = os.path.join(data_dir, 'mascot_elements.json')
        self.mascots = self._load_mascots()
        self.elements = self._load_elements()
        
        # S'assurer que les éléments par défaut sont disponibles
        if not self.elements:
            self._initialize_default_elements()
            self._save_elements()
    
    def _load_mascots(self) -> Dict[str, Any]:
        """
        Charge les mascottes existantes depuis le fichier
        
        Returns:
            Dict: Dictionnaire des mascottes par utilisateur
        """
        if os.path.exists(self.mascots_file):
            try:
                with open(self.mascots_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Erreur de chargement des mascottes: {e}")
                return {}
        return {}
    
    def _save_mascots(self) -> None:
        """Sauvegarde les mascottes dans le fichier JSON"""
        os.makedirs(self.data_dir, exist_ok=True)
        try:
            with open(self.mascots_file, 'w', encoding='utf-8') as f:
                json.dump(self.mascots, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"Erreur de sauvegarde des mascottes: {e}")
    
    def _load_elements(self) -> Dict[str, Any]:
        """
        Charge les éléments de mascotte depuis le fichier
        
        Returns:
            Dict: Dictionnaire des éléments disponibles
        """
        if os.path.exists(self.elements_file):
            try:
                with open(self.elements_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Erreur de chargement des éléments: {e}")
                return {}
        return {}
    
    def _save_elements(self) -> None:
        """Sauvegarde les éléments dans le fichier JSON"""
        os.makedirs(self.data_dir, exist_ok=True)
        try:
            with open(self.elements_file, 'w', encoding='utf-8') as f:
                json.dump(self.elements, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"Erreur de sauvegarde des éléments: {e}")
    
    def _initialize_default_elements(self) -> None:
        """Initialise les éléments par défaut pour les mascottes"""
        self.elements = {
            "base": [
                {"id": "penguin", "name": "Pingouin", "security_level": "high", "svg": "penguin.svg"},
                {"id": "fox", "name": "Renard", "security_level": "medium", "svg": "fox.svg"},
                {"id": "owl", "name": "Hibou", "security_level": "high", "svg": "owl.svg"},
                {"id": "dragon", "name": "Dragon", "security_level": "very_high", "svg": "dragon.svg"},
                {"id": "cat", "name": "Chat", "security_level": "medium", "svg": "cat.svg"},
                {"id": "dog", "name": "Chien", "security_level": "medium", "svg": "dog.svg"}
            ],
            "hats": [
                {"id": "security_helmet", "name": "Casque de sécurité", "security_boost": 15, "svg": "security_helmet.svg"},
                {"id": "hacker_hood", "name": "Capuche de hacker", "security_boost": 10, "svg": "hacker_hood.svg"},
                {"id": "wizard_hat", "name": "Chapeau de magicien", "security_boost": 20, "svg": "wizard_hat.svg"},
                {"id": "crown", "name": "Couronne", "security_boost": 25, "svg": "crown.svg"},
                {"id": "cap", "name": "Casquette", "security_boost": 5, "svg": "cap.svg"}
            ],
            "accessories": [
                {"id": "shield", "name": "Bouclier", "security_boost": 30, "svg": "shield.svg"},
                {"id": "sword", "name": "Épée", "security_boost": 20, "svg": "sword.svg"},
                {"id": "wand", "name": "Baguette magique", "security_boost": 15, "svg": "wand.svg"},
                {"id": "key", "name": "Clé", "security_boost": 25, "svg": "key.svg"},
                {"id": "lock", "name": "Cadenas", "security_boost": 35, "svg": "lock.svg"}
            ],
            "outfits": [
                {"id": "armor", "name": "Armure", "security_boost": 40, "svg": "armor.svg"},
                {"id": "cloak", "name": "Cape", "security_boost": 25, "svg": "cloak.svg"},
                {"id": "suit", "name": "Costume", "security_boost": 30, "svg": "suit.svg"},
                {"id": "ninja", "name": "Ninja", "security_boost": 35, "svg": "ninja.svg"},
                {"id": "lab_coat", "name": "Blouse de laboratoire", "security_boost": 20, "svg": "lab_coat.svg"}
            ],
            "backgrounds": [
                {"id": "castle", "name": "Château", "theme": "defense", "svg": "castle.svg"},
                {"id": "matrix", "name": "Matrix", "theme": "hacker", "svg": "matrix.svg"},
                {"id": "cloud", "name": "Nuage", "theme": "modern", "svg": "cloud.svg"},
                {"id": "mountain", "name": "Montagne", "theme": "natural", "svg": "mountain.svg"},
                {"id": "datacenter", "name": "Centre de données", "theme": "tech", "svg": "datacenter.svg"}
            ]
        }
    
    def get_all_elements(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère tous les éléments disponibles pour la création de mascottes
        
        Returns:
            Dict: Dictionnaire de tous les éléments par catégorie
        """
        return self.elements
    
    def get_user_mascots(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les mascottes d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            List: Liste des mascottes de l'utilisateur
        """
        return self.mascots.get(user_id, [])
    
    def get_mascot(self, user_id: str, mascot_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une mascotte spécifique d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            mascot_id: ID de la mascotte
            
        Returns:
            Dict or None: Données de la mascotte ou None si non trouvée
        """
        user_mascots = self.get_user_mascots(user_id)
        for mascot in user_mascots:
            if mascot.get('id') == mascot_id:
                return mascot
        return None
    
    def create_mascot(self, user_id: str, mascot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée une nouvelle mascotte pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            mascot_data: Données de la mascotte (nom, éléments choisis, etc.)
            
        Returns:
            Dict: Données de la mascotte créée
        """
        # Générer un ID unique pour la mascotte
        mascot_id = f"mascot_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
        
        # Valider et compléter les données de la mascotte
        mascot = {
            "id": mascot_id,
            "name": mascot_data.get("name", "Mascotte sans nom"),
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "base": mascot_data.get("base", "penguin"),
            "hat": mascot_data.get("hat"),
            "accessory": mascot_data.get("accessory"),
            "outfit": mascot_data.get("outfit"),
            "background": mascot_data.get("background"),
            "colors": mascot_data.get("colors", {"primary": "#3498db", "secondary": "#2ecc71", "accent": "#e74c3c"}),
            "security_score": self._calculate_security_score(mascot_data),
            "personality": mascot_data.get("personality", "friendly")
        }
        
        # Ajouter la mascotte à la liste de l'utilisateur
        if user_id not in self.mascots:
            self.mascots[user_id] = []
        
        self.mascots[user_id].append(mascot)
        self._save_mascots()
        
        return mascot
    
    def update_mascot(self, user_id: str, mascot_id: str, mascot_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Met à jour une mascotte existante
        
        Args:
            user_id: ID de l'utilisateur
            mascot_id: ID de la mascotte à mettre à jour
            mascot_data: Nouvelles données de la mascotte
            
        Returns:
            Dict or None: Données de la mascotte mise à jour ou None si non trouvée
        """
        user_mascots = self.get_user_mascots(user_id)
        
        for i, mascot in enumerate(user_mascots):
            if mascot.get('id') == mascot_id:
                # Mettre à jour les champs de la mascotte
                mascot.update({
                    "name": mascot_data.get("name", mascot["name"]),
                    "last_modified": datetime.now().isoformat(),
                    "base": mascot_data.get("base", mascot["base"]),
                    "hat": mascot_data.get("hat", mascot.get("hat")),
                    "accessory": mascot_data.get("accessory", mascot.get("accessory")),
                    "outfit": mascot_data.get("outfit", mascot.get("outfit")),
                    "background": mascot_data.get("background", mascot.get("background")),
                    "colors": mascot_data.get("colors", mascot["colors"]),
                    "personality": mascot_data.get("personality", mascot["personality"])
                })
                
                # Recalculer le score de sécurité
                mascot["security_score"] = self._calculate_security_score(mascot)
                
                # Mettre à jour la mascotte dans la liste
                self.mascots[user_id][i] = mascot
                self._save_mascots()
                
                return mascot
        
        return None
    
    def delete_mascot(self, user_id: str, mascot_id: str) -> bool:
        """
        Supprime une mascotte
        
        Args:
            user_id: ID de l'utilisateur
            mascot_id: ID de la mascotte à supprimer
            
        Returns:
            bool: True si supprimée, False sinon
        """
        user_mascots = self.get_user_mascots(user_id)
        
        for i, mascot in enumerate(user_mascots):
            if mascot.get('id') == mascot_id:
                # Supprimer la mascotte de la liste
                del self.mascots[user_id][i]
                self._save_mascots()
                return True
        
        return False
    
    def generate_random_mascot(self, user_id: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Génère une mascotte aléatoire pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            name: Nom de la mascotte (facultatif)
            
        Returns:
            Dict: Données de la mascotte aléatoire
        """
        # Choisir des éléments aléatoires
        base = random.choice(self.elements["base"])["id"]
        hat = random.choice([item["id"] for item in self.elements["hats"]] + [None])
        accessory = random.choice([item["id"] for item in self.elements["accessories"]] + [None])
        outfit = random.choice([item["id"] for item in self.elements["outfits"]] + [None])
        background = random.choice([item["id"] for item in self.elements["backgrounds"]] + [None])
        
        # Générer des couleurs aléatoires
        colors = {
            "primary": "#{:06x}".format(random.randint(0, 0xFFFFFF)),
            "secondary": "#{:06x}".format(random.randint(0, 0xFFFFFF)),
            "accent": "#{:06x}".format(random.randint(0, 0xFFFFFF))
        }
        
        # Personnalités possibles
        personalities = ["friendly", "serious", "playful", "wise", "brave"]
        
        mascot_data = {
            "name": name or f"Mascotte {random.randint(1000, 9999)}",
            "base": base,
            "hat": hat,
            "accessory": accessory,
            "outfit": outfit,
            "background": background,
            "colors": colors,
            "personality": random.choice(personalities)
        }
        
        return self.create_mascot(user_id, mascot_data)
    
    def _calculate_security_score(self, mascot_data: Dict[str, Any]) -> int:
        """
        Calcule le score de sécurité d'une mascotte en fonction des éléments choisis
        
        Args:
            mascot_data: Données de la mascotte
            
        Returns:
            int: Score de sécurité (0-100)
        """
        score = 0
        
        # Points de base selon la base choisie
        base_id = mascot_data.get("base")
        for base in self.elements.get("base", []):
            if base["id"] == base_id:
                security_level = base.get("security_level", "medium")
                if security_level == "low":
                    score += 10
                elif security_level == "medium":
                    score += 20
                elif security_level == "high":
                    score += 30
                elif security_level == "very_high":
                    score += 40
                break
        
        # Points supplémentaires pour chaque élément
        for category in ["hats", "accessories", "outfits"]:
            element_id = mascot_data.get(category[:-1] if category.endswith("s") else category)
            if element_id:
                for element in self.elements.get(category, []):
                    if element["id"] == element_id:
                        score += element.get("security_boost", 0)
                        break
        
        # S'assurer que le score ne dépasse pas 100
        return min(score, 100)
    
    def generate_mascot_svg(self, mascot_data: Dict[str, Any]) -> str:
        """
        Génère une représentation SVG d'une mascotte
        
        Args:
            mascot_data: Données de la mascotte
            
        Returns:
            str: Code SVG de la mascotte
        """
        # Cette fonction serait idéalement implémentée pour combiner les différents
        # éléments SVG en une seule image, mais pour simplifier nous allons
        # supposer que nous avons tous les éléments SVG.
        
        # Dans une implémentation réelle, cette fonction combinerait les différents
        # éléments SVG (base, chapeau, accessoire, etc.) et appliquerait les couleurs.
        
        # Pour l'instant, on se contente de retourner un template de SVG adapté
        primary_color = mascot_data.get("colors", {}).get("primary", "#3498db")
        secondary_color = mascot_data.get("colors", {}).get("secondary", "#2ecc71")
        accent_color = mascot_data.get("colors", {}).get("accent", "#e74c3c")
        
        base_type = mascot_data.get("base", "penguin")
        
        # Générer un SVG de base en fonction du type de base
        if base_type == "penguin":
            return self._generate_penguin_svg(primary_color, secondary_color, accent_color)
        elif base_type == "fox":
            return self._generate_fox_svg(primary_color, secondary_color, accent_color)
        elif base_type == "owl":
            return self._generate_owl_svg(primary_color, secondary_color, accent_color)
        elif base_type == "dragon":
            return self._generate_dragon_svg(primary_color, secondary_color, accent_color)
        elif base_type == "cat":
            return self._generate_cat_svg(primary_color, secondary_color, accent_color)
        elif base_type == "dog":
            return self._generate_dog_svg(primary_color, secondary_color, accent_color)
        else:
            # SVG de base générique si le type n'est pas reconnu
            return self._generate_default_svg(primary_color, secondary_color, accent_color)
    
    def _generate_penguin_svg(self, primary_color: str, secondary_color: str, accent_color: str) -> str:
        """Génère un SVG pour une mascotte pingouin"""
        return f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="80" fill="{primary_color}" />
            <circle cx="80" cy="80" r="15" fill="white" />
            <circle cx="120" cy="80" r="15" fill="white" />
            <circle cx="80" cy="80" r="5" fill="black" />
            <circle cx="120" cy="80" r="5" fill="black" />
            <path d="M70,120 Q100,140 130,120" stroke="{accent_color}" stroke-width="5" fill="none" />
            <ellipse cx="100" cy="100" rx="20" ry="10" fill="{secondary_color}" />
            <text x="50" y="170" font-family="Arial" font-size="12" fill="white">Mascotte Pingouin</text>
        </svg>'''
    
    def _generate_fox_svg(self, primary_color: str, secondary_color: str, accent_color: str) -> str:
        """Génère un SVG pour une mascotte renard"""
        return f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <path d="M50,50 L100,20 L150,50 L130,120 Q100,140 70,120 Z" fill="{primary_color}" />
            <circle cx="80" cy="80" r="10" fill="white" />
            <circle cx="120" cy="80" r="10" fill="white" />
            <circle cx="80" cy="80" r="5" fill="black" />
            <circle cx="120" cy="80" r="5" fill="black" />
            <path d="M90,100 L100,110 L110,100" stroke="black" stroke-width="2" fill="none" />
            <path d="M70,50 L60,30 M130,50 L140,30" stroke="{secondary_color}" stroke-width="3" fill="none" />
            <path d="M100,110 L100,120" stroke="black" stroke-width="2" fill="none" />
            <ellipse cx="100" cy="125" rx="10" ry="5" fill="{accent_color}" />
            <text x="50" y="170" font-family="Arial" font-size="12" fill="white">Mascotte Renard</text>
        </svg>'''
    
    def _generate_owl_svg(self, primary_color: str, secondary_color: str, accent_color: str) -> str:
        """Génère un SVG pour une mascotte hibou"""
        return f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="70" fill="{primary_color}" />
            <circle cx="70" cy="80" r="25" fill="{secondary_color}" />
            <circle cx="130" cy="80" r="25" fill="{secondary_color}" />
            <circle cx="70" cy="80" r="10" fill="white" />
            <circle cx="130" cy="80" r="10" fill="white" />
            <circle cx="70" cy="80" r="5" fill="black" />
            <circle cx="130" cy="80" r="5" fill="black" />
            <path d="M85,120 Q100,130 115,120" stroke="black" stroke-width="3" fill="none" />
            <path d="M100,100 L100,120" stroke="black" stroke-width="2" fill="none" />
            <path d="M70,40 L100,20 L130,40" fill="{accent_color}" />
            <text x="50" y="170" font-family="Arial" font-size="12" fill="white">Mascotte Hibou</text>
        </svg>'''
    
    def _generate_dragon_svg(self, primary_color: str, secondary_color: str, accent_color: str) -> str:
        """Génère un SVG pour une mascotte dragon"""
        return f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <path d="M50,100 C50,60 150,60 150,100 C150,140 130,160 100,160 C70,160 50,140 50,100 Z" fill="{primary_color}" />
            <path d="M60,70 L50,40 M140,70 L150,40" stroke="{secondary_color}" stroke-width="4" fill="none" />
            <circle cx="80" cy="90" r="10" fill="white" />
            <circle cx="120" cy="90" r="10" fill="white" />
            <circle cx="80" cy="90" r="5" fill="black" />
            <circle cx="120" cy="90" r="5" fill="black" />
            <path d="M70,120 Q100,140 130,120" stroke="{accent_color}" stroke-width="5" fill="none" />
            <path d="M100,160 L100,180 L80,200 M100,180 L120,200" stroke="{secondary_color}" stroke-width="3" fill="none" />
            <text x="50" y="40" font-family="Arial" font-size="12" fill="white">Mascotte Dragon</text>
        </svg>'''
    
    def _generate_cat_svg(self, primary_color: str, secondary_color: str, accent_color: str) -> str:
        """Génère un SVG pour une mascotte chat"""
        return f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="70" fill="{primary_color}" />
            <path d="M50,80 L30,50 M150,80 L170,50" stroke="{secondary_color}" stroke-width="3" fill="none" />
            <circle cx="80" cy="80" r="10" fill="white" />
            <circle cx="120" cy="80" r="10" fill="white" />
            <circle cx="80" cy="80" r="5" fill="black" />
            <circle cx="120" cy="80" r="5" fill="black" />
            <path d="M90,100 L100,110 L110,100" stroke="black" stroke-width="2" fill="none" />
            <ellipse cx="100" cy="120" rx="15" ry="5" fill="{accent_color}" />
            <path d="M100,110 L100,120" stroke="black" stroke-width="2" fill="none" />
            <text x="50" y="170" font-family="Arial" font-size="12" fill="white">Mascotte Chat</text>
        </svg>'''
    
    def _generate_dog_svg(self, primary_color: str, secondary_color: str, accent_color: str) -> str:
        """Génère un SVG pour une mascotte chien"""
        return f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="70" fill="{primary_color}" />
            <path d="M40,70 L20,80 M160,70 L180,80" stroke="{secondary_color}" stroke-width="3" fill="none" />
            <circle cx="80" cy="80" r="10" fill="white" />
            <circle cx="120" cy="80" r="10" fill="white" />
            <circle cx="80" cy="80" r="5" fill="black" />
            <circle cx="120" cy="80" r="5" fill="black" />
            <path d="M70,120 Q100,140 130,120" stroke="{accent_color}" stroke-width="5" fill="none" />
            <ellipse cx="100" cy="100" rx="20" ry="10" fill="{secondary_color}" />
            <text x="50" y="170" font-family="Arial" font-size="12" fill="white">Mascotte Chien</text>
        </svg>'''
    
    def _generate_default_svg(self, primary_color: str, secondary_color: str, accent_color: str) -> str:
        """Génère un SVG par défaut pour une mascotte"""
        return f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="80" fill="{primary_color}" />
            <circle cx="70" cy="80" r="15" fill="white" />
            <circle cx="130" cy="80" r="15" fill="white" />
            <circle cx="70" cy="80" r="7" fill="black" />
            <circle cx="130" cy="80" r="7" fill="black" />
            <path d="M70,120 Q100,140 130,120" stroke="{accent_color}" stroke-width="5" fill="none" />
            <circle cx="100" cy="100" r="10" fill="{secondary_color}" />
            <text x="30" y="170" font-family="Arial" font-size="12" fill="white">Mascotte Personnalisée</text>
        </svg>'''
    
    def add_custom_element(self, category: str, element_data: Dict[str, Any]) -> bool:
        """
        Ajoute un élément personnalisé à une catégorie
        
        Args:
            category: Catégorie de l'élément ('base', 'hats', 'accessories', etc.)
            element_data: Données de l'élément à ajouter
            
        Returns:
            bool: True si ajouté avec succès, False sinon
        """
        if category not in self.elements:
            return False
        
        # Vérifier que l'élément a les champs requis
        if "id" not in element_data or "name" not in element_data or "svg" not in element_data:
            return False
        
        # Vérifier que l'ID n'existe pas déjà
        for elem in self.elements[category]:
            if elem["id"] == element_data["id"]:
                return False
        
        # Ajouter l'élément
        self.elements[category].append(element_data)
        self._save_elements()
        
        return True
    
    def get_mascot_security_level(self, security_score: int) -> Tuple[str, str]:
        """
        Détermine le niveau de sécurité et le titre correspondant pour un score donné
        
        Args:
            security_score: Score de sécurité (0-100)
            
        Returns:
            Tuple[str, str]: (niveau, titre descriptif)
        """
        if security_score >= 90:
            return "expert", "Expert en cybersécurité"
        elif security_score >= 75:
            return "advanced", "Gardien avancé"
        elif security_score >= 60:
            return "intermediate", "Protecteur confirmé"
        elif security_score >= 40:
            return "basic", "Défenseur en formation"
        else:
            return "novice", "Apprenti en sécurité"
    
    def get_personality_traits(self, personality: str) -> List[str]:
        """
        Récupère les traits de personnalité pour un type donné
        
        Args:
            personality: Type de personnalité
            
        Returns:
            List[str]: Traits de personnalité
        """
        traits = {
            "friendly": ["Accueillant", "Coopératif", "Positif", "Attentif"],
            "serious": ["Méthodique", "Rigoureux", "Vigilant", "Déterminé"],
            "playful": ["Inventif", "Spontané", "Optimiste", "Flexible"],
            "wise": ["Perspicace", "Réfléchi", "Prévoyant", "Expérimenté"],
            "brave": ["Courageux", "Audacieux", "Proactif", "Persévérant"]
        }
        
        return traits.get(personality, ["Polyvalent", "Adaptatif"])
    
    def generate_mascot_story(self, mascot_data: Dict[str, Any]) -> str:
        """
        Génère une histoire pour la mascotte basée sur ses caractéristiques
        
        Args:
            mascot_data: Données de la mascotte
            
        Returns:
            str: Histoire de la mascotte
        """
        name = mascot_data.get("name", "Mascotte")
        security_score = mascot_data.get("security_score", 50)
        personality = mascot_data.get("personality", "friendly")
        base = mascot_data.get("base", "penguin")
        
        level, title = self.get_mascot_security_level(security_score)
        traits = self.get_personality_traits(personality)
        
        base_descriptions = {
            "penguin": f"{name} est un pingouin numérique qui navigue avec agilité dans les eaux froides du cyberespace.",
            "fox": f"{name} est un renard rusé qui rôde dans les systèmes pour détecter les vulnérabilités.",
            "owl": f"{name} est un hibou observateur qui veille sur les réseaux la nuit comme le jour.",
            "dragon": f"{name} est un dragon puissant qui maintient un bouclier de feu contre les intrusions.",
            "cat": f"{name} est un chat curieux qui s'infiltre silencieusement pour évaluer les menaces.",
            "dog": f"{name} est un chien loyal qui monte la garde et aboie à l'approche des dangers."
        }
        
        intro = base_descriptions.get(base, f"{name} est votre gardien personnel dans le monde de la cybersécurité.")
        
        trait_sentence = f"En tant que {traits[0].lower()} et {traits[1].lower()}, {name.lower()} "
        
        personality_actions = {
            "friendly": "vous accompagne en toute convivialité dans votre parcours de sécurité.",
            "serious": "surveille avec rigueur chaque tentative d'intrusion dans vos systèmes.",
            "playful": "transforme l'apprentissage de la sécurité en une aventure ludique.",
            "wise": "partage sa sagesse et ses conseils précieux pour anticiper les menaces.",
            "brave": "n'hésite pas à affronter les cybermenaces les plus dangereuses."
        }
        
        action = personality_actions.get(personality, "est toujours prêt à vous assister dans vos défis de sécurité.")
        
        level_descriptions = {
            "expert": f"Avec une maîtrise exceptionnelle des technologies de protection, {name} représente l'élite de la cyberdéfense.",
            "advanced": f"Grâce à ses compétences avancées, {name} peut détecter et neutraliser la plupart des menaces sophistiquées.",
            "intermediate": f"{name} possède une solide expérience lui permettant de gérer efficacement les incidents de sécurité courants.",
            "basic": f"En constante progression, {name} développe chaque jour de nouvelles compétences pour mieux vous protéger.",
            "novice": f"Bien que débutant, {name} apprend rapidement et compense son manque d'expérience par un enthousiasme sans faille."
        }
        
        level_desc = level_descriptions.get(level, f"{name} s'adapte constamment pour répondre à vos besoins de sécurité.")
        
        conclusion = f"Ensemble, vous formez une équipe idéale pour renforcer votre sécurité numérique et profiter d'une expérience en ligne plus sereine."
        
        story = f"{intro} {trait_sentence}{action} {level_desc} {conclusion}"
        
        return story


# Si exécuté directement, initialiser les éléments par défaut
if __name__ == "__main__":
    creator = MascotCreator()
    logger.info(f"Module d'éléments de mascotte initialisé avec {sum(len(v) for v in creator.elements.values())} éléments au total")