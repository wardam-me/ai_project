/**
 * Classe pour gérer la création et l'édition de mascottes de cybersécurité
 */
class MascotCreator {
    /**
     * Initialise le créateur de mascottes
     */
    constructor() {
        this.currentMascot = {
            id: null,
            name: 'Nouvelle Mascotte',
            base: 'penguin',
            hat: null,
            accessory: null,
            outfit: null,
            background: null,
            colors: {
                primary: '#3498db',
                secondary: '#2ecc71',
                accent: '#e74c3c'
            },
            personality: 'friendly',
            security_score: 50
        };
        
        this.elements = {
            base: [],
            hats: [],
            glasses: [],
            outfits: [],
            backgrounds: []
        };
        
        this.isEditing = false;
    }
    
    /**
     * Charge tous les éléments disponibles depuis l'API
     */
    loadElements() {
        fetch('/api/mascots/elements')
            .then(response => response.json())
            .then(data => {
                this.elements = data;
                this._populateElementOptions();
                this._updatePreview();
            })
            .catch(error => {
                console.error('Erreur lors du chargement des éléments:', error);
                this._showToast('Erreur lors du chargement des éléments', 'error');
            });
    }
    
    /**
     * Remplit les options d'éléments dans l'interface
     */
    _populateElementOptions() {
        // Remplir les options de base
        const baseContainer = document.getElementById('baseOptions');
        if (baseContainer) {
            baseContainer.innerHTML = '';
            this.elements.base.forEach(element => {
                const option = document.createElement('div');
                option.className = 'col';
                option.innerHTML = `
                    <div class="element-option ${this.currentMascot.base === element.id ? 'active' : ''}" data-element-id="${element.id}">
                        <div class="d-flex align-items-center">
                            <div class="element-preview me-2">
                                <i class="fas ${element.icon || 'fa-shapes'}"></i>
                            </div>
                            <div>
                                <span>${element.name}</span>
                            </div>
                        </div>
                    </div>
                `;
                option.querySelector('.element-option').addEventListener('click', () => {
                    this.updateBase(element.id);
                    baseContainer.querySelectorAll('.element-option').forEach(el => el.classList.remove('active'));
                    option.querySelector('.element-option').classList.add('active');
                });
                baseContainer.appendChild(option);
            });
        }
        
        // Remplir les options de chapeaux
        const hatContainer = document.getElementById('hatOptions');
        if (hatContainer) {
            hatContainer.innerHTML = '';
            // Ajouter une option "Aucun"
            const noneOption = document.createElement('div');
            noneOption.className = 'col';
            noneOption.innerHTML = `
                <div class="element-option ${this.currentMascot.hat === null ? 'active' : ''}" data-element-id="none">
                    <div class="d-flex align-items-center">
                        <div class="element-preview me-2">
                            <i class="fas fa-times"></i>
                        </div>
                        <div>
                            <span>Aucun</span>
                        </div>
                    </div>
                </div>
            `;
            noneOption.querySelector('.element-option').addEventListener('click', () => {
                this.updateHat(null);
                hatContainer.querySelectorAll('.element-option').forEach(el => el.classList.remove('active'));
                noneOption.querySelector('.element-option').classList.add('active');
            });
            hatContainer.appendChild(noneOption);
            
            this.elements.hats.forEach(element => {
                const option = document.createElement('div');
                option.className = 'col';
                option.innerHTML = `
                    <div class="element-option ${this.currentMascot.hat === element.id ? 'active' : ''}" data-element-id="${element.id}">
                        <div class="d-flex align-items-center">
                            <div class="element-preview me-2">
                                <i class="fas ${element.icon || 'fa-hat-cowboy'}"></i>
                            </div>
                            <div>
                                <span>${element.name}</span>
                            </div>
                        </div>
                    </div>
                `;
                option.querySelector('.element-option').addEventListener('click', () => {
                    this.updateHat(element.id);
                    hatContainer.querySelectorAll('.element-option').forEach(el => el.classList.remove('active'));
                    option.querySelector('.element-option').classList.add('active');
                });
                hatContainer.appendChild(option);
            });
        }
        
        // Remplir les options de lunettes
        const glassesContainer = document.getElementById('glassesOptions');
        if (glassesContainer) {
            glassesContainer.innerHTML = '';
            // Ajouter une option "Aucun"
            const noneOption = document.createElement('div');
            noneOption.className = 'col';
            noneOption.innerHTML = `
                <div class="element-option ${this.currentMascot.accessory === null ? 'active' : ''}" data-element-id="none">
                    <div class="d-flex align-items-center">
                        <div class="element-preview me-2">
                            <i class="fas fa-times"></i>
                        </div>
                        <div>
                            <span>Aucun</span>
                        </div>
                    </div>
                </div>
            `;
            noneOption.querySelector('.element-option').addEventListener('click', () => {
                this.updateAccessory(null);
                glassesContainer.querySelectorAll('.element-option').forEach(el => el.classList.remove('active'));
                noneOption.querySelector('.element-option').classList.add('active');
            });
            glassesContainer.appendChild(noneOption);
            
            this.elements.glasses.forEach(element => {
                const option = document.createElement('div');
                option.className = 'col';
                option.innerHTML = `
                    <div class="element-option ${this.currentMascot.accessory === element.id ? 'active' : ''}" data-element-id="${element.id}">
                        <div class="d-flex align-items-center">
                            <div class="element-preview me-2">
                                <i class="fas ${element.icon || 'fa-glasses'}"></i>
                            </div>
                            <div>
                                <span>${element.name}</span>
                            </div>
                        </div>
                    </div>
                `;
                option.querySelector('.element-option').addEventListener('click', () => {
                    this.updateAccessory(element.id);
                    glassesContainer.querySelectorAll('.element-option').forEach(el => el.classList.remove('active'));
                    option.querySelector('.element-option').classList.add('active');
                });
                glassesContainer.appendChild(option);
            });
        }
        
        // Remplir les options de tenues
        const outfitContainer = document.getElementById('outfitOptions');
        if (outfitContainer) {
            outfitContainer.innerHTML = '';
            // Ajouter une option "Aucun"
            const noneOption = document.createElement('div');
            noneOption.className = 'col';
            noneOption.innerHTML = `
                <div class="element-option ${this.currentMascot.outfit === null ? 'active' : ''}" data-element-id="none">
                    <div class="d-flex align-items-center">
                        <div class="element-preview me-2">
                            <i class="fas fa-times"></i>
                        </div>
                        <div>
                            <span>Aucun</span>
                        </div>
                    </div>
                </div>
            `;
            noneOption.querySelector('.element-option').addEventListener('click', () => {
                this.updateOutfit(null);
                outfitContainer.querySelectorAll('.element-option').forEach(el => el.classList.remove('active'));
                noneOption.querySelector('.element-option').classList.add('active');
            });
            outfitContainer.appendChild(noneOption);
            
            this.elements.outfits.forEach(element => {
                const option = document.createElement('div');
                option.className = 'col';
                option.innerHTML = `
                    <div class="element-option ${this.currentMascot.outfit === element.id ? 'active' : ''}" data-element-id="${element.id}">
                        <div class="d-flex align-items-center">
                            <div class="element-preview me-2">
                                <i class="fas ${element.icon || 'fa-tshirt'}"></i>
                            </div>
                            <div>
                                <span>${element.name}</span>
                            </div>
                        </div>
                    </div>
                `;
                option.querySelector('.element-option').addEventListener('click', () => {
                    this.updateOutfit(element.id);
                    outfitContainer.querySelectorAll('.element-option').forEach(el => el.classList.remove('active'));
                    option.querySelector('.element-option').classList.add('active');
                });
                outfitContainer.appendChild(option);
            });
        }
        
        // Remplir les options d'arrière-plans
        const backgroundContainer = document.getElementById('backgroundOptions');
        if (backgroundContainer) {
            backgroundContainer.innerHTML = '';
            // Ajouter une option "Aucun"
            const noneOption = document.createElement('div');
            noneOption.className = 'col';
            noneOption.innerHTML = `
                <div class="element-option ${this.currentMascot.background === null ? 'active' : ''}" data-element-id="none">
                    <div class="d-flex align-items-center">
                        <div class="element-preview me-2">
                            <i class="fas fa-times"></i>
                        </div>
                        <div>
                            <span>Aucun</span>
                        </div>
                    </div>
                </div>
            `;
            noneOption.querySelector('.element-option').addEventListener('click', () => {
                this.updateBackground(null);
                backgroundContainer.querySelectorAll('.element-option').forEach(el => el.classList.remove('active'));
                noneOption.querySelector('.element-option').classList.add('active');
            });
            backgroundContainer.appendChild(noneOption);
            
            this.elements.backgrounds.forEach(element => {
                const option = document.createElement('div');
                option.className = 'col';
                option.innerHTML = `
                    <div class="element-option ${this.currentMascot.background === element.id ? 'active' : ''}" data-element-id="${element.id}">
                        <div class="d-flex align-items-center">
                            <div class="element-preview me-2">
                                <i class="fas ${element.icon || 'fa-image'}"></i>
                            </div>
                            <div>
                                <span>${element.name}</span>
                            </div>
                        </div>
                    </div>
                `;
                option.querySelector('.element-option').addEventListener('click', () => {
                    this.updateBackground(element.id);
                    backgroundContainer.querySelectorAll('.element-option').forEach(el => el.classList.remove('active'));
                    option.querySelector('.element-option').classList.add('active');
                });
                backgroundContainer.appendChild(option);
            });
        }
    }
    
