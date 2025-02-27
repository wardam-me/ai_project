# Module d'assistant de sécurité conversationnel avancé pour la cyberdéfense
import logging
import json
import os
import random
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from network_security import NetworkSecurityAnalyzer
try:
    from module_IA import SecurityAnalysisAI
    ai_available = True
except ImportError:
    ai_available = False

# Configuration du logging
logger = logging.getLogger(__name__)

class CyberDefenseAssistant:
    """Assistant avancé de cyberdéfense pour l'analyse de sécurité et les recommandations"""
    
    def __init__(self):
        self.security_analyzer = NetworkSecurityAnalyzer()
        self.conversations_dir = "instance/conversations"
        os.makedirs(self.conversations_dir, exist_ok=True)
        
        # Initialiser le module IA si disponible
        self.ai_module = None
        if ai_available:
            try:
                self.ai_module = SecurityAnalysisAI()
                logger.info("Module IA chargé avec succès pour l'assistant de cyberdéfense")
            except (ValueError, TypeError) as e:
                logger.error(f"Erreur de configuration lors de l'initialisation du module IA: {e}")
            except ImportError as e:
                logger.error(f"Erreur d'importation lors de l'initialisation du module IA: {e}")
            except ConnectionError as e:
                logger.error(f"Erreur de connexion lors de l'initialisation du module IA: {e}")
            except RuntimeError as e:
                logger.error(f"Erreur d'exécution lors de l'initialisation du module IA: {e}")
        
        # Charger les modèles de réponses et les connaissances
        self.load_response_templates()
        self.load_threat_database()
    
    def load_response_templates(self):
        """Charge les modèles de réponses pour différents types de questions"""
        self.templates = {
            "greeting": [
                "Bonjour ! Je suis votre assistant de cyberdéfense. Je peux vous aider sur la sécurité réseau, les menaces Wi-Fi et les meilleures pratiques. Que puis-je faire pour vous aujourd'hui ?",
                "Bienvenue ! Je suis l'Assistant IA de Cyberdéfense. Je surveille et analyse la sécurité de vos réseaux. Comment puis-je vous assister ?",
                "Salut ! En tant qu'assistant de cyberdéfense, je peux vous aider à protéger vos réseaux, détecter les vulnérabilités et vous recommander les meilleures pratiques. Quelle est votre préoccupation ?"
            ],
            "general_security": [
                "La sécurité de votre réseau est primordiale pour la protection de vos données. Voici mes recommandations : {advice}",
                "Pour renforcer votre posture de sécurité réseau, je vous conseille de : {advice}",
                "Basé sur mon analyse de cyberdéfense, voici les mesures prioritaires à mettre en œuvre : {advice}"
            ],
            "encryption": [
                "Le chiffrement {encryption_type} offre un niveau de sécurité {security_level}. {recommendation}",
                "Votre réseau utilise le protocole {encryption_type}, qui {security_description}. {recommendation}",
                "Le niveau de protection offert par {encryption_type} est {security_level}. {recommendation}"
            ],
            "password": [
                "Pour un mot de passe réseau robuste, suivez ces principes de cybersécurité : utilisez au moins 12 caractères avec une combinaison de lettres majuscules/minuscules, chiffres et caractères spéciaux. Évitez les informations personnelles identifiables.",
                "Selon les standards de sécurité actuels, votre mot de passe Wi-Fi devrait être changé tous les 3 mois. Utilisez un gestionnaire de mots de passe pour générer des phrases complexes et uniques pour chaque réseau.",
                "La robustesse d'un mot de passe est votre première ligne de défense. Privilégiez une phrase longue et mémorisable (plus de 16 caractères) plutôt qu'une séquence courte et complexe. N'utilisez jamais le même mot de passe pour plusieurs services."
            ],
            "threats": [
                "Les principales menaces actuelles pour les réseaux Wi-Fi incluent : {threats}. Voici comment vous protéger : {protection}",
                "D'après ma base de données de cyberdéfense, votre réseau pourrait être vulnérable à : {threats}. Je recommande : {protection}",
                "L'analyse de menaces révèle ces risques potentiels : {threats}. Pour renforcer votre sécurité : {protection}"
            ],
            "unknown": [
                "Je ne suis pas certain de comprendre votre question. En tant qu'assistant de cyberdéfense, je peux vous aider sur la sécurité des réseaux Wi-Fi, l'analyse des menaces et les recommandations de protection. Pourriez-vous reformuler ?",
                "Cette question semble sortir de mon domaine de spécialisation en cyberdéfense réseau. Je peux vous assister sur l'analyse de sécurité Wi-Fi, les menaces réseau et les meilleures pratiques de protection. Quel aspect de la sécurité vous préoccupe ?",
                "Je suis spécialisé dans la cyberdéfense des réseaux. Votre question nécessite peut-être des précisions. Souhaitez-vous des informations sur les vulnérabilités Wi-Fi, l'analyse de risques ou les stratégies de protection ?"
            ],
            "network_specific": [
                "Analyse de cyberdéfense pour '{network_name}' : {observation}. Recommandation de sécurité : {recommendation}",
                "Rapport de sécurité pour le réseau '{network_name}' : {observation}. Actions recommandées : {recommendation}",
                "Évaluation des risques pour '{network_name}' : {observation}. Plan d'action de sécurité : {recommendation}"
            ],
            "vulnerability_assessment": [
                "L'analyse de vulnérabilité de votre réseau révèle : {vulnerabilities}. Niveau de risque global : {risk_level}. Actions prioritaires : {actions}",
                "Évaluation des failles de sécurité : {vulnerabilities}. Exposition aux risques : {risk_level}. Mesures de remédiation : {actions}",
                "Résultats du scan de vulnérabilités : {vulnerabilities}. Classification du risque : {risk_level}. Recommandations de cyberdéfense : {actions}"
            ],
            "device_security": [
                "Analyse de l'appareil {device_name} : Score de sécurité {security_score}/100. Points faibles identifiés : {weaknesses}. Recommandations : {recommendations}",
                "Évaluation de sécurité pour {device_name} : Niveau de protection {security_score}/100. Vulnérabilités détectées : {weaknesses}. Actions conseillées : {recommendations}",
                "Rapport de cyberdéfense pour {device_name} : Indice de sécurité {security_score}/100. Risques principaux : {weaknesses}. Plan de renforcement : {recommendations}"
            ],
            "attack_detection": [
                "Alerte de sécurité ! Activité suspecte détectée : {attack_type}. Niveau de menace : {threat_level}. Actions recommandées : {defense_actions}",
                "Détection d'une possible tentative d'intrusion : {attack_type}. Évaluation de la menace : {threat_level}. Protocole de défense : {defense_actions}",
                "Notification de cyberdéfense : Patron d'attaque identifié ({attack_type}). Criticité : {threat_level}. Contre-mesures immédiates : {defense_actions}"
            ]
        }
        
        # Conseils de sécurité généraux avancés
        self.security_advice = [
            "migrer vers WPA3 avec l'authentification SAE pour une protection supérieure contre les attaques par dictionnaire",
            "configurer un accès VPN pour la connexion à distance plutôt que d'ouvrir des ports directement sur votre routeur",
            "implémenter la segmentation de réseau (VLAN) pour isoler les appareils IoT peu sécurisés du reste de votre réseau",
            "activer le filtrage MAC avec liste blanche, tout en sachant que cette mesure peut être contournée mais ajoute une couche de défense",
            "désactiver totalement WPS qui présente des vulnérabilités inhérentes à sa conception",
            "mettre en place une rotation régulière des mots de passe réseau avec un calendrier prédéfini",
            "utiliser un DNS sécurisé (comme Quad9 ou Cloudflare) pour bloquer l'accès aux domaines malveillants connus",
            "configurer des plages horaires d'accès au réseau pour limiter les fenêtres d'opportunité d'attaque",
            "activer la journalisation des connexions et configurer des alertes pour les activités suspectes",
            "mettre régulièrement à jour tous les firmwares (routeur, points d'accès, IoT) dès que des correctifs sont disponibles",
            "établir un réseau invité isolé avec des restrictions de bande passante et d'accès au réseau local",
            "configurer un pare-feu réseau avec des règles strictes de trafic entrant et sortant",
            "mettre en place l'authentification 802.1X pour un contrôle d'accès réseau basé sur l'identité"
        ]
        
        # Descriptions détaillées des types de chiffrement
        self.encryption_info = {
            "WPA3": {
                "level": "très élevé",
                "description": "offre une protection supérieure grâce à l'authentification SAE (Simultaneous Authentication of Equals) qui résiste aux attaques par dictionnaire et offre une confidentialité persistante",
                "recommendation": "Vous utilisez le standard de sécurité Wi-Fi le plus récent et le plus robuste. Assurez-vous que tous vos appareils sont compatibles WPA3 pour bénéficier pleinement de cette protection."
            },
            "WPA2": {
                "level": "élevé",
                "description": "offre une bonne protection générale mais reste vulnérable aux attaques KRACK, aux attaques par dictionnaire si votre mot de passe est faible, et n'offre pas de confidentialité persistante",
                "recommendation": "Migrez vers WPA3 si votre équipement le supporte. En attendant, utilisez un mot de passe fort d'au moins 12 caractères aléatoires et désactivez WPS."
            },
            "WPA": {
                "level": "faible",
                "description": "est obsolète et vulnérable à plusieurs attaques critiques comme TKIP Michael, qui permettent de déchiffrer les communications",
                "recommendation": "Remplacez immédiatement ce protocole par WPA2-AES au minimum, ou idéalement WPA3. Le protocole WPA original n'est plus considéré comme sécurisé."
            },
            "WEP": {
                "level": "critique (extrêmement faible)",
                "description": "est totalement compromis et peut être craqué en quelques minutes avec des outils facilement accessibles",
                "recommendation": "Changez immédiatement pour WPA2 ou WPA3 ! WEP offre une protection illusoire et expose toutes vos communications à l'interception."
            },
            "OPEN": {
                "level": "nul",
                "description": "n'offre aucune protection et permet à quiconque d'intercepter tout le trafic réseau en clair",
                "recommendation": "Configurez immédiatement un chiffrement sur votre réseau ! Toutes vos données transitent actuellement en clair et sont visibles par n'importe qui à proximité."
            },
            "WPA2-ENTERPRISE": {
                "level": "très élevé",
                "description": "utilise l'authentification 802.1X avec des certificats individuels, offrant une excellente sécurité pour les environnements professionnels",
                "recommendation": "Ce mode offre une excellente sécurité. Assurez-vous que votre serveur RADIUS est correctement configuré et que les certificats sont régulièrement renouvelés."
            },
            "WPA3-ENTERPRISE": {
                "level": "maximal",
                "description": "combine l'authentification 802.1X avec les améliorations de WPA3 pour une protection optimale en environnement professionnel",
                "recommendation": "Vous utilisez le niveau de sécurité le plus élevé disponible actuellement. Maintenez à jour votre infrastructure d'authentification et vos certificats."
            }
        }
    
    def load_threat_database(self):
        """Charge la base de données des menaces Wi-Fi connues"""
        self.threat_database = {
            "evil_twin": {
                "name": "Attaque Evil Twin (Point d'accès jumeau)",
                "description": "L'attaquant crée un point d'accès qui imite votre réseau légitime pour intercepter les communications",
                "severity": "élevée",
                "indicators": ["points d'accès multiples avec le même SSID", "signal fluctuant anormalement", "déconnexions fréquentes"],
                "defense": "Vérifiez l'adresse MAC de votre point d'accès et utilisez WPA3 lorsque possible. Configurez votre appareil pour se connecter uniquement à des réseaux spécifiques."
            },
            "krack": {
                "name": "Attaque KRACK (Key Reinstallation Attack)",
                "description": "Exploite une faille dans le protocole WPA2 pour forcer la réinstallation de clés et potentiellement déchiffrer le trafic",
                "severity": "élevée",
                "indicators": ["déconnexions inexpliquées", "lenteur soudaine du réseau"],
                "defense": "Mettre à jour tous les appareils et points d'accès avec les derniers correctifs de sécurité. Migrer vers WPA3 si possible."
            },
            "wps_pin": {
                "name": "Attaque WPS PIN",
                "description": "Exploite la faiblesse du mécanisme WPS pour deviner le code PIN et accéder au réseau",
                "severity": "élevée",
                "indicators": ["tentatives de connexion répétées", "activité réseau suspecte"],
                "defense": "Désactiver complètement la fonctionnalité WPS sur votre routeur, ou au minimum désactiver la méthode PIN."
            },
            "deauth": {
                "name": "Attaque par désauthentification",
                "description": "Envoie des paquets de désauthentification pour déconnecter les utilisateurs légitimes, souvent comme première étape d'autres attaques",
                "severity": "moyenne",
                "indicators": ["déconnexions fréquentes et simultanées de tous les appareils", "reconnexions immédiates"],
                "defense": "Utiliser WPA3 qui protège contre ce type d'attaque grâce à sa gestion améliorée des trames de gestion protégées (802.11w)."
            },
            "pmkid": {
                "name": "Attaque PMKID",
                "description": "Permet de capturer des données pour une attaque par force brute sans avoir besoin d'intercepter de handshake",
                "severity": "élevée",
                "indicators": ["difficilement détectable sans outils spécialisés"],
                "defense": "Utiliser des mots de passe extrêmement forts (20+ caractères) et migrer vers WPA3 dès que possible."
            },
            "rogue_dhcp": {
                "name": "Serveur DHCP malveillant",
                "description": "Un attaquant installe un serveur DHCP non autorisé pour rediriger le trafic via ses propres équipements",
                "severity": "élevée",
                "indicators": ["changements inattendus de configuration IP", "problèmes de résolution DNS"],
                "defense": "Activer l'inspection DHCP sur votre routeur/switch et configurer des adresses IP statiques pour les appareils importants."
            },
            "karma": {
                "name": "Attaque KARMA",
                "description": "Exploite la fonctionnalité de recherche active des appareils mobiles pour créer des réseaux spécifiquement ciblés",
                "severity": "moyenne",
                "indicators": ["connexion automatique à des réseaux inconnus"],
                "defense": "Désactiver la connexion automatique aux réseaux précédemment connectés et effacer régulièrement la liste des réseaux connus."
            },
            "wpa_handshake": {
                "name": "Capture de handshake WPA",
                "description": "Capture de la négociation initiale entre client et point d'accès pour tenter de casser le mot de passe hors ligne",
                "severity": "moyenne",
                "indicators": ["déconnexions brèves suivies de reconnexions"],
                "defense": "Utiliser un mot de passe très complexe (20+ caractères) et migrer vers WPA3 qui résiste mieux à ces attaques."
            }
        }
        
        # Classification des attaques par type pour l'analyse
        self.attack_categories = {
            "authentication": ["evil_twin", "wps_pin", "wpa_handshake", "pmkid"],
            "protocol": ["krack", "deauth"],
            "infrastructure": ["rogue_dhcp", "karma"],
            "eavesdropping": ["evil_twin", "krack", "wpa_handshake"]
        }
        
        # Niveaux de priorité pour les recommandations
        self.priority_levels = {
            "critical": "Critique - Action immédiate requise",
            "high": "Élevée - À résoudre rapidement",
            "medium": "Moyenne - À planifier",
            "low": "Faible - Bonnes pratiques"
        }

