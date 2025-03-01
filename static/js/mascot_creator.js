// Créateur de mascottes de cybersécurité

// État global pour stocker les éléments et les sélections actuelles
const mascotState = {
    elements: {},
    selectedElements: {
        base: 'penguin',
        hat: null,
        accessory: null,
        outfit: null,
        background: null
    },
    colors: {
        primary: '#3498db',
        secondary: '#2ecc71',
        accent: '#e74c3c'
    },
    personality: 'friendly',
    securityScore: 0,
    currentMascotId: null
};

// Initialiser l'application quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    // Charger les éléments de mascotte
    loadMascotElements();
    
    // Charger la galerie des mascottes
    loadMascotGallery();
    
    // Configurer les écouteurs d'événements
    setupEventListeners();
});

// Fonction pour charger les éléments de mascotte depuis l'API
function loadMascotElements() {
    fetch('/api/mascot-elements')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors du chargement des éléments de mascotte');
            }
            return response.json();
        })
        .then(data => {
            mascotState.elements = data;
            renderMascotElements();
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur lors du chargement des éléments', 'danger');
        });
}

// Fonction pour charger la galerie des mascottes de l'utilisateur
function loadMascotGallery() {
    const galleryContainer = document.getElementById('mascotGallery');
    
    fetch('/api/mascots')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors du chargement de la galerie');
            }
            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                galleryContainer.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <i class="fas fa-robot fa-4x mb-3 text-muted"></i>
                        <p>Vous n'avez pas encore créé de mascottes.</p>
                        <button class="btn btn-primary mt-2" id="createFirstMascotBtn">
                            <i class="fas fa-plus-circle me-1"></i>Créer votre première mascotte
                        </button>
                    </div>
                `;
                
                document.getElementById('createFirstMascotBtn').addEventListener('click', () => {
                    document.getElementById('nav-creator-tab').click();
                });
            } else {
                galleryContainer.innerHTML = '';
                
                data.forEach(mascot => {
                    const mascotCard = document.createElement('div');
                    mascotCard.className = 'col-md-6 col-lg-4 mascot-gallery-item';
                    mascotCard.dataset.mascotId = mascot.id;
                    
                    const securityLevelClass = getSecurityLevelClass(mascot.security_score);
                    
                    mascotCard.innerHTML = `
                        <div class="card h-100">
                            <div class="card-img-top p-3">
                                ${mascot.svg || '<div class="text-center py-4"><i class="fas fa-user-shield fa-4x text-muted"></i></div>'}
                            </div>
                            <div class="card-body">
                                <h5 class="card-title">${mascot.name}</h5>
                                <div class="d-flex justify-content-between">
                                    <span class="badge ${securityLevelClass}">${mascot.security_score} points</span>
                                    <small class="text-muted">Créé le ${new Date(mascot.created_at).toLocaleDateString()}</small>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    galleryContainer.appendChild(mascotCard);
                    
                    mascotCard.addEventListener('click', () => {
                        openMascotDetails(mascot.id);
                    });
                });
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            galleryContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-4x mb-3 text-danger"></i>
                    <p>Erreur lors du chargement de la galerie.</p>
                    <button class="btn btn-primary mt-2" id="retryGalleryBtn">
                        <i class="fas fa-sync me-1"></i>Réessayer
                    </button>
                </div>
            `;
            
            document.getElementById('retryGalleryBtn').addEventListener('click', () => {
                loadMascotGallery();
            });
        });
}

// Fonction pour configurer les écouteurs d'événements
function setupEventListeners() {
    // Formulaire de création de mascotte
    const mascotForm = document.getElementById('mascotForm');
    mascotForm.addEventListener('submit', (event) => {
        event.preventDefault();
        saveMascot();
    });
    
    // Bouton d'aperçu
    const previewBtn = document.getElementById('previewBtn');
    previewBtn.addEventListener('click', updateMascotPreview);
    
    // Bouton de randomisation
    const randomizeBtn = document.getElementById('randomizeBtn');
    randomizeBtn.addEventListener('click', randomizeMascot);
    
    // Écouteurs pour les sélecteurs de couleur
    document.getElementById('primaryColor').addEventListener('change', (e) => {
        mascotState.colors.primary = e.target.value;
    });
    
    document.getElementById('secondaryColor').addEventListener('change', (e) => {
        mascotState.colors.secondary = e.target.value;
    });
    
    document.getElementById('accentColor').addEventListener('change', (e) => {
        mascotState.colors.accent = e.target.value;
    });
    
    // Écouteur pour le sélecteur de personnalité
    document.getElementById('mascotPersonality').addEventListener('change', (e) => {
        mascotState.personality = e.target.value;
    });
    
    // Bouton de suppression dans le modal
    document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
        deleteMascot(mascotState.currentMascotId);
    });
    
    // Bouton d'édition dans le modal
    document.getElementById('editMascotBtn').addEventListener('click', () => {
        loadMascotForEditing(mascotState.currentMascotId);
        $('#mascotModal').modal('hide');
        document.getElementById('nav-creator-tab').click();
    });
}

// Fonction pour rendre les éléments de mascotte dans l'interface
function renderMascotElements() {
    // Rendre les éléments de base
    renderElementCategory('base', mascotState.elements.base || []);
    
    // Rendre les chapeaux
    renderElementCategory('hat', mascotState.elements.hats || []);
    
    // Rendre les accessoires
    renderElementCategory('accessory', mascotState.elements.accessories || []);
    
    // Rendre les tenues
    renderElementCategory('outfit', mascotState.elements.outfits || []);
    
    // Rendre les arrière-plans
    renderElementCategory('background', mascotState.elements.backgrounds || []);
    
    // Sélectionner le premier élément de base par défaut
    if (mascotState.elements.base && mascotState.elements.base.length > 0) {
        const defaultBaseElement = document.querySelector(`[data-element-type="base"][data-element-id="${mascotState.selectedElements.base}"]`);
        if (defaultBaseElement) {
            defaultBaseElement.classList.add('selected');
        }
    }
}

// Fonction pour rendre une catégorie d'éléments
function renderElementCategory(category, elements) {
    const pluralCategory = category === 'hat' ? 'hats' : 
                          category === 'accessory' ? 'accessories' : 
                          category === 'outfit' ? 'outfits' : 
                          category === 'background' ? 'backgrounds' : category;
    
    const container = document.getElementById(`${category}Elements`);
    container.innerHTML = '';
    
    if (!elements || elements.length === 0) {
        container.innerHTML = `<div class="col-12 text-center py-3 text-muted">Aucun élément disponible</div>`;
        return;
    }
    
    // Ajouter l'option "Aucun" pour les catégories optionnelles
    if (category !== 'base') {
        const noneElement = document.createElement('div');
        noneElement.className = 'col-md-3 col-sm-4 col-6 mb-3';
        noneElement.innerHTML = `
            <div class="mascot-element-item ${mascotState.selectedElements[category] === null ? 'selected' : ''}" 
                 data-element-type="${category}" 
                 data-element-id="none">
                <i class="fas fa-ban fa-2x text-muted"></i>
                <div class="mascot-element-name">Aucun</div>
            </div>
        `;
        container.appendChild(noneElement);
        
        noneElement.querySelector('.mascot-element-item').addEventListener('click', (e) => {
            selectElement(category, null, e.currentTarget);
        });
    }
    
    // Ajouter les éléments de la catégorie
    elements.forEach(element => {
        const elementDiv = document.createElement('div');
        elementDiv.className = 'col-md-3 col-sm-4 col-6 mb-3';
        
        const securityBoost = element.security_boost ? 
            `<div class="element-boost">+${element.security_boost}</div>` : '';
        
        elementDiv.innerHTML = `
            <div class="mascot-element-item ${mascotState.selectedElements[category] === element.id ? 'selected' : ''}" 
                 data-element-type="${category}" 
                 data-element-id="${element.id}">
                <svg width="50" height="50" viewBox="0 0 100 100">
                    <rect width="100" height="100" fill="#f0f0f0" rx="10" ry="10" />
                    <text x="50" y="50" font-family="Arial" font-size="8" fill="#888" text-anchor="middle" dominant-baseline="middle">
                        ${element.id}
                    </text>
                </svg>
                ${securityBoost}
                <div class="mascot-element-name">${element.name}</div>
            </div>
        `;
        
        container.appendChild(elementDiv);
        
        elementDiv.querySelector('.mascot-element-item').addEventListener('click', (e) => {
            selectElement(category, element.id, e.currentTarget);
        });
    });
}

// Fonction pour sélectionner un élément
function selectElement(category, elementId, element) {
    // Désélectionner tous les éléments de cette catégorie
    document.querySelectorAll(`[data-element-type="${category}"].selected`).forEach(el => {
        el.classList.remove('selected');
    });
    
    // Sélectionner le nouvel élément
    if (element) {
        element.classList.add('selected');
    }
    
    // Mettre à jour l'état
    mascotState.selectedElements[category] = elementId;
    
    // Mettre à jour le score de sécurité
    updateSecurityScore();
}

// Fonction pour mettre à jour le score de sécurité
function updateSecurityScore() {
    let score = 0;
    
    // Score de base selon le type de base
    const baseElement = mascotState.elements.base?.find(e => e.id === mascotState.selectedElements.base);
    if (baseElement) {
        const securityLevel = baseElement.security_level || 'medium';
        if (securityLevel === 'low') score += 10;
        else if (securityLevel === 'medium') score += 20;
        else if (securityLevel === 'high') score += 30;
        else if (securityLevel === 'very_high') score += 40;
    }
    
    // Ajouter les bonus des éléments
    const hatElement = mascotState.elements.hats?.find(e => e.id === mascotState.selectedElements.hat);
    if (hatElement) {
        score += hatElement.security_boost || 0;
    }
    
    const accessoryElement = mascotState.elements.accessories?.find(e => e.id === mascotState.selectedElements.accessory);
    if (accessoryElement) {
        score += accessoryElement.security_boost || 0;
    }
    
    const outfitElement = mascotState.elements.outfits?.find(e => e.id === mascotState.selectedElements.outfit);
    if (outfitElement) {
        score += outfitElement.security_boost || 0;
    }
    
    // S'assurer que le score ne dépasse pas 100
    mascotState.securityScore = Math.min(score, 100);
}

// Fonction pour mettre à jour l'aperçu de la mascotte
function updateMascotPreview() {
    const previewContainer = document.getElementById('mascotPreview');
    const mascotDetails = document.getElementById('mascotDetails');
    const name = document.getElementById('mascotName').value || 'Mascotte sans nom';
    
    // Afficher le spinner de chargement
    previewContainer.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Génération de l'aperçu...</span>
            </div>
            <p class="mt-2">Génération de votre mascotte...</p>
        </div>
    `;
    
    // Construire les données pour l'aperçu
    const previewData = {
        name: name,
        base: mascotState.selectedElements.base,
        hat: mascotState.selectedElements.hat,
        accessory: mascotState.selectedElements.accessory,
        outfit: mascotState.selectedElements.outfit,
        background: mascotState.selectedElements.background,
        colors: mascotState.colors,
        personality: mascotState.personality
    };
    
    // Obtenir l'aperçu SVG de l'API
    fetch('/api/mascot-preview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(previewData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur lors de la génération de l\'aperçu');
        }
        return response.json();
    })
    .then(data => {
        // Afficher l'aperçu SVG
        previewContainer.innerHTML = data.svg;
        
        // Mettre à jour les détails de la mascotte
        document.getElementById('previewName').textContent = name;
        document.getElementById('securityScore').textContent = mascotState.securityScore;
        document.getElementById('securityLevel').textContent = getSecurityLevel(mascotState.securityScore);
        document.getElementById('securityTitle').textContent = getSecurityTitle(mascotState.securityScore);
        
        // Afficher les traits de personnalité
        const personalityTraits = document.getElementById('personalityTraits');
        personalityTraits.innerHTML = '';
        
        getPersonalityTraits(mascotState.personality).forEach(trait => {
            const traitSpan = document.createElement('span');
            traitSpan.className = 'personality-trait';
            traitSpan.textContent = trait;
            personalityTraits.appendChild(traitSpan);
        });
        
        // Afficher l'histoire de la mascotte
        document.getElementById('mascotStory').textContent = data.story;
        
        // Afficher les détails
        mascotDetails.style.display = 'block';
    })
    .catch(error => {
        console.error('Erreur:', error);
        previewContainer.innerHTML = `
            <div class="text-center py-5 text-danger">
                <i class="fas fa-exclamation-circle fa-3x mb-3"></i>
                <p>Erreur lors de la génération de l'aperçu.</p>
                <button class="btn btn-sm btn-primary mt-2" onclick="updateMascotPreview()">
                    <i class="fas fa-sync me-1"></i>Réessayer
                </button>
            </div>
        `;
        mascotDetails.style.display = 'none';
    });
}

