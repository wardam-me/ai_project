/**
 * Script pour la visualisation interactive du radar de sécurité
 * Permet de comparer et d'analyser différentes dimensions de sécurité WiFi
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation du radar de sécurité interactif');
    
    // Récupérer les données
    const securityDimensionsElement = document.getElementById('security-dimensions-data');
    const networksElement = document.getElementById('networks-data');
    const historicalElement = document.getElementById('historical-data');
    const wifiAnalysisElement = document.getElementById('wifi-analysis-data');
    
    let securityDimensions = {};
    let networks = [];
    let historicalData = [];
    let wifiAnalysis = {};
    
    if (securityDimensionsElement) {
        securityDimensions = JSON.parse(securityDimensionsElement.textContent);
    }
    
    if (networksElement) {
        networks = JSON.parse(networksElement.textContent);
    }
    
    if (historicalElement) {
        historicalData = JSON.parse(historicalElement.textContent);
    }
    
    if (wifiAnalysisElement) {
        wifiAnalysis = JSON.parse(wifiAnalysisElement.textContent);
    }
    
    // Initialiser le graphique radar principal
    initializeRadarChart(securityDimensions);
    
    // Initialiser les graphiques de détails
    initializeDetailsCharts(wifiAnalysis);
    
    // Configurer les boutons de mode d'affichage
    setupViewModeButtons();
    
    // Configurer les panneaux de contrôle
    setupControlPanels();
    
    // Configurer le bouton d'actualisation
    setupRefreshButton();
});

/**
 * Initialise le graphique radar principal
 */
function initializeRadarChart(securityDimensions) {
    const ctx = document.getElementById('securityRadarChart');
    if (!ctx) return;
    
    // Transformer les données en format pour le radar
    const labels = [
        'Protocole', 
        'Chiffrement', 
        'Authentification',
        'Mots de passe',
        'Confidentialité'
    ];
    
    const values = [
        securityDimensions.protocol || 0,
        securityDimensions.encryption || 0,
        securityDimensions.authentication || 0,
        securityDimensions.password || 0,
        securityDimensions.privacy || 0
    ];
    
    // Valeurs cibles "idéales" pour comparaison
    const targetValues = [100, 100, 100, 100, 100];
    
    // Créer le graphique
    window.radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Sécurité Actuelle',
                    data: values,
                    fill: true,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgb(54, 162, 235)',
                    pointBackgroundColor: 'rgb(54, 162, 235)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(54, 162, 235)',
                    pointRadius: 5,
                    borderWidth: 2
                },
                {
                    label: 'Cible Optimale',
                    data: targetValues,
                    fill: true,
                    backgroundColor: 'rgba(75, 192, 75, 0.1)',
                    borderColor: 'rgba(75, 192, 75, 0.6)',
                    pointBackgroundColor: 'rgba(75, 192, 75, 0.8)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(75, 192, 75)',
                    pointRadius: 3,
                    borderWidth: 1,
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: {
                        stepSize: 20,
                        backdropColor: 'rgba(0, 0, 0, 0)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.2)'
                    },
                    pointLabels: {
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#555'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}/100`;
                        },
                        title: function(context) {
                            return context[0].label;
                        }
                    }
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Initialise les graphiques de détails pour chaque dimension
 */
function initializeDetailsCharts(wifiAnalysis) {
    // Graphique pour le protocole
    createDimensionDetailsChart('protocolDetailsChart', 'Protocoles', {
        'WPA3': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.security_type === 'WPA3').length : 0,
        'WPA2': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.security_type === 'WPA2' || n.security_type === 'WPA2-Enterprise').length : 0,
        'WPA': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.security_type === 'WPA').length : 0,
        'WEP': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.security_type === 'WEP').length : 0,
        'OPEN': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.security_type === 'OPEN').length : 0
    });
    
    // Graphique pour le chiffrement
    createDimensionDetailsChart('encryptionDetailsChart', 'Chiffrement', {
        'GCMP': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.encryption === 'GCMP').length : 0,
        'AES/CCMP': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.encryption === 'AES' || n.encryption === 'CCMP').length : 0,
        'TKIP': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.encryption === 'TKIP').length : 0,
        'Aucun': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => !n.encryption).length : 0
    });
    
    // Graphique pour l'authentification
    createDimensionDetailsChart('authenticationDetailsChart', 'Authentification', {
        'SAE': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.authentication === 'SAE').length : 0,
        'ENTERPRISE': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.authentication === 'ENTERPRISE').length : 0,
        'PSK': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.authentication === 'PSK').length : 0,
        'OWE': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => n.authentication === 'OWE').length : 0,
        'Aucune': wifiAnalysis.network_scores ? wifiAnalysis.network_scores.filter(n => !n.authentication).length : 0
    });
    
    // Pour les mots de passe et la confidentialité, on utilise des graphiques simplifiés
    // car ces valeurs sont dérivées et non directement mesurables
    createSimpleGaugeChart('passwordDetailsChart', 'Robustesse des mots de passe', 
        wifiAnalysis.security_dimensions ? wifiAnalysis.security_dimensions.password || 0 : 0);
    
    createSimpleGaugeChart('privacyDetailsChart', 'Niveau de confidentialité', 
        wifiAnalysis.security_dimensions ? wifiAnalysis.security_dimensions.privacy || 0 : 0);
}

