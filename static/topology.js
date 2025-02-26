/**
 * Visualisation interactive de la topologie du réseau
 * Utilise D3.js pour le rendu graphique et permet le drag-and-drop des appareils
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser la visualisation de la topologie
    initializeTopology();

    // Configurer les boutons de contrôle
    document.getElementById('refresh-topology').addEventListener('click', function() {
        loadTopologyData();
    });

    document.getElementById('reset-layout').addEventListener('click', function() {
        // Réinitialiser la disposition des appareils
        simulation.alpha(0.3).restart();
    });
});

// Variables globales pour la visualisation
let svg, simulation, tooltip;
let nodes = [], links = [];
let deviceInfoPanel;
let width, height;
let layout = {};

// Initialisation de la visualisation
function initializeTopology() {
    const container = document.getElementById('topology-canvas');
    
    // Obtenir les dimensions du conteneur
    width = container.clientWidth;
    height = container.clientHeight;
    
    // Créer l'élément SVG
    svg = d3.select('#topology-canvas')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Créer le groupe principal pour les éléments de la topologie
    const g = svg.append('g');
    
    // Créer des groupes pour les liens et les nœuds
    g.append('g').attr('class', 'links');
    g.append('g').attr('class', 'nodes');
    
    // Créer un tooltip pour les informations au survol
    tooltip = d3.select('body')
        .append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0);
    
    // Créer le panneau d'informations de l'appareil
    deviceInfoPanel = d3.select('#device-info-panel');
    
    // Initialiser la simulation de force
    simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(50))
        .on('tick', ticked);
    
    // Charger les données de topologie
    loadTopologyData();
}

// Charger les données de la topologie depuis le serveur
function loadTopologyData() {
    // Montrer un indicateur de chargement
    showNotification('Chargement des données de topologie...', 'info');
    
    // Émettre une demande WebSocket pour obtenir les données de topologie
    socket.emit('request_topology_data');
    
    // Gérer la réception des données de topologie
    socket.on('topology_update', function(data) {
        processTopologyData(data);
    });
}

// Traiter les données de topologie reçues
function processTopologyData(data) {
    // Extraire les appareils et le routeur des données
    const devices = data.devices || [];
    const router = data.router || { name: 'Router/AP' };
    
    // Réinitialiser les nœuds et les liens
    nodes = [];
    links = [];
    
    // Ajouter le routeur au centre
    const routerNode = {
        id: 'router',
        name: router.name,
        type: 'router',
        radius: 30,
        fixed: true
    };
    
    // Positionner le routeur au centre
    routerNode.fx = width / 2;
    routerNode.fy = height / 2;
    
    // Ajouter le routeur aux nœuds
    nodes.push(routerNode);
    
    // Ajouter les appareils et leurs connexions
    devices.forEach(device => {
        // Créer un nœud pour l'appareil
        const deviceNode = {
            id: device.mac_address,
            name: device.device_name,
            type: 'device',
            radius: 20,
            data: device,
            status: device.status || 'offline',
            security_score: device.security_score || 50
        };
        
        // Appliquer la position enregistrée si disponible
        if (device.position) {
            deviceNode.fx = device.position.x;
            deviceNode.fy = device.position.y;
        } else if (layout[device.mac_address]) {
            deviceNode.fx = layout[device.mac_address].x;
            deviceNode.fy = layout[device.mac_address].y;
        }
        
        // Ajouter l'appareil aux nœuds
        nodes.push(deviceNode);
        
        // Créer un lien entre l'appareil et le routeur
        const link = {
            source: 'router',
            target: device.mac_address,
            strength: device.signal_strength || 'medium'
        };
        
        // Ajouter le lien aux liens
        links.push(link);
    });
    
    // Mettre à jour les statistiques du réseau
    updateNetworkStats();
    
    // Mettre à jour la visualisation
    updateTopologyVisualization();
    
    // Notification de chargement terminé
    showNotification('Données de topologie chargées avec succès', 'success');
}

// Mettre à jour les statistiques du réseau
function updateNetworkStats() {
    // Calculer les statistiques
    const totalDevices = nodes.length - 1; // Sans compter le routeur
    const onlineDevices = nodes.filter(n => n.type === 'device' && n.status === 'online').length;
    
    // Calculer les niveaux de sécurité
    const securityLevels = {
        high: nodes.filter(n => n.type === 'device' && n.security_score >= 80).length,
        medium: nodes.filter(n => n.type === 'device' && n.security_score >= 50 && n.security_score < 80).length,
        low: nodes.filter(n => n.type === 'device' && n.security_score < 50).length
    };
    
    // Mettre à jour l'affichage des statistiques
    document.getElementById('total-devices').textContent = totalDevices;
    document.getElementById('online-devices').textContent = onlineDevices;
    document.getElementById('secure-devices').textContent = securityLevels.high;
    document.getElementById('vulnerable-devices').textContent = securityLevels.low;
}

// Mettre à jour la visualisation de la topologie
function updateTopologyVisualization() {
    // Sélectionner les liens
    const link = svg.select('.links')
        .selectAll('line')
        .data(links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);
    
    // Gérer les liens qui sortent
    link.exit().remove();
    
    // Ajouter de nouveaux liens
    const linkEnter = link.enter()
        .append('line')
        .attr('class', d => `device-link ${d.strength}`)
        .attr('stroke-width', d => {
            if (d.strength === 'high') return 3;
            if (d.strength === 'medium') return 2;
            return 1;
        });
    
    // Fusionner les liens
    const linkMerge = linkEnter.merge(link);
    
    // Sélectionner les nœuds
    const node = svg.select('.nodes')
        .selectAll('.device-node-group')
        .data(nodes, d => d.id);
    
    // Gérer les nœuds qui sortent
    node.exit().remove();
    
    // Ajouter de nouveaux nœuds
    const nodeEnter = node.enter()
        .append('g')
        .attr('class', 'device-node-group')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Ajouter des cercles pour les nœuds
    nodeEnter.append('circle')
        .attr('r', d => d.radius)
        .attr('class', d => {
            if (d.type === 'router') return 'device-node router-node';
            if (d.status === 'offline') return 'device-node device-offline';
            if (d.security_score >= 80) return 'device-node device-high';
            if (d.security_score >= 50) return 'device-node device-medium';
            return 'device-node device-low';
        })
        .on('click', selectNode)
        .on('mouseover', function(event, d) {
            // Afficher le tooltip au survol
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(d.name)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function() {
            // Masquer le tooltip
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
    
    // Ajouter les étiquettes pour les nœuds de type routeur
    nodeEnter.filter(d => d.type === 'router')
        .append('text')
        .attr('dy', 5)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .text(d => 'R');
    
    // Ajouter des icônes pour les types d'appareils
    nodeEnter.filter(d => d.type === 'device')
        .append('text')
        .attr('dy', 5)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .text(d => {
            const deviceType = d.data.device_type;
            if (deviceType === 'Smartphone') return '📱';
            if (deviceType === 'Ordinateur portable') return '💻';
            if (deviceType === 'Tablette') return '📟';
            if (deviceType === 'Smart TV') return '📺';
            if (deviceType === 'Enceinte connectée') return '🔊';
            if (deviceType === 'Caméra IP') return '📹';
            if (deviceType === 'Console de jeu') return '🎮';
            return '📡';
        });
    
    // Fusionner les nœuds
    const nodeMerge = nodeEnter.merge(node);
    
    // Mettre à jour la simulation
    simulation.nodes(nodes);
    simulation.force('link').links(links);
    
    // Redémarrer la simulation
    simulation.alpha(0.3).restart();
    
    // Fonction appelée à chaque tick de la simulation
    function ticked() {
        // Mettre à jour la position des liens
        linkMerge
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        // Mettre à jour la position des nœuds
        nodeMerge
            .attr('transform', d => `translate(${d.x},${d.y})`);
    }
    
    // Fonction appelée au début du drag d'un nœud
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    // Fonction appelée pendant le drag d'un nœud
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    // Fonction appelée à la fin du drag d'un nœud
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        
        // Enregistrer la position dans le layout
        if (d.type === 'device') {
            layout[d.id] = { x: d.fx, y: d.fy };
            
            // Envoyer la mise à jour de la disposition au serveur
            socket.emit('update_topology_layout', layout);
        }
    }
}

// Sélectionner un nœud pour afficher ses informations
function selectNode(event, d) {
    // Ne rien faire si c'est le routeur
    if (d.type === 'router') {
        deviceInfoPanel.classed('visible', false);
        return;
    }
    
    // Afficher les informations de l'appareil
    showDeviceInfo(d.data);
    
    // Ajouter une classe selected au nœud sélectionné
    svg.selectAll('.device-node').classed('selected', false);
    d3.select(this).classed('selected', true);
}

// Afficher les informations d'un appareil dans le panneau latéral
function showDeviceInfo(device) {
    // Mettre à jour le contenu du panneau d'informations
    deviceInfoPanel.html(`
        <h3>${device.device_name}</h3>
        <div class="device-security-score ${getScoreLevel(device.security_score)}">
            ${device.security_score}/100
        </div>
        <div class="device-info-item">
            <span class="device-info-label">Statut:</span> 
            ${device.status === 'online' ? 'En ligne' : 'Hors ligne'}
        </div>
        <div class="device-info-item">
            <span class="device-info-label">Type:</span> 
            ${device.device_type}
        </div>
        <div class="device-info-item">
            <span class="device-info-label">Fabricant:</span> 
            ${device.manufacturer}
        </div>
        <div class="device-info-item">
            <span class="device-info-label">Adresse IP:</span> 
            ${device.ip_address}
        </div>
        <div class="device-info-item">
            <span class="device-info-label">Connexion:</span> 
            ${formatConnectionType(device.connection_type)}
        </div>
        <div class="device-info-item">
            <span class="device-info-label">Force du signal:</span> 
            ${getSignalPercentage(device.signal_strength)}%
        </div>
        <div class="device-actions">
            <button onclick="showDeviceDetailsModal('${device.mac_address}')">Détails complets</button>
        </div>
    `);
    
    // Afficher le panneau
    deviceInfoPanel.classed('visible', true);
}

// Afficher une fenêtre modale avec les détails complets de l'appareil
function showDeviceDetailsModal(mac_address) {
    // Trouver l'appareil par son adresse MAC
    const device = nodes.find(n => n.id === mac_address)?.data;
    
    if (!device) {
        showNotification('Appareil non trouvé', 'error');
        return;
    }
    
    // Créer le contenu de la modale
    const modalContent = `
        <div class="device-modal-content">
            <span class="close-modal">&times;</span>
            <div class="device-detail-header">
                <h2>${device.device_name}</h2>
                <span class="device-status-badge ${device.status === 'online' ? 'status-online' : 'status-offline'}">
                    ${device.status === 'online' ? 'En ligne' : 'Hors ligne'}
                </span>
            </div>
            <div class="device-details-grid">
                <div class="device-detail-section">
                    <h3>Informations générales</h3>
                    <div class="detail-row">
                        <span class="detail-label">Type d'appareil:</span>
                        <span class="detail-value">${device.device_type}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Fabricant:</span>
                        <span class="detail-value">${device.manufacturer}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Adresse MAC:</span>
                        <span class="detail-value">${device.mac_address}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Adresse IP:</span>
                        <span class="detail-value">${device.ip_address}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Première détection:</span>
                        <span class="detail-value">${formatDate(device.first_seen)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Dernière activité:</span>
                        <span class="detail-value">${formatDate(device.last_seen)}</span>
                    </div>
                </div>
                <div class="device-detail-section">
                    <h3>Sécurité</h3>
                    <div class="gauge-container">
                        <svg width="120" height="120" viewBox="0 0 120 120">
                            <circle class="gauge-background" cx="60" cy="60" r="50" stroke-width="15" fill="none" />
                            <circle class="gauge-value" cx="60" cy="60" r="50" stroke-width="15" fill="none"
                                stroke="${getScoreColor(device.security_score)}" 
                                stroke-dasharray="${3.14 * 100}"
                                stroke-dashoffset="${3.14 * (100 - device.security_score)}" />
                            <circle class="gauge-center" cx="60" cy="60" r="42" />
                            <text class="gauge-text" x="60" y="70">${device.security_score}</text>
                        </svg>
                    </div>
                    <div class="security-recommendations">
                        <h4>Recommandations</h4>
                        <ul class="security-recommendation-list">
                            ${getSecurityRecommendations(device).map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="device-detail-section">
                    <h3>Connexion</h3>
                    <div class="detail-row">
                        <span class="detail-label">Type de connexion:</span>
                        <span class="detail-value">${formatConnectionType(device.connection_type)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Force du signal:</span>
                        <span class="detail-value">${getSignalPercentage(device.signal_strength)}%</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Bande passante:</span>
                        <span class="detail-value">${getBandwidth(device.connection_type)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Données transférées:</span>
                        <span class="detail-value">${getRandomDataTransferred()}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Créer la modale et l'ajouter au document
    const modal = document.createElement('div');
    modal.className = 'device-modal';
    modal.id = 'device-details-modal';
    modal.innerHTML = modalContent;
    document.body.appendChild(modal);
    
    // Afficher la modale
    modal.style.display = 'block';
    
    // Configurer la fermeture de la modale
    setupEventListeners();
}

// Configurer les écouteurs d'événements pour la modale
function setupEventListeners() {
    // Fermer la modale au clic sur la croix
    document.querySelector('.close-modal').addEventListener('click', function() {
        document.getElementById('device-details-modal').remove();
    });
    
    // Fermer la modale au clic en dehors du contenu
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('device-details-modal');
        if (event.target === modal) {
            modal.remove();
        }
    });
}

// Fonctions utilitaires
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleString();
}

function formatConnectionType(type) {
    if (type === 'wireless') return 'Sans fil';
    if (type === 'ethernet') return 'Ethernet';
    return type || 'Inconnu';
}

function getSignalPercentage(strength) {
    if (strength === 'high') return 90;
    if (strength === 'medium') return 60;
    if (strength === 'low') return 30;
    return 0;
}

function getScoreLevel(score) {
    if (score >= 80) return 'score-high';
    if (score >= 50) return 'score-medium';
    return 'score-low';
}

function getScoreColor(score) {
    if (score >= 80) return '#4CAF50';
    if (score >= 50) return '#FFC107';
    return '#F44336';
}

function getBandwidth(connectionType) {
    if (connectionType === 'ethernet') return '1 Gbps';
    if (connectionType === 'wireless') return Math.floor(Math.random() * 300 + 100) + ' Mbps';
    return 'Inconnu';
}

function getRandomDataTransferred() {
    return (Math.random() * 10).toFixed(2) + ' GB';
}

function getSecurityRecommendations(device) {
    // Recommandations basées sur le score de sécurité
    const recommendations = [];
    
    if (device.security_score < 50) {
        recommendations.push('Mettre à jour le firmware de l\'appareil vers la dernière version disponible.');
        recommendations.push('Activer le pare-feu sur cet appareil.');
        recommendations.push('Changer les identifiants par défaut.');
    } else if (device.security_score < 80) {
        recommendations.push('Vérifier les mises à jour de sécurité régulièrement.');
        recommendations.push('Activer l\'authentification à deux facteurs si disponible.');
    }
    
    // Recommandations basées sur le type d'appareil
    if (device.device_type === 'Caméra IP') {
        recommendations.push('Désactiver l\'accès à distance si non utilisé.');
    } else if (device.device_type === 'Smart TV') {
        recommendations.push('Désactiver les fonctionnalités de suivi et de publicité.');
    }
    
    // Recommandations basées sur le type de connexion
    if (device.connection_type === 'wireless') {
        recommendations.push('Utiliser une connexion filaire pour une meilleure sécurité et stabilité.');
    }
    
    // Assurer un minimum de recommandations
    if (recommendations.length === 0) {
        recommendations.push('Maintenir les bonnes pratiques de sécurité pour cet appareil.');
    }
    
    return recommendations;
}

// Afficher une notification
function showNotification(message, type = 'info') {
    // Créer l'élément de notification s'il n'existe pas
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.className = 'notification';
        document.body.appendChild(notification);
    }
    
    // Définir le contenu et le type de la notification
    notification.textContent = message;
    notification.className = `notification ${type}`;
    
    // Afficher la notification
    setTimeout(() => {
        notification.classList.add('visible');
    }, 10);
    
    // Masquer la notification après 3 secondes
    setTimeout(() => {
        notification.classList.remove('visible');
    }, 3000);
}

// Utilitaire pour capitaliser la première lettre
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}