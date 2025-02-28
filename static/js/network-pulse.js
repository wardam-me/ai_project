/**
 * Script pour l'animation Network Health Pulse
 * Ajoute des effets visuels dynamiques à l'indicateur de santé du réseau
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Initialisation de network-pulse.js");
    initializeNetworkPulse();
    
    // Actualiser la pulsation toutes les 30 secondes
    setInterval(refreshNetworkPulse, 30000);
});

/**
 * Initialise l'animation de pulsation du réseau
 */
function initializeNetworkPulse() {
    const scoreContainers = document.querySelectorAll('.security-score-container');
    
    scoreContainers.forEach(container => {
        const scoreElement = container.querySelector('.security-score');
        if (!scoreElement) return;
        
        // Détermine la classe de pulsation en fonction du niveau de sécurité
        let pulseClass = 'network-pulse';
        if (scoreElement.classList.contains('security-score-medium')) {
            pulseClass = 'network-pulse-warning';
        } else if (scoreElement.classList.contains('security-score-low')) {
            pulseClass = 'network-pulse-danger';
        }
        
        // Ajoute l'élément de pulsation
        const pulseElement = document.createElement('div');
        pulseElement.className = pulseClass;
        container.insertBefore(pulseElement, scoreElement);
        
        // Ajoute l'effet d'aura
        const auraElement = document.createElement('div');
        auraElement.className = 'network-aura';
        container.insertBefore(auraElement, scoreElement);
        
        // Ajoute des points de données pour un effet visuel supplémentaire
        createDataPoints(container, 8);
    });
}

/**
 * Crée des points de données animés pour simuler le trafic réseau
 */
function createDataPoints(container, count) {
    for (let i = 0; i < count; i++) {
        const point = document.createElement('div');
        point.className = 'data-point';
        
        // Positionne aléatoirement le point à l'intérieur du cercle
        const angle = Math.random() * 2 * Math.PI;
        const radius = 40 + Math.random() * 15; // Entre 40 et 55px du centre
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        
        point.style.left = `calc(50% + ${x}px)`;
        point.style.top = `calc(50% + ${y}px)`;
        
        // Définit la destination du point (direction vers/depuis le centre)
        const moveToCenter = Math.random() > 0.5;
        const tx = moveToCenter ? -x : x * 1.5;
        const ty = moveToCenter ? -y : y * 1.5;
        point.style.setProperty('--tx', `${tx}px`);
        point.style.setProperty('--ty', `${ty}px`);
        
        // Configure l'animation
        point.style.animation = `data-point-motion ${1 + Math.random() * 2}s linear ${Math.random() * 2}s infinite`;
        
        container.appendChild(point);
    }
}

/**
 * Rafraîchit l'animation de pulsation pour simuler une mise à jour des données
 */
function refreshNetworkPulse() {
    const scoreContainers = document.querySelectorAll('.security-score-container');
    
    scoreContainers.forEach(container => {
        const scoreElement = container.querySelector('.security-score');
        if (!scoreElement) return;
        
        // Applique un léger effet de scale pour simuler une mise à jour
        scoreElement.style.transform = 'scale(1.1)';
        
        // Revient à la normale après l'animation
        setTimeout(() => {
            scoreElement.style.transform = '';
        }, 500);
        
        // Supprime et recrée les points de données pour actualiser l'animation
        const dataPoints = container.querySelectorAll('.data-point');
        dataPoints.forEach(point => point.remove());
        createDataPoints(container, 8);
    });
}

/**
 * Met à jour les statuts de santé du réseau lors des changements
 */
function updateNetworkHealth(score) {
    const container = document.querySelector('.security-score-container');
    if (!container) return;
    
    const scoreElement = container.querySelector('.security-score');
    const pulseElement = container.querySelector('.network-pulse, .network-pulse-warning, .network-pulse-danger');
    
    if (scoreElement) {
        // Met à jour la valeur du score
        scoreElement.textContent = score;
        
        // Met à jour les classes de couleur
        scoreElement.classList.remove('security-score-high', 'security-score-medium', 'security-score-low');
        
        if (score >= 80) {
            scoreElement.classList.add('security-score-high');
        } else if (score >= 50) {
            scoreElement.classList.add('security-score-medium');
        } else {
            scoreElement.classList.add('security-score-low');
        }
    }
    
    if (pulseElement) {
        // Met à jour la classe de pulsation
        pulseElement.classList.remove('network-pulse', 'network-pulse-warning', 'network-pulse-danger');
        
        if (score >= 80) {
            pulseElement.classList.add('network-pulse');
        } else if (score >= 50) {
            pulseElement.classList.add('network-pulse-warning');
        } else {
            pulseElement.classList.add('network-pulse-danger');
        }
    }
    
    // Effet visuel de mise à jour
    container.classList.add('pulse-update');
    setTimeout(() => {
        container.classList.remove('pulse-update');
    }, 1000);
}

// Fonction exportée pour permettre à d'autres scripts de mettre à jour le pouls
window.networkPulse = {
    update: updateNetworkHealth,
    refresh: refreshNetworkPulse
};