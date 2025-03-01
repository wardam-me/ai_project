/**
 * Threat Wheel Visualization
 * Script pour la visualisation interactive de la roue des menaces réseau
 */

// Variables globales
let wheelData = null;
let currentView = 'severity'; // 'severity', 'frequency', 'recency'
let filteredData = null;
let severityRange = [1, 10];
let timeframeFilter = 'all';
let activeCategories = new Set();
let wheelChart = null;

/**
 * Initialise la roue des menaces
 */
function initThreatWheel() {
  // Initialiser les contrôles
  initWheelControls();
  
  // Initialiser le slider de sévérité
  const severitySlider = document.getElementById('severitySlider');
  if (severitySlider) {
    noUiSlider.create(severitySlider, {
      start: [1, 10],
      connect: true,
      range: {
        'min': 1,
        'max': 10
      },
      step: 1,
      tooltips: true,
      format: {
        to: value => Math.round(value),
        from: value => parseInt(value)
      }
    });
    
    severitySlider.noUiSlider.on('update', function(values, handle) {
      severityRange = [parseInt(values[0]), parseInt(values[1])];
      updateVisualization();
    });
  }
  
  // Initialiser le filtre de période
  const timeframeFilter = document.getElementById('timeframeFilter');
  if (timeframeFilter) {
    timeframeFilter.addEventListener('change', function() {
      timeframeFilter = this.value;
      updateVisualization();
    });
  }
}

/**
 * Initialise les contrôles de la roue
 */
function initWheelControls() {
  const viewButtons = document.querySelectorAll('.wheel-btn');
  viewButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      viewButtons.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      currentView = this.dataset.view;
      updateVisualization();
    });
  });
}

/**
 * Récupère les données de la roue des menaces depuis l'API
 */
function fetchThreatWheelData() {
  fetch('/api/threat-wheel-data')
    .then(response => {
      if (!response.ok) {
        throw new Error('Erreur réseau lors de la récupération des données');
      }
      return response.json();
    })
    .then(data => {
      wheelData = data;
      
      // Initialiser les catégories actives
      activeCategories = new Set(data.categories.map(cat => cat.id));
      
      // Mettre à jour les statistiques
      updateStats(data.stats);
      
      // Générer la légende des catégories
      generateCategoryLegend(data.categories);
      
      // Créer la visualisation
      createVisualization(data);
    })
    .catch(error => {
      console.error('Erreur:', error);
      displayErrorMessage('Impossible de charger les données de la roue des menaces.');
    });
}

/**
 * Met à jour les statistiques affichées
 */
function updateStats(stats) {
  document.getElementById('totalThreats').textContent = stats.total_threats;
  document.getElementById('avgSeverity').textContent = stats.avg_severity;
  document.getElementById('lowSeverity').textContent = stats.severity_distribution.low;
  document.getElementById('mediumSeverity').textContent = stats.severity_distribution.medium;
  document.getElementById('highSeverity').textContent = stats.severity_distribution.high;
  document.getElementById('recentThreats').textContent = stats.recent_threats;
  
  // Trouver la catégorie la plus active
  let topCategory = '';
  let topCount = 0;
  
  for (const [category, count] of Object.entries(stats.category_distribution)) {
    if (count > topCount) {
      topCount = count;
      topCategory = category;
    }
  }
  
  // Mettre à jour l'affichage de la catégorie la plus active
  if (topCategory && wheelData) {
    const categoryInfo = wheelData.categories.find(cat => cat.id === topCategory);
    if (categoryInfo) {
      document.getElementById('topCategory').textContent = categoryInfo.name;
      document.getElementById('topCategoryInfo').textContent = 
        `${topCount} menace${topCount > 1 ? 's' : ''} (${Math.round(topCount / stats.total_threats * 100)}%)`;
      
      // Ajouter la couleur de la catégorie
      document.getElementById('topCategory').style.color = categoryInfo.color;
    }
  }
}

