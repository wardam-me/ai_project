"""
Routes API pour l'application NetSecure Pro
"""
import json
import logging
from functools import wraps

from flask import jsonify, request, current_app
from flask_login import current_user, login_required

from ai_clone_manager import get_clone_manager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Décorateur pour vérifier si l'utilisateur est administrateur
def admin_api_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({
                "success": False,
                "error": "Accès refusé. Vous devez être administrateur pour accéder à cette API."
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def register_api_routes(app):
    """
    Enregistre les routes API de l'application
    """
    
    # ======================================================
    # API pour la gestion des clones IA
    # ======================================================
    
    @app.route('/api/admin/clones', methods=['GET'])
    @admin_api_required
    def get_all_clones():
        """API: Récupère tous les clones IA"""
        try:
            clone_manager = get_clone_manager()
            clones = clone_manager.get_all_clones()
            return jsonify({
                "success": True,
                "clones": clones
            })
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des clones: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/admin/clones/<clone_id>', methods=['GET'])
    @admin_api_required
    def get_clone(clone_id):
        """API: Récupère un clone IA spécifique"""
        try:
            clone_manager = get_clone_manager()
            clone = clone_manager.get_clone(clone_id)
            
            if not clone:
                return jsonify({
                    "success": False,
                    "error": f"Clone non trouvé: {clone_id}"
                }), 404
            
            return jsonify({
                "success": True,
                "clone": clone.to_dict()
            })
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du clone {clone_id}: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/admin/clones', methods=['POST'])
    @admin_api_required
    def create_clone():
        """API: Crée un nouveau clone IA"""
        try:
            data = request.json
            
            # Validation des données
            if not data.get('name'):
                return jsonify({
                    "success": False,
                    "error": "Le nom du clone est requis"
                }), 400
            
            specialization = data.get('specialization', 'general')
            learning_rate = float(data.get('learning_rate', 0.5))
            confidence_threshold = float(data.get('confidence_threshold', 0.7))
            
            # Créer le clone
            clone_manager = get_clone_manager()
            new_clone = clone_manager.create_clone(
                name=data['name'],
                specialization=specialization,
                learning_rate=learning_rate,
                confidence_threshold=confidence_threshold
            )
            
            return jsonify({
                "success": True,
                "clone": new_clone.to_dict()
            })
        except Exception as e:
            logger.error(f"Erreur lors de la création du clone: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/admin/clones/<clone_id>', methods=['PATCH'])
    @admin_api_required
    def update_clone(clone_id):
        """API: Met à jour un clone IA existant"""
        try:
            data = request.json
            
            # Vérifier si des données ont été fournies
            if not data:
                return jsonify({
                    "success": False,
                    "error": "Aucune donnée fournie pour la mise à jour"
                }), 400
            
            # Mettre à jour le clone
            clone_manager = get_clone_manager()
            updated_clone = clone_manager.update_clone(clone_id, data)
            
            if not updated_clone:
                return jsonify({
                    "success": False,
                    "error": f"Clone non trouvé: {clone_id}"
                }), 404
            
            return jsonify({
                "success": True,
                "clone": updated_clone.to_dict()
            })
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du clone {clone_id}: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/admin/clones/<clone_id>', methods=['DELETE'])
    @admin_api_required
    def delete_clone(clone_id):
        """API: Supprime un clone IA"""
        try:
            clone_manager = get_clone_manager()
            success = clone_manager.delete_clone(clone_id)
            
            if not success:
                return jsonify({
                    "success": False,
                    "error": f"Clone non trouvé: {clone_id}"
                }), 404
            
            return jsonify({
                "success": True,
                "message": f"Clone {clone_id} supprimé avec succès"
            })
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du clone {clone_id}: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/admin/clones/statistics', methods=['GET'])
    @admin_api_required
    def get_clones_statistics():
        """API: Récupère les statistiques des clones IA"""
        try:
            clone_manager = get_clone_manager()
            statistics = clone_manager.get_clone_statistics()
            
            return jsonify({
                "success": True,
                "statistics": statistics
            })
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques des clones: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/admin/clones/<clone_id>/train', methods=['POST'])
    @admin_api_required
    def train_clone(clone_id):
        """API: Démarre l'entraînement d'un clone IA"""
        try:
            data = request.json
            
            # Validation des données
            if not data.get('datasets'):
                return jsonify({
                    "success": False,
                    "error": "Les jeux de données d'entraînement sont requis"
                }), 400
            
            # Préparer les paramètres d'entraînement
            training_params = {
                "datasets": data.get('datasets', []),
                "epochs": int(data.get('epochs', 10)),
                "batch_size": int(data.get('batch_size', 32)),
                "preserve_previous": bool(data.get('preserve_previous', True))
            }
            
            # Démarrer l'entraînement
            clone_manager = get_clone_manager()
            clone = clone_manager.get_clone(clone_id)
            
            if not clone:
                return jsonify({
                    "success": False,
                    "error": f"Clone non trouvé: {clone_id}"
                }), 404
            
            # Simuler les résultats d'entraînement pour la démo
            import random
            import time
            from threading import Thread
            
            def simulate_training(clone, params):
                """Fonction pour simuler l'entraînement en arrière-plan"""
                # Démarrer l'entraînement
                training_result = clone.start_training(params)
                session_id = training_result["session_id"]
                
                # Attendre un délai simulé (proportionnel au nombre d'époques)
                training_time = params.get("epochs", 10) * 0.5  # 0.5 seconde par époque
                time.sleep(training_time)
                
                # Simuler les améliorations de performance
                improvement = random.uniform(0.05, 0.15)  # 5% à 15% d'amélioration
                
                # Générer des résultats d'entraînement
                results = {
                    "improvement": f"+{(improvement * 100):.1f}%",
                    "performance_metrics": {
                        "accuracy": min(1.0, clone.performance_metrics["accuracy"] + improvement),
                        "precision": min(1.0, clone.performance_metrics["precision"] + improvement),
                        "recall": min(1.0, clone.performance_metrics["recall"] + improvement),
                        "f1_score": min(1.0, clone.performance_metrics["f1_score"] + improvement),
                    }
                }
                
                # Terminer l'entraînement
                clone.complete_training(session_id, results)
                
                # Sauvegarder les modifications
                clone_manager.save_clones()
            
            # Démarrer l'entraînement dans un thread séparé
            training_thread = Thread(target=simulate_training, args=(clone, training_params))
            training_thread.daemon = True
            training_thread.start()
            
            return jsonify({
                "success": True,
                "message": f"Entraînement du clone {clone_id} démarré avec succès",
                "params": training_params
            })
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de l'entraînement du clone {clone_id}: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/ai/process', methods=['POST'])
    @login_required
    def process_ai_request():
        """API: Traite une demande avec l'IA"""
        try:
            data = request.json
            
            # Validation des données
            if not data.get('request_type'):
                return jsonify({
                    "success": False,
                    "error": "Le type de demande est requis"
                }), 400
            
            request_type = data.get('request_type')
            request_data = data.get('data', {})
            clone_id = data.get('clone_id')  # Optionnel
            
            # Traiter la demande avec le gestionnaire de clones
            clone_manager = get_clone_manager()
            result = clone_manager.process_request(request_type, request_data, clone_id)
            
            # Vérifier s'il y a une erreur
            if "error" in result:
                return jsonify({
                    "success": False,
                    "error": result["error"]
                }), 400
            
            return jsonify({
                "success": True,
                "result": result
            })
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la demande IA: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500