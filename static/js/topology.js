/**
 * Visualisation interactive de la topologie du réseau
 * Utilise D3.js pour le rendu graphique et permet le drag-and-drop des appareils
 */

// Variables globales
let svg, simulation, link, node, nodeLabels;
let topologyData = { devices: [], connections: [] };
let deviceRadius = 15;
let showLabels = true;
let selectedNode = null;
let dragging = false;
let tooltip = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation de la topologie réseau');
    initializeTopology();
    setupEventListeners();
    
    // Connexion au serveur via Socket.IO pour les mises à jour en temps réel
    const socket = io();
    
    socket.on('connect', function() {
        console.log('Connecté au serveur Socket.IO');
        socket.emit('request_topology');
    });
    
    socket.on('topology_data', function(data) {
        console.log('Données de topologie reçues');
        processTopologyData(data);
    });
    
    socket.on('device_update', function(data) {
        console.log('Mise à jour d\'appareil reçue:', data.mac_address);
        // Mettre à jour les données locales
        const deviceIndex = topologyData.devices.findIndex(d => d.mac_address === data.mac_address);
        if (deviceIndex !== -1) {
            // Mettre à jour les propriétés modifiées
            Object.keys(data).forEach(key => {
                topologyData.devices[deviceIndex][key] = data[key];
            });
            
            // Rafraîchir la visualisation
            updateTopologyVisualization();
            
            // Si c'est le nœud sélectionné, mettre à jour les détails
            if (selectedNode && selectedNode.mac_address === data.mac_address) {
                showDeviceInfo(topologyData.devices[deviceIndex]);
            }
        }
    });
    
    socket.on('layout_update', function(layoutData) {
        console.log('Disposition mise à jour reçue');
        // Appliquer les nouvelles positions aux appareils
        topologyData.devices.forEach(device => {
            if (layoutData[device.mac_address]) {
                device.x = layoutData[device.mac_address].x;
                device.y = layoutData[device.mac_address].y;
                // Mettre à jour la position dans la simulation
                const nodeElement = node.filter(n => n.mac_address === device.mac_address);
                if (!nodeElement.empty()) {
                    nodeElement.datum().x = device.x;
                    nodeElement.datum().y = device.y;
                }
            }
        });
        
        // Rafraîchir la visualisation avec les positions fixes
        updateTopologyVisualization(true);
    });
    
    // Connexion perdue
    socket.on('disconnect', function() {
        console.log('Déconnecté du serveur Socket.IO');
        showNotification('Connexion au serveur perdue. Tentative de reconnexion...', 'warning');
    });
    
    // Charger les données de topologie
    loadTopologyData();
});

/**
 * Initialise la visualisation de la topologie
 */
function initializeTopology() {
    const container = document.querySelector('.network-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Créer le tooltip
    tooltip = d3.select('.network-container')
        .append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0);
    
    // Créer le SVG
    svg = d3.select('.network-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Créer les groupes pour les liens et les nœuds
    svg.append('g').attr('class', 'links');
    svg.append('g').attr('class', 'nodes');
    svg.append('g').attr('class', 'node-labels');
    
    // Initialiser la simulation D3 Force
    simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.mac_address).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(deviceRadius * 2));
}

/**
 * Charge les données de topologie depuis l'API
 */
function loadTopologyData() {
    fetch('/api/topology')
        .then(response => response.json())
        .then(data => {
            console.log('Données de topologie chargées depuis l\'API');
            processTopologyData(data);
        })
        .catch(error => {
            console.error('Erreur lors du chargement des données de topologie:', error);
            showNotification('Erreur lors du chargement des données de topologie', 'danger');
            
            // Générer des données de démonstration en cas d'erreur
            generateDemoTopology();
        });
}

/**
 * Traite les données de topologie reçues et met à jour la visualisation
 */
function processTopologyData(data) {
    topologyData = data;
    console.log(`Traitement de ${data.devices.length} appareils et ${data.connections.length} connexions`);
    
    // Mettre à jour les statistiques
    updateNetworkStats();
    
    // Mettre à jour la visualisation
    updateTopologyVisualization();
}

/**
 * Met à jour les statistiques du réseau
 */
function updateNetworkStats() {
    const devices = topologyData.devices;
    const onlineDevices = devices.filter(d => d.online);
    const securityScores = devices.map(d => d.security_score || 0);
    const avgScore = securityScores.length > 0 ? securityScores.reduce((a, b) => a + b, 0) / securityScores.length : 0;
    
    document.getElementById('deviceCount').textContent = devices.length;
    document.getElementById('onlineCount').textContent = onlineDevices.length;
    document.getElementById('avgScore').textContent = avgScore.toFixed(1);
    
    if (topologyData.timestamp) {
        const date = new Date(topologyData.timestamp);
        document.getElementById('lastUpdate').textContent = date.toLocaleTimeString();
    }
}

/**
 * Met à jour la visualisation de la topologie
 * @param {boolean} fixedPositions - Si vrai, utilise les positions fixes des appareils sans simulation
 */
function updateTopologyVisualization(fixedPositions = false) {
    const container = document.querySelector('.network-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    const showOffline = document.getElementById('showOfflineDevices').checked;
    const colorByScore = document.getElementById('colorBySecurityScore').checked;
    
    // Filtrer les appareils hors ligne si nécessaire
    let devices = topologyData.devices;
    if (!showOffline) {
        devices = devices.filter(d => d.online);
    }
    
    // Filtrer les connexions pour n'inclure que celles entre les appareils visibles
    const macAddresses = devices.map(d => d.mac_address);
    const connections = topologyData.connections.filter(c => 
        macAddresses.includes(c.source) && macAddresses.includes(c.target)
    );
    
    // Liens
    link = d3.select('.links')
        .selectAll('line')
        .data(connections);
    
    link.exit().remove();
    
    const linkEnter = link.enter()
        .append('line')
        .attr('class', d => `link ${d.connection_type}`);
    
    link = linkEnter.merge(link);
    
    // Nœuds
    node = d3.select('.nodes')
        .selectAll('circle')
        .data(devices, d => d.mac_address);
    
    node.exit().remove();
    
    const nodeEnter = node.enter()
        .append('circle')
        .attr('class', d => `node node-${d.device_type} ${d.online ? 'online' : 'offline'}`)
        .attr('r', deviceRadius)
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('click', selectNode)
        .on('mouseover', function(event, d) {
            if (dragging) return;
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(`
                <strong>${d.name}</strong><br>
                ${d.device_type}<br>
                ${d.ip_address}
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function() {
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
    
    node = nodeEnter.merge(node);
    
    // Appliquer la couleur en fonction du score de sécurité si demandé
    if (colorByScore) {
        node.style('fill', function(d) {
            return getScoreColor(d.security_score || 0);
        });
    } else {
        node.style('fill', null);
    }
    
    // Étiquettes des nœuds
    nodeLabels = d3.select('.node-labels')
        .selectAll('text')
        .data(devices, d => d.mac_address);
    
    nodeLabels.exit().remove();
    
    const labelEnter = nodeLabels.enter()
        .append('text')
        .attr('class', 'node-label')
        .attr('text-anchor', 'middle')
        .attr('dy', deviceRadius * 2)
        .style('fill', 'white')
        .style('font-size', '10px')
        .style('pointer-events', 'none')
        .style('text-shadow', '0 0 3px black')
        .text(d => d.name.length > 15 ? d.name.substring(0, 12) + '...' : d.name);
    
    nodeLabels = labelEnter.merge(nodeLabels);
    
    // Afficher ou masquer les étiquettes
    nodeLabels.style('display', showLabels ? 'block' : 'none');
    
    // Mise à jour de la simulation
    simulation.nodes(devices);
    simulation.force('link').links(connections);
    
    // Ajout de l'écouteur de tick après avoir défini les nœuds et les liens
    simulation.on('tick', ticked);
    
    if (fixedPositions) {
        // Utiliser les positions fixes sans simulation
        node.attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        nodeLabels.attr('x', d => d.x)
            .attr('y', d => d.y);
        
        link.attr('x1', d => {
            const sourceNode = devices.find(node => node.mac_address === d.source);
            return sourceNode ? sourceNode.x : 0;
        })
        .attr('y1', d => {
            const sourceNode = devices.find(node => node.mac_address === d.source);
            return sourceNode ? sourceNode.y : 0;
        })
        .attr('x2', d => {
            const targetNode = devices.find(node => node.mac_address === d.target);
            return targetNode ? targetNode.x : 0;
        })
        .attr('y2', d => {
            const targetNode = devices.find(node => node.mac_address === d.target);
            return targetNode ? targetNode.y : 0;
        });
    } else {
        // Redémarrer la simulation avec les nouvelles données
        simulation.alpha(0.3).restart();
    }
    
    /**
     * Fonction appelée à chaque "tick" de la simulation
     */
    function ticked() {
        // Maintenir les nœuds dans les limites du SVG
        node.attr('cx', d => d.x = Math.max(deviceRadius, Math.min(width - deviceRadius, d.x)))
            .attr('cy', d => d.y = Math.max(deviceRadius, Math.min(height - deviceRadius, d.y)));
        
        // Mettre à jour les positions des liens
        link.attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        // Mettre à jour les positions des étiquettes
        nodeLabels.attr('x', d => d.x)
            .attr('y', d => d.y);
    }
    
    /**
     * Gestion du début du glisser-déposer
     */
    function dragstarted(event, d) {
        dragging = true;
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    /**
     * Gestion du glisser-déposer en cours
     */
    function dragged(event, d) {
        d.fx = Math.max(deviceRadius, Math.min(width - deviceRadius, event.x));
        d.fy = Math.max(deviceRadius, Math.min(height - deviceRadius, event.y));
    }
    
    /**
     * Gestion de la fin du glisser-déposer
     */
    function dragended(event, d) {
        dragging = false;
        if (!event.active) simulation.alphaTarget(0);
        
        // Enregistrer la nouvelle position de l'appareil
        const layoutData = {
            mac_address: d.mac_address,
            x: d.x,
            y: d.y
        };
        
        // Envoyer la nouvelle position au serveur
        fetch('/api/topology/layout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(layoutData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Position sauvegardée avec succès');
            } else {
                console.error('Erreur lors de la sauvegarde de la position:', data.error);
                showNotification('Erreur lors de la sauvegarde de la position', 'danger');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la sauvegarde de la position:', error);
            showNotification('Erreur lors de la sauvegarde de la position', 'danger');
        });
    }
}

/**
 * Gestion de la sélection d'un nœud
 */
function selectNode(event, d) {
    // Ignorer si on est en train de faire glisser
    if (dragging) return;
    
    event.stopPropagation();
    
    // Mettre à jour le nœud sélectionné
    if (selectedNode === d) {
        // Désélectionner si on clique à nouveau sur le même nœud
        selectedNode = null;
        
        // Masquer le panneau d'informations
        document.querySelector('.device-info-panel').style.display = 'none';
        
        // Réinitialiser l'apparence des nœuds
        node.style('stroke', null)
            .style('stroke-width', null);
    } else {
        selectedNode = d;
        
        // Afficher les informations de l'appareil
        showDeviceInfo(d);
        
        // Mettre en évidence le nœud sélectionné
        node.style('stroke', n => n === d ? '#fff' : null)
            .style('stroke-width', n => n === d ? 2 : null);
    }
}

/**
 * Affiche les informations de l'appareil sélectionné
 */
function showDeviceInfo(device) {
    const infoPanel = document.querySelector('.device-info-panel');
    
    // Mettre à jour les informations
    infoPanel.querySelector('.device-name').textContent = device.name;
    infoPanel.querySelector('.device-type').textContent = capitalizeFirstLetter(device.device_type);
    infoPanel.querySelector('.device-ip').textContent = device.ip_address;
    
    const securityScore = device.security_score || 0;
    const scoreBadge = infoPanel.querySelector('.score-badge');
    scoreBadge.textContent = Math.round(securityScore);
    scoreBadge.className = 'score-badge ' + getScoreLevel(securityScore);
    
    infoPanel.querySelector('.device-manufacturer').textContent = device.manufacturer || 'Inconnu';
    infoPanel.querySelector('.device-model').textContent = device.model || 'Inconnu';
    infoPanel.querySelector('.device-os').textContent = device.os || 'Inconnu';
    
    // Créer un indicateur de signal
    const signalMeter = infoPanel.querySelector('.signal-meter');
    signalMeter.innerHTML = '';
    
    if (device.signal_strength) {
        const signalPercent = getSignalPercentage(device.signal_strength);
        const bars = 5;
        const activeBars = Math.round(signalPercent * bars / 100);
        
        for (let i = 0; i < bars; i++) {
            const bar = document.createElement('div');
            bar.classList.add('signal-indicator');
            bar.style.backgroundColor = i < activeBars ? '#4cd964' : '#555';
            bar.style.height = `${(i+1) * 4}px`;
            bar.style.width = '4px';
            bar.style.display = 'inline-block';
            bar.style.marginRight = '2px';
            signalMeter.appendChild(bar);
        }
        
        signalMeter.appendChild(document.createTextNode(` ${signalPercent}% (${device.signal_strength} dBm)`));
    } else {
        signalMeter.textContent = 'Non disponible';
    }
    
    // Configurer le bouton de détails
    infoPanel.querySelector('.device-details-btn').onclick = function() {
        showDeviceDetailsModal(device.mac_address);
    };
    
    // Afficher le panneau
    infoPanel.style.display = 'block';
}

/**
 * Affiche la fenêtre modale avec les détails complets de l'appareil
 */
function showDeviceDetailsModal(mac_address) {
    const device = topologyData.devices.find(d => d.mac_address === mac_address);
    if (!device) return;
    
    // Mettre à jour les informations générales
    document.getElementById('modal-device-name').textContent = device.name;
    document.getElementById('modal-device-type').textContent = capitalizeFirstLetter(device.device_type);
    document.getElementById('modal-mac-address').textContent = device.mac_address;
    document.getElementById('modal-ip-address').textContent = device.ip_address;
    document.getElementById('modal-manufacturer').textContent = device.manufacturer || 'Inconnu';
    document.getElementById('modal-model').textContent = device.model || 'Inconnu';
    document.getElementById('modal-os').textContent = device.os || 'Inconnu';
    document.getElementById('modal-connection').textContent = formatConnectionType(device.connection_type);
    
    // Icône de l'appareil
    const deviceIcon = document.getElementById('modal-device-icon');
    deviceIcon.className = `fas ${getDeviceIcon(device.device_type)} device-icon`;
    
    // Score de sécurité
    const securityScore = device.security_score || 0;
    const scoreBadge = document.getElementById('modal-security-score');
    scoreBadge.textContent = Math.round(securityScore);
    scoreBadge.className = 'score-badge ' + getScoreLevel(securityScore);
    
    // Date de dernière vue
    if (device.last_seen) {
        document.getElementById('modal-last-seen').textContent = formatDate(device.last_seen);
    } else {
        document.getElementById('modal-last-seen').textContent = 'Inconnue';
    }
    
    // Problèmes de sécurité
    const issuesContainer = document.getElementById('security-issues-container');
    issuesContainer.innerHTML = '';
    
    if (device.security_issues && device.security_issues.length > 0) {
        device.security_issues.forEach(issue => {
            const issueDiv = document.createElement('div');
            issueDiv.className = `security-risk risk-${issue.severity}`;
            
            const issueTitleDiv = document.createElement('div');
            issueTitleDiv.className = 'fw-bold mb-1';
            
            const severityBadge = document.createElement('span');
            severityBadge.className = `badge bg-${issue.severity === 'high' ? 'danger' : (issue.severity === 'medium' ? 'warning' : 'success')} me-2`;
            severityBadge.textContent = issue.severity.toUpperCase();
            
            issueTitleDiv.appendChild(severityBadge);
            issueTitleDiv.appendChild(document.createTextNode(issue.description));
            
            const solutionDiv = document.createElement('div');
            solutionDiv.className = 'small';
            solutionDiv.textContent = issue.solution;
            
            issueDiv.appendChild(issueTitleDiv);
            issueDiv.appendChild(solutionDiv);
            issuesContainer.appendChild(issueDiv);
        });
    } else {
        issuesContainer.innerHTML = '<div class="alert alert-success">Aucun problème de sécurité détecté</div>';
    }
    
    // Recommandations
    const recommendationsContainer = document.getElementById('recommendations-container');
    recommendationsContainer.innerHTML = '';
    
    if (device.recommendations && device.recommendations.length > 0) {
        device.recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.className = 'list-group-item bg-transparent text-white border-light';
            
            const icon = document.createElement('i');
            icon.className = 'fas fa-check-circle me-2 text-success';
            
            li.appendChild(icon);
            li.appendChild(document.createTextNode(recommendation));
            recommendationsContainer.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent text-white border-light';
        li.textContent = 'Aucune recommandation disponible';
        recommendationsContainer.appendChild(li);
    }
    
    // Données de trafic (simulées)
    document.getElementById('modal-data-downloaded').textContent = getRandomDataTransferred(device.device_type, 'download');
    document.getElementById('modal-data-uploaded').textContent = getRandomDataTransferred(device.device_type, 'upload');
    
    // Bande passante
    const bandwidth = getBandwidth(device.connection_type);
    const bandwidthBar = document.getElementById('modal-bandwidth');
    bandwidthBar.style.width = `${bandwidth.percent}%`;
    bandwidthBar.textContent = `${bandwidth.value} Mbps`;
    
    // Configurer le bouton de mise à jour
    document.getElementById('update-security-btn').onclick = function() {
        fetch(`/api/device/${device.mac_address}/security`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Informations de sécurité mises à jour', 'success');
                // La mise à jour réelle sera gérée par Socket.IO
            } else {
                showNotification('Erreur lors de la mise à jour des informations', 'danger');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la mise à jour des informations:', error);
            showNotification('Erreur lors de la mise à jour des informations', 'danger');
        });
    };
    
    // Afficher la fenêtre modale
    const modal = new bootstrap.Modal(document.getElementById('deviceDetailsModal'));
    modal.show();
}

/**
 * Configure les écouteurs d'événements
 */
function setupEventListeners() {
    // Événements pour les contrôles
    document.getElementById('showOfflineDevices').addEventListener('change', updateTopologyVisualization);
    document.getElementById('colorBySecurityScore').addEventListener('change', updateTopologyVisualization);
    
    // Événement pour le bouton de réinitialisation
    document.getElementById('resetLayoutBtn').addEventListener('click', function() {
        // Réinitialiser les positions fixes
        topologyData.devices.forEach(device => {
            delete device.fx;
            delete device.fy;
        });
        
        // Redémarrer la simulation
        simulation.alpha(1).restart();
        
        showNotification('Disposition réinitialisée', 'info');
    });
    
    // Événement pour le bouton d'étiquettes
    document.getElementById('toggleLabelsBtn').addEventListener('click', function() {
        showLabels = !showLabels;
        d3.select('.node-labels')
            .selectAll('text')
            .style('display', showLabels ? 'block' : 'none');
        
        showNotification(`Étiquettes ${showLabels ? 'affichées' : 'masquées'}`, 'info');
    });
    
    // Événement pour le bouton de statistiques
    document.getElementById('toggleStatsBtn').addEventListener('click', function() {
        const statsPanel = document.querySelector('.stats-panel');
        const isVisible = statsPanel.style.display !== 'none';
        statsPanel.style.display = isVisible ? 'none' : 'block';
        
        showNotification(`Statistiques ${isVisible ? 'masquées' : 'affichées'}`, 'info');
    });
    
    // Événement pour le bouton d'export
    document.getElementById('exportTopologyBtn').addEventListener('click', function() {
        const dataStr = JSON.stringify(topologyData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        
        const exportLink = document.createElement('a');
        exportLink.setAttribute('href', dataUri);
        exportLink.setAttribute('download', 'topology_data.json');
        document.body.appendChild(exportLink);
        exportLink.click();
        document.body.removeChild(exportLink);
        
        showNotification('Données de topologie exportées', 'success');
    });
    
    // Événement pour le formulaire de sauvegarde
    document.getElementById('saveLayoutForm').addEventListener('submit', function(event) {
        event.preventDefault();
        
        const layoutName = document.getElementById('layoutName').value;
        if (!layoutName) return;
        
        // Créer l'objet de disposition
        const layoutData = {
            name: layoutName,
            layout: {}
        };
        
        // Ajouter les positions de chaque appareil
        topologyData.devices.forEach(device => {
            layoutData.layout[device.mac_address] = {
                x: device.x,
                y: device.y
            };
        });
        
        // Envoyer au serveur
        fetch('/api/topology/layout/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(layoutData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Disposition sauvegardée avec succès', 'success');
                // Fermer la fenêtre modale
                const modal = bootstrap.Modal.getInstance(document.getElementById('saveLayoutModal'));
                modal.hide();
            } else {
                showNotification('Erreur lors de la sauvegarde: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la sauvegarde de la disposition:', error);
            showNotification('Erreur lors de la sauvegarde', 'danger');
        });
    });
    
    // Fermer le panneau d'info en cliquant ailleurs
    document.querySelector('.network-container').addEventListener('click', function(event) {
        if (event.target.closest('.device-info-panel') || dragging) return;
        
        // Réinitialiser la sélection
        selectedNode = null;
        
        // Masquer le panneau d'informations
        document.querySelector('.device-info-panel').style.display = 'none';
        
        // Réinitialiser l'apparence des nœuds
        node.style('stroke', null)
            .style('stroke-width', null);
    });
}

/**
 * Formate une date relative
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    
    if (diffSec < 60) return 'à l\'instant';
    if (diffSec < 3600) return `il y a ${Math.floor(diffSec / 60)} minutes`;
    if (diffSec < 86400) return `il y a ${Math.floor(diffSec / 3600)} heures`;
    return `le ${date.toLocaleDateString()}`;
}

/**
 * Formate le type de connexion
 */
function formatConnectionType(type) {
    if (!type) return 'Inconnu';
    
    switch (type.toLowerCase()) {
        case 'wifi':
            return 'WiFi';
        case 'ethernet':
            return 'Ethernet';
        case 'bluetooth':
            return 'Bluetooth';
        default:
            return capitalizeFirstLetter(type);
    }
}

/**
 * Convertit la force du signal en pourcentage
 */
function getSignalPercentage(strength) {
    // Signal WiFi typiquement entre -30 dBm (excellent) et -90 dBm (très faible)
    const min = -90;
    const max = -30;
    const limited = Math.max(min, Math.min(max, strength));
    return Math.round(((limited - min) / (max - min)) * 100);
}

/**
 * Détermine la classe de score de sécurité
 */
function getScoreLevel(score) {
    if (score >= 80) return 'security-score-high';
    if (score >= 50) return 'security-score-medium';
    return 'security-score-low';
}

/**
 * Détermine la couleur en fonction du score de sécurité
 */
function getScoreColor(score) {
    // Gradient de couleur du rouge (0) au vert (100)
    if (score >= 80) return '#1dd1a1'; // Vert
    if (score >= 60) return '#feca57'; // Jaune
    if (score >= 40) return '#ff9f43'; // Orange
    return '#ff6b6b'; // Rouge
}

/**
 * Détermine la bande passante en fonction du type de connexion
 */
function getBandwidth(connectionType) {
    if (!connectionType) return { value: 0, percent: 0 };
    
    let bandwidth;
    switch (connectionType.toLowerCase()) {
        case 'ethernet':
            bandwidth = Math.floor(Math.random() * 500) + 500; // 500-1000 Mbps
            break;
        case 'wifi':
            bandwidth = Math.floor(Math.random() * 200) + 50; // 50-250 Mbps
            break;
        case 'bluetooth':
            bandwidth = Math.floor(Math.random() * 2) + 1; // 1-3 Mbps
            break;
        default:
            bandwidth = Math.floor(Math.random() * 50) + 10; // 10-60 Mbps
    }
    
    // Calculer le pourcentage sur une échelle de 1000 Mbps
    const percent = Math.min(100, Math.round((bandwidth / 1000) * 100));
    
    return { value: bandwidth, percent };
}

/**
 * Génère une quantité aléatoire de données transférées
 */
function getRandomDataTransferred(deviceType, direction) {
    let base, unit;
    
    // Différentes plages selon le type d'appareil et la direction
    if (deviceType === 'tv' || deviceType === 'laptop') {
        if (direction === 'download') {
            base = Math.random() * 10 + 1; // 1-11 GB
            unit = 'GB';
        } else {
            base = Math.random() * 500 + 100; // 100-600 MB
            unit = 'MB';
        }
    } else if (deviceType === 'phone' || deviceType === 'tablet') {
        if (direction === 'download') {
            base = Math.random() * 5 + 0.5; // 0.5-5.5 GB
            unit = 'GB';
        } else {
            base = Math.random() * 300 + 50; // 50-350 MB
            unit = 'MB';
        }
    } else if (deviceType === 'iot') {
        if (direction === 'download') {
            base = Math.random() * 100 + 10; // 10-110 MB
            unit = 'MB';
        } else {
            base = Math.random() * 50 + 5; // 5-55 MB
            unit = 'MB';
        }
    } else {
        if (direction === 'download') {
            base = Math.random() * 1 + 0.1; // 0.1-1.1 GB
            unit = 'GB';
        } else {
            base = Math.random() * 200 + 20; // 20-220 MB
            unit = 'MB';
        }
    }
    
    return `${base.toFixed(1)} ${unit}`;
}

/**
 * Retourne l'icône Font Awesome correspondant au type d'appareil
 */
function getDeviceIcon(deviceType) {
    switch (deviceType) {
        case 'router':
            return 'fa-network-wired';
        case 'laptop':
            return 'fa-laptop';
        case 'phone':
            return 'fa-mobile-alt';
        case 'tablet':
            return 'fa-tablet-alt';
        case 'desktop':
            return 'fa-desktop';
        case 'tv':
            return 'fa-tv';
        case 'iot':
            return 'fa-microchip';
        case 'printer':
            return 'fa-print';
        default:
            return 'fa-hdd';
    }
}

/**
 * Affiche une notification
 */
function showNotification(message, type = 'info') {
    const container = document.createElement('div');
    container.className = `toast align-items-center text-white bg-${type} border-0 position-fixed top-0 end-0 m-3`;
    container.style.zIndex = '1050';
    container.setAttribute('role', 'alert');
    container.setAttribute('aria-live', 'assertive');
    container.setAttribute('aria-atomic', 'true');
    
    const flexContainer = document.createElement('div');
    flexContainer.className = 'd-flex';
    
    const body = document.createElement('div');
    body.className = 'toast-body';
    body.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Fermer');
    
    flexContainer.appendChild(body);
    flexContainer.appendChild(closeButton);
    container.appendChild(flexContainer);
    
    document.body.appendChild(container);
    
    const toast = new bootstrap.Toast(container, { autohide: true, delay: 3000 });
    toast.show();
    
    container.addEventListener('hidden.bs.toast', function() {
        document.body.removeChild(container);
    });
}

/**
 * Met en majuscule la première lettre d'une chaîne
 */
function capitalizeFirstLetter(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Génère des données de démonstration pour la topologie réseau
 */
function generateDemoTopology() {
    console.log('Génération de données de démonstration pour la topologie');
    
    // Appareils de démonstration
    const devices = [
        {
            mac_address: '00:11:22:33:44:55',
            name: 'Routeur WiFi Principal',
            device_type: 'router',
            manufacturer: 'Netgear',
            model: 'Nighthawk RAX50',
            ip_address: '192.168.1.1',
            connection_type: 'ethernet',
            online: true,
            signal_strength: -35,
            security_score: 85,
            os: 'Propriétaire',
            x: 400,
            y: 300
        },
        {
            mac_address: '66:77:88:99:AA:BB',
            name: 'Ordinateur Portable',
            device_type: 'laptop',
            manufacturer: 'Dell',
            model: 'XPS 15',
            ip_address: '192.168.1.100',
            connection_type: 'wifi',
            online: true,
            signal_strength: -55,
            security_score: 75,
            os: 'Windows 11',
            x: 300,
            y: 200
        },
        {
            mac_address: 'CC:DD:EE:FF:00:11',
            name: 'Smartphone',
            device_type: 'phone',
            manufacturer: 'Samsung',
            model: 'Galaxy S22',
            ip_address: '192.168.1.101',
            connection_type: 'wifi',
            online: true,
            signal_strength: -60,
            security_score: 65,
            os: 'Android 13',
            x: 500,
            y: 200
        },
        {
            mac_address: '22:33:44:55:66:77',
            name: 'Caméra IP',
            device_type: 'iot',
            manufacturer: 'Hikvision',
            model: 'DS-2CD2342WD-I',
            ip_address: '192.168.1.102',
            connection_type: 'wifi',
            online: true,
            signal_strength: -65,
            security_score: 35,
            os: 'Propriétaire',
            x: 600,
            y: 400
        },
        {
            mac_address: '88:99:AA:BB:CC:DD',
            name: 'Smart TV',
            device_type: 'tv',
            manufacturer: 'LG',
            model: 'OLED C2',
            ip_address: '192.168.1.103',
            connection_type: 'wifi',
            online: true,
            signal_strength: -70,
            security_score: 55,
            os: 'WebOS 6.0',
            x: 200,
            y: 400
        }
    ];
    
    // Connexions de démonstration
    const connections = [
        {
            source: '00:11:22:33:44:55',
            target: '66:77:88:99:AA:BB',
            connection_type: 'wifi'
        },
        {
            source: '00:11:22:33:44:55',
            target: 'CC:DD:EE:FF:00:11',
            connection_type: 'wifi'
        },
        {
            source: '00:11:22:33:44:55',
            target: '22:33:44:55:66:77',
            connection_type: 'wifi'
        },
        {
            source: '00:11:22:33:44:55',
            target: '88:99:AA:BB:CC:DD',
            connection_type: 'wifi'
        }
    ];
    
    const demoData = {
        devices: devices,
        connections: connections,
        timestamp: new Date().toISOString()
    };
    
    // Traiter les données de démonstration
    processTopologyData(demoData);
}