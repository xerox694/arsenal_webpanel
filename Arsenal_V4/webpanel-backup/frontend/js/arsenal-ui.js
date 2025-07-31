/**
 * Arsenal V4 WebPanel - Utilitaires Interface
 * Fonctions d'amélioration UX/UI
 */

class ArsenalUI {
    constructor() {
        this.notifications = [];
        this.themes = {
            arsenal: { primary: '#00fff7', secondary: '#0088ff' },
            matrix: { primary: '#00ff00', secondary: '#66ff66' },
            galaxy: { primary: '#9d4edd', secondary: '#c77dff' },
            fire: { primary: '#ff6b35', secondary: '#f7931e' },
            ocean: { primary: '#0077be', secondary: '#00a8cc' },
            sunset: { primary: '#ff6b6b', secondary: '#ffa726' },
            neon: { primary: '#ff1744', secondary: '#e91e63' },
            cyber: { primary: '#673ab7', secondary: '#3f51b5' }
        };
        this.currentTheme = 'arsenal';
        this.init();
    }

    init() {
        this.setupGlobalFunctions();
        this.loadUserPreferences();
        this.setupKeyboardShortcuts();
        console.log('✅ Arsenal UI - Initialisé');
    }

    // ==================== NOTIFICATIONS ====================
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `arsenal-notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; cursor: pointer; margin-left: auto;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animer l'apparition
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto-suppression
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
        
        return notification;
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }

    // ==================== THÈMES ====================
    changeTheme(themeName) {
        if (!this.themes[themeName]) return;
        
        const theme = this.themes[themeName];
        const root = document.documentElement;
        
        root.style.setProperty('--primary-color', theme.primary);
        root.style.setProperty('--secondary-color', theme.secondary);
        root.style.setProperty('--accent-color', theme.primary);
        
        // Mettre à jour les sélecteurs de thème
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.toggle('active', option.dataset.theme === themeName);
        });
        
        this.currentTheme = themeName;
        this.saveUserPreferences();
        this.showNotification(`Thème ${themeName} appliqué`, 'success');
    }

    // ==================== GESTION SIDEBAR ====================
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        
        if (sidebar && mainContent) {
            sidebar.classList.toggle('open');
            mainContent.classList.toggle('sidebar-open');
        }
    }

    // ==================== GESTION PAGES ====================
    showPage(pageId, menuElement = null) {
        // Cacher toutes les pages
        document.querySelectorAll('.content-page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Afficher la page demandée
        const targetPage = document.getElementById(pageId);
        if (targetPage) {
            targetPage.classList.add('active');
        }
        
        // Mettre à jour le menu
        if (menuElement) {
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('active');
            });
            menuElement.classList.add('active');
        }
        
        // Charger les données de la page
        this.loadPageData(pageId);
    }

    async loadPageData(pageId) {
        if (window.arsenalAPI && window.arsenalAPI.currentServer) {
            switch (pageId) {
                case 'dashboard':
                    await window.arsenalAPI.loadDashboardData();
                    break;
                case 'economy':
                    await window.arsenalAPI.loadEconomyData(window.arsenalAPI.currentServer);
                    break;
                case 'moderation':
                    await window.arsenalAPI.loadModerationData(window.arsenalAPI.currentServer);
                    break;
                case 'music':
                    await window.arsenalAPI.loadMusicData(window.arsenalAPI.currentServer);
                    break;
                case 'games':
                    await window.arsenalAPI.loadGamingData(window.arsenalAPI.currentServer);
                    break;
                case 'analytics':
                    await window.arsenalAPI.loadAnalyticsData(window.arsenalAPI.currentServer);
                    break;
            }
        }
    }

    // ==================== DROPDOWN UTILISATEUR ====================
    toggleUserDropdown() {
        const dropdown = document.getElementById('userDropdown');
        const chevron = document.getElementById('userDropdownChevron');
        
        if (dropdown) {
            dropdown.classList.toggle('show');
            if (chevron) {
                chevron.style.transform = dropdown.classList.contains('show') 
                    ? 'rotate(180deg)' : 'rotate(0deg)';
            }
        }
    }

    showThemeSelector() {
        const selector = document.getElementById('themeSelector');
        if (selector) {
            selector.style.display = selector.style.display === 'none' ? 'block' : 'none';
        }
    }

    hideThemeSelector() {
        const selector = document.getElementById('themeSelector');
        if (selector) {
            selector.style.display = 'none';
        }
    }

    // ==================== PRÉFÉRENCES UTILISATEUR ====================
    saveUserPreferences() {
        const preferences = {
            theme: this.currentTheme,
            sidebarOpen: document.getElementById('sidebar')?.classList.contains('open') || false
        };
        localStorage.setItem('arsenal_preferences', JSON.stringify(preferences));
    }

    loadUserPreferences() {
        try {
            const saved = localStorage.getItem('arsenal_preferences');
            if (saved) {
                const preferences = JSON.parse(saved);
                if (preferences.theme) {
                    this.changeTheme(preferences.theme);
                }
                if (preferences.sidebarOpen) {
                    this.toggleSidebar();
                }
            }
        } catch (error) {
            console.warn('Impossible de charger les préférences:', error);
        }
    }

    // ==================== RACCOURCIS CLAVIER ====================
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl + / pour ouvrir/fermer la sidebar
            if (e.ctrlKey && e.key === '/') {
                e.preventDefault();
                this.toggleSidebar();
            }
            
            // Ctrl + 1-9 pour naviguer dans le menu
            if (e.ctrlKey && e.key >= '1' && e.key <= '9') {
                e.preventDefault();
                const menuItems = document.querySelectorAll('.menu-item');
                const index = parseInt(e.key) - 1;
                if (menuItems[index]) {
                    menuItems[index].click();
                }
            }
            
            // Échap pour fermer les dropdowns
            if (e.key === 'Escape') {
                document.querySelectorAll('.user-dropdown.show').forEach(dropdown => {
                    dropdown.classList.remove('show');
                });
                this.hideThemeSelector();
            }
        });
    }

    // ==================== FONCTIONS GLOBALES ====================
    setupGlobalFunctions() {
        // Rendre les fonctions disponibles globalement
        window.showPage = this.showPage.bind(this);
        window.toggleSidebar = this.toggleSidebar.bind(this);
        window.toggleUserDropdown = this.toggleUserDropdown.bind(this);
        window.changeTheme = this.changeTheme.bind(this);
        window.showThemeSelector = this.showThemeSelector.bind(this);
        window.hideThemeSelector = this.hideThemeSelector.bind(this);
        window.arsenalNotify = this.showNotification.bind(this);
    }

    // ==================== UTILITAIRES ====================
    formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'À l\'instant';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
        return `${Math.floor(diff / 86400000)}j`;
    }

    showLoading(element) {
        if (element) {
            element.innerHTML = '<div class="arsenal-loading"></div>';
        }
    }

    hideLoading(element, content = '') {
        if (element) {
            element.innerHTML = content;
        }
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    window.arsenalUI = new ArsenalUI();
    console.log('🎨 Arsenal UI - Prêt !');
});

// Fermer les dropdowns en cliquant à l'extérieur
document.addEventListener('click', (e) => {
    if (!e.target.closest('.user-info')) {
        document.querySelectorAll('.user-dropdown.show').forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    }
});

console.log('🎨 Arsenal UI Utils - Chargé !');
