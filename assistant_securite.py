# Module d'assistant de sécurité conversationnel
import logging
import json
import os
import random
from datetime import datetime
from network_security import NetworkSecurityAnalyzer

# Configuration du logging
logger = logging.getLogger(__name__)

class AssistantSecurite:
    def __init__(self):
        self.security_analyzer = NetworkSecurityAnalyzer()
        self.conversations_dir = os.path.expanduser("~/.network_detect/conversations")
        os.makedirs(self.conversations_dir, exist_ok=True)
        
        # Charger les modèles de réponses
        self.load_response_templates()
    
    def load_response_templates(self):
        """Charge les modèles de réponses pour différents types de questions"""
        self.templates = {
            "greeting": [
                "Bonjour ! Je suis votre assistant de sécurité réseau. Comment puis-je vous aider aujourd'hui ?",
                "Bienvenue ! Je suis là pour répondre à vos questions sur la sécurité de vos réseaux WiFi.",
                "Salut ! Comment puis-je vous aider à améliorer la sécurité de vos réseaux ?"
            ],
            "general_security": [
                "La sécurité de votre réseau WiFi est essentielle pour protéger vos données personnelles. Voici quelques conseils : {advice}",
                "Pour améliorer la sécurité de votre réseau, je vous recommande de : {advice}",
                "D'après mon analyse, voici les mesures que vous pourriez prendre : {advice}"
            ],
            "encryption": [
                "Le chiffrement {encryption_type} offre {security_level}. {recommendation}",
                "Votre réseau utilise le protocole {encryption_type}, qui {security_description}. {recommendation}",
                "Le niveau de sécurité de {encryption_type} est {security_level}. {recommendation}"
            ],
            "password": [
                "Pour un mot de passe WiFi sécurisé, utilisez au moins 12 caractères avec un mélange de lettres, chiffres et symboles.",
                "Je recommande de changer votre mot de passe WiFi tous les 3 à 6 mois. Utilisez des phrases complexes plutôt que des mots simples.",
                "Un bon mot de passe WiFi ne doit jamais contenir d'informations personnelles. Optez pour une combinaison aléatoire de caractères."
            ],
            "unknown": [
                "Je ne suis pas sûr de comprendre votre question. Pourriez-vous reformuler ou me demander spécifiquement sur la sécurité WiFi ?",
                "Désolé, mais je me spécialise dans la sécurité des réseaux WiFi. Pourriez-vous me poser une question dans ce domaine ?",
                "Cette question semble sortir de mon domaine d'expertise. Je peux vous aider avec tout ce qui concerne la sécurité de vos réseaux."
            ],
            "network_specific": [
                "Concernant votre réseau '{network_name}', je constate que {observation}. {recommendation}",
                "D'après mon analyse du réseau '{network_name}', {observation}. Je vous conseille de {recommendation}",
                "Le réseau '{network_name}' présente les caractéristiques suivantes : {observation}. {recommendation}"
            ]
        }
        
        # Conseils de sécurité généraux
        self.security_advice = [
            "utiliser WPA3 si votre matériel le supporte",
            "changer régulièrement votre mot de passe WiFi",
            "désactiver WPS (WiFi Protected Setup)",
            "utiliser un SSID non identifiable",
            "activer le filtrage par adresse MAC",
            "mettre à jour le firmware de votre routeur",
            "créer un réseau invité séparé pour les visiteurs",
            "utiliser un VPN pour une protection supplémentaire"
        ]
        
        # Descriptions des types de chiffrement
        self.encryption_info = {
            "WPA3": {
                "level": "très élevé",
                "description": "offre la meilleure protection disponible actuellement",
                "recommendation": "Vous utilisez déjà le meilleur standard de sécurité. Assurez-vous que tous vos appareils sont également à jour."
            },
            "WPA2": {
                "level": "élevé",
                "description": "offre une bonne protection mais présente quelques vulnérabilités connues",
                "recommendation": "Envisagez de passer à WPA3 si votre routeur le supporte."
            },
            "WPA": {
                "level": "moyen",
                "description": "est obsolète et présente des vulnérabilités significatives",
                "recommendation": "Passez à WPA2 ou idéalement WPA3 dès que possible."
            },
            "WEP": {
                "level": "très faible",
                "description": "est facilement piratable en quelques minutes",
                "recommendation": "Changez immédiatement pour WPA2 ou WPA3 ! WEP n'offre pratiquement aucune protection."
            },
            "OPEN": {
                "level": "inexistant",
                "description": "n'offre aucune protection pour vos données",
                "recommendation": "Configurez immédiatement un chiffrement sur votre réseau ! Vos données sont actuellement exposées."
            }
        }
    
    def generate_response(self, user_input, conversation_id=None, network_data=None):
        """Génère une réponse en fonction de l'entrée utilisateur"""
        user_input = user_input.lower().strip()
        response = ""
        
        # Créer ou récupérer la conversation
        if not conversation_id:
            conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
        # Analyse de l'entrée utilisateur pour déterminer l'intention
        if any(word in user_input for word in ['bonjour', 'salut', 'hello', 'coucou']):
            response = random.choice(self.templates["greeting"])
        
        elif any(word in user_input for word in ['mot de passe', 'password', 'mdp']):
            response = random.choice(self.templates["password"])
        
        elif any(word in user_input for word in ['chiffrement', 'encryption', 'wpa', 'wep', 'sécurité']):
            if network_data and 'security' in network_data:
                encryption_type = self._get_encryption_type(network_data['security'])
                if encryption_type in self.encryption_info:
                    info = self.encryption_info[encryption_type]
                    response = random.choice(self.templates["encryption"]).format(
                        encryption_type=encryption_type,
                        security_level=info["level"],
                        security_description=info["description"],
                        recommendation=info["recommendation"]
                    )
                else:
                    # Type de chiffrement inconnu, donner des conseils généraux
                    random_advice = self._get_random_advice(3)
                    response = random.choice(self.templates["general_security"]).format(
                        advice=random_advice
                    )
            else:
                # Pas de données réseau, donner des conseils généraux sur le chiffrement
                response = "Pour un chiffrement optimal, je recommande d'utiliser WPA3 si votre matériel le supporte, ou au minimum WPA2. Évitez absolument WEP et les réseaux ouverts."
        
        elif any(word in user_input for word in ['conseil', 'recommandation', 'améliorer']):
            random_advice = self._get_random_advice(3)
            response = random.choice(self.templates["general_security"]).format(
                advice=random_advice
            )
        
        elif network_data and network_data.get('ssid', '') in user_input:
            # L'utilisateur pose une question sur un réseau spécifique
            network_name = network_data['ssid']
            signal_quality = self._evaluate_signal(network_data.get('rssi', -100))
            encryption_type = self._get_encryption_type(network_data.get('security', ''))
            
            observation = f"le signal est {signal_quality} et il utilise le chiffrement {encryption_type}"
            recommendation = "vérifiez que votre réseau utilise WPA2 ou WPA3 et un mot de passe fort"
            
            if encryption_type in self.encryption_info:
                recommendation = self.encryption_info[encryption_type]["recommendation"]
            
            response = random.choice(self.templates["network_specific"]).format(
                network_name=network_name,
                observation=observation,
                recommendation=recommendation
            )
        
        else:
            # Si l'intention de l'utilisateur n'est pas claire, utiliser une réponse générique
            response = random.choice(self.templates["unknown"])
        
        # Sauvegarder la conversation
        self._save_conversation(conversation_id, user_input, response, network_data)
        
        return {
            "response": response,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_conversation_history(self, conversation_id):
        """Récupère l'historique d'une conversation"""
        if not conversation_id:
            return []
            
        conversation_file = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        
        if not os.path.exists(conversation_file):
            return []
            
        try:
            with open(conversation_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de la conversation {conversation_id}: {e}")
            return []
    
    def get_all_conversations(self):
        """Récupère la liste de toutes les conversations"""
        conversations = []
        
        if not os.path.exists(self.conversations_dir):
            return conversations
            
        for filename in os.listdir(self.conversations_dir):
            if filename.endswith(".json"):
                conversation_id = filename.replace(".json", "")
                try:
                    with open(os.path.join(self.conversations_dir, filename), "r") as f:
                        data = json.load(f)
                        if data:
                            first_message = data[0] if data else {}
                            conversations.append({
                                "id": conversation_id,
                                "date": conversation_id[:8],  # Format YYYYMMDD
                                "message_count": len(data),
                                "first_message": first_message.get("user_input", "")[:50] + "..."
                            })
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture de {filename}: {e}")
        
        # Trier par date (plus récent en premier)
        conversations.sort(key=lambda x: x["date"], reverse=True)
        return conversations
    
    def _save_conversation(self, conversation_id, user_input, response, network_data=None):
        """Sauvegarde une conversation"""
        conversation_file = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        
        # Charger la conversation existante ou créer une nouvelle
        if os.path.exists(conversation_file):
            try:
                with open(conversation_file, "r") as f:
                    conversation = json.load(f)
            except Exception:
                conversation = []
        else:
            conversation = []
        
        # Ajouter le nouvel échange
        conversation.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "network_data": network_data
        })
        
        # Sauvegarder la conversation mise à jour
        with open(conversation_file, "w") as f:
            json.dump(conversation, f, indent=2)
    
    def _get_random_advice(self, count=3):
        """Retourne quelques conseils aléatoires sous forme de liste à puces"""
        selected_advice = random.sample(self.security_advice, min(count, len(self.security_advice)))
        return " ".join([f"• {advice};" for advice in selected_advice])
    
    def _get_encryption_type(self, security_string):
        """Détermine le type de chiffrement à partir de la chaîne de sécurité"""
        if not security_string:
            return "OPEN"
            
        security_upper = security_string.upper()
        
        if "WPA3" in security_upper:
            return "WPA3"
        elif "WPA2" in security_upper:
            return "WPA2"
        elif "WPA" in security_upper:
            return "WPA"
        elif "WEP" in security_upper:
            return "WEP"
        else:
            return "OPEN"
    
    def _evaluate_signal(self, rssi):
        """Évalue la qualité du signal en fonction du RSSI"""
        if rssi >= -50:
            return "excellent"
        elif rssi >= -60:
            return "très bon"
        elif rssi >= -70:
            return "bon"
        elif rssi >= -80:
            return "moyen"
        else:
            return "faible"
