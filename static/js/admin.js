/**
 * Script pour la page d'administration centrale
 * Gestion avancée des fonctionnalités d'administration avec intégration du module IA
 */

class AdminIA {
    constructor() {
        this.iaModuleActive = false;
        this.currentIAMode = 'autonomous';
        this.clones = [];
        this.securityThreats = [];
        this.systemResources = {};
        this.initEventListeners();
    }

    /**
     * Initialisation des écouteurs d'événements
     */
    initEventListeners() {
        // Boutons de gestion des clones IA
        document.querySelectorAll('[id^="clone-action-"]').forEach(button => {
            button.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                const cloneId = e.currentTarget.dataset.cloneId;
                this.handleCloneAction(action, cloneId);
            });
        });

        // Bouton de création de clone
        const createCloneBtn = document.getElementById('createCloneBtn');
        if (createCloneBtn) {
            createCloneBtn.addEventListener('click', () => this.createNewClone());
        }

        // Changement de mode IA
        const learningMode = document.getElementById('learningMode');
        if (learningMode) {
            learningMode.addEventListener('change', (e) => {
                this.currentIAMode = e.target.value;
                this.updateIAModeSettings(this.currentIAMode);
            });
        }

        // Commutateur Mode Admin / Mode Démo
        const adminModeSwitch = document.getElementById('adminModeSwitch');
        const demoModeSwitch = document.getElementById('demoModeSwitch');
        
        if (adminModeSwitch && demoModeSwitch) {
            adminModeSwitch.addEventListener('change', (e) => {
                if (e.target.checked) {
                    demoModeSwitch.checked = false;
                    this.activateAdminMode();
                } else if (!demoModeSwitch.checked) {
                    // Si on tente de désactiver le mode admin sans activer le mode démo
                    e.target.checked = true;
                    this.showMessage("Le mode administrateur ne peut pas être désactivé directement", "warning");
                }
            });
            
            demoModeSwitch.addEventListener('change', (e) => {
                if (e.target.checked) {
                    adminModeSwitch.checked = false;
                    this.activateDemoMode();
                }
            });
        }

        // Bouton de scan de sécurité
        const securityScanBtn = document.getElementById('securityScanBtn');
        if (securityScanBtn) {
            securityScanBtn.addEventListener('click', () => this.runSecurityScan());
        }

        // Bouton d'exécution de commande système (Zone restreinte)
        const executeCommandBtn = document.getElementById('executeCommandBtn');
        if (executeCommandBtn) {
            executeCommandBtn.addEventListener('click', () => this.executeSystemCommand());
        }

        // Confirmation de réinitialisation
        const resetConfirmInput = document.getElementById('resetConfirmInput');
        const confirmResetBtn = document.getElementById('confirmResetBtn');
        
        if (resetConfirmInput && confirmResetBtn) {
            resetConfirmInput.addEventListener('input', (e) => {
                confirmResetBtn.disabled = e.target.value !== 'RÉINITIALISER';
            });
            
            confirmResetBtn.addEventListener('click', () => {
                if (resetConfirmInput.value === 'RÉINITIALISER') {
                    this.resetAllData();
                    const modal = bootstrap.Modal.getInstance(document.getElementById('confirmResetModal'));
                    if (modal) modal.hide();
                }
            });
        }

        // Boutons divers avec comportements standards
        this.setupStandardButtons();
    }

    /**
     * Gestion des actions sur les clones IA
     */
    handleCloneAction(action, cloneId) {
        switch (action) {
            case 'view':
                this.viewCloneDetails(cloneId);
                break;
            case 'pause':
                this.pauseClone(cloneId);
                break;
            case 'resume':
                this.resumeClone(cloneId);
                break;
            case 'stop':
                this.stopClone(cloneId);
                break;
            case 'restart':
                this.restartClone(cloneId);
                break;
            default:
                console.error(`Action non reconnue: ${action}`);
        }
    }

    /**
     * Affiche les détails d'un clone IA
     */
    viewCloneDetails(cloneId) {
        fetch(`/api/admin/clones/${cloneId}`)
            .then(response => response.json())
            .then(data => {
                // Afficher les détails dans une modale ou une section dédiée
                console.log('Détails du clone:', data);
                this.showMessage(`Affichage des détails du clone ${cloneId.substring(0, 8)}`, 'info');
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des détails:', error);
                this.showMessage('Erreur lors de la récupération des détails du clone', 'danger');
            });
    }

    /**
     * Met en pause un clone IA
     */
    pauseClone(cloneId) {
        fetch(`/api/admin/clones/${cloneId}/pause`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            this.showMessage(`Clone ${cloneId.substring(0, 8)} mis en pause`, 'warning');
            // Mettre à jour l'interface utilisateur
        })
        .catch(error => {
            console.error('Erreur lors de la mise en pause:', error);
            this.showMessage('Erreur lors de la mise en pause du clone', 'danger');
        });
    }

    /**
     * Reprend l'exécution d'un clone IA
     */
    resumeClone(cloneId) {
        fetch(`/api/admin/clones/${cloneId}/resume`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            this.showMessage(`Clone ${cloneId.substring(0, 8)} repris`, 'success');
            // Mettre à jour l'interface utilisateur
        })
        .catch(error => {
            console.error('Erreur lors de la reprise:', error);
            this.showMessage('Erreur lors de la reprise du clone', 'danger');
        });
    }

    /**
     * Arrête un clone IA
     */
    stopClone(cloneId) {
        fetch(`/api/admin/clones/${cloneId}/stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            this.showMessage(`Clone ${cloneId.substring(0, 8)} arrêté`, 'danger');
            // Mettre à jour l'interface utilisateur
        })
        .catch(error => {
            console.error('Erreur lors de l\'arrêt:', error);
            this.showMessage('Erreur lors de l\'arrêt du clone', 'danger');
        });
    }

    /**
     * Redémarre un clone IA
     */
    restartClone(cloneId) {
        fetch(`/api/admin/clones/${cloneId}/restart`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            this.showMessage(`Clone ${cloneId.substring(0, 8)} redémarré`, 'success');
            // Mettre à jour l'interface utilisateur
        })
        .catch(error => {
            console.error('Erreur lors du redémarrage:', error);
            this.showMessage('Erreur lors du redémarrage du clone', 'danger');
        });
    }

    /**
     * Crée un nouveau clone IA
     */
    createNewClone() {
        const cloneType = document.getElementById('cloneType').value;
        const clonePriority = document.getElementById('clonePriority').value;
        
        // Récupération des permissions
        const permissions = {
            network: document.getElementById('clonePermNetwork').checked,
            repair: document.getElementById('clonePermRepair').checked,
            notify: document.getElementById('clonePermNotify').checked,
            system: document.getElementById('clonePermSystem').checked
        };
        
        // Configuration personnalisée pour le type 'custom'
        let customConfig = null;
        if (cloneType === 'custom') {
            try {
                const configText = document.getElementById('customConfig').value;
                customConfig = configText ? JSON.parse(configText) : {};
            } catch (e) {
                this.showMessage('Configuration JSON invalide', 'danger');
                return;
            }
        }
        
        const cloneData = {
            type: cloneType,
            priority: clonePriority,
            permissions: permissions,
            custom_config: customConfig
        };
        
        fetch('/api/admin/clones/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cloneData)
        })
        .then(response => response.json())
        .then(data => {
            this.showMessage(`Nouveau clone IA créé avec succès: ${data.clone_id.substring(0, 8)}`, 'success');
            // Fermer la modale et rafraîchir la liste des clones
            const modal = bootstrap.Modal.getInstance(document.getElementById('createCloneModal'));
            if (modal) modal.hide();
            this.refreshClonesList();
        })
        .catch(error => {
            console.error('Erreur lors de la création du clone:', error);
            this.showMessage('Erreur lors de la création du clone IA', 'danger');
        });
    }

    /**
     * Met à jour les paramètres selon le mode d'IA sélectionné
     */
    updateIAModeSettings(mode) {
        const resourceLimit = document.getElementById('resourceLimit');
        const scanInterval = document.getElementById('scanInterval');
        
        // Ajuster les valeurs par défaut selon le mode
        switch (mode) {
            case 'passive':
                resourceLimit.value = 30;
                scanInterval.value = 120;
                break;
            case 'active':
                resourceLimit.value = 50;
                scanInterval.value = 60;
                break;
            case 'supervised':
                resourceLimit.value = 70;
                scanInterval.value = 45;
                break;
            case 'autonomous':
                resourceLimit.value = 85;
                scanInterval.value = 30;
                break;
        }
        
        // Mettre à jour l'affichage du pourcentage
        const resourceLimitValue = document.getElementById('resourceLimitValue');
        if (resourceLimitValue) {
            resourceLimitValue.textContent = resourceLimit.value + '%';
        }
        
        this.showMessage(`Mode d'apprentissage IA défini sur: ${mode}`, 'info');
    }

    /**
     * Active le mode administrateur (accès complet)
     */
    activateAdminMode() {
        document.querySelectorAll('.admin-only').forEach(el => {
            el.classList.remove('disabled');
            el.removeAttribute('disabled');
        });
        
        document.querySelectorAll('.restricted-zone').forEach(el => {
            el.classList.remove('d-none');
        });
        
        this.showMessage('Mode administrateur activé - Accès complet', 'success');
        
        // Mettre à jour les options d'API côté serveur
        fetch('/api/admin/set-mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: 'admin' })
        }).catch(error => console.error('Erreur lors du changement de mode:', error));
    }

    /**
     * Active le mode démo (accès restreint)
     */
    activateDemoMode() {
        document.querySelectorAll('.admin-only').forEach(el => {
            el.classList.add('disabled');
            el.setAttribute('disabled', 'disabled');
        });
        
        document.querySelectorAll('.restricted-zone').forEach(el => {
            el.classList.add('d-none');
        });
        
        this.showMessage('Mode démo activé - Fonctionnalités restreintes', 'warning');
        
        // Mettre à jour les options d'API côté serveur
        fetch('/api/admin/set-mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: 'demo' })
        }).catch(error => console.error('Erreur lors du changement de mode:', error));
    }

    /**
     * Lance un scan de sécurité complet avec IA
     */
    runSecurityScan() {
        this.showMessage('Scan de sécurité complet lancé - Analyse en cours...', 'info');
        
        // Simuler un traitement en cours (spinner)
        const scanButton = document.getElementById('securityScanBtn');
        if (scanButton) {
            const originalText = scanButton.innerHTML;
            scanButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyse...';
            scanButton.disabled = true;
            
            // Appel à l'API de scan
            fetch('/api/admin/security/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                // Restaurer le bouton
                scanButton.innerHTML = originalText;
                scanButton.disabled = false;
                
                // Afficher les résultats
                this.showMessage(`Scan terminé - ${data.threats_count} menaces détectées`, 'success');
                this.updateSecurityDashboard(data);
            })
            .catch(error => {
                console.error('Erreur lors du scan:', error);
                scanButton.innerHTML = originalText;
                scanButton.disabled = false;
                this.showMessage('Erreur lors du scan de sécurité', 'danger');
            });
        }
    }

    /**
     * Met à jour le tableau de bord de sécurité avec les nouvelles données
     */
    updateSecurityDashboard(data) {
        // Mettre à jour les compteurs
        const threatCount = document.getElementById('threatCount');
        if (threatCount) threatCount.textContent = data.threats_count;
        
        // Mettre à jour la liste des menaces
        const threatsList = document.getElementById('threatsList');
        if (threatsList) {
            threatsList.innerHTML = '';
            data.threats.forEach(threat => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${threat.timestamp}</td>
                    <td>${threat.type}</td>
                    <td>${threat.description}</td>
                    <td><span class="badge bg-${this.getSeverityClass(threat.severity)}">${threat.severity}</span></td>
                `;
                threatsList.appendChild(row);
            });
        }
        
        // Mettre à jour le score de sécurité global
        const securityScore = document.getElementById('securityScore');
        if (securityScore) {
            securityScore.textContent = data.security_score + '%';
            securityScore.className = `badge bg-${this.getScoreClass(data.security_score)}`;
        }
    }

    /**
     * Obtient la classe CSS pour une sévérité donnée
     */
    getSeverityClass(severity) {
        switch (severity.toLowerCase()) {
            case 'critical': return 'danger';
            case 'high': return 'warning';
            case 'medium': return 'info';
            case 'low': return 'success';
            default: return 'secondary';
        }
    }

    /**
     * Obtient la classe CSS pour un score de sécurité
     */
    getScoreClass(score) {
        if (score >= 90) return 'success';
        if (score >= 70) return 'info';
        if (score >= 50) return 'warning';
        return 'danger';
    }

    /**
     * Exécute une commande système (zone restreinte)
     */
    executeSystemCommand() {
        const commandInput = document.getElementById('systemCommand');
        const commandOutput = document.getElementById('commandOutput');
        
        if (!commandInput || !commandOutput) return;
        
        const command = commandInput.value.trim();
        if (!command) {
            this.showMessage('Veuillez saisir une commande', 'warning');
            return;
        }
        
        // Ajouter la commande au terminal
        commandOutput.innerHTML += `<div>$ ${command}</div>`;
        
        // Appel à l'API d'exécution de commande
        fetch('/api/admin/system/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            // Afficher la sortie
            if (data.success) {
                commandOutput.innerHTML += `<div class="text-success">${data.output}</div>`;
            } else {
                commandOutput.innerHTML += `<div class="text-danger">${data.error}</div>`;
            }
            
            // Scroller vers le bas
            commandOutput.scrollTop = commandOutput.scrollHeight;
            
            // Effacer l'entrée
            commandInput.value = '';
        })
        .catch(error => {
            console.error('Erreur lors de l\'exécution:', error);
            commandOutput.innerHTML += `<div class="text-danger">Erreur: Impossible d'exécuter la commande</div>`;
            commandOutput.scrollTop = commandOutput.scrollHeight;
        });
    }

    /**
     * Rafraîchit la liste des clones IA
     */
    refreshClonesList() {
        fetch('/api/admin/clones')
            .then(response => response.json())
            .then(data => {
                this.clones = data.clones;
                this.updateClonesTable();
            })
            .catch(error => {
                console.error('Erreur lors du rafraîchissement de la liste des clones:', error);
                this.showMessage('Erreur lors du chargement des clones IA', 'danger');
            });
    }

    /**
     * Met à jour le tableau des clones
     */
    updateClonesTable() {
        const clonesTable = document.getElementById('clonesTable');
        if (!clonesTable || !clonesTable.querySelector('tbody')) return;
        
        const tbody = clonesTable.querySelector('tbody');
        tbody.innerHTML = '';
        
        this.clones.forEach(clone => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${clone.id.substring(0, 8)}</td>
                <td>${clone.type}</td>
                <td>
                    <span class="badge bg-${this.getStatusClass(clone.status)}">${clone.status}</span>
                </td>
                <td>${this.formatDate(clone.created_at)}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar bg-info" role="progressbar" style="width: ${clone.performance}%">
                            ${clone.performance}%
                        </div>
                    </div>
                </td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-info" onclick="window.adminIA.viewCloneDetails('${clone.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${clone.status === 'running' ? 
                            `<button class="btn btn-sm btn-warning" onclick="window.adminIA.pauseClone('${clone.id}')">
                                <i class="fas fa-pause"></i>
                            </button>` : 
                            `<button class="btn btn-sm btn-success" onclick="window.adminIA.resumeClone('${clone.id}')">
                                <i class="fas fa-play"></i>
                            </button>`
                        }
                        <button class="btn btn-sm btn-danger" onclick="window.adminIA.stopClone('${clone.id}')">
                            <i class="fas fa-stop"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    /**
     * Obtient la classe CSS pour un statut donné
     */
    getStatusClass(status) {
        switch (status.toLowerCase()) {
            case 'running': return 'success';
            case 'paused': return 'warning';
            case 'stopped': return 'secondary';
            case 'error': return 'danger';
            default: return 'info';
        }
    }

    /**
     * Formate une date
     */
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    /**
     * Réinitialise toutes les données (action irréversible)
     */
    resetAllData() {
        fetch('/api/admin/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showMessage('Toutes les données ont été réinitialisées avec succès', 'success');
                // Recharger la page après un court délai
                setTimeout(() => window.location.reload(), 2000);
            } else {
                this.showMessage('Erreur lors de la réinitialisation: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la réinitialisation:', error);
            this.showMessage('Erreur lors de la réinitialisation des données', 'danger');
        });
    }

    /**
     * Configure les boutons standards
     */
    setupStandardButtons() {
        const buttonActions = {
            'clearCacheBtn': { message: 'Cache vidé avec succès', type: 'success' },
            'optimizeDbBtn': { message: 'Base de données optimisée', type: 'success' },
            'rebootSystemBtn': { message: 'Redémarrage programmé', type: 'warning' },
            'resetPermissionsBtn': { message: 'Permissions réinitialisées', type: 'warning' },
            'revokeSessionsBtn': { message: 'Sessions révoquées', type: 'warning' },
            'backupDbBtn': { message: 'Sauvegarde de la base de données en cours', type: 'info' },
            'exportLogsBtn': { message: 'Journaux exportés', type: 'success' },
            'clearLogsBtn': { message: 'Journaux effacés', type: 'warning' },
            'exportAnalyticsBtn': { message: 'Analytique exportée', type: 'success' },
            'refreshAnalyticsBtn': { message: 'Données analytiques actualisées', type: 'info' },
            'saveSettingsBtn': { message: 'Paramètres enregistrés', type: 'success' },
            'addUserBtn': { message: 'Utilisateur ajouté avec succès', type: 'success' }
        };
        
        Object.entries(buttonActions).forEach(([buttonId, action]) => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.addEventListener('click', () => {
                    // Simuler une action réussie
                    setTimeout(() => {
                        this.showMessage(action.message, action.type);
                    }, 500);
                });
            }
        });
    }

    /**
     * Affiche un message toast
     */
    showMessage(message, type = 'info') {
        // On utilise la fonction globale si elle existe, sinon on crée un toast manuellement
        if (window.showToast) {
            window.showToast(message, type);
            return;
        }
        
        // Créer un élément toast
        const toastContainer = document.createElement('div');
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1050';
        
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        const toastContent = document.createElement('div');
        toastContent.className = 'd-flex';
        
        const toastBody = document.createElement('div');
        toastBody.className = 'toast-body';
        toastBody.textContent = message;
        
        const toastClose = document.createElement('button');
        toastClose.type = 'button';
        toastClose.className = 'btn-close btn-close-white me-2 m-auto';
        toastClose.setAttribute('data-bs-dismiss', 'toast');
        toastClose.setAttribute('aria-label', 'Close');
        
        toastContent.appendChild(toastBody);
        toastContent.appendChild(toastClose);
        toastEl.appendChild(toastContent);
        toastContainer.appendChild(toastEl);
        
        document.body.appendChild(toastContainer);
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Supprimer le toast après disparition
        toastEl.addEventListener('hidden.bs.toast', function() {
            document.body.removeChild(toastContainer);
        });
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Rendre l'instance accessible globalement
    window.adminIA = new AdminIA();
    
    // Charger les données initiales
    window.adminIA.refreshClonesList();
    
    console.log('Module d\'administration IA initialisé');
});