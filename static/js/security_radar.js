/**
 * Script pour la visualisation interactive du radar de sécurité
 * Permet de comparer et d'analyser différentes dimensions de sécurité WiFi
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Initialisation du radar de sécurité...");

    // Récupérer les dimensions de sécurité
    const securityDimensions = getSecurityDimensionsData();
    
    // Initialiser les graphiques principaux
    initializeRadarChart(securityDimensions);
    initializeDetailsCharts();
    
    // Configurer les interactions utilisateur
    setupViewModeButtons();
    setupControlPanels();
    setupRefreshButton();
});

/**
 * Récupère les données de dimensions de sécurité depuis les variables du template
 */
function getSecurityDimensionsData() {
    // Ces données seraient normalement récupérées du serveur via une API
    // Pour cette démo, nous les extrayons des variables injectées dans le template
    const dimensionsElement = document.getElementById('security-dimensions-data');
    
    if (dimensionsElement) {
        try {
            return JSON.parse(dimensionsElement.textContent);
        } catch (e) {
            console.error("Erreur lors de l'analyse des dimensions de sécurité:", e);
        }
    }
    
    // Valeurs par défaut si les données ne sont pas disponibles
    return {
        protocol: 75,
        encryption: 80,
        authentication: 70,
        password: 65,
        privacy: 60
    };
}

/**
 * Initialise le graphique radar principal
 */
function initializeRadarChart(securityDimensions) {
    const ctx = document.getElementById('securityRadarChart').getContext('2d');
    
    // Configurer les données du radar
    const dimensions = Object.keys(securityDimensions);
    const values = dimensions.map(dim => securityDimensions[dim]);
    
    // Déterminer la couleur en fonction du score moyen
    const avgScore = values.reduce((sum, val) => sum + val, 0) / values.length;
    let color = getScoreColor(avgScore);
    
    // Créer le graphique radar
    window.radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: dimensions.map(dim => dim.charAt(0).toUpperCase() + dim.slice(1)),
            datasets: [
                {
                    label: 'Niveau actuel',
                    data: values,
                    backgroundColor: color + '40', // Avec transparence
                    borderColor: color,
                    pointBackgroundColor: color,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: color,
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'Niveau optimal',
                    data: dimensions.map(() => 90), // Cible optimale fixée à 90
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderColor: 'rgba(0, 123, 255, 0.5)',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.2)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)'
                    },
                    pointLabels: {
                        color: '#666',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: {
                        stepSize: 20,
                        backdropColor: 'transparent'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw + '%';
                        }
                    }
                }
            }
        }
    });
    
    console.log("Graphique radar initialisé");
}

/**
 * Initialise les graphiques de détails pour chaque dimension
 */
function initializeDetailsCharts() {
    // Initialiser les graphiques pour chaque dimension
    createDimensionDetailsChart('protocolDetailsChart', 'Distribution des Protocoles', {
        'WPA3': 15,
        'WPA2': 45,
        'WPA': 25,
        'WEP': 10,
        'Ouvert': 5
    });
    
    createDimensionDetailsChart('encryptionDetailsChart', 'Types de Chiffrement', {
        'GCMP': 10,
        'AES/CCMP': 55,
        'TKIP': 25,
        'Aucun': 10
    });
    
    createDimensionDetailsChart('authenticationDetailsChart', 'Méthodes d\'Authentification', {
        'SAE': 15,
        'Enterprise': 10,
        'PSK': 65,
        'Aucune': 10
    });
    
    createSimpleGaugeChart('passwordDetailsChart', 'Force des Mots de Passe', 65);
    
    createSimpleGaugeChart('privacyDetailsChart', 'Niveau de Confidentialité', 60);
    
    console.log("Graphiques de détails initialisés");
}

/**
 * Crée un graphique en barres pour les détails d'une dimension
 */
function createDimensionDetailsChart(canvasId, title, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    // Déterminer les couleurs en fonction des types
    const colors = labels.map(label => {
        if (label.includes('WPA3') || label === 'GCMP' || label === 'SAE' || label === 'Enterprise') {
            return '#28a745'; // Vert pour les options les plus sécurisées
        } else if (label.includes('WPA2') || label === 'AES/CCMP' || label === 'PSK') {
            return '#17a2b8'; // Bleu pour les options acceptables
        } else if (label.includes('WPA') || label === 'TKIP') {
            return '#ffc107'; // Jaune pour les options moyennes
        } else {
            return '#dc3545'; // Rouge pour les options non sécurisées
        }
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.raw + '%';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Pourcentage (%)'
                    }
                }
            }
        }
    });
}

/**
 * Crée un graphique jauge simple pour les dimensions estimées
 */
