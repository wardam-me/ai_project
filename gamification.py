"""
Module de gamification pour le système de sécurité réseau
"""
import os
import json
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityGamification:
    """Système de gamification pour encourager l'amélioration de la sécurité réseau"""
    
    def __init__(self):
        """Initialise le système de gamification"""
        self.user_scores = {}
        self.user_achievements = {}
        self.user_challenges = {}
        self.user_rewards = {}
        self.user_streaks = {}
        
        # Créer le dossier de données si nécessaire
        os.makedirs('instance', exist_ok=True)
        
        # Charger les données de gamification
        self.load_gamification_data()
    
    def load_gamification_data(self):
        """Charge les données de gamification depuis le fichier"""
        try:
            if os.path.exists('instance/gamification.json'):
                with open('instance/gamification.json', 'r') as f:
                    data = json.load(f)
                    self.user_scores = data.get('user_scores', {})
                    self.user_achievements = data.get('user_achievements', {})
                    self.user_challenges = data.get('user_challenges', {})
                    self.user_rewards = data.get('user_rewards', {})
                    self.user_streaks = data.get('user_streaks', {})
                logger.info("Données de gamification chargées")
            else:
                logger.info("Aucun fichier de données de gamification existant")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données de gamification: {e}")
    
    def save_gamification_data(self):
        """Sauvegarde les données de gamification dans un fichier"""
        try:
            data = {
                'user_scores': self.user_scores,
                'user_achievements': self.user_achievements,
                'user_challenges': self.user_challenges,
                'user_rewards': self.user_rewards,
                'user_streaks': self.user_streaks
            }
            with open('instance/gamification.json', 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Données de gamification sauvegardées")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données de gamification: {e}")
    
    def initialize_user(self, user_id):
        """Initialise les données de gamification pour un nouvel utilisateur"""
        if str(user_id) not in self.user_scores:
            self.user_scores[str(user_id)] = {
                'xp': 0,
                'level': 1,
                'next_level_xp': 100,
                'security_points': 0,
                'defense_rating': 0,
                'last_updated': datetime.now().isoformat()
            }
        
        if str(user_id) not in self.user_achievements:
            self.user_achievements[str(user_id)] = []
        
        if str(user_id) not in self.user_challenges:
            self.user_challenges[str(user_id)] = self._generate_challenges()
        
        if str(user_id) not in self.user_rewards:
            self.user_rewards[str(user_id)] = []
        
        if str(user_id) not in self.user_streaks:
            self.user_streaks[str(user_id)] = {
                'current_streak': 0,
                'last_activity': datetime.now().isoformat(),
                'highest_streak': 0
            }
        
        self.save_gamification_data()
    
    def update_score_from_security(self, user_id, network_stats, fixed_issues=None):
        """
        Met à jour le score de l'utilisateur en fonction des statistiques de sécurité du réseau
        
        Args:
            user_id: ID de l'utilisateur
            network_stats: Statistiques de sécurité du réseau
            fixed_issues: Liste des problèmes de sécurité résolus (optionnel)
        
        Returns:
            dict: Données de progression mises à jour
        """
        user_id = str(user_id)
        if user_id not in self.user_scores:
            self.initialize_user(user_id)
        
        user_data = self.user_scores[user_id]
        
        # Points de sécurité basés sur le score global
        old_security_points = user_data['security_points']
        new_security_points = int(network_stats['overall_score'])
        user_data['security_points'] = new_security_points
        
        # Calcul du taux de défense basé sur les appareils à risque faible par rapport au total
        defense_rating = int(100 * network_stats['low_risk_count'] / network_stats['device_count']) if network_stats['device_count'] > 0 else 0
        user_data['defense_rating'] = defense_rating
        
        # Gain d'XP basé sur l'amélioration de la sécurité
        xp_gain = 0
        
        # XP pour l'amélioration du score de sécurité
        if new_security_points > old_security_points:
            security_improvement = new_security_points - old_security_points
            xp_gain += security_improvement * 5  # 5 XP par point d'amélioration
        
        # XP pour les problèmes résolus
        if fixed_issues:
            for issue in fixed_issues:
                if issue['severity'] == 'high':
                    xp_gain += 50
                elif issue['severity'] == 'medium':
                    xp_gain += 25
                else:
                    xp_gain += 10
        
        # Mise à jour de l'XP et vérification du niveau
        if xp_gain > 0:
            level_up_info = self._add_xp(user_id, xp_gain)
            
            # Mise à jour de la date de dernière activité
            user_data['last_updated'] = datetime.now().isoformat()
            
            # Vérifier et mettre à jour la série d'activités (streak)
            self._update_streak(user_id)
            
            # Vérifier les réalisations débloquées
            new_achievements = self._check_achievements(user_id, network_stats)
            
            # Mettre à jour les défis
            challenge_progress = self._update_challenges(user_id, network_stats, fixed_issues)
            
            # Sauvegarder les modifications
            self.save_gamification_data()
            
            return {
                'user_data': user_data,
                'xp_gain': xp_gain,
                'level_up': level_up_info,
                'new_achievements': new_achievements,
                'challenge_progress': challenge_progress,
                'streak': self.user_streaks[user_id]
            }
        
        # Si aucun XP n'a été gagné, retourner uniquement les données utilisateur
        return {
            'user_data': user_data,
            'xp_gain': 0,
            'level_up': None,
            'new_achievements': [],
            'challenge_progress': [],
            'streak': self.user_streaks[user_id]
        }
    
    def _add_xp(self, user_id, xp_amount):
        """
        Ajoute de l'XP au score de l'utilisateur et gère les montées de niveau
        
        Returns:
            dict: Informations sur la montée de niveau ou None
        """
        user_data = self.user_scores[user_id]
        old_level = user_data['level']
        
        # Ajouter l'XP
        user_data['xp'] += xp_amount
        
        # Vérifier si l'utilisateur monte de niveau
        while user_data['xp'] >= user_data['next_level_xp']:
            user_data['level'] += 1
            user_data['xp'] -= user_data['next_level_xp']
            
            # La prochaine montée de niveau nécessite plus d'XP
            user_data['next_level_xp'] = int(user_data['next_level_xp'] * 1.5)
        
        # Si l'utilisateur a monté de niveau, retourner les informations
        if user_data['level'] > old_level:
            return {
                'old_level': old_level,
                'new_level': user_data['level'],
                'next_level_xp': user_data['next_level_xp'],
                'rewards': self._generate_level_rewards(user_data['level'])
            }
        
        return None
    
    def _generate_level_rewards(self, level):
        """Génère des récompenses pour une montée de niveau"""
        rewards = []
        
        # Badges disponibles par niveau
        badges = {
            2: "Gardien Novice",
            5: "Protecteur du Réseau",
            10: "Maître des Défenses",
            15: "Expert en Cyber-Sécurité",
            20: "Légende de la Sécurité"
        }
        
        # Ajouter un badge si disponible pour ce niveau
        if level in badges:
            rewards.append({
                'type': 'badge',
                'name': badges[level],
                'description': f"Badge obtenu en atteignant le niveau {level}"
            })
        
        # Ajouter d'autres types de récompenses (thèmes, avatars, etc.)
        if level % 3 == 0:  # Tous les 3 niveaux
            themes = [
                "Thème Nuit Cybernétique",
                "Thème Matrice",
                "Thème Néon",
                "Thème Glacier",
                "Thème Lave"
            ]
            rewards.append({
                'type': 'theme',
                'name': random.choice(themes),
                'description': "Nouveau thème d'interface débloqué"
            })
        
        if level % 5 == 0:  # Tous les 5 niveaux
            rewards.append({
                'type': 'avatar',
                'name': f"Avatar premium niveau {level}",
                'description': "Nouvel avatar exclusif débloqué"
            })
        
        return rewards
    
    def _update_streak(self, user_id):
        """Met à jour la série d'activités (streak) de l'utilisateur"""
        streak_data = self.user_streaks[user_id]
        last_activity = datetime.fromisoformat(streak_data['last_activity'])
        now = datetime.now()
        
        # Calculer le nombre de jours depuis la dernière activité
        days_diff = (now - last_activity).days
        
        if days_diff == 0:
            # Même jour, rien à faire
            pass
        elif days_diff == 1:
            # Jour consécutif, augmenter le streak
            streak_data['current_streak'] += 1
            streak_data['last_activity'] = now.isoformat()
            
            # Mettre à jour le record
            if streak_data['current_streak'] > streak_data['highest_streak']:
                streak_data['highest_streak'] = streak_data['current_streak']
        else:
            # Streak rompu
            streak_data['current_streak'] = 1
            streak_data['last_activity'] = now.isoformat()
    
    def _check_achievements(self, user_id, network_stats):
        """
        Vérifie si de nouvelles réalisations ont été débloquées
        
        Returns:
            list: Nouvelles réalisations débloquées
        """
        user_achievements = self.user_achievements[user_id]
        new_achievements = []
        
        # Définition des réalisations possibles
        all_achievements = [
            {
                'id': 'secure_network',
                'name': 'Réseau sécurisé',
                'description': 'Atteindre un score de sécurité global de 80 ou plus',
                'condition': lambda stats: stats['overall_score'] >= 80,
                'icon': 'shield-check'
            },
            {
                'id': 'defender',
                'name': 'Défenseur',
                'description': 'Avoir au moins 5 appareils avec un risque faible',
                'condition': lambda stats: stats['low_risk_count'] >= 5,
                'icon': 'users-shield'
            },
            {
                'id': 'security_expert',
                'name': 'Expert en sécurité',
                'description': 'Atteindre un score de sécurité global de 90 ou plus',
                'condition': lambda stats: stats['overall_score'] >= 90,
                'icon': 'user-shield'
            },
            {
                'id': 'network_master',
                'name': 'Maître du réseau',
                'description': 'Surveiller plus de 10 appareils sur votre réseau',
                'condition': lambda stats: stats['device_count'] >= 10,
                'icon': 'network-wired'
            },
            {
                'id': 'perfect_security',
                'name': 'Sécurité parfaite',
                'description': 'Atteindre un score de sécurité de 100',
                'condition': lambda stats: stats['overall_score'] >= 100,
                'icon': 'medal'
            }
        ]
        
        # Vérifier chaque réalisation
        for achievement in all_achievements:
            # Si l'utilisateur n'a pas déjà cette réalisation
            if achievement['id'] not in [ach.get('id') for ach in user_achievements]:
                # Si la condition est remplie
                if achievement['condition'](network_stats):
                    # Ajouter la réalisation avec la date de déverrouillage
                    achievement_copy = achievement.copy()
                    achievement_copy['unlocked_at'] = datetime.now().isoformat()
                    user_achievements.append(achievement_copy)
                    new_achievements.append(achievement_copy)
        
        return new_achievements
    
    def _generate_challenges(self):
        """Génère une liste de défis pour l'utilisateur"""
        all_challenges = [
            {
                'id': 'update_firmware',
                'name': 'Mise à jour du firmware',
                'description': 'Mettre à jour le firmware de 3 appareils',
                'category': 'maintenance',
                'progress': 0,
                'target': 3,
                'xp_reward': 50,
                'status': 'active',
                'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
            },
            {
                'id': 'secure_devices',
                'name': 'Sécurisation des appareils',
                'description': 'Améliorer le score de sécurité de 5 appareils',
                'category': 'security',
                'progress': 0,
                'target': 5,
                'xp_reward': 100,
                'status': 'active',
                'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
            },
            {
                'id': 'fix_vulnerabilities',
                'name': 'Correction des vulnérabilités',
                'description': 'Corriger 3 vulnérabilités de niveau élevé',
                'category': 'security',
                'progress': 0,
                'target': 3,
                'xp_reward': 75,
                'status': 'active',
                'expires_at': (datetime.now() + timedelta(days=5)).isoformat()
            },
            {
                'id': 'security_scan',
                'name': 'Analyse de sécurité',
                'description': 'Effectuer une analyse complète du réseau',
                'category': 'scan',
                'progress': 0,
                'target': 1,
                'xp_reward': 30,
                'status': 'active',
                'expires_at': (datetime.now() + timedelta(days=2)).isoformat()
            },
            {
                'id': 'login_streak',
                'name': 'Suivi régulier',
                'description': 'Se connecter 5 jours consécutifs',
                'category': 'engagement',
                'progress': 0,
                'target': 5,
                'xp_reward': 60,
                'status': 'active',
                'expires_at': (datetime.now() + timedelta(days=10)).isoformat()
            }
        ]
        
        # Sélectionner 3 défis aléatoires
        return random.sample(all_challenges, 3)
    
    def _update_challenges(self, user_id, network_stats, fixed_issues):
        """
        Met à jour la progression des défis
        
        Returns:
            list: Défis mis à jour ou complétés
        """
        updated_challenges = []
        challenges = self.user_challenges[user_id]
        
        for challenge in challenges:
            # Si le défi est déjà complété ou expiré, passer au suivant
            if challenge['status'] != 'active':
                continue
            
            # Vérifier si le défi a expiré
            if datetime.fromisoformat(challenge['expires_at']) < datetime.now():
                challenge['status'] = 'expired'
                updated_challenges.append(challenge)
                continue
            
            # Mise à jour de la progression en fonction du type de défi
            if challenge['id'] == 'update_firmware' and fixed_issues:
                # Compter les mises à jour de firmware dans les problèmes résolus
                firmware_fixes = sum(1 for issue in fixed_issues if 'firmware' in issue['description'].lower())
                if firmware_fixes > 0:
                    old_progress = challenge['progress']
                    challenge['progress'] = min(challenge['target'], challenge['progress'] + firmware_fixes)
                    updated_challenges.append(challenge)
            
            elif challenge['id'] == 'secure_devices':
                # Ce défi progresse automatiquement quand le score global augmente
                challenge['progress'] = min(challenge['target'], 
                                           int(network_stats['low_risk_count'] * 0.5 + network_stats['medium_risk_count'] * 0.2))
                updated_challenges.append(challenge)
            
            elif challenge['id'] == 'fix_vulnerabilities' and fixed_issues:
                # Compter les vulnérabilités de niveau élevé corrigées
                high_fixes = sum(1 for issue in fixed_issues if issue['severity'] == 'high')
                if high_fixes > 0:
                    old_progress = challenge['progress']
                    challenge['progress'] = min(challenge['target'], challenge['progress'] + high_fixes)
                    updated_challenges.append(challenge)
            
            elif challenge['id'] == 'security_scan':
                # Ce défi est complété automatiquement lors d'une analyse complète
                challenge['progress'] = 1
                updated_challenges.append(challenge)
            
            elif challenge['id'] == 'login_streak':
                # Ce défi se base sur la série de connexions
                streak_data = self.user_streaks[user_id]
                challenge['progress'] = min(challenge['target'], streak_data['current_streak'])
                updated_challenges.append(challenge)
            
            # Vérifier si le défi est maintenant complété
            if challenge['progress'] >= challenge['target']:
                challenge['status'] = 'completed'
                challenge['completed_at'] = datetime.now().isoformat()
                
                # Attribuer la récompense XP
                self._add_xp(user_id, challenge['xp_reward'])
                
                # Remplacer le défi complété par un nouveau
                index = challenges.index(challenge)
                all_challenges = self._generate_challenges()
                
                # Trouver un défi qui n'est pas déjà dans la liste
                for new_challenge in all_challenges:
                    if new_challenge['id'] not in [c['id'] for c in challenges]:
                        challenges[index] = new_challenge
                        break
        
        return updated_challenges
    
    def get_user_gamification_data(self, user_id):
        """Récupère toutes les données de gamification pour un utilisateur"""
        user_id = str(user_id)
        if user_id not in self.user_scores:
            self.initialize_user(user_id)
        
        return {
            'scores': self.user_scores[user_id],
            'achievements': self.user_achievements[user_id],
            'challenges': self.user_challenges[user_id],
            'rewards': self.user_rewards[user_id],
            'streak': self.user_streaks[user_id]
        }
    
    def get_leaderboard(self, limit=10):
        """Récupère le classement des utilisateurs par score de sécurité"""
        # Trier les utilisateurs par niveau puis par XP
        user_scores_list = [
            {
                'user_id': user_id,
                **data
            }
            for user_id, data in self.user_scores.items()
        ]
        
        # Tri par niveau (décroissant) puis par XP (décroissant)
        sorted_users = sorted(
            user_scores_list,
            key=lambda x: (x['level'], x['xp']),
            reverse=True
        )
        
        # Limiter le nombre de résultats
        return sorted_users[:limit]