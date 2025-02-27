"""
Test du système de gestion des clones IA pour NetSecure Pro
"""
import json
import logging
from ai_clone_manager import get_clone_manager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_clone_manager():
    """Teste les fonctionnalités du gestionnaire de clones IA"""
    logger.info("Début des tests du gestionnaire de clones IA")
    
    # Récupérer l'instance du gestionnaire
    clone_manager = get_clone_manager()
    
    # Vérifier que des clones sont chargés
    clones = clone_manager.get_all_clones()
    logger.info(f"Nombre de clones chargés: {len(clones)}")
    
    # Récupérer les statistiques
    stats = clone_manager.get_clone_statistics()
    logger.info(f"Statistiques des clones: {json.dumps(stats, indent=2)}")
    
    # Tester le traitement d'une demande d'analyse réseau
    logger.info("Test d'analyse réseau avec le meilleur clone disponible")
    result = clone_manager.process_request(
        "analyze_network", 
        {
            "overall_score": 75,
            "device_count": 8,
            "recommendation_count": 5
        }
    )
    
    # Afficher les résultats
    logger.info(f"Résultat de l'analyse: {json.dumps(result, indent=2)}")
    
    # Création d'un nouveau clone pour les tests
    logger.info("Création d'un nouveau clone de test")
    new_clone = clone_manager.create_clone(
        name="Clone de Test",
        specialization="vulnerability",
        learning_rate=0.6,
        confidence_threshold=0.8
    )
    
    logger.info(f"Nouveau clone créé: {json.dumps(new_clone.to_dict(), indent=2)}")
    
    # Lancer un entraînement simulé
    logger.info("Démarrage d'un entraînement simulé")
    training_result = new_clone.start_training({
        "datasets": ["vulnerability_analysis", "wifi_threats"],
        "epochs": 5,
        "batch_size": 32,
        "preserve_previous": True
    })
    
    logger.info(f"Résultat de l'initialisation d'entraînement: {json.dumps(training_result, indent=2)}")
    
    # Compléter l'entraînement avec des résultats simulés
    session_id = training_result["session_id"]
    logger.info(f"Complétion de l'entraînement pour la session {session_id}")
    
    completion_result = new_clone.complete_training(session_id, {
        "improvement": "+12.5%",
        "performance_metrics": {
            "accuracy": 0.85,
            "precision": 0.88,
            "recall": 0.82,
            "f1_score": 0.85
        }
    })
    
    logger.info(f"Résultat de la fin d'entraînement: {json.dumps(completion_result, indent=2)}")
    
    # Sauvegarder les clones mis à jour
    clone_manager.save_clones()
    
    # Charger à nouveau pour vérifier la persistance
    new_manager = get_clone_manager()
    reloaded_clones = new_manager.get_all_clones()
    logger.info(f"Nombre de clones après rechargement: {len(reloaded_clones)}")
    
    logger.info("Tests terminés avec succès")

if __name__ == "__main__":
    test_clone_manager()