function createSimpleGaugeChart(canvasId, title, value) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const color = getScoreColor(value);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Score', 'Restant'],
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [color, '#eee'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            circumference: 180,
            rotation: -90,
            cutout: '70%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        },
        plugins: [{
            id: 'gaugeText',
            afterDraw: function(chart) {
                const width = chart.width;
                const height = chart.height;
                const ctx = chart.ctx;
                
                ctx.restore();
                ctx.font = "bold 16px Arial";
                ctx.textBaseline = "middle";
                ctx.textAlign = "center";
                
                const text = value + '%';
                const textX = width / 2;
                const textY = height - 10;
                
                ctx.fillText(text, textX, textY);
                ctx.save();
                
                // Afficher le titre
                ctx.font = "14px Arial";
                ctx.fillText(title, textX, height - 40);
            }
        }]
    });
}

/**
 * Configure les boutons de mode d'affichage
 */
function setupViewModeButtons() {
    const viewCurrentBtn = document.getElementById('viewCurrentBtn');
    const viewComparisonBtn = document.getElementById('viewComparisonBtn');
    const viewHistoricalBtn = document.getElementById('viewHistoricalBtn');
    
    const currentControls = document.getElementById('currentControls');
    const comparisonControls = document.getElementById('comparisonControls');
    const historicalControls = document.getElementById('historicalControls');
    
    if (viewCurrentBtn && viewComparisonBtn && viewHistoricalBtn) {
        // Vue actuelle
        viewCurrentBtn.addEventListener('click', function() {
            // Activer/désactiver les boutons
            viewCurrentBtn.classList.add('active');
            viewComparisonBtn.classList.remove('active');
            viewHistoricalBtn.classList.remove('active');
            
            // Afficher les contrôles appropriés
            currentControls.style.display = 'block';
            comparisonControls.style.display = 'none';
            historicalControls.style.display = 'none';
            
            // Mettre à jour le radar
            updateRadarToCurrentView();
        });
        
        // Vue comparative
        viewComparisonBtn.addEventListener('click', function() {
            // Activer/désactiver les boutons
            viewCurrentBtn.classList.remove('active');
            viewComparisonBtn.classList.add('active');
            viewHistoricalBtn.classList.remove('active');
            
            // Afficher les contrôles appropriés
            currentControls.style.display = 'none';
            comparisonControls.style.display = 'block';
            historicalControls.style.display = 'none';
            
            // Mettre à jour le radar (utilise le réseau sélectionné si disponible)
            const selectedNetwork = document.getElementById('comparisonNetworkSelect').value;
            if (selectedNetwork) {
                updateRadarToComparisonView(selectedNetwork);
            } else {
                showNotification('Veuillez sélectionner un réseau pour la comparaison', 'warning');
            }
        });
        
        // Vue historique
        viewHistoricalBtn.addEventListener('click', function() {
            // Activer/désactiver les boutons
            viewCurrentBtn.classList.remove('active');
            viewComparisonBtn.classList.remove('active');
            viewHistoricalBtn.classList.add('active');
            
            // Afficher les contrôles appropriés
            currentControls.style.display = 'none';
            comparisonControls.style.display = 'none';
            historicalControls.style.display = 'block';
            
            // Mettre à jour le radar (utilise la date sélectionnée si disponible)
            const selectedDate = document.getElementById('historicalDateSelect').value;
            if (selectedDate) {
                updateRadarToHistoricalView(selectedDate);
            } else {
                showNotification('Veuillez sélectionner une date pour la comparaison historique', 'warning');
            }
        });
        
        console.log("Boutons de mode d'affichage configurés");
    }
}

/**
 * Configure les panneaux de contrôle interactifs
 */
function setupControlPanels() {
    // Configuration des sélecteurs de réseaux pour les comparaisons
    const comparisonNetworkSelect = document.getElementById('comparisonNetworkSelect');
    if (comparisonNetworkSelect) {
        comparisonNetworkSelect.addEventListener('change', function() {
            const selectedNetwork = this.value;
            if (selectedNetwork) {
                updateRadarToComparisonView(selectedNetwork);
            }
        });
    }
    
    // Configuration des sélecteurs de dates pour les comparaisons historiques
    const historicalDateSelect = document.getElementById('historicalDateSelect');
    if (historicalDateSelect) {
        historicalDateSelect.addEventListener('change', function() {
            const selectedDate = this.value;
            if (selectedDate) {
                updateRadarToHistoricalView(selectedDate);
            }
        });
    }
    
    // Configuration des cases à cocher pour les options d'affichage
    const showTargetCheckbox = document.getElementById('showTarget');
    if (showTargetCheckbox) {
        showTargetCheckbox.addEventListener('change', function() {
            if (window.radarChart) {
                window.radarChart.data.datasets[1].hidden = !this.checked;
                window.radarChart.update();
            }
        });
    }
    
    console.log("Panneaux de contrôle configurés");
}