// Fonction pour sauvegarder une mascotte
function saveMascot() {
    const saveBtn = document.getElementById('saveBtn');
    const name = document.getElementById('mascotName').value;
    
    if (!name) {
        showNotification('Veuillez donner un nom à votre mascotte', 'warning');
        return;
    }
    
    // Désactiver le bouton pendant la sauvegarde
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Sauvegarde...';
    
    // Construire les données de la mascotte
    const mascotData = {
        name: name,
        base: mascotState.selectedElements.base,
        hat: mascotState.selectedElements.hat,
        accessory: mascotState.selectedElements.accessory,
        outfit: mascotState.selectedElements.outfit,
        background: mascotState.selectedElements.background,
        colors: mascotState.colors,
        personality: mascotState.personality,
        security_score: mascotState.securityScore,
        id: mascotState.currentMascotId // Si c'est une édition
    };
    
    const url = mascotState.currentMascotId ? 
        `/api/mascots/${mascotState.currentMascotId}` : 
        '/api/mascots';
    
    const method = mascotState.currentMascotId ? 'PUT' : 'POST';
    
    // Envoyer les données à l'API
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(mascotData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur lors de la sauvegarde de la mascotte');
        }
        return response.json();
    })
    .then(data => {
        // Réactiver le bouton
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-save me-1"></i>Sauvegarder';
        
        // Afficher le message de réussite
        showNotification('Mascotte sauvegardée avec succès!', 'success');
        
        // Réinitialiser le formulaire si c'est une nouvelle mascotte
        if (!mascotState.currentMascotId) {
            resetMascotForm();
        }
        
        // Mettre à jour la galerie
        loadMascotGallery();
        
        // Aller à l'onglet galerie
        document.getElementById('nav-gallery-tab').click();
    })
    .catch(error => {
        console.error('Erreur:', error);
        
        // Réactiver le bouton
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-save me-1"></i>Sauvegarder';
        
        // Afficher le message d'erreur
        showNotification('Erreur lors de la sauvegarde: ' + error.message, 'danger');
    });
}