/**
 * Crée un graphique en barres pour les détails d'une dimension
 */
function createDimensionDetailsChart(canvasId, title, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    // Définir les couleurs en fonction du type de données
    const colors = labels.map(label => {
        switch(label.toLowerCase()) {
            case 'wpa3':
            case 'gcmp':
            case 'sae':
                return 'rgba(40, 167, 69, 0.8)'; // Vert
            case 'wpa2':
            case 'wpa2-enterprise':
            case 'aes/ccmp':
            case 'enterprise':
            case 'owe':
                return 'rgba(23, 162, 184, 0.8)'; // Bleu
            case 'wpa':
            case 'psk':
            case 'tkip':
                return 'rgba(255, 193, 7, 0.8)'; // Jaune
            case 'wep':
                return 'rgba(253, 126, 20, 0.8)'; // Orange
            case 'open':
            case 'aucun':
            case 'aucune':
                return 'rgba(220, 53, 69, 0.8)'; // Rouge
            default:
                return 'rgba(108, 117, 125, 0.8)'; // Gris
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
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
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
    
    // Déterminer la couleur en fonction de la valeur
    let color;
    if (value >= 80) {
        color = 'rgba(40, 167, 69, 0.8)'; // Vert
    } else if (value >= 50) {
        color = 'rgba(255, 193, 7, 0.8)'; // Jaune
    } else {
        color = 'rgba(220, 53, 69, 0.8)'; // Rouge
    }
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Score', 'Restant'],
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [color, 'rgba(200, 200, 200, 0.2)'],
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
                    callbacks: {
                        label: function(context) {
                            return context.label === 'Score' ? `${value}/100` : '';
                        }
                    }
                }
            }
        }
    });
    
    // Ajouter le texte du score au centre
    const fontSize = ctx.width / 8;
    const valueText = document.createElement('div');
    valueText.style.position = 'absolute';
    valueText.style.top = '60%';
    valueText.style.left = '50%';
    valueText.style.transform = 'translate(-50%, -50%)';
    valueText.style.fontSize = `${fontSize}px`;
    valueText.style.fontWeight = 'bold';
    valueText.style.color = color.replace('0.8', '1');
    valueText.textContent = `${Math.round(value)}%`;
    
    ctx.parentNode.style.position = 'relative';
    ctx.parentNode.appendChild(valueText);
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
        viewCurrentBtn.addEventListener('click', function() {
            // Activer ce bouton et désactiver les autres
            viewCurrentBtn.classList.add('active');
            viewComparisonBtn.classList.remove('active');
            viewHistoricalBtn.classList.remove('active');
            
            // Afficher le panneau de contrôle correspondant
            if (currentControls) currentControls.style.display = 'block';
            if (comparisonControls) comparisonControls.style.display = 'none';
            if (historicalControls) historicalControls.style.display = 'none';
            
            // Revenir à l'affichage du radar standard
            updateRadarToCurrentView();
        });
        
        viewComparisonBtn.addEventListener('click', function() {
            viewCurrentBtn.classList.remove('active');
            viewComparisonBtn.classList.add('active');
            viewHistoricalBtn.classList.remove('active');
            
            if (currentControls) currentControls.style.display = 'none';
            if (comparisonControls) comparisonControls.style.display = 'block';
            if (historicalControls) historicalControls.style.display = 'none';
            
            // Déclencher le changement initial si un réseau est sélectionné
            const comparisonSelect = document.getElementById('comparisonNetworkSelect');
            if (comparisonSelect && comparisonSelect.value) {
                updateRadarToComparisonView(comparisonSelect.value);
            }
        });
        
        viewHistoricalBtn.addEventListener('click', function() {
            viewCurrentBtn.classList.remove('active');
            viewComparisonBtn.classList.remove('active');
            viewHistoricalBtn.classList.add('active');
            
            if (currentControls) currentControls.style.display = 'none';
            if (comparisonControls) comparisonControls.style.display = 'none';
            if (historicalControls) historicalControls.style.display = 'block';
            
            // Déclencher le changement initial si une date est sélectionnée
            const historicalSelect = document.getElementById('historicalDateSelect');
            if (historicalSelect && historicalSelect.value) {
                updateRadarToHistoricalView(historicalSelect.value);
            }
        });
    }
}

