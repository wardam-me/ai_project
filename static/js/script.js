/**
 * Script principal pour l'application NetSecure Pro
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Initialisation de script.js");

    // Configuration des tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Configuration des popovers Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Configuration du déclenchement automatique des toasts
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        }).show();
    });

    // Fonction pour afficher des notifications
    window.showNotification = function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
            container.appendChild(toast);
        } else {
            toastContainer.appendChild(toast);
        }

        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });
        bsToast.show();
    };

    // Fonction pour animer les compteurs
    window.animateCounter = function(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    };

    // Fonction pour formater les octets en unités lisibles
    window.formatBytes = function(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };

    // Fonction pour formater une date relative
    window.formatRelativeTime = function(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.round(diffMs / 1000);
        const diffMin = Math.round(diffSec / 60);
        const diffHour = Math.round(diffMin / 60);
        const diffDay = Math.round(diffHour / 24);

        if (diffSec < 60) {
            return "à l'instant";
        } else if (diffMin < 60) {
            return `il y a ${diffMin} minute${diffMin > 1 ? 's' : ''}`;
        } else if (diffHour < 24) {
            return `il y a ${diffHour} heure${diffHour > 1 ? 's' : ''}`;
        } else if (diffDay < 30) {
            return `il y a ${diffDay} jour${diffDay > 1 ? 's' : ''}`;
        } else {
            return date.toLocaleDateString();
        }
    };

    // Gestionnaire pour le changement de langue
    const languageLinks = document.querySelectorAll('[data-language]');
    languageLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.getAttribute('data-language');

            // Stocker la préférence de langue dans un cookie
            document.cookie = `preferred_language=${lang}; path=/; max-age=${60*60*24*30}`;

            // Appeler l'API pour changer la langue
            fetch('/api/change-language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ language: lang }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`Langue changée pour ${lang}`);
                    // Recharger la page pour appliquer les changements
                    window.location.reload();
                } else {
                    console.error("Erreur lors du changement de langue:", data.error);
                }
            })
            .catch(error => {
                console.error("Erreur lors de la requête:", error);
                // En cas d'erreur, recharger quand même la page
                window.location.reload();
            });
        });
    });

    // Fonction de débogage pour module IA
    window.debugAIModule = function(data) {
        console.group('Debug IA Module');
        console.log('Data:', data);
        console.groupEnd();
    };

    // Gestion des clones IA - Données globales
    window.aiCloneManager = {
        activeClones: {},

        // Enregistrer un nouveau clone
        registerClone: function(cloneId, cloneData) {
            this.activeClones[cloneId] = cloneData;
            console.log(`Clone IA enregistré: ${cloneId}`);
            return this.activeClones[cloneId];
        },

        // Mettre à jour les données d'un clone
        updateCloneStatus: function(cloneId, statusData) {
            if (!this.activeClones[cloneId]) {
                this.registerClone(cloneId, {});
            }
            this.activeClones[cloneId] = {...this.activeClones[cloneId], ...statusData};
            console.log(`Statut du clone mis à jour: ${cloneId}`);
            return this.activeClones[cloneId];
        },

        // Supprimer un clone
        removeClone: function(cloneId) {
            if (this.activeClones[cloneId]) {
                delete this.activeClones[cloneId];
                console.log(`Clone IA supprimé: ${cloneId}`);
                return true;
            }
            return false;
        },

        // Récupérer tous les clones actifs
        getAllClones: function() {
            return Object.values(this.activeClones);
        },

        // Récupérer un clone spécifique
        getClone: function(cloneId) {
            return this.activeClones[cloneId] || null;
        }
    };

    // Initialiser les éléments d'interface si présents
    initializeAIErrorDetection();
    initializeAIClones();
});

/**
 * Initialise la page de détection d'erreurs IA si elle est présente
 */
function initializeAIErrorDetection() {
    // Vérifier si la page est la page de détection d'erreurs
    if (document.getElementById('errorTabs')) {
        console.log('Initialisation de la page de détection d\'erreurs IA');

        // Mettre à jour en temps réel les statuts des clones IA (simulation)
        const cloneProgressBars = document.querySelectorAll('.progress-bar');
        cloneProgressBars.forEach(bar => {
            const currentValue = parseInt(bar.style.width);
            const targetValue = Math.min(currentValue + Math.round(Math.random() * 20), 100);

            setTimeout(() => {
                bar.style.width = `${targetValue}%`;
                bar.setAttribute('aria-valuenow', targetValue);
                bar.innerText = `${targetValue}%`;
            }, Math.random() * 5000 + 1000);
        });
    }
}

/**
 * Initialise la page de gestion des clones IA si elle est présente
 */
function initializeAIClones() {
    // Vérifier si la page est la page de gestion des clones
    if (document.querySelector('.clone-card')) {
        console.log('Initialisation de la page de gestion des clones IA');

        // Simulation de mises à jour périodiques des clones
        setInterval(() => {
            const cloneCards = document.querySelectorAll('.clone-card');
            if (cloneCards.length === 0) return;

            // Choisir un clone aléatoire pour mettre à jour ses statistiques
            const randomIndex = Math.floor(Math.random() * cloneCards.length);
            const cloneCard = cloneCards[randomIndex];
            const cloneId = cloneCard.getAttribute('data-clone-id');

            if (!cloneId) return;

            // Simuler une mise à jour du statut via l'API
            fetch(`/api/ai-clone/${cloneId}/status`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Mettre à jour l'interface avec les nouvelles données
                        updateCloneUI(cloneCard, data.status);
                    }
                })
                .catch(error => console.error('Erreur lors de la mise à jour du clone:', error));
        }, 10000); // Toutes les 10 secondes
    }
}

/**
 * Met à jour l'interface d'un clone avec les nouvelles données
 */
function updateCloneUI(cloneCard, cloneData) {
    // Mise à jour du pourcentage de progression
    const progressBar = cloneCard.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.width = `${cloneData.scan_progress}%`;
        progressBar.setAttribute('aria-valuenow', cloneData.scan_progress);
        progressBar.innerText = `${cloneData.scan_progress}%`;
    }

    // Mise à jour des statistiques
    const statsValueElements = cloneCard.querySelectorAll('.stat-value');
    if (statsValueElements.length >= 3) {
        // Erreurs détectées
        statsValueElements[0].innerText = cloneData.detected_errors_count;
        // Corrections appliquées
        statsValueElements[1].innerText = cloneData.corrections_count;
        // Nombre de scans
        statsValueElements[2].innerText = cloneData.scan_count;
    }

    // Mise à jour de la dernière activité
    const lastActivityElement = cloneCard.querySelector('[data-last-activity]');
    if (lastActivityElement) {
        lastActivityElement.innerText = formatRelativeTime(cloneData.last_activity_at);
    }
}