/**
 * Met à jour le radar pour afficher la vue actuelle standard
 */
function updateRadarToCurrentView() {
    // Utiliser les données de dimensions actuelles
    const dimensions = getSecurityDimensionsData();
    
    if (window.radarChart) {
        // Mise à jour des données actuelles
        window.radarChart.data.datasets[0].data = Object.values(dimensions);
        
        // Réinitialiser le style du dataset actuel
        const avgScore = Object.values(dimensions).reduce((sum, val) => sum + val, 0) / Object.keys(dimensions).length;
        const color = getScoreColor(avgScore);
        
        window.radarChart.data.datasets[0].backgroundColor = color + '40';
        window.radarChart.data.datasets[0].borderColor = color;
        window.radarChart.data.datasets[0].pointBackgroundColor = color;
        window.radarChart.data.datasets[0].pointHoverBorderColor = color;
        
        // Supprimer tout dataset de comparaison supplémentaire
        if (window.radarChart.data.datasets.length > 2) {
            window.radarChart.data.datasets.splice(2, window.radarChart.data.datasets.length - 2);
        }
        
        window.radarChart.update();
        console.log("Vue actuelle mise à jour");
    }
}

/**
 * Met à jour le radar pour afficher une comparaison avec un réseau spécifique
 */
function updateRadarToComparisonView(bssid) {
    // Dans une application réelle, ces données viendraient d'une API
    // Pour cette démonstration, nous utilisons des données fictives
    const comparisonData = {
        "00:11:22:33:44:55": { // Réseau Domicile (WPA2)
            protocol: 80,
            encryption: 85,
            authentication: 75,
            password: 70,
            privacy: 75
        },
        "AA:BB:CC:DD:EE:FF": { // Réseau Ancien (WEP)
            protocol: 20,
            encryption: 15,
            authentication: 10,
            password: 30,
            privacy: 25
        },
        "11:22:33:44:55:66": { // Réseau Public (OPEN)
            protocol: 0,
            encryption: 0,
            authentication: 0,
            password: 0,
            privacy: 5
        },
        "22:33:44:55:66:77": { // Réseau Enterprise (WPA2-Enterprise)
            protocol: 85,
            encryption: 85,
            authentication: 95,
            password: 90,
            privacy: 90
        },
        "33:44:55:66:77:88": { // Réseau Moderne (WPA3)
            protocol: 95,
            encryption: 95,
            authentication: 90,
            password: 85,
            privacy: 85
        }
    };
    
    // Récupérer les données du réseau sélectionné
    const networkData = comparisonData[bssid];
    if (!networkData) {
        showNotification('Données non disponibles pour ce réseau', 'warning');
        return;
    }
    
    // Obtenir les dimensions actuelles
    const currentDimensions = getSecurityDimensionsData();
    
    if (window.radarChart) {
        // Mise à jour des données actuelles
        window.radarChart.data.datasets[0].data = Object.values(currentDimensions);
        
        // Réinitialiser le style du dataset actuel
        const avgCurrentScore = Object.values(currentDimensions).reduce((sum, val) => sum + val, 0) / Object.keys(currentDimensions).length;
        const currentColor = getScoreColor(avgCurrentScore);
        
        window.radarChart.data.datasets[0].backgroundColor = currentColor + '40';
        window.radarChart.data.datasets[0].borderColor = currentColor;
        window.radarChart.data.datasets[0].pointBackgroundColor = currentColor;
        window.radarChart.data.datasets[0].pointHoverBorderColor = currentColor;
        
        // Ajouter ou mettre à jour le dataset de comparaison
        if (window.radarChart.data.datasets.length > 2) {
            window.radarChart.data.datasets[2].data = Object.values(networkData);
        } else {
            const avgCompareScore = Object.values(networkData).reduce((sum, val) => sum + val, 0) / Object.keys(networkData).length;
            const compareColor = getScoreColor(avgCompareScore);
            
            window.radarChart.data.datasets.push({
                label: 'Réseau comparé',
                data: Object.values(networkData),
                backgroundColor: compareColor + '40',
                borderColor: compareColor,
                pointBackgroundColor: compareColor,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: compareColor,
                pointRadius: 5,
                pointHoverRadius: 7
            });
        }
        
        window.radarChart.update();
        console.log("Vue comparative mise à jour");
    }
}