    /**
     * Met à jour la prévisualisation de la mascotte
     */
    _updatePreview() {
        const previewContainer = document.getElementById('mascotPreview');
        if (previewContainer) {
            previewContainer.innerHTML = '<div class="text-center p-5">Chargement de la prévisualisation...</div>';
            
            // Créer un SVG temporaire pour la prévisualisation
            // Dans une implémentation réelle, nous appellerions une API pour générer le SVG
            const svgPreview = this._generateTempSvg();
            previewContainer.innerHTML = svgPreview;
        }
    }
    
    /**
     * Génère un SVG temporaire pour la prévisualisation
     * Dans une implémentation réelle, cette fonction appelerait une API
     */
    _generateTempSvg() {
        // Couleurs
        const primary = this.currentMascot.colors.primary;
        const secondary = this.currentMascot.colors.secondary;
        const accent = this.currentMascot.colors.accent;
        
        // Base simple (cercle avec visage)
        let svgContent = `
            <svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                <!-- Fond -->
                <circle cx="100" cy="100" r="80" fill="${primary}" />
                
                <!-- Détails -->
                <circle cx="100" cy="110" r="60" fill="${secondary}" />
                
                <!-- Yeux -->
                <circle cx="70" cy="80" r="10" fill="white" />
                <circle cx="130" cy="80" r="10" fill="white" />
                <circle cx="70" cy="80" r="5" fill="#222" />
                <circle cx="130" cy="80" r="5" fill="#222" />
                
                <!-- Sourire -->
                <path d="M70 120 Q100 140 130 120" stroke="#222" stroke-width="3" fill="none" />
                
                <!-- Indicateur de niveau de sécurité -->
                <rect x="75" y="150" width="50" height="10" rx="5" ry="5" fill="${accent}" />
                <text x="100" y="170" text-anchor="middle" font-size="12" fill="#222">Niveau ${this.currentMascot.security_score}</text>
            </svg>
        `;
        
        return svgContent;
    }
    