/**
 * Configure les panneaux de contrôle interactifs
 */
function setupControlPanels() {
    // Contrôles pour l'affichage actuel
    const showTargetCheckbox = document.getElementById('showTarget');
    const showLabelsCheckbox = document.getElementById('showLabels');
    const animateChangesCheckbox = document.getElementById('animateChanges');
    
    if (showTargetCheckbox) {
        showTargetCheckbox.addEventListener('change', function() {
            if (window.radarChart) {
                window.radarChart.data.datasets[1].hidden = !this.checked;
                window.radarChart.update();
            }
        });
    }
    
    // Contrôles pour la comparaison avec un réseau
    const comparisonNetworkSelect = document.getElementById('comparisonNetworkSelect');
    const showDifferenceCheckbox = document.getElementById('showDifference');
    
    if (comparisonNetworkSelect) {
        comparisonNetworkSelect.addEventListener('change', function() {
            updateRadarToComparisonView(this.value);
        });
    }
    
    // Contrôles pour la comparaison historique
    const historicalDateSelect = document.getElementById('historicalDateSelect');
    const showTrendCheckbox = document.getElementById('showTrend');
    
    if (historicalDateSelect) {
        historicalDateSelect.addEventListener('change', function() {
            updateRadarToHistoricalView(this.value);
        });
    }
}

/**
 * Met à jour le radar pour afficher la vue actuelle standard
 */
function updateRadarToCurrentView() {
    const securityDimensionsElement = document.getElementById('security-dimensions-data');
    if (!securityDimensionsElement || !window.radarChart) return;
    
    const securityDimensions = JSON.parse(securityDimensionsElement.textContent);
    
    // Extraire les valeurs pour le radar
    const values = [
        securityDimensions.protocol || 0,
        securityDimensions.encryption || 0,
        securityDimensions.authentication || 0,
        securityDimensions.password || 0,
        securityDimensions.privacy || 0
    ];
    
    // Mettre à jour le premier dataset (sécurité actuelle)
    window.radarChart.data.datasets[0].data = values;
    window.radarChart.data.datasets[0].label = 'Sécurité Actuelle';
    window.radarChart.data.datasets[0].backgroundColor = 'rgba(54, 162, 235, 0.2)';
    window.radarChart.data.datasets[0].borderColor = 'rgb(54, 162, 235)';
    
    // S'assurer que seuls deux datasets sont affichés
    if (window.radarChart.data.datasets.length > 2) {
        window.radarChart.data.datasets = window.radarChart.data.datasets.slice(0, 2);
    }
    
    // Mettre à jour le graphique
    window.radarChart.update();
}

/**
 * Met à jour le radar pour afficher une comparaison avec un réseau spécifique
 */