/**
 * Met à jour le radar pour afficher une comparaison avec des données historiques
 */
function updateRadarToHistoricalView(date) {
    // Dans une application réelle, ces données viendraient d'une API
    // Pour cette démonstration, nous utilisons des données fictives
    const historicalData = {
        // Date il y a 30 jours
        [(new Date(Date.now() - 30*24*60*60*1000)).toISOString().split('T')[0]]: {
            protocol: 60,
            encryption: 55,
            authentication: 50,
            password: 45,
            privacy: 40
        },
        // Date il y a 15 jours
        [(new Date(Date.now() - 15*24*60*60*1000)).toISOString().split('T')[0]]: {
            protocol: 65,
            encryption: 70,
            authentication: 60,
            password: 55,
            privacy: 50
        },
        // Date il y a 7 jours
        [(new Date(Date.now() - 7*24*60*60*1000)).toISOString().split('T')[0]]: {
            protocol: 70,
            encryption: 75,
            authentication: 65,
            password: 60,
            privacy: 55
        }
    };
    
    // Récupérer les données historiques pour la date sélectionnée
    const historicalDimensions = historicalData[date];
    if (!historicalDimensions) {
        showNotification('Données historiques non disponibles pour cette date', 'warning');
        return;
    }
    
    // Obtenir les dimensions actuelles
    const currentDimensions = getSecurityDimensionsData();
    
    if (window.radarChart) {
        // Mise à jour des données actuelles
        window.radarChart.data.datasets[0].data = Object.values(currentDimensions);
        
        // Réinitialiser le style du dataset actuel
        const avgCurrentScore = Object.values(currentDimensions).reduce((sum, val) => sum + val, 0) / Object.keys(currentDimensions).length;
        const currentColor = getScoreColor(avgCurrentScore);
        
        window.radarChart.data.datasets[0].backgroundColor = currentColor + '40';
        window.radarChart.data.datasets[0].borderColor = currentColor;
        window.radarChart.data.datasets[0].pointBackgroundColor = currentColor;
        window.radarChart.data.datasets[0].pointHoverBorderColor = currentColor;
        
        // Ajouter ou mettre à jour le dataset historique
        if (window.radarChart.data.datasets.length > 2) {
            window.radarChart.data.datasets[2].data = Object.values(historicalDimensions);
            window.radarChart.data.datasets[2].label = `Données du ${formatDate(date)}`;
        } else {
            window.radarChart.data.datasets.push({
                label: `Données du ${formatDate(date)}`,
                data: Object.values(historicalDimensions),
                backgroundColor: 'rgba(108, 117, 125, 0.4)',
                borderColor: 'rgba(108, 117, 125, 0.8)',
                pointBackgroundColor: 'rgba(108, 117, 125, 0.8)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(108, 117, 125, 0.8)',
                pointRadius: 5,
                pointHoverRadius: 7
            });
        }
        
        window.radarChart.update();
        console.log("Vue historique mise à jour");
    }
}

/**
 * Configure le bouton d'actualisation
 */
function setupRefreshButton() {
    const refreshButton = document.getElementById('refreshRadarBtn');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            // Simulation d'une nouvelle analyse
            showNotification('Analyse en cours...', 'info');
            
            // Dans une application réelle, nous ferions un appel AJAX pour récupérer de nouvelles données
            setTimeout(function() {
                updateRadarToCurrentView();
                showNotification('Analyse terminée avec succès !', 'success');
            }, 1500);
        });
        
        console.log("Bouton d'actualisation configuré");
    }
}

/**
 * Affiche une notification temporaire
 */
function showNotification(message, type = 'success') {
    const container = document.createElement('div');
    container.className = `toast-container position-fixed bottom-0 end-0 p-3`;
    container.style.zIndex = "1050";
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const flexContainer = document.createElement('div');
    flexContainer.className = 'd-flex';
    
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Fermer');
    
    flexContainer.appendChild(toastBody);
    flexContainer.appendChild(closeButton);
    toast.appendChild(flexContainer);
    container.appendChild(toast);
    
    document.body.appendChild(container);
    
    const toastInstance = new bootstrap.Toast(toast, { delay: 3000 });
    toastInstance.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        document.body.removeChild(container);
    });
}

/**
 * Formate une date en format français
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

/**
 * Détermine la couleur en fonction du score de sécurité
 */
function getScoreColor(score) {
    if (score >= 80) {
        return 'rgba(40, 167, 69, 1)'; // Vert - Bon
    } else if (score >= 50) {
        return 'rgba(255, 193, 7, 1)'; // Jaune - Moyen
    } else {
        return 'rgba(220, 53, 69, 1)'; // Rouge - Mauvais
    }
}