    /**
     * Affiche une notification Toast
     */
    _showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center ${type === 'error' ? 'bg-danger' : 'bg-primary'} text-white border-0`;
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
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 3000
        });
        
        bsToast.show();
        
        // Supprimer le toast du DOM après sa disparition
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    /**
     * Met à jour le type de base de la mascotte
     */
    updateBase(baseId) {
        this.currentMascot.base = baseId;
        this._updatePreview();
    }
    
    /**
     * Met à jour le chapeau de la mascotte
     */
    updateHat(hatId) {
        this.currentMascot.hat = hatId;
        this._updatePreview();
    }
    
    /**
     * Met à jour l'accessoire de la mascotte
     */
    updateAccessory(accessoryId) {
        this.currentMascot.accessory = accessoryId;
        this._updatePreview();
    }
    
    /**
     * Met à jour la tenue de la mascotte
     */
    updateOutfit(outfitId) {
        this.currentMascot.outfit = outfitId;
        this._updatePreview();
    }
    
    /**
     * Met à jour l'arrière-plan de la mascotte
     */
    updateBackground(backgroundId) {
        this.currentMascot.background = backgroundId;
        this._updatePreview();
    }
    
    /**
     * Met à jour la couleur de la mascotte
     */
    updateColor(colorType, colorValue) {
        if (colorType in this.currentMascot.colors) {
            this.currentMascot.colors[colorType] = colorValue;
            this._updatePreview();
        }
    }
    
    /**
     * Met à jour le nom de la mascotte
     */
    updateName(name) {
        this.currentMascot.name = name;
    }
    
    /**
     * Met à jour la personnalité de la mascotte
     */
    updatePersonality(personality) {
        this.currentMascot.personality = personality;
    }
    
    /**
     * Met à jour le score de sécurité de la mascotte
     */
    updateSecurityScore(score) {
        this.currentMascot.security_score = score;
        this._updatePreview();
    }
    
    /**
     * Sauvegarde la mascotte actuelle
     */
    saveMascot() {
        const url = this.isEditing && this.currentMascot.id ? 
                   `/api/mascots/${this.currentMascot.id}` : 
                   '/api/mascots';
        
        const method = this.isEditing && this.currentMascot.id ? 'PUT' : 'POST';
        
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(this.currentMascot)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this._showToast(this.isEditing ? 'Mascotte mise à jour avec succès' : 'Mascotte créée avec succès', 'success');
                // Rediriger vers la galerie après quelques secondes
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                this._showToast('Erreur : ' + (data.error || 'Échec de l\'opération'), 'error');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la sauvegarde:', error);
            this._showToast('Erreur de connexion', 'error');
        });
    }
    
    /**
     * Charge les données d'une mascotte existante pour l'édition
     */
    editMascot(mascotId) {
        fetch(`/api/mascots/${mascotId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.currentMascot = data.mascot;
                    this.isEditing = true;
                    
                    // Mettre à jour l'interface
                    document.getElementById('mascotName').value = this.currentMascot.name;
                    document.getElementById('personalityType').value = this.currentMascot.personality;
                    document.getElementById('securityScore').value = this.currentMascot.security_score;
                    document.getElementById('securityScoreValue').textContent = this.currentMascot.security_score;
                    
                    // Mettre à jour les couleurs
                    document.getElementById('primaryColorPicker').value = this.currentMascot.colors.primary;
                    document.getElementById('primaryColorValue').textContent = this.currentMascot.colors.primary;
                    
                    document.getElementById('secondaryColorPicker').value = this.currentMascot.colors.secondary;
                    document.getElementById('secondaryColorValue').textContent = this.currentMascot.colors.secondary;
                    
                    document.getElementById('accentColorPicker').value = this.currentMascot.colors.accent;
                    document.getElementById('accentColorValue').textContent = this.currentMascot.colors.accent;
                    
                    // Mettre à jour les options sélectionnées
                    this._populateElementOptions();
                    this._updatePreview();
                } else {
                    this._showToast('Erreur : ' + (data.error || 'Mascotte non trouvée'), 'error');
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement de la mascotte:', error);
                this._showToast('Erreur de connexion', 'error');
            });
    }
    
    /**
     * Supprime une mascotte
     */
    deleteMascot(mascotId) {
        fetch(`/api/mascots/${mascotId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this._showToast('Mascotte supprimée avec succès', 'success');
                // Recharger la page après quelques secondes
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                this._showToast('Erreur : ' + (data.error || 'Échec de la suppression'), 'error');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la suppression:', error);
            this._showToast('Erreur de connexion', 'error');
        });
    }
    
    /**
     * Charge l'histoire d'une mascotte et l'affiche dans un modal
     */
    loadMascotStory(mascotId) {
        fetch(`/api/mascots/story/${mascotId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const storyModal = document.getElementById('mascotStoryModal');
                    const storyContent = document.getElementById('mascotStoryContent');
                    const modalTitle = document.getElementById('mascotStoryModalLabel');
                    const modalPreview = document.getElementById('modalMascotPreview');
                    
                    // Charger l'image de la mascotte
                    modalPreview.innerHTML = `<img src="/api/mascots/generate-svg/${mascotId}" alt="Mascotte" class="img-fluid" style="max-height: 150px;">`;
                    
                    // Charger les données dans le modal
                    storyContent.innerHTML = data.story;
                    
                    // Obtenir les détails de la mascotte pour le titre
                    fetch(`/api/mascots/${mascotId}`)
                        .then(response => response.json())
                        .then(mascotData => {
                            if (mascotData.success) {
                                modalTitle.textContent = `Histoire de ${mascotData.mascot.name}`;
                            }
                        });
                    
                    // Afficher le modal
                    const bsModal = new bootstrap.Modal(storyModal);
                    bsModal.show();
                } else {
                    this._showToast('Erreur : ' + (data.error || 'Histoire non disponible'), 'error');
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement de l\'histoire:', error);
                this._showToast('Erreur de connexion', 'error');
            });
    }
    
    /**
     * Génère une mascotte aléatoire
     */
    randomizeMascot() {
        fetch('/api/mascots/random')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.currentMascot = {...this.currentMascot, ...data.mascot};
                    
                    // Mettre à jour l'interface
                    document.getElementById('mascotName').value = this.currentMascot.name;
                    document.getElementById('personalityType').value = this.currentMascot.personality;
                    document.getElementById('securityScore').value = this.currentMascot.security_score;
                    document.getElementById('securityScoreValue').textContent = this.currentMascot.security_score;
                    
                    // Mettre à jour les couleurs
                    document.getElementById('primaryColorPicker').value = this.currentMascot.colors.primary;
                    document.getElementById('primaryColorValue').textContent = this.currentMascot.colors.primary;
                    
                    document.getElementById('secondaryColorPicker').value = this.currentMascot.colors.secondary;
                    document.getElementById('secondaryColorValue').textContent = this.currentMascot.colors.secondary;
                    
                    document.getElementById('accentColorPicker').value = this.currentMascot.colors.accent;
                    document.getElementById('accentColorValue').textContent = this.currentMascot.colors.accent;
                    
                    // Mettre à jour les options sélectionnées
                    this._populateElementOptions();
                    this._updatePreview();
                    
                    this._showToast('Mascotte aléatoire générée', 'info');
                } else {
                    this._showToast('Erreur : ' + (data.error || 'Échec de la génération aléatoire'), 'error');
                }
            })
            .catch(error => {
                console.error('Erreur lors de la génération aléatoire:', error);
                this._showToast('Erreur de connexion', 'error');
            });
    }
    
    /**
     * Réinitialise la mascotte actuelle
     */
    resetMascot() {
        if (this.isEditing && this.currentMascot.id) {
            // Si on édite une mascotte existante, recharger ses données
            this.editMascot(this.currentMascot.id);
        } else {
            // Sinon, réinitialiser à une mascotte par défaut
            this.currentMascot = {
                id: null,
                name: 'Nouvelle Mascotte',
                base: 'penguin',
                hat: null,
                accessory: null,
                outfit: null,
                background: null,
                colors: {
                    primary: '#3498db',
                    secondary: '#2ecc71',
                    accent: '#e74c3c'
                },
                personality: 'friendly',
                security_score: 50
            };
            
            // Mettre à jour l'interface
            document.getElementById('mascotName').value = this.currentMascot.name;
            document.getElementById('personalityType').value = this.currentMascot.personality;
            document.getElementById('securityScore').value = this.currentMascot.security_score;
            document.getElementById('securityScoreValue').textContent = this.currentMascot.security_score;
            
            // Mettre à jour les couleurs
            document.getElementById('primaryColorPicker').value = this.currentMascot.colors.primary;
            document.getElementById('primaryColorValue').textContent = this.currentMascot.colors.primary;
            
            document.getElementById('secondaryColorPicker').value = this.currentMascot.colors.secondary;
            document.getElementById('secondaryColorValue').textContent = this.currentMascot.colors.secondary;
            
            document.getElementById('accentColorPicker').value = this.currentMascot.colors.accent;
            document.getElementById('accentColorValue').textContent = this.currentMascot.colors.accent;
            
            // Mettre à jour les options sélectionnées
            this._populateElementOptions();
            this._updatePreview();
        }
        
        this._showToast('Mascotte réinitialisée', 'info');
    }
}