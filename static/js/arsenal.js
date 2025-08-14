// 🚀 Arsenal WebPanel V5 - JavaScript Principal

class ArsenalWebPanel {
    constructor() {
        this.socket = null;
        this.currentTheme = 'dark';
        this.sidebarCollapsed = false;
        this.init();
    }

    init() {
        console.log('🚀 Arsenal WebPanel V5 - Initialisation');
        
        // DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
    }

    onDOMReady() {
        this.setupEventListeners();
        this.initSocketIO();
        this.loadSavedPreferences();
        this.startBotStatusUpdates();
        this.initAnimations();
    }

    setupEventListeners() {
        // Sidebar Toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
        
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }
        
        if (mobileSidebarToggle) {
            mobileSidebarToggle.addEventListener('click', () => this.toggleMobileSidebar());
        }

        // Theme Toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Fullscreen Toggle
        const fullscreenToggle = document.getElementById('fullscreenToggle');
        if (fullscreenToggle) {
            fullscreenToggle.addEventListener('click', () => this.toggleFullscreen());
        }

        // Notifications Toggle
        const notificationsToggle = document.getElementById('notificationsToggle');
        const notificationsDropdown = document.getElementById('notificationsDropdown');
        
        if (notificationsToggle && notificationsDropdown) {
            notificationsToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                notificationsDropdown.classList.toggle('show');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!notificationsToggle.contains(e.target) && !notificationsDropdown.contains(e.target)) {
                    notificationsDropdown.classList.remove('show');
                }
            });
        }

        // Global Search
        const globalSearch = document.getElementById('globalSearch');
        if (globalSearch) {
            globalSearch.addEventListener('input', (e) => this.handleGlobalSearch(e.target.value));
            globalSearch.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.executeSearch(e.target.value);
                }
            });
        }

        // Flash Messages Close
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('flash-close')) {
                e.target.parentElement.style.animation = 'slideOut 0.3s ease-in forwards';
                setTimeout(() => {
                    e.target.parentElement.remove();
                }, 300);
            }
        });

        // Auto-close flash messages
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(message => {
            setTimeout(() => {
                if (message.parentElement) {
                    message.style.animation = 'slideOut 0.3s ease-in forwards';
                    setTimeout(() => message.remove(), 300);
                }
            }, 5000);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Window resize
        window.addEventListener('resize', () => this.handleResize());
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
            this.sidebarCollapsed = !this.sidebarCollapsed;
            
            // Save preference
            localStorage.setItem('arsenal_sidebar_collapsed', this.sidebarCollapsed.toString());
            
            // Update icon
            const icon = document.querySelector('#sidebarToggle i');
            if (icon) {
                icon.style.transform = this.sidebarCollapsed ? 'rotate(180deg)' : 'rotate(0deg)';
            }
        }
    }

    toggleMobileSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('mobile-open');
        }
    }

    toggleTheme() {
        const body = document.body;
        const themeIcon = document.querySelector('#themeToggle i');
        
        if (this.currentTheme === 'dark') {
            body.setAttribute('data-theme', 'light');
            this.currentTheme = 'light';
            if (themeIcon) themeIcon.className = 'fas fa-sun';
        } else {
            body.setAttribute('data-theme', 'dark');
            this.currentTheme = 'dark';
            if (themeIcon) themeIcon.className = 'fas fa-moon';
        }
        
        localStorage.setItem('arsenal_theme', this.currentTheme);
        this.showNotification('Thème changé vers ' + this.currentTheme, 'info');
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.error('Erreur fullscreen:', err);
                this.showNotification('Impossible de passer en plein écran', 'error');
            });
        } else {
            document.exitFullscreen();
        }
    }

    handleGlobalSearch(query) {
        if (query.length < 2) return;
        
        // Simulation de recherche (à connecter avec le backend)
        const suggestions = this.getSearchSuggestions(query);
        this.displaySearchSuggestions(suggestions);
    }

    getSearchSuggestions(query) {
        // Suggestions de recherche simulées
        const allItems = [
            { type: 'page', title: 'Dashboard', url: '/dashboard', icon: 'fas fa-home' },
            { type: 'page', title: 'Serveurs', url: '/servers', icon: 'fas fa-server' },
            { type: 'page', title: 'Commandes', url: '/commands', icon: 'fas fa-list' },
            { type: 'page', title: 'Musique', url: '/music', icon: 'fas fa-music' },
            { type: 'page', title: 'Modération', url: '/moderation', icon: 'fas fa-gavel' },
            { type: 'page', title: 'Hunt Royal', url: '/hunt-royal', icon: 'fas fa-crown' },
            { type: 'page', title: 'Gaming', url: '/gaming', icon: 'fas fa-dice' },
            { type: 'page', title: 'Social', url: '/social', icon: 'fas fa-users' },
            { type: 'page', title: 'Crypto', url: '/crypto', icon: 'fab fa-bitcoin' },
            { type: 'page', title: 'Logs', url: '/logs', icon: 'fas fa-file-alt' },
            { type: 'page', title: 'Paramètres', url: '/settings', icon: 'fas fa-sliders-h' },
            { type: 'command', title: '/play - Jouer de la musique', icon: 'fas fa-play' },
            { type: 'command', title: '/info - Informations serveur', icon: 'fas fa-info-circle' },
            { type: 'command', title: '/hunt - Système Hunt Royal', icon: 'fas fa-crown' }
        ];
        
        return allItems.filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 8);
    }

    executeSearch(query) {
        console.log('Recherche:', query);
        // Implémenter la logique de recherche
        this.showNotification(`Recherche: "${query}"`, 'info');
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K = Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const search = document.getElementById('globalSearch');
            if (search) search.focus();
        }
        
        // Ctrl/Cmd + B = Toggle sidebar
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            this.toggleSidebar();
        }
        
        // Escape = Close modals/dropdowns
        if (e.key === 'Escape') {
            const dropdown = document.querySelector('.notifications-dropdown.show');
            if (dropdown) dropdown.classList.remove('show');
        }
    }

    handleResize() {
        // Handle responsive behavior
        const sidebar = document.getElementById('sidebar');
        if (window.innerWidth <= 768 && sidebar) {
            sidebar.classList.remove('mobile-open');
        }
    }

    initSocketIO() {
        try {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('🔗 WebSocket connecté');
                this.updateConnectionStatus(true);
            });

            this.socket.on('disconnect', () => {
                console.log('🔌 WebSocket déconnecté');
                this.updateConnectionStatus(false);
            });

            this.socket.on('bot_status_update', (data) => {
                this.updateBotStatus(data);
            });

            this.socket.on('notification', (data) => {
                this.showNotification(data.message, data.type || 'info');
            });

        } catch (error) {
            console.warn('⚠️ SocketIO non disponible:', error);
        }
    }

    updateConnectionStatus(connected) {
        const statusElements = document.querySelectorAll('.connection-status');
        statusElements.forEach(el => {
            el.textContent = connected ? 'Connecté' : 'Déconnecté';
            el.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
        });
    }

    startBotStatusUpdates() {
        this.updateBotStatusFromAPI();
        setInterval(() => this.updateBotStatusFromAPI(), 30000); // Toutes les 30 secondes
    }

    async updateBotStatusFromAPI() {
        try {
            const response = await fetch('/api/bot/status');
            const data = await response.json();
            this.updateBotStatus(data);
        } catch (error) {
            console.warn('⚠️ Erreur récupération status bot:', error);
            this.updateBotStatus({ online: false, status: 'error' });
        }
    }

    updateBotStatus(status) {
        const statusDot = document.getElementById('botStatusDot');
        const statusText = document.getElementById('botStatusText');
        const uptime = document.getElementById('botUptime');

        if (statusDot) {
            statusDot.className = `w-3 h-3 rounded-full ${status.online ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`;
        }

        if (statusText) {
            statusText.textContent = status.online ? 'En ligne' : 'Hors ligne';
        }

        if (uptime && status.uptime) {
            uptime.textContent = status.uptime;
        }

        // Update page title with status
        if (status.online !== this.lastBotStatus) {
            const emoji = status.online ? '🟢' : '🔴';
            document.title = `${emoji} Arsenal WebPanel V5`;
            this.lastBotStatus = status.online;
        }
    }

    loadSavedPreferences() {
        // Load saved theme
        const savedTheme = localStorage.getItem('arsenal_theme');
        if (savedTheme) {
            this.currentTheme = savedTheme;
            document.body.setAttribute('data-theme', savedTheme);
            
            const themeIcon = document.querySelector('#themeToggle i');
            if (themeIcon) {
                themeIcon.className = savedTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
            }
        }

        // Load saved sidebar state
        const savedSidebarState = localStorage.getItem('arsenal_sidebar_collapsed');
        if (savedSidebarState === 'true') {
            this.sidebarCollapsed = true;
            const sidebar = document.getElementById('sidebar');
            if (sidebar) sidebar.classList.add('collapsed');
        }
    }

    initAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                }
            });
        }, observerOptions);

        // Observe cards and elements for animation
        document.querySelectorAll('.card, .nav-item').forEach(el => {
            observer.observe(el);
        });
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.flash-messages') || this.createNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `flash-message flash-${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="${icons[type] || icons.info}"></i>
            <span>${message}</span>
            <button class="flash-close">&times;</button>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOut 0.3s ease-in forwards';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
        
        return notification;
    }

    createNotificationContainer() {
        const container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
        return container;
    }

    // Utility methods
    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    formatTime(date) {
        return new Intl.DateTimeFormat('fr-FR', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }).format(date);
    }

    formatRelativeTime(date) {
        const now = new Date();
        const diff = now - date;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `il y a ${days} jour${days > 1 ? 's' : ''}`;
        if (hours > 0) return `il y a ${hours} heure${hours > 1 ? 's' : ''}`;
        if (minutes > 0) return `il y a ${minutes} minute${minutes > 1 ? 's' : ''}`;
        return `il y a ${seconds} seconde${seconds > 1 ? 's' : ''}`;
    }
}

// Animation CSS additionnelles
const additionalCSS = `
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideOut {
    to {
        opacity: 0;
        transform: translateX(100%);
    }
}
`;

// Inject additional CSS
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);

// Initialize Arsenal WebPanel when DOM is ready
window.ArsenalWebPanel = new ArsenalWebPanel();

// Export for global use
window.arsenal = {
    showNotification: (message, type, duration) => window.ArsenalWebPanel.showNotification(message, type, duration),
    toggleSidebar: () => window.ArsenalWebPanel.toggleSidebar(),
    toggleTheme: () => window.ArsenalWebPanel.toggleTheme(),
    formatBytes: (bytes, decimals) => window.ArsenalWebPanel.formatBytes(bytes, decimals),
    formatTime: (date) => window.ArsenalWebPanel.formatTime(date),
    formatRelativeTime: (date) => window.ArsenalWebPanel.formatRelativeTime(date)
};

console.log('✅ Arsenal WebPanel V5 JavaScript chargé avec succès !');