// Fonction pour supprimer une mascotte
function deleteMascot(mascotId) {
    if (!mascotId) return;
    
    // Fermer le modal de confirmation
    $('#deleteConfirmModal').modal('hide');
    
    // Envoyer la requête de suppression
    fetch(`/api/mascots/${mascotId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur lors de la suppression');
        }
        return response.json();
    })
    .then(data => {
        // Afficher le message de réussite
        showNotification('Mascotte supprimée avec succès', 'success');
        
        // Fermer le modal de détails
        $('#mascotModal').modal('hide');
        
        // Mettre à jour la galerie
        loadMascotGallery();
        
        // Réinitialiser l'ID courant
        mascotState.currentMascotId = null;
    })
    .catch(error => {
        console.error('Erreur:', error);
        showNotification('Erreur lors de la suppression: ' + error.message, 'danger');
    });
}

// Fonction pour ouvrir les détails d'une mascotte
function openMascotDetails(mascotId) {
    fetch(`/api/mascots/${mascotId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors du chargement des détails');
            }
            return response.json();
        })
        .then(mascot => {
            // Mettre à jour l'ID courant
            mascotState.currentMascotId = mascot.id;
            
            // Mettre à jour le modal
            document.getElementById('mascotModalLabel').textContent = mascot.name;
            document.getElementById('modalMascotPreview').innerHTML = mascot.svg || '';
            document.getElementById('modalMascotName').textContent = mascot.name;
            document.getElementById('modalSecurityScore').textContent = mascot.security_score;
            document.getElementById('modalSecurityLevel').textContent = getSecurityLevel(mascot.security_score);
            document.getElementById('modalSecurityTitle').textContent = getSecurityTitle(mascot.security_score);
            
            // Afficher les traits de personnalité
            const personalityTraits = document.getElementById('modalPersonalityTraits');
            personalityTraits.innerHTML = '';
            
            getPersonalityTraits(mascot.personality).forEach(trait => {
                const traitSpan = document.createElement('span');
                traitSpan.className = 'personality-trait';
                traitSpan.textContent = trait;
                personalityTraits.appendChild(traitSpan);
            });
            
            // Afficher l'histoire de la mascotte
            document.getElementById('modalMascotStory').textContent = mascot.story;
            
            // Ouvrir le modal
            $('#mascotModal').modal('show');
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur lors du chargement des détails: ' + error.message, 'danger');
        });
}