function updateRadarToComparisonView(bssid) {
    const networksElement = document.getElementById('networks-data');
    const securityDimensionsElement = document.getElementById('security-dimensions-data');
    
    if (!networksElement || !securityDimensionsElement || !window.radarChart) return;
    
    const networks = JSON.parse(networksElement.textContent);
    const securityDimensions = JSON.parse(securityDimensionsElement.textContent);
    
    // Trouver le réseau sélectionné
    const selectedNetwork = networks.find(n => n.bssid === bssid);
    if (!selectedNetwork) return;
    
    // Valeurs actuelles
    const currentValues = [
        securityDimensions.protocol || 0,
        securityDimensions.encryption || 0,
        securityDimensions.authentication || 0,
        securityDimensions.password || 0,
        securityDimensions.privacy || 0
    ];
    
    // Estimer les valeurs pour le réseau sélectionné
    // Ceci est une simplification - dans un système réel, vous feriez une analyse complète
    const networkType = selectedNetwork.security || 'OPEN';
    const encryption = selectedNetwork.encryption;
    const authentication = selectedNetwork.authentication;
    
    // Scores simplifiés basés sur le type de réseau
    let protocolScore = 0;
    switch(networkType) {
        case 'WPA3': protocolScore = 95; break;
        case 'WPA2-Enterprise': protocolScore = 90; break;
        case 'WPA2': protocolScore = 80; break;
        case 'WPA': protocolScore = 50; break;
        case 'WEP': protocolScore = 20; break;
        default: protocolScore = 0; // OPEN
    }
    
    // Score de chiffrement
    let encryptionScore = 0;
    switch(encryption) {
        case 'GCMP': encryptionScore = 95; break;
        case 'AES': 
        case 'CCMP': encryptionScore = 90; break;
        case 'TKIP': encryptionScore = 50; break;
        default: encryptionScore = 0; // Aucun
    }
    
    // Score d'authentification
    let authScore = 0;
    switch(authentication) {
        case 'SAE': authScore = 95; break;
        case 'ENTERPRISE': authScore = 90; break;
        case 'OWE': authScore = 85; break;
        case 'PSK': authScore = 70; break;
        default: authScore = 0; // Aucun
    }
    
    // Estimation du score de mot de passe et confidentialité
    let passwordScore = 0;
    let privacyScore = 0;
    
    if (networkType === 'WPA3') {
        passwordScore = 90;
        privacyScore = 85;
    } else if (networkType === 'WPA2-Enterprise') {
        passwordScore = 85;
        privacyScore = 90;
    } else if (networkType === 'WPA2') {
        passwordScore = 70;
        privacyScore = 70;
    } else if (networkType === 'WPA') {
        passwordScore = 50;
        privacyScore = 40;
    } else if (networkType === 'WEP') {
        passwordScore = 20;
        privacyScore = 20;
    } else {
        passwordScore = 0;
        privacyScore = 0;
    }
    
    const comparisonValues = [
        protocolScore,
        encryptionScore,
        authScore,
        passwordScore,
        privacyScore
    ];
    
    // Mettre à jour le graphique avec les deux séries
    window.radarChart.data.datasets[0].data = currentValues;
    window.radarChart.data.datasets[0].label = 'Réseau Actuel';
    
    // Définir le deuxième dataset pour le réseau comparé
    window.radarChart.data.datasets[1].data = comparisonValues;
    window.radarChart.data.datasets[1].label = `Réseau: ${selectedNetwork.ssid}`;
    window.radarChart.data.datasets[1].backgroundColor = 'rgba(255, 159, 64, 0.2)';
    window.radarChart.data.datasets[1].borderColor = 'rgb(255, 159, 64)';
    window.radarChart.data.datasets[1].borderDash = [];
    
    // Afficher les différences si demandé
    const showDifference = document.getElementById('showDifference');
    if (showDifference && showDifference.checked) {
        // Calculer les différences
        const diffValues = currentValues.map((val, idx) => Math.max(0, val - comparisonValues[idx]));
        
        // Ajouter un troisième dataset pour les différences
        if (window.radarChart.data.datasets.length < 3) {
            window.radarChart.data.datasets.push({
                label: 'Différence',
                data: diffValues,
                fill: true,
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgb(153, 102, 255)',
                pointBackgroundColor: 'rgb(153, 102, 255)',
                pointBorderColor: '#fff',
                pointRadius: 4
            });
        } else {
            window.radarChart.data.datasets[2].data = diffValues;
        }
    } else if (window.radarChart.data.datasets.length > 2) {
        // Supprimer le dataset de différence s'il existe
        window.radarChart.data.datasets = window.radarChart.data.datasets.slice(0, 2);
    }
    
    window.radarChart.update();
}

/**
 * Met à jour le radar pour afficher une comparaison avec des données historiques
 */