# Maintenir la classe originale pour compatibilité, mais en déléguant à la nouvelle implémentation
class AssistantSecurite:
    def __init__(self):
        self.assistant = CyberDefenseAssistant()
        self.security_analyzer = self.assistant.security_analyzer
        # Conserver l'accès direct aux attributs pour compatibilité
        self.templates = self.assistant.templates
        self.security_advice = self.assistant.security_advice
        self.encryption_info = self.assistant.encryption_info
        self.conversations_dir = self.assistant.conversations_dir
        
    def load_response_templates(self):
        """Délègue à la nouvelle implémentation"""
        self.assistant.load_response_templates()
        self.templates = self.assistant.templates
        self.security_advice = self.assistant.security_advice
        self.encryption_info = self.assistant.encryption_info
        
    def generate_response(self, user_input, conversation_id=None, network_data=None):
        """Génère une réponse en fonction de l'entrée utilisateur"""
        # Vérifier et préparer les données réseau
        if isinstance(network_data, list) and len(network_data) > 0:
            # Si on reçoit une liste de réseaux, prendre le premier pour l'analyse
            network_data = network_data[0]
        elif not network_data:
            network_data = {}
            
        user_input = user_input.lower().strip()
        response = ""
        
        # Créer ou récupérer la conversation
        if not conversation_id:
            conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
        # Détection des intentions avancée
        if self._detect_greeting(user_input):
            response = random.choice(self.templates["greeting"])
        
        elif self._detect_intent(user_input, ["menace", "attaque", "vulnérabilité", "risque", "danger", "exploit"]):
            # L'utilisateur demande des informations sur les menaces
            threats = self._get_relevant_threats(user_input, network_data)
            threat_names = ", ".join([t["name"] for t in threats[:3]])
            protection_advice = "; ".join([t["defense"] for t in threats[:2]])
            
            response = random.choice(self.templates["threats"]).format(
                threats=threat_names,
                protection=protection_advice
            )
        
        elif self._detect_intent(user_input, ["mot de passe", "password", "mdp", "authentification"]):
            response = random.choice(self.templates["password"])
        
        elif self._detect_intent(user_input, ["chiffrement", "encryption", "cryptage", "wpa", "wep", "protocole"]):
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
                # Pas de données réseau, donner des conseils de chiffrement avancés
                response = ("Pour un chiffrement optimal, utilisez WPA3 avec authentification SAE qui résiste aux attaques par dictionnaire. "
                           "Si WPA3 n'est pas disponible, configurez WPA2-AES (évitez TKIP) avec un mot de passe de plus de 16 caractères. "
                           "Pour les environnements professionnels, envisagez WPA2/WPA3-Enterprise avec 802.1X et des certificats.")
        
        elif self._detect_intent(user_input, ["conseil", "recommandation", "améliorer", "renforcer", "sécuriser"]):
            random_advice = self._get_random_advice(3)
            response = random.choice(self.templates["general_security"]).format(
                advice=random_advice
            )
        
        elif network_data and network_data.get('ssid', '') and (network_data.get('ssid', '') in user_input or "réseau" in user_input):
            # L'utilisateur pose une question sur un réseau spécifique
            network_name = network_data.get('ssid', 'Ce réseau')
            signal_quality = self._evaluate_signal(network_data.get('rssi', -100))
            encryption_type = self._get_encryption_type(network_data.get('security', ''))
            
            # Analyse approfondie des risques
            risks = []
            if encryption_type == "OPEN":
                risks.append("absence totale de chiffrement (réseau ouvert)")
            elif encryption_type == "WEP":
                risks.append("utilisation d'un protocole obsolète et compromis (WEP)")
            elif encryption_type == "WPA":
                risks.append("utilisation d'un protocole obsolète (WPA/TKIP)")
            
            if "canal" in user_input or "channel" in user_input:
                channel = network_data.get('channel', 'inconnu')
                risks.append(f"configuration sur le canal {channel}")
            
            observation = f"le signal est {signal_quality} et il utilise le chiffrement {encryption_type}"
            if risks:
                observation += f". Risques identifiés : {', '.join(risks)}"
            
            if encryption_type in self.encryption_info:
                recommendation = self.encryption_info[encryption_type]["recommendation"]
            else:
                recommendation = "vérifiez que votre réseau utilise WPA2 ou WPA3 et un mot de passe fort"
            
            response = random.choice(self.templates["network_specific"]).format(
                network_name=network_name,
                observation=observation,
                recommendation=recommendation
            )
        
        elif self._detect_intent(user_input, ["analyse", "scanner", "évaluer", "diagnostic"]):
            # L'utilisateur demande une analyse de vulnérabilité
            vulnerabilities = ["configuration par défaut non modifiée", "absence de pare-feu réseau", "mises à jour manquantes"]
            risk_level = "moyen à élevé"
            actions = "mettre à jour le firmware, modifier les identifiants par défaut, activer le pare-feu"
            
            response = random.choice(self.templates["vulnerability_assessment"]).format(
                vulnerabilities=", ".join(vulnerabilities),
                risk_level=risk_level,
                actions=actions
            )
        
        else:
            # Si l'intention de l'utilisateur n'est pas claire
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
        except FileNotFoundError as e:
            logger.error(f"Fichier de conversation introuvable pour {conversation_id}: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Format JSON invalide pour la conversation {conversation_id}: {e}")
            return []
        except PermissionError as e:
            logger.error(f"Erreur de permission lors de la lecture de la conversation {conversation_id}: {e}")
            return []
        except IOError as e:
            logger.error(f"Erreur d'I/O lors de la lecture de la conversation {conversation_id}: {e}")
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
                except FileNotFoundError as e:
                    logger.error(f"Fichier de conversation introuvable pour {filename}: {e}")
                except json.JSONDecodeError as e:
                    logger.error(f"Format JSON invalide pour le fichier {filename}: {e}")
                except PermissionError as e:
                    logger.error(f"Erreur de permission lors de la lecture de {filename}: {e}")
                except IOError as e:
                    logger.error(f"Erreur d'I/O lors de la lecture de {filename}: {e}")
        
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
            except (json.JSONDecodeError, FileNotFoundError, PermissionError, IOError):
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
        try:
            os.makedirs(os.path.dirname(conversation_file), exist_ok=True)
            with open(conversation_file, "w") as f:
                json.dump(conversation, f, indent=2)
        except FileNotFoundError as e:
            logger.error(f"Chemin de fichier invalide lors de la sauvegarde de la conversation: {e}")
        except PermissionError as e:
            logger.error(f"Erreur de permission lors de la sauvegarde de la conversation: {e}")
        except IOError as e:
            logger.error(f"Erreur d'I/O lors de la sauvegarde de la conversation: {e}")
        except TypeError as e:
            logger.error(f"Erreur de type lors de la sérialisation JSON: {e}")
    
    def _get_random_advice(self, count=3):
        """Retourne quelques conseils aléatoires sous forme de liste à puces"""
        selected_advice = random.sample(self.security_advice, min(count, len(self.security_advice)))
        return " ".join([f"• {advice};" for advice in selected_advice])
    
    def _get_encryption_type(self, security_string):
        """Détermine le type de chiffrement à partir de la chaîne de sécurité"""
        if not security_string:
            return "OPEN"
            
        security_upper = security_string.upper()
        
        if "WPA3" in security_upper and "ENTERPRISE" in security_upper:
            return "WPA3-ENTERPRISE"
        elif "WPA2" in security_upper and "ENTERPRISE" in security_upper:
            return "WPA2-ENTERPRISE"
        elif "WPA3" in security_upper:
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
    
    def _detect_greeting(self, text):
        """Détecte une salutation dans le texte"""
        greeting_words = ['bonjour', 'salut', 'hello', 'coucou', 'hi', 'hey']
        return any(word in text for word in greeting_words)
    
    def _detect_intent(self, text, keywords):
        """Détecte une intention basée sur des mots-clés"""
        return any(keyword in text for keyword in keywords)
    
    def _get_relevant_threats(self, user_input, network_data):
        """Identifie les menaces les plus pertinentes en fonction du contexte"""
        # Déterminer les mots-clés de la question
        query_keywords = set(re.findall(r'\b\w+\b', user_input.lower()))
        
        # Déterminer le type de chiffrement si disponible
        encryption_type = "UNKNOWN"
        if network_data and 'security' in network_data:
            encryption_type = self._get_encryption_type(network_data['security'])
        
        # Calculer la pertinence pour chaque menace
        threat_relevance = []
        for threat_id, threat in self.assistant.threat_database.items():
            relevance = 0
            
            # Chercher les mots-clés de la menace dans la question
            threat_keywords = set(re.findall(r'\b\w+\b', threat["name"].lower() + " " + threat["description"].lower()))
            keyword_match = len(query_keywords.intersection(threat_keywords))
            relevance += keyword_match * 3
            
            # Augmenter la pertinence si le type de chiffrement est vulnérable à cette menace
            if encryption_type == "WEP" and threat_id in ["wps_pin", "wpa_handshake"]:
                relevance += 5
            elif encryption_type == "WPA" and threat_id in ["wpa_handshake"]:
                relevance += 4
            elif encryption_type == "WPA2" and threat_id in ["krack", "pmkid"]:
                relevance += 3
            elif encryption_type == "OPEN" and threat_id in ["evil_twin", "karma"]:
                relevance += 5
            
            # Bonus pour les menaces à gravité élevée
            if threat["severity"] == "élevée":
                relevance += 2
            
            threat_relevance.append((threat_id, relevance, threat))
        
        # Trier par pertinence décroissante
        threat_relevance.sort(key=lambda x: x[1], reverse=True)
        
        # Si aucune menace n'est particulièrement pertinente, inclure les plus graves
        if not threat_relevance or threat_relevance[0][1] == 0:
            high_severity_threats = [t for t in self.assistant.threat_database.values() if t["severity"] == "élevée"]
            return sorted(high_severity_threats, key=lambda x: x["name"])[:3]
        
        # Retourner les menaces les plus pertinentes
        return [t[2] for t in threat_relevance[:3]]
    
    # Aucune autre méthode nécessaire - toutes les méthodes implémentées ci-dessus