// Fonction pour charger une mascotte pour l'édition
function loadMascotForEditing(mascotId) {
    fetch(`/api/mascots/${mascotId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors du chargement de la mascotte');
            }
            return response.json();
        })
        .then(mascot => {
            // Mettre à jour l'ID courant
            mascotState.currentMascotId = mascot.id;
            
            // Remplir le formulaire avec les données de la mascotte
            document.getElementById('mascotName').value = mascot.name;
            document.getElementById('mascotPersonality').value = mascot.personality;
            
            // Mettre à jour les couleurs
            const colors = typeof mascot.colors === 'string' ? 
                JSON.parse(mascot.colors) : mascot.colors;
            
            document.getElementById('primaryColor').value = colors.primary;
            document.getElementById('secondaryColor').value = colors.secondary;
            document.getElementById('accentColor').value = colors.accent;
            
            mascotState.colors = colors;
            
            // Mettre à jour les éléments sélectionnés
            mascotState.selectedElements = {
                base: mascot.base,
                hat: mascot.hat,
                accessory: mascot.accessory,
                outfit: mascot.outfit,
                background: mascot.background
            };
            
            // Mettre à jour les sélections visuelles
            document.querySelectorAll('.mascot-element-item.selected').forEach(el => {
                el.classList.remove('selected');
            });
            
            // Sélectionner les éléments correspondants
            Object.entries(mascotState.selectedElements).forEach(([category, elementId]) => {
                if (elementId) {
                    const selectedElement = document.querySelector(`[data-element-type="${category}"][data-element-id="${elementId}"]`);
                    if (selectedElement) {
                        selectedElement.classList.add('selected');
                    }
                } else if (category !== 'base') {
                    // Sélectionner "Aucun" pour les catégories facultatives
                    const noneElement = document.querySelector(`[data-element-type="${category}"][data-element-id="none"]`);
                    if (noneElement) {
                        noneElement.classList.add('selected');
                    }
                }
            });
            
            // Mettre à jour le score de sécurité
            mascotState.securityScore = mascot.security_score;
            
            // Mettre à jour l'aperçu
            updateMascotPreview();
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur lors du chargement de la mascotte: ' + error.message, 'danger');
        });
}

// Fonction pour réinitialiser le formulaire
function resetMascotForm() {
    document.getElementById('mascotForm').reset();
    
    mascotState.currentMascotId = null;
    mascotState.selectedElements = {
        base: 'penguin',
        hat: null,
        accessory: null,
        outfit: null,
        background: null
    };
    
    mascotState.colors = {
        primary: '#3498db',
        secondary: '#2ecc71',
        accent: '#e74c3c'
    };
    
    mascotState.personality = 'friendly';
    
    // Réinitialiser les sélections visuelles
    document.querySelectorAll('.mascot-element-item.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    // Sélectionner l'élément de base par défaut
    const defaultBaseElement = document.querySelector('[data-element-type="base"][data-element-id="penguin"]');
    if (defaultBaseElement) {
        defaultBaseElement.classList.add('selected');
    }
    
    // Sélectionner "Aucun" pour les catégories facultatives
    ['hat', 'accessory', 'outfit', 'background'].forEach(category => {
        const noneElement = document.querySelector(`[data-element-type="${category}"][data-element-id="none"]`);
        if (noneElement) {
            noneElement.classList.add('selected');
        }
    });
    
    // Mettre à jour le score de sécurité
    updateSecurityScore();
    
    // Masquer l'aperçu
    document.getElementById('mascotDetails').style.display = 'none';
    document.getElementById('mascotPreview').innerHTML = `
        <div class="text-center py-5 text-muted">
            <i class="fas fa-user-shield fa-4x mb-3"></i>
            <p>Votre mascotte apparaîtra ici</p>
        </div>
    `;
}

// Fonction pour randomiser la mascotte
function randomizeMascot() {
    // Choisir un élément de base aléatoire
    const baseElements = mascotState.elements.base || [];
    if (baseElements.length > 0) {
        const randomBase = baseElements[Math.floor(Math.random() * baseElements.length)];
        mascotState.selectedElements.base = randomBase.id;
    }
    
    // Choisir un chapeau aléatoire (ou aucun)
    const hatElements = mascotState.elements.hats || [];
    const includeHat = Math.random() > 0.3; // 70% de chance d'avoir un chapeau
    if (includeHat && hatElements.length > 0) {
        const randomHat = hatElements[Math.floor(Math.random() * hatElements.length)];
        mascotState.selectedElements.hat = randomHat.id;
    } else {
        mascotState.selectedElements.hat = null;
    }
    
    // Choisir un accessoire aléatoire (ou aucun)
    const accessoryElements = mascotState.elements.accessories || [];
    const includeAccessory = Math.random() > 0.3; // 70% de chance d'avoir un accessoire
    if (includeAccessory && accessoryElements.length > 0) {
        const randomAccessory = accessoryElements[Math.floor(Math.random() * accessoryElements.length)];
        mascotState.selectedElements.accessory = randomAccessory.id;
    } else {
        mascotState.selectedElements.accessory = null;
    }
    
    // Choisir une tenue aléatoire (ou aucune)
    const outfitElements = mascotState.elements.outfits || [];
    const includeOutfit = Math.random() > 0.3; // 70% de chance d'avoir une tenue
    if (includeOutfit && outfitElements.length > 0) {
        const randomOutfit = outfitElements[Math.floor(Math.random() * outfitElements.length)];
        mascotState.selectedElements.outfit = randomOutfit.id;
    } else {
        mascotState.selectedElements.outfit = null;
    }
    
    // Choisir un arrière-plan aléatoire (ou aucun)
    const backgroundElements = mascotState.elements.backgrounds || [];
    const includeBackground = Math.random() > 0.5; // 50% de chance d'avoir un arrière-plan
    if (includeBackground && backgroundElements.length > 0) {
        const randomBackground = backgroundElements[Math.floor(Math.random() * backgroundElements.length)];
        mascotState.selectedElements.background = randomBackground.id;
    } else {
        mascotState.selectedElements.background = null;
    }
    
    // Générer des couleurs aléatoires
    mascotState.colors = {
        primary: getRandomColor(),
        secondary: getRandomColor(),
        accent: getRandomColor()
    };
    
    // Mettre à jour les input color
    document.getElementById('primaryColor').value = mascotState.colors.primary;
    document.getElementById('secondaryColor').value = mascotState.colors.secondary;
    document.getElementById('accentColor').value = mascotState.colors.accent;
    
    // Choisir une personnalité aléatoire
    const personalities = ['friendly', 'serious', 'playful', 'wise', 'brave'];
    mascotState.personality = personalities[Math.floor(Math.random() * personalities.length)];
    document.getElementById('mascotPersonality').value = mascotState.personality;
    
    // Mettre à jour les sélections visuelles
    document.querySelectorAll('.mascot-element-item.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    // Sélectionner les éléments correspondants
    Object.entries(mascotState.selectedElements).forEach(([category, elementId]) => {
        if (elementId) {
            const selectedElement = document.querySelector(`[data-element-type="${category}"][data-element-id="${elementId}"]`);
            if (selectedElement) {
                selectedElement.classList.add('selected');
            }
        } else if (category !== 'base') {
            // Sélectionner "Aucun" pour les catégories facultatives
            const noneElement = document.querySelector(`[data-element-type="${category}"][data-element-id="none"]`);
            if (noneElement) {
                noneElement.classList.add('selected');
            }
        }
    });
    
    // Suggérer un nom aléatoire
    const prefixes = ['Cyber', 'Secure', 'Guard', 'Shield', 'Safe', 'Protect', 'Defend', 'Sentinel', 'Watch', 'Alert'];
    const suffixes = ['Bot', 'Guardian', 'Keeper', 'Knight', 'Warrior', 'Sentinel', 'Agent', 'Hero', 'Protector', 'Defender'];
    
    const randomName = `${prefixes[Math.floor(Math.random() * prefixes.length)]}${suffixes[Math.floor(Math.random() * suffixes.length)]}`;
    document.getElementById('mascotName').value = randomName;
    
    // Mettre à jour le score de sécurité
    updateSecurityScore();
    
    // Mettre à jour l'aperçu
    updateMascotPreview();
}

// Fonction pour obtenir une couleur aléatoire
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Fonction pour afficher une notification
function showNotification(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    const toastId = 'toast-' + Date.now();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.setAttribute('id', toastId);
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        animation: true,
        autohide: true,
        delay: 5000
    });
    
    bsToast.show();
    
    // Supprimer le toast après qu'il soit masqué
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Fonction pour obtenir le niveau de sécurité en fonction du score
function getSecurityLevel(score) {
    if (score >= 90) return 'Expert';
    if (score >= 75) return 'Avancé';
    if (score >= 60) return 'Intermédiaire';
    if (score >= 40) return 'Basique';
    return 'Novice';
}

// Fonction pour obtenir le titre de sécurité en fonction du score
function getSecurityTitle(score) {
    if (score >= 90) return 'Expert en cybersécurité';
    if (score >= 75) return 'Gardien avancé';
    if (score >= 60) return 'Protecteur confirmé';
    if (score >= 40) return 'Défenseur en formation';
    return 'Apprenti en sécurité';
}

// Fonction pour obtenir la classe CSS du niveau de sécurité
function getSecurityLevelClass(score) {
    if (score >= 90) return 'bg-success';
    if (score >= 75) return 'bg-primary';
    if (score >= 60) return 'bg-info text-dark';
    if (score >= 40) return 'bg-warning text-dark';
    return 'bg-danger';
}

// Fonction pour obtenir les traits de personnalité
function getPersonalityTraits(personality) {
    const traits = {
        'friendly': ['Accueillant', 'Coopératif', 'Positif', 'Attentif'],
        'serious': ['Méthodique', 'Rigoureux', 'Vigilant', 'Déterminé'],
        'playful': ['Inventif', 'Spontané', 'Optimiste', 'Flexible'],
        'wise': ['Perspicace', 'Réfléchi', 'Prévoyant', 'Expérimenté'],
        'brave': ['Courageux', 'Audacieux', 'Proactif', 'Persévérant']
    };
    
    return traits[personality] || ['Polyvalent', 'Adaptatif'];
}