function updateRadarToHistoricalView(date) {
    const historicalElement = document.getElementById('historical-data');
    if (!historicalElement || !window.radarChart) return;
    
    const historicalData = JSON.parse(historicalElement.textContent);
    
    // Trouver les données pour la date sélectionnée
    const selectedData = historicalData.find(d => d.date === date);
    if (!selectedData || !selectedData.dimensions) return;
    
    // Extraire les valeurs actuelles et historiques
    const currentValues = [
        selectedData.dimensions.protocol || 0,
        selectedData.dimensions.encryption || 0,
        selectedData.dimensions.authentication || 0,
        selectedData.dimensions.password || 0,
        selectedData.dimensions.privacy || 0
    ];
    
    // Mettre à jour le premier dataset
    window.radarChart.data.datasets[0].data = currentValues;
    window.radarChart.data.datasets[0].label = `Sécurité le ${date}`;
    window.radarChart.data.datasets[0].backgroundColor = 'rgba(54, 162, 235, 0.2)';
    window.radarChart.data.datasets[0].borderColor = 'rgb(54, 162, 235)';
    
    // Pour la tendance, ajouter les données de la période précédente si disponible
    const showTrend = document.getElementById('showTrend');
    if (showTrend && showTrend.checked) {
        const currentIndex = historicalData.findIndex(d => d.date === date);
        
        if (currentIndex > 0) {
            const previousData = historicalData[currentIndex - 1];
            const previousValues = [
                previousData.dimensions.protocol || 0,
                previousData.dimensions.encryption || 0,
                previousData.dimensions.authentication || 0,
                previousData.dimensions.password || 0,
                previousData.dimensions.privacy || 0
            ];
            
            // Mettre à jour le second dataset pour la comparaison historique
            window.radarChart.data.datasets[1].data = previousValues;
            window.radarChart.data.datasets[1].label = `Sécurité le ${previousData.date}`;
            window.radarChart.data.datasets[1].backgroundColor = 'rgba(255, 99, 132, 0.2)';
            window.radarChart.data.datasets[1].borderColor = 'rgb(255, 99, 132)';
            window.radarChart.data.datasets[1].borderDash = [];
        } else {
            // S'il n'y a pas de données précédentes, cacher le deuxième dataset
            window.radarChart.data.datasets[1].hidden = true;
        }
    } else {
        // Afficher le dataset cible standard
        window.radarChart.data.datasets[1].data = [100, 100, 100, 100, 100];
        window.radarChart.data.datasets[1].label = 'Cible Optimale';
        window.radarChart.data.datasets[1].backgroundColor = 'rgba(75, 192, 75, 0.1)';
        window.radarChart.data.datasets[1].borderColor = 'rgba(75, 192, 75, 0.6)';
        window.radarChart.data.datasets[1].borderDash = [5, 5];
        window.radarChart.data.datasets[1].hidden = false;
    }
    
    // S'assurer que seuls deux datasets sont affichés
    if (window.radarChart.data.datasets.length > 2) {
        window.radarChart.data.datasets = window.radarChart.data.datasets.slice(0, 2);
    }
    
    window.radarChart.update();
}

/**
 * Configure le bouton d'actualisation
 */
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refreshRadarBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            // Afficher une animation de chargement sur le bouton
            const originalText = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Actualisation...';
            refreshBtn.disabled = true;
            
            // Simuler une actualisation des données (normalement appel AJAX)
            setTimeout(function() {
                // Restaurer le bouton
                refreshBtn.innerHTML = originalText;
                refreshBtn.disabled = false;
                
                // Actualiser la vue
                const viewCurrentBtn = document.getElementById('viewCurrentBtn');
                const viewComparisonBtn = document.getElementById('viewComparisonBtn');
                const viewHistoricalBtn = document.getElementById('viewHistoricalBtn');
                
                if (viewCurrentBtn && viewCurrentBtn.classList.contains('active')) {
                    updateRadarToCurrentView();
                } else if (viewComparisonBtn && viewComparisonBtn.classList.contains('active')) {
                    const comparisonSelect = document.getElementById('comparisonNetworkSelect');
                    if (comparisonSelect && comparisonSelect.value) {
                        updateRadarToComparisonView(comparisonSelect.value);
                    }
                } else if (viewHistoricalBtn && viewHistoricalBtn.classList.contains('active')) {
                    const historicalSelect = document.getElementById('historicalDateSelect');
                    if (historicalSelect && historicalSelect.value) {
                        updateRadarToHistoricalView(historicalSelect.value);
                    }
                }
                
                // Afficher une notification
                showNotification('Données de sécurité actualisées');
            }, 1000);
        });
    }
}

/**
 * Affiche une notification temporaire
 */
function showNotification(message, type = 'success') {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast fade show`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>${message}
        <button type="button" class="btn-close float-end" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Styler la notification
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
    notification.style.opacity = '0';
    notification.style.transition = 'opacity 0.3s ease-in-out';
    
    // Ajouter la notification au document
    document.body.appendChild(notification);
    
    // Afficher la notification avec une animation
    setTimeout(() => { notification.style.opacity = '1'; }, 10);
    
    // Fermer automatiquement après 5 secondes
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}