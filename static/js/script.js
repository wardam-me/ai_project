/**
 * Fichier JavaScript commun pour toutes les pages
 * Contient des fonctionnalités partagées comme les notifications, la validation de formulaires, etc.
 */

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation de script.js');
    
    // Initialiser les tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialiser les popovers Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Configuration de la date du copyright dans le footer
    const yearEl = document.querySelector('.copyright-year');
    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }
    
    // Gestion des événements pour les formulaires
    setupFormValidation();
    
    // Gestion des événements pour les messages flash
    setupFlashMessages();
});

/**
 * Configure la validation des formulaires
 */
function setupFormValidation() {
    // Récupérer tous les formulaires qui ont besoin de validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Boucler sur les formulaires et empêcher la soumission si non valides
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Configure les messages flash
 */
function setupFlashMessages() {
    // Auto-disparition des messages flash après 5 secondes
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
}

/**
 * Affiche une notification
 * @param {string} message - Le message à afficher
 * @param {string} type - Le type de notification (success, danger, warning, info)
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
 * Copie le texte dans le presse-papiers
 * @param {string} text - Le texte à copier
 * @returns {Promise}
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text)
            .then(() => {
                showNotification('Texte copié dans le presse-papiers', 'success');
                return true;
            })
            .catch(err => {
                console.error('Erreur lors de la copie dans le presse-papiers:', err);
                showNotification('Erreur lors de la copie', 'danger');
                return false;
            });
    } else {
        // Fallback pour les navigateurs plus anciens
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            const msg = successful ? 'successful' : 'unsuccessful';
            console.log('Fallback: Copying text command was ' + msg);
            showNotification('Texte copié dans le presse-papiers', 'success');
            return Promise.resolve(true);
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
            showNotification('Erreur lors de la copie', 'danger');
            return Promise.resolve(false);
        } finally {
            document.body.removeChild(textArea);
        }
    }
}

/**
 * Formate un nombre d'octets en une chaîne lisible par l'homme
 * @param {number} bytes - Le nombre d'octets à formater
 * @param {number} decimals - Le nombre de décimales à afficher
 * @returns {string}
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Formate une date relative (il y a X minutes, etc.)
 * @param {string|Date} date - La date à formater
 * @returns {string}
 */
function formatRelativeTime(date) {
    const now = new Date();
    const inputDate = typeof date === 'string' ? new Date(date) : date;
    const diffMs = now - inputDate;
    const diffSec = Math.floor(diffMs / 1000);
    
    if (diffSec < 60) return 'à l\'instant';
    if (diffSec < 3600) return `il y a ${Math.floor(diffSec / 60)} minutes`;
    if (diffSec < 86400) return `il y a ${Math.floor(diffSec / 3600)} heures`;
    if (diffSec < 2592000) return `il y a ${Math.floor(diffSec / 86400)} jours`;
    if (diffSec < 31536000) return `il y a ${Math.floor(diffSec / 2592000)} mois`;
    return `il y a ${Math.floor(diffSec / 31536000)} ans`;
}

/**
 * Vérifie si une chaîne est un email valide
 * @param {string} email - L'email à vérifier
 * @returns {boolean}
 */
function isValidEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

/**
 * Vérifie si une chaîne est une adresse MAC valide
 * @param {string} mac - L'adresse MAC à vérifier
 * @returns {boolean}
 */
function isValidMacAddress(mac) {
    const re = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
    return re.test(mac);
}

/**
 * Vérifie si une chaîne est une adresse IP valide
 * @param {string} ip - L'adresse IP à vérifier
 * @returns {boolean}
 */
function isValidIpAddress(ip) {
    const re = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return re.test(ip);
}

/**
 * Débounce une fonction pour éviter les appels répétés
 * @param {Function} func - La fonction à débouncer
 * @param {number} wait - Le temps d'attente en ms
 * @returns {Function}
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}