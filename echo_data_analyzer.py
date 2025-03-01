
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'analyse automatique des données échographiques pour NetSecure Pro
Ce module utilise l'intelligence artificielle pour analyser les données d'écho réseau
et générer des rapports de sécurité basés sur les patterns détectés.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import random

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instance/echo_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("echo_analyzer")

# Vérification et import conditionnel du module IA principal
try:
    from module_IA import SecurityAnalysisAI
    ai_available = True
    logger.info("Module IA principal importé avec succès")
except ImportError:
    ai_available = False
    logger.warning("Module IA principal non disponible, fonctionnement en mode dégradé")

class EchoDataAnalyzer:
    """
    Analyseur automatique des données d'écho réseau
    Utilise l'IA pour identifier les patterns de sécurité et les anomalies
    """
    
    def __init__(self, data_dir: str = "instance/echo_data", 
                 results_dir: str = "instance/echo_reports"):
        """
        Initialise l'analyseur de données d'écho
        
        Args:
            data_dir: Répertoire contenant les données d'écho brutes
            results_dir: Répertoire pour stocker les résultats d'analyse
        """
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.security_ai = None
        self.last_analysis = None
        
        # Créer les répertoires s'ils n'existent pas
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Initialiser le module d'IA si disponible
        if ai_available:
            try:
                self.security_ai = SecurityAnalysisAI()
                logger.info("Module d'IA de sécurité initialisé pour l'analyse d'écho")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du module IA: {e}")
    
    def load_echo_data(self, filename: str) -> Optional[List[Dict[str, Any]]]:
        """
        Charge les données d'écho depuis un fichier JSON
        
        Args:
            filename: Nom du fichier dans le répertoire data_dir
            
        Returns:
            Liste de données d'écho ou None en cas d'erreur
        """
        try:
            file_path = os.path.join(self.data_dir, filename)
            if not os.path.exists(file_path):
                logger.error(f"Fichier introuvable: {file_path}")
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Données d'écho chargées depuis {filename}: {len(data)} entrées")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de format JSON dans {filename}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données d'écho: {e}")
            return None
    
    def save_analysis_results(self, results: Dict[str, Any], filename: str = None) -> bool:
        """
        Enregistre les résultats d'analyse dans un fichier JSON
        
        Args:
            results: Résultats d'analyse à sauvegarder
            filename: Nom du fichier de sortie (généré automatiquement si None)
            
        Returns:
            True si sauvegarde réussie, False sinon
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"echo_analysis_{timestamp}.json"
                
            file_path = os.path.join(self.results_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Résultats d'analyse sauvegardés dans {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats: {e}")
            return False
    
    def analyze_round_trip_times(self, echo_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse les temps d'aller-retour pour détecter des anomalies ou latences
        
        Args:
            echo_data: Données d'écho contenant des informations de temps
            
        Returns:
            Résultats d'analyse des temps d'aller-retour
        """
        if not echo_data:
            return {"error": "Aucune donnée d'écho à analyser"}
            
        # Extraire les temps d'aller-retour
        rtt_values = []
        for entry in echo_data:
            if "rtt" in entry and isinstance(entry["rtt"], (int, float)):
                rtt_values.append(entry["rtt"])
        
        if not rtt_values:
            return {"error": "Aucune valeur RTT valide dans les données"}
            
        # Calculer les statistiques de base
        avg_rtt = sum(rtt_values) / len(rtt_values)
        min_rtt = min(rtt_values)
        max_rtt = max(rtt_values)
        
        # Détecter les anomalies (valeurs > 2x la moyenne)
        anomalies = [rtt for rtt in rtt_values if rtt > 2 * avg_rtt]
        
        # Préparer les résultats
        results = {
            "avg_rtt_ms": round(avg_rtt, 2),
            "min_rtt_ms": round(min_rtt, 2),
            "max_rtt_ms": round(max_rtt, 2),
            "rtt_variance": round(sum((x - avg_rtt) ** 2 for x in rtt_values) / len(rtt_values), 2),
            "samples_count": len(rtt_values),
            "anomalies_count": len(anomalies),
            "anomalies_percentage": round(len(anomalies) / len(rtt_values) * 100, 2),
        }
        
        # Interprétation IA si disponible
        if self.security_ai:
            latency_insight = "Le temps de réponse moyen est "
            if avg_rtt < 10:
                latency_insight += "excellent, indiquant une connexion très performante."
            elif avg_rtt < 50:
                latency_insight += "bon, typique d'une connexion saine."
            elif avg_rtt < 100:
                latency_insight += "acceptable, mais pourrait être amélioré."
            else:
                latency_insight += "élevé, suggérant des problèmes potentiels de congestion ou de routage."
                
            results["ai_latency_insight"] = latency_insight
            
            if len(anomalies) > 0:
                anomaly_risk = self.security_ai.analyze_vulnerability(
                    "rtt-anomalies",
                    f"Anomalies de temps de réponse ({len(anomalies)} détectées)",
                    "medium" if len(anomalies) > len(rtt_values) / 5 else "low"
                )
                results["ai_anomaly_insight"] = anomaly_risk
        
        return results
    
    def analyze_packet_loss(self, echo_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse les pertes de paquets pour évaluer la fiabilité du réseau
        
        Args:
            echo_data: Données d'écho contenant des informations sur les paquets envoyés/reçus
            
        Returns:
            Résultats d'analyse des pertes de paquets
        """
        if not echo_data:
            return {"error": "Aucune donnée d'écho à analyser"}
            
        # Extraire les informations sur les paquets
        total_sent = 0
        total_received = 0
        
        for entry in echo_data:
            if "sent" in entry and isinstance(entry["sent"], (int)):
                total_sent += entry["sent"]
            if "received" in entry and isinstance(entry["received"], (int)):
                total_received += entry["received"]
        
        if total_sent == 0:
            return {"error": "Aucune information sur les paquets envoyés"}
            
        # Calculer le taux de perte
        loss_rate = (total_sent - total_received) / total_sent if total_sent > 0 else 0
        
        # Préparer les résultats
        results = {
            "packets_sent": total_sent,
            "packets_received": total_received,
            "packets_lost": total_sent - total_received,
            "loss_rate_percentage": round(loss_rate * 100, 2)
        }
        
        # Interprétation IA si disponible
        if self.security_ai:
            loss_insight = "Le taux de perte de paquets est "
            if loss_rate < 0.01:
                loss_insight += "excellent, indiquant un réseau très fiable."
                loss_severity = "low"
            elif loss_rate < 0.05:
                loss_insight += "acceptable, mais à surveiller."
                loss_severity = "low"
            elif loss_rate < 0.10:
                loss_insight += "préoccupant, indiquant des problèmes potentiels de réseau."
                loss_severity = "medium"
            else:
                loss_insight += "critique, nécessitant une investigation immédiate."
                loss_severity = "high"
                
            results["ai_loss_insight"] = loss_insight
            
            if loss_rate > 0.01:
                loss_risk = self.security_ai.analyze_vulnerability(
                    "packet-loss",
                    f"Perte de paquets significative ({results['loss_rate_percentage']}%)",
                    loss_severity
                )
                results["ai_loss_risk"] = loss_risk
        
        return results
    
    def analyze_hop_count(self, echo_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse le nombre de sauts pour détecter des routages inefficaces ou suspects
        
        Args:
            echo_data: Données d'écho contenant des informations sur les sauts réseau
            
        Returns:
            Résultats d'analyse du nombre de sauts
        """
        if not echo_data:
            return {"error": "Aucune donnée d'écho à analyser"}
            
        # Extraire les informations sur les sauts
        hop_counts = []
        for entry in echo_data:
            if "hops" in entry and isinstance(entry["hops"], (int)):
                hop_counts.append(entry["hops"])
        
        if not hop_counts:
            return {"error": "Aucune information sur les sauts réseau"}
            
        # Calculer les statistiques
        avg_hops = sum(hop_counts) / len(hop_counts)
        min_hops = min(hop_counts)
        max_hops = max(hop_counts)
        
        # Compter les changements de route (différences de sauts)
        route_changes = 0
        for i in range(1, len(hop_counts)):
            if hop_counts[i] != hop_counts[i-1]:
                route_changes += 1
        
        # Préparer les résultats
        results = {
            "avg_hop_count": round(avg_hops, 2),
            "min_hop_count": min_hops,
            "max_hop_count": max_hops,
            "route_changes": route_changes,
            "samples_count": len(hop_counts)
        }
        
        # Interprétation IA si disponible
        if self.security_ai:
            hop_insight = "Le nombre moyen de sauts est "
            if avg_hops <= 3:
                hop_insight += "faible, indiquant un routage direct et efficace."
            elif avg_hops <= 8:
                hop_insight += "normal pour une connexion internet standard."
            else:
                hop_insight += "élevé, ce qui peut contribuer à une latence accrue."
                
            results["ai_hop_insight"] = hop_insight
            
            if route_changes > len(hop_counts) / 10:
                route_risk = self.security_ai.analyze_vulnerability(
                    "route-changes",
                    f"Changements fréquents de route ({route_changes} détectés)",
                    "medium"
                )
                results["ai_routing_insight"] = route_risk
        
        return results
    
    def analyze_echo_patterns(self, echo_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse les patterns dans les données d'écho pour détecter des comportements suspects
        
        Args:
            echo_data: Données d'écho complètes
            
        Returns:
            Résultats d'analyse des patterns
        """
        if not echo_data:
            return {"error": "Aucune donnée d'écho à analyser"}
            
        # Extraire les timestamps pour analyser la périodicité
        timestamps = []
        for entry in echo_data:
            if "timestamp" in entry and entry["timestamp"]:
                try:
                    if isinstance(entry["timestamp"], (int, float)):
                        timestamps.append(entry["timestamp"])
                    else:
                        dt = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
                        timestamps.append(dt.timestamp())
                except (ValueError, TypeError):
                    continue
        
        time_diffs = []
        if len(timestamps) > 1:
            timestamps.sort()
            time_diffs = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        # Détecter les patterns réguliers
        is_regular = False
        avg_diff = 0
        std_dev = 0
        
        if time_diffs:
            avg_diff = sum(time_diffs) / len(time_diffs)
            std_dev = (sum((d - avg_diff) ** 2 for d in time_diffs) / len(time_diffs)) ** 0.5
            is_regular = std_dev / avg_diff < 0.2  # Coefficient de variation < 20%
        
        # Préparer les résultats
        results = {
            "data_points": len(echo_data),
            "time_span_seconds": round(max(timestamps) - min(timestamps)) if timestamps else 0,
            "avg_interval_seconds": round(avg_diff, 2) if time_diffs else 0,
            "interval_std_dev": round(std_dev, 2) if time_diffs else 0,
            "is_regular_pattern": is_regular
        }
        
        # Interprétation IA si disponible
        if self.security_ai:
            pattern_insight = ""
            if is_regular:
                pattern_insight = "Les données suivent un pattern régulier, typique d'un processus automatisé."
                # Analyser si ce pattern régulier pourrait être malveillant
                regularity_insight = self.security_ai.generate_recommendation_insight({
                    "title": "Analyse de la régularité des échos",
                    "priority": "medium"
                })
                results["ai_regularity_insight"] = regularity_insight
            else:
                pattern_insight = "Les données suivent un pattern irrégulier, typique d'une utilisation humaine ou de conditions réseau variables."
            
            results["ai_pattern_insight"] = pattern_insight
            
            # Approfondir avec une analyse de tendance
            trend_analysis = self.security_ai.predict_security_trend([
                {"date": "récente", "score": 50 + random.randint(-10, 10)},
                {"date": "actuelle", "score": 50 + random.randint(-10, 10)}
            ])
            
            if trend_analysis:
                results["ai_trend_prediction"] = trend_analysis
        
        return results
    
    def perform_full_analysis(self, filename: str) -> Dict[str, Any]:
        """
        Réalise une analyse complète des données d'écho
        
        Args:
            filename: Nom du fichier de données d'écho
            
        Returns:
            Résultats complets de l'analyse
        """
        start_time = time.time()
        logger.info(f"Démarrage de l'analyse complète pour {filename}")
        
        # Charger les données
        echo_data = self.load_echo_data(filename)
        if not echo_data:
            return {"error": f"Impossible de charger les données d'écho depuis {filename}"}
        
        # Préparer le rapport d'analyse
        analysis_report = {
            "filename": filename,
            "timestamp": datetime.now().isoformat(),
            "data_points": len(echo_data),
            "analyses": {}
        }
        
        # Réaliser les analyses individuelles
        analysis_report["analyses"]["round_trip_times"] = self.analyze_round_trip_times(echo_data)
        analysis_report["analyses"]["packet_loss"] = self.analyze_packet_loss(echo_data)
        analysis_report["analyses"]["hop_count"] = self.analyze_hop_count(echo_data)
        analysis_report["analyses"]["echo_patterns"] = self.analyze_echo_patterns(echo_data)
        
        # Générer un score de santé réseau global
        health_score = 100
        
        # Pénalités basées sur les temps d'aller-retour
        rtt_analysis = analysis_report["analyses"]["round_trip_times"]
        if "avg_rtt_ms" in rtt_analysis:
            if rtt_analysis["avg_rtt_ms"] > 100:
                health_score -= 15
            elif rtt_analysis["avg_rtt_ms"] > 50:
                health_score -= 5
            
            if "anomalies_percentage" in rtt_analysis and rtt_analysis["anomalies_percentage"] > 10:
                health_score -= 10
        
        # Pénalités basées sur les pertes de paquets
        loss_analysis = analysis_report["analyses"]["packet_loss"]
        if "loss_rate_percentage" in loss_analysis:
            loss_rate = loss_analysis["loss_rate_percentage"]
            if loss_rate > 10:
                health_score -= 30
            elif loss_rate > 5:
                health_score -= 15
            elif loss_rate > 1:
                health_score -= 5
        
        # Pénalités basées sur les sauts
        hop_analysis = analysis_report["analyses"]["hop_count"]
        if "avg_hop_count" in hop_analysis and hop_analysis["avg_hop_count"] > 10:
            health_score -= 5
            
        if "route_changes" in hop_analysis and hop_analysis["route_changes"] > 5:
            health_score -= 10
        
        # Limiter le score entre 0 et 100
        health_score = max(0, min(100, health_score))
        
        # Attribuer un niveau de santé
        health_level = "Excellent"
        if health_score < 60:
            health_level = "Critique"
        elif health_score < 70:
            health_level = "Mauvais"
        elif health_score < 80:
            health_level = "Moyen"
        elif health_score < 90:
            health_level = "Bon"
        
        analysis_report["network_health"] = {
            "score": health_score,
            "level": health_level
        }
        
        # Générer des recommandations globales
        recommendations = []
        
        if rtt_analysis.get("avg_rtt_ms", 0) > 50:
            recommendations.append("Investiguer les causes de latence réseau élevée")
            
        if loss_analysis.get("loss_rate_percentage", 0) > 1:
            recommendations.append("Vérifier la qualité de la connexion pour réduire les pertes de paquets")
            
        if hop_analysis.get("route_changes", 0) > 5:
            recommendations.append("Analyser les changements fréquents de route qui peuvent indiquer des problèmes de routage")
        
        # Ajouter une recommandation IA si disponible
        if self.security_ai:
            ai_recommendation = self.security_ai.generate_network_security_analysis(
                health_score, 
                len(echo_data), 
                len(recommendations)
            )
            if ai_recommendation:
                analysis_report["ai_recommendation"] = ai_recommendation
        
        analysis_report["recommendations"] = recommendations
        
        # Calculer la durée de l'analyse
        analysis_report["analysis_duration_seconds"] = round(time.time() - start_time, 2)
        
        # Sauvegarder les résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"echo_analysis_{timestamp}.json"
        self.save_analysis_results(analysis_report, result_filename)
        
        self.last_analysis = result_filename
        logger.info(f"Analyse complète terminée en {analysis_report['analysis_duration_seconds']}s")
        
        return analysis_report
    
    def generate_test_data(self, filename: str = "test_echo_data.json", 
                          entries: int = 100, with_anomalies: bool = True) -> bool:
        """
        Génère des données d'écho de test pour les démos et les tests
        
        Args:
            filename: Nom du fichier pour les données générées
            entries: Nombre d'entrées à générer
            with_anomalies: Inclure des anomalies dans les données
            
        Returns:
            True si génération réussie, False sinon
        """
        try:
            test_data = []
            base_time = time.time() - (entries * 60)  # Partir de il y a (entries * 60) secondes
            
            # Paramètres normaux
            normal_rtt_mean = 30  # ms
            normal_rtt_std = 5  # ms
            normal_hops = 5
            packet_loss_rate = 0.02  # 2%
            
            for i in range(entries):
                # Calculer le timestamp
                entry_time = base_time + (i * 60)  # Une entrée par minute
                
                # Déterminer si cette entrée est anormale
                is_anomaly = with_anomalies and random.random() < 0.1  # 10% d'anomalies
                
                # Générer les valeurs RTT et sauts
                if is_anomaly:
                    rtt = normal_rtt_mean * 3 + random.uniform(0, 50)  # Anomalie de latence
                    hops = normal_hops + random.randint(0, 5)  # Plus de sauts
                    packet_loss = random.random() < 0.2  # 20% de chance de perte
                else:
                    rtt = normal_rtt_mean + random.normalvariate(0, normal_rtt_std)
                    hops = normal_hops + random.choice([-1, 0, 0, 0, 1])
                    packet_loss = random.random() < packet_loss_rate
                
                # Créer l'entrée
                entry = {
                    "timestamp": datetime.fromtimestamp(entry_time).isoformat(),
                    "rtt": max(1, round(rtt, 2)),
                    "hops": max(1, hops),
                    "sent": 1,
                    "received": 0 if packet_loss else 1,
                    "target": "test-target.netsecurepro.local",
                    "size_bytes": 64,
                    "seq": i + 1
                }
                
                test_data.append(entry)
            
            # Sauvegarder les données de test
            file_path = os.path.join(self.data_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Données de test générées dans {file_path}: {entries} entrées")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la génération des données de test: {e}")
            return False

# Fonction pour exécuter une analyse rapide
def run_quick_analysis(filename: str = "test_echo_data.json", generate_test: bool = True):
    """
    Exécute une analyse rapide sur un fichier de données echo
    
    Args:
        filename: Nom du fichier à analyser
        generate_test: Générer des données de test si True
    """
    analyzer = EchoDataAnalyzer()
    
    # Générer des données de test si demandé
    if generate_test:
        logger.info("Génération de données de test...")
        analyzer.generate_test_data(filename)
    
    # Exécuter l'analyse
    logger.info(f"Analyse du fichier {filename}...")
    results = analyzer.perform_full_analysis(filename)
    
    # Afficher un résumé des résultats
    print("\n=== RÉSUMÉ DE L'ANALYSE D'ÉCHO RÉSEAU ===")
    print(f"Fichier: {filename}")
    print(f"Points de données: {results.get('data_points', 'N/A')}")
    print(f"Score de santé réseau: {results.get('network_health', {}).get('score', 'N/A')}/100 " +
          f"({results.get('network_health', {}).get('level', 'N/A')})")
    print("\nAnalyse des temps d'aller-retour:")
    rtt = results.get('analyses', {}).get('round_trip_times', {})
    print(f"  - Moyenne: {rtt.get('avg_rtt_ms', 'N/A')} ms")
    print(f"  - Min/Max: {rtt.get('min_rtt_ms', 'N/A')}/{rtt.get('max_rtt_ms', 'N/A')} ms")
    print(f"  - Anomalies: {rtt.get('anomalies_percentage', 'N/A')}%")
    
    print("\nAnalyse des pertes de paquets:")
    loss = results.get('analyses', {}).get('packet_loss', {})
    print(f"  - Taux de perte: {loss.get('loss_rate_percentage', 'N/A')}%")
    print(f"  - Paquets perdus: {loss.get('packets_lost', 'N/A')}/{loss.get('packets_sent', 'N/A')}")
    
    print("\nRecommandations:")
    for i, rec in enumerate(results.get('recommendations', []), 1):
        print(f"  {i}. {rec}")
    
    if 'ai_recommendation' in results:
        print("\nRecommandation IA:")
        print(f"  {results['ai_recommendation']}")
    
    print(f"\nRésultats complets sauvegardés dans: {analyzer.results_dir}/{analyzer.last_analysis}")

# Point d'entrée pour les tests
if __name__ == "__main__":
    run_quick_analysis()
