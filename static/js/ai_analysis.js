/**
 * Script pour la page d'analyse IA
 * Ajoute des visualisations interactives pour les données d'analyse
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation des graphiques d\'analyse IA');
    
    // Récupérer les données pour les graphiques
    const securityLevelsElement = document.getElementById('security-levels-data');
    const vulnerabilityStatsElement = document.getElementById('vulnerability-stats-data');
    
    if (securityLevelsElement && vulnerabilityStatsElement) {
        const securityLevelsData = JSON.parse(securityLevelsElement.textContent);
        const vulnerabilityStatsData = JSON.parse(vulnerabilityStatsElement.textContent);
        
        // Créer les graphiques
        createSecurityLevelsChart(securityLevelsData);
        createVulnerabilityStatsChart(vulnerabilityStatsData);
    }
    
    // Ajouter le comportement interactif aux recommandations
    setupRecommendationToggle();
});

/**
 * Crée un graphique en camembert pour les niveaux de sécurité WiFi
 */
function createSecurityLevelsChart(securityLevelsData) {
    const ctx = document.getElementById('security-levels-chart');
    if (!ctx) return;
    
    // Convertir les données en format compatible avec Chart.js
    const labels = Object.keys(securityLevelsData).map(key => key.charAt(0).toUpperCase() + key.slice(1));
    const data = Object.values(securityLevelsData);
    
    // Définir les couleurs pour chaque niveau de sécurité
    const colors = labels.map(label => {
        switch(label.toLowerCase()) {
            case 'secure': return '#28a745'; // Vert
            case 'low': return '#17a2b8';    // Bleu clair
            case 'medium': return '#ffc107'; // Jaune
            case 'high': return '#fd7e14';   // Orange
            case 'critical': return '#dc3545'; // Rouge
            default: return '#6c757d';       // Gris
        }
    });
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Distribution des niveaux de sécurité WiFi'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Crée un graphique à barres pour les statistiques de vulnérabilités
 */
function createVulnerabilityStatsChart(vulnerabilityStatsData) {
    const ctx = document.getElementById('vulnerability-stats-chart');
    if (!ctx) return;
    
    // Convertir les données en format compatible avec Chart.js
    const labels = Object.keys(vulnerabilityStatsData).map(key => key.charAt(0).toUpperCase() + key.slice(1));
    const data = Object.values(vulnerabilityStatsData);
    
    // Définir les couleurs pour chaque niveau de sécurité
    const colors = labels.map(label => {
        switch(label.toLowerCase()) {
            case 'low': return '#17a2b8';    // Bleu clair
            case 'medium': return '#ffc107'; // Jaune
            case 'high': return '#fd7e14';   // Orange
            case 'critical': return '#dc3545'; // Rouge
            default: return '#6c757d';       // Gris
        }
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nombre de vulnérabilités',
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Vulnérabilités par niveau de sévérité'
                }
            }
        }
    });
}

/**
 * Configure les comportements interactifs pour les sections de recommandations
 */
function setupRecommendationToggle() {
    // Ajouter un bouton pour montrer/cacher les détails des recommandations
    document.querySelectorAll('.recommendation-item').forEach(item => {
        const header = item.querySelector('.recommendation-header');
        const content = item.querySelector('.recommendation-content');
        
        if (header && content) {
            header.addEventListener('click', () => {
                content.classList.toggle('show');
                const icon = header.querySelector('i.toggle-icon');
                if (icon) {
                    icon.classList.toggle('fa-chevron-down');
                    icon.classList.toggle('fa-chevron-up');
                }
            });
        }
    });
    
    // Ajouter une fonction de filtre pour les recommandations
    const filterButtons = document.querySelectorAll('.recommendation-filter');
    if (filterButtons.length) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const priority = this.dataset.priority;
                
                // Mettre à jour l'état actif des boutons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Filtrer les recommandations
                document.querySelectorAll('.recommendation-item').forEach(item => {
                    if (priority === 'all' || item.dataset.priority === priority) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }
}

/**
 * Crée un radar chart pour comparer les différentes dimensions de sécurité
 */
function createSecurityRadarChart(data) {
    const ctx = document.getElementById('security-radar-chart');
    if (!ctx || !data) return;
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Protocole', 
                'Chiffrement', 
                'Authentification',
                'Gestion des mots de passe',
                'Mises à jour',
                'Vulnérabilités connues'
            ],
            datasets: [{
                label: 'Votre réseau',
                data: data,
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(54, 162, 235)'
            }]
        },
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            }
        }
    });
}