/**
 * Génère la légende des catégories
 */
function generateCategoryLegend(categories) {
  const legendContainer = document.getElementById('categoryLegend');
  if (!legendContainer) return;
  
  legendContainer.innerHTML = '';
  
  categories.forEach(category => {
    const categoryItem = document.createElement('div');
    categoryItem.className = 'category-item';
    categoryItem.dataset.category = category.id;
    
    const colorIndicator = document.createElement('div');
    colorIndicator.className = 'category-color';
    colorIndicator.style.backgroundColor = category.color;
    
    const categoryName = document.createElement('div');
    categoryName.className = 'category-name';
    categoryName.textContent = category.name;
    
    categoryItem.appendChild(colorIndicator);
    categoryItem.appendChild(categoryName);
    
    // Ajouter l'événement de clic pour filtrer
    categoryItem.addEventListener('click', function() {
      const categoryId = this.dataset.category;
      
      if (activeCategories.has(categoryId)) {
        // Si toutes les catégories sont sélectionnées sauf une, ne pas permettre sa désélection
        if (activeCategories.size > 1) {
          activeCategories.delete(categoryId);
          this.classList.add('faded');
        }
      } else {
        activeCategories.add(categoryId);
        this.classList.remove('faded');
      }
      
      updateVisualization();
    });
    
    legendContainer.appendChild(categoryItem);
  });
}

/**
 * Crée la visualisation de la roue
 */
function createVisualization(data) {
  const container = document.getElementById('threatWheel');
  if (!container) return;
  
  // Vider le conteneur
  container.innerHTML = '';
  
  // Obtenir les dimensions du conteneur
  const width = container.clientWidth;
  const height = container.clientHeight || 600;
  const radius = Math.min(width, height) / 2 - 40;
  
  // Créer l'élément SVG
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 2}, ${height / 2})`);
  
  // Préparer les données filtrées
  filteredData = filterData(data);
  
  // Créer les sections de l'arc
  const arc = d3.arc()
    .innerRadius(radius * 0.3)
    .outerRadius(d => radius * 0.7 + radiusScale(getValueByView(d, currentView)));
  
  // Créer la disposition en secteurs
  const pie = d3.pie()
    .value(d => d.size)
    .sort(null);
  
  // Ajouter les arcs pour les menaces
  const arcs = svg.selectAll('.arc')
    .data(pie(filteredData.threats))
    .enter()
    .append('g')
    .attr('class', 'arc');
  
  // Ajouter les chemins pour les arcs
  arcs.append('path')
    .attr('d', arc)
    .attr('fill', d => d.data.color)
    .attr('stroke', '#222')
    .attr('stroke-width', 1)
    .attr('opacity', 0.8)
    .on('mouseover', function(event, d) {
      // Mettre en surbrillance le segment
      d3.select(this)
        .transition()
        .duration(200)
        .attr('opacity', 1)
        .attr('transform', 'scale(1.05)');
      
      // Afficher l'infobulle
      const tooltip = document.getElementById('wheelTooltip');
      if (tooltip) {
        const categoryInfo = filteredData.categories.find(cat => cat.id === d.data.category);
        const category = categoryInfo ? categoryInfo.name : d.data.category;
        
        let lastSeen = 'Inconnu';
        if (d.data.lastSeen) {
          try {
            const date = new Date(d.data.lastSeen);
            lastSeen = date.toLocaleDateString();
          } catch (e) {
            console.error('Date format error:', e);
          }
        }
        
        tooltip.innerHTML = `
          <div><strong>${d.data.name}</strong></div>
          <div>Catégorie: <span style="color:${d.data.color}">${category}</span></div>
          <div>Sévérité: ${d.data.severity}/10</div>
          <div>Fréquence: ${d.data.frequency}</div>
          <div>Dernière détection: ${lastSeen}</div>
          <div>${d.data.description}</div>
        `;
        
        tooltip.style.opacity = 1;
        tooltip.style.left = `${event.pageX + 10}px`;
        tooltip.style.top = `${event.pageY + 10}px`;
      }
    })
    .on('mouseout', function() {
      // Réinitialiser le segment
      d3.select(this)
        .transition()
        .duration(200)
        .attr('opacity', 0.8)
        .attr('transform', 'scale(1)');
      
      // Masquer l'infobulle
      const tooltip = document.getElementById('wheelTooltip');
      if (tooltip) {
        tooltip.style.opacity = 0;
      }
    })
    .on('click', function(event, d) {
      // Afficher les détails complets de la menace
      showThreatDetails(d.data);
    });
  
  // Ajouter les étiquettes pour les menaces
  arcs.append('text')
    .attr('transform', d => {
      const centroid = arc.centroid(d);
      const x = centroid[0] * 1.5;
      const y = centroid[1] * 1.5;
      const rotation = (d.startAngle + d.endAngle) / 2 * 180 / Math.PI;
      return `translate(${x}, ${y}) rotate(${rotation})`;
    })
    .attr('dy', '0.35em')
    .attr('text-anchor', 'middle')
    .text(d => {
      // Afficher le nom de la menace si l'arc est assez grand
      const arcLength = (d.endAngle - d.startAngle) * radius;
      return arcLength > 30 ? d.data.name : '';
    })
    .attr('fill', 'white')
    .attr('font-size', '10px')
    .attr('pointer-events', 'none');
  
  // Ajouter le cercle central
  svg.append('circle')
    .attr('cx', 0)
    .attr('cy', 0)
    .attr('r', radius * 0.3)
    .attr('fill', '#222')
    .attr('stroke', '#444')
    .attr('stroke-width', 2);
  
  // Ajouter le titre central
  svg.append('text')
    .attr('x', 0)
    .attr('y', -5)
    .attr('text-anchor', 'middle')
    .attr('fill', 'white')
    .attr('font-size', '16px')
    .attr('font-weight', 'bold')
    .text('Menaces');
  
  svg.append('text')
    .attr('x', 0)
    .attr('y', 15)
    .attr('text-anchor', 'middle')
    .attr('fill', '#aaa')
    .attr('font-size', '12px')
    .text('Réseau');
  
  // Sauvegarder la référence au graphique
  wheelChart = {
    svg: svg,
    arc: arc,
    pie: pie
  };
}

/**
 * Filtre les données selon les critères actuels
 */
function filterData(data) {
  if (!data || !data.threats) return { categories: [], threats: [] };
  
  // Cloner les données
  const result = {
    categories: [...data.categories],
    threats: []
  };
  
  // Filtrer les menaces
  result.threats = data.threats.filter(threat => {
    // Filtrer par catégorie active
    if (!activeCategories.has(threat.category)) {
      return false;
    }
    
    // Filtrer par plage de sévérité
    if (threat.severity < severityRange[0] || threat.severity > severityRange[1]) {
      return false;
    }
    
    // Filtrer par période
    if (timeframeFilter !== 'all' && threat.lastSeen) {
      try {
        const lastSeen = new Date(threat.lastSeen);
        const now = new Date();
        const daysDiff = Math.floor((now - lastSeen) / (1000 * 60 * 60 * 24));
        
        if (daysDiff > parseInt(timeframeFilter)) {
          return false;
        }
      } catch (e) {
        console.error('Date parsing error:', e);
      }
    }
    
    return true;
  });
  
  return result;
}

/**
 * Met à jour la visualisation avec les filtres actuels
 */
function updateVisualization() {
  if (!wheelData) return;
  
  filteredData = filterData(wheelData);
  
  if (!wheelChart) {
    createVisualization(wheelData);
    return;
  }
  
  const container = document.getElementById('threatWheel');
  const width = container.clientWidth;
  const height = container.clientHeight || 600;
  const radius = Math.min(width, height) / 2 - 40;
  
  // Mettre à jour la fonction d'arc
  wheelChart.arc
    .innerRadius(radius * 0.3)
    .outerRadius(d => radius * 0.7 + radiusScale(getValueByView(d.data, currentView)));
  
  // Mettre à jour les données
  const arcs = wheelChart.svg.selectAll('.arc')
    .data(wheelChart.pie(filteredData.threats));
  
  // Supprimer les éléments qui ne sont plus dans les données
  arcs.exit().remove();
  
  // Ajouter les nouveaux éléments
  const newArcs = arcs.enter()
    .append('g')
    .attr('class', 'arc');
  
  newArcs.append('path')
    .attr('fill', d => d.data.color)
    .attr('stroke', '#222')
    .attr('stroke-width', 1)
    .attr('opacity', 0.8)
    .on('mouseover', function(event, d) {
      // Même événement que dans createVisualization
    })
    .on('mouseout', function() {
      // Même événement que dans createVisualization
    })
    .on('click', function(event, d) {
      // Même événement que dans createVisualization
    });
  
  newArcs.append('text')
    .attr('dy', '0.35em')
    .attr('text-anchor', 'middle')
    .attr('fill', 'white')
    .attr('font-size', '10px')
    .attr('pointer-events', 'none');
  
  // Mettre à jour tous les éléments
  wheelChart.svg.selectAll('.arc path')
    .transition()
    .duration(500)
    .attr('d', wheelChart.arc)
    .attr('fill', d => d.data.color);
  
  wheelChart.svg.selectAll('.arc text')
    .transition()
    .duration(500)
    .attr('transform', d => {
      const centroid = wheelChart.arc.centroid(d);
      const x = centroid[0] * 1.5;
      const y = centroid[1] * 1.5;
      const rotation = (d.startAngle + d.endAngle) / 2 * 180 / Math.PI;
      return `translate(${x}, ${y}) rotate(${rotation})`;
    })
    .text(d => {
      const arcLength = (d.endAngle - d.startAngle) * radius;
      return arcLength > 30 ? d.data.name : '';
    });
}

/**
 * Échelle pour ajuster le rayon selon la valeur
 */
function radiusScale(value) {
  // Valeur entre 0 et 1
  let normalized = 0;
  
  // Normaliser selon le type de valeur
  if (typeof value === 'number') {
    normalized = Math.min(Math.max(value / 10, 0), 1);
  }
  
  // Retourner une valeur entre 0 et 50px
  return normalized * 50;
}

/**
 * Obtient la valeur à utiliser selon la vue actuelle
 */
function getValueByView(data, view) {
  switch (view) {
    case 'severity':
      return data.severity;
    case 'frequency':
      return data.frequency / 10; // Normaliser la fréquence
    case 'recency':
      if (data.lastSeen) {
        try {
          const lastSeen = new Date(data.lastSeen);
          const now = new Date();
          const daysDiff = Math.floor((now - lastSeen) / (1000 * 60 * 60 * 24));
          
          // Convertir les jours en une valeur entre 0 et 10 (plus récent = plus grand)
          return Math.max(10 - (daysDiff / 3), 1);
        } catch (e) {
          console.error('Date parsing error:', e);
          return 5; // Valeur par défaut
        }
      }
      return 5; // Valeur par défaut si pas de date
    default:
      return data.severity;
  }
}

/**
 * Affiche les détails complets d'une menace
 */
function showThreatDetails(threat) {
  // Cette fonction pourrait afficher une modale avec les détails complets
  console.log('Affichage des détails de la menace:', threat);
  
  // À implémenter: création d'une modale avec les détails complets
}

/**
 * Affiche un message d'erreur
 */
function displayErrorMessage(message) {
  const container = document.getElementById('threatWheel');
  if (container) {
    container.innerHTML = `
      <div class="alert alert-danger m-3" role="alert">
        <i class="fas fa-exclamation-triangle mr-2"></i> ${message}
      </div>
    `;
  }
}