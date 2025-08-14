/**
 * Arsenal V4 WebPanel - API JavaScript
 * Connexion interface frontend avec backend Flask
 * Toutes les 6 phases intégrées
 */

class ArsenalAPI {
    constructor() {
        this.baseURL = window.location.origin;
        this.currentServer = null;
        this.isLoggedIn = false;
        this.user = null;
        this.init();
    }

    async init() {
        console.log('🚀 Arsenal WebPanel API - Initialisation...');
        await this.checkAuth();
        await this.loadUserServers();
        await this.startRealTimeUpdates();
        this.setupEventListeners();
    }

    // ==================== AUTH & USER ====================
    async checkAuth() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/user`);
            if (response.ok) {
                this.user = await response.json();
                this.isLoggedIn = true;
                this.updateUserUI();
                console.log('✅ Utilisateur connecté:', this.user);
            } else {
                this.redirectToLogin();
            }
        } catch (error) {
            console.error('❌ Erreur auth:', error);
            this.redirectToLogin();
        }
    }

    updateUserUI() {
        if (this.user) {
            document.getElementById('userDisplayName').textContent = this.user.username || 'Utilisateur';
            document.getElementById('userDisplayRole').textContent = this.user.role || 'Membre';
            document.getElementById('dropdownUserName').textContent = this.user.username || 'Utilisateur';
            document.getElementById('dropdownUserRole').textContent = this.user.role || 'Membre';
        }
    }

    redirectToLogin() {
        window.location.href = '/auth/login';
    }

    // ==================== SERVEURS ====================
    async loadUserServers() {
        try {
            const response = await fetch(`${this.baseURL}/api/servers`);
            const servers = await response.json();
            
            this.updateServersList(servers);
            this.updateMainServersList(servers);
            
            if (servers.length > 0 && !this.currentServer) {
                this.currentServer = servers[0].id;
                this.selectServer(servers[0]);
            }
        } catch (error) {
            console.error('❌ Erreur chargement serveurs:', error);
        }
    }

    updateServersList(servers) {
        const serversList = document.getElementById('servers-list');
        if (!serversList) return;

        serversList.innerHTML = '';
        
        servers.forEach(server => {
            const serverItem = document.createElement('div');
            serverItem.className = 'server-item';
            serverItem.onclick = () => this.selectServer(server);
            
            serverItem.innerHTML = `
                <div class="server-icon">${server.name.charAt(0).toUpperCase()}</div>
                <div class="server-info">
                    <div class="server-name">${server.name}</div>
                    <div class="server-members">${server.member_count || 0} membres</div>
                </div>
                <div class="server-status ${server.bot_connected ? 'online' : 'offline'}"></div>
            `;
            
            serversList.appendChild(serverItem);
        });
    }

    updateMainServersList(servers) {
        const mainServersList = document.getElementById('main-servers-list');
        if (!mainServersList) return;

        mainServersList.innerHTML = '';
        
        servers.forEach(server => {
            const serverCard = document.createElement('div');
            serverCard.className = 'server-card';
            serverCard.onclick = () => this.selectServerConfig(server);
            
            serverCard.innerHTML = `
                <div class="server-card-header">
                    <div class="server-card-icon">${server.name.charAt(0).toUpperCase()}</div>
                    <div class="server-card-info">
                        <h3>${server.name}</h3>
                        <p>${server.member_count || 0} membres</p>
                    </div>
                </div>
                <div class="server-card-stats">
                    <div class="server-stat">
                        <div class="server-stat-value">${server.bot_connected ? 'ON' : 'OFF'}</div>
                        <div class="server-stat-label">Bot</div>
                    </div>
                    <div class="server-stat">
                        <div class="server-stat-value">${server.commands_count || 0}</div>
                        <div class="server-stat-label">Commandes</div>
                    </div>
                    <div class="server-stat">
                        <div class="server-stat-value">${server.music_active ? 'ON' : 'OFF'}</div>
                        <div class="server-stat-label">Musique</div>
                    </div>
                </div>
            `;
            
            mainServersList.appendChild(serverCard);
        });
    }

    selectServer(server) {
        this.currentServer = server.id;
        
        // Mettre à jour l'UI
        document.querySelectorAll('.server-item').forEach(item => {
            item.classList.remove('selected');
        });
        event.currentTarget.classList.add('selected');
        
        // Recharger les données
        this.loadDashboardData();
        this.loadServerData(server.id);
    }

    selectServerConfig(server) {
        this.currentServer = server.id;
        
        // Afficher le panel de configuration
        const configPanel = document.getElementById('server-config-panel');
        if (configPanel) {
            configPanel.style.display = 'block';
            this.loadServerConfig(server.id);
        }
    }

    // ==================== DASHBOARD ====================
    async loadDashboardData() {
        try {
            await Promise.all([
                this.loadBotStats(),
                this.loadActivity(),
                this.loadPerformance()
            ]);
        } catch (error) {
            console.error('❌ Erreur dashboard:', error);
        }
    }

    async loadBotStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/stats/bot`);
            const stats = await response.json();
            
            document.getElementById('servers-count').textContent = stats.servers_count || 0;
            document.getElementById('users-count').textContent = stats.users_count || 0;
            document.getElementById('commands-count').textContent = stats.commands_count || 0;
            
            // Status du bot
            const statusDot = document.getElementById('bot-status');
            const statusText = document.getElementById('bot-text');
            if (stats.bot_online) {
                statusDot.className = 'status-dot online';
                statusText.textContent = 'En ligne';
            } else {
                statusDot.className = 'status-dot offline';
                statusText.textContent = 'Hors ligne';
            }
            
            document.getElementById('last-online').textContent = stats.last_online || 'Inconnue';
            
        } catch (error) {
            console.error('❌ Erreur stats bot:', error);
        }
    }

    async loadActivity() {
        try {
            const response = await fetch(`${this.baseURL}/api/activity/recent`);
            const activities = await response.json();
            
            const activityFeed = document.getElementById('activity-feed');
            if (!activityFeed) return;
            
            activityFeed.innerHTML = '';
            
            activities.forEach(activity => {
                const item = document.createElement('div');
                item.className = 'activity-item';
                item.innerHTML = `
                    <div class="activity-icon">
                        <i class="fas ${this.getActivityIcon(activity.type)}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-text">${activity.description}</div>
                        <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
                    </div>
                `;
                activityFeed.appendChild(item);
            });
            
        } catch (error) {
            console.error('❌ Erreur activité:', error);
        }
    }

    async loadPerformance() {
        try {
            const response = await fetch(`${this.baseURL}/api/performance`);
            const perf = await response.json();
            
            // Mettre à jour les métriques de performance
            // À implémenter selon vos besoins
            
        } catch (error) {
            console.error('❌ Erreur performance:', error);
        }
    }

    // ==================== PHASE 2: ÉCONOMIE ====================
    async loadEconomyData(serverId) {
        try {
            const [users, config, transactions] = await Promise.all([
                fetch(`${this.baseURL}/api/economy/users/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/economy/config/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/economy/transactions/${serverId}`).then(r => r.json())
            ]);
            
            this.updateEconomyUI(users, config, transactions);
            
        } catch (error) {
            console.error('❌ Erreur économie:', error);
        }
    }

    updateEconomyUI(users, config, transactions) {
        // Mettre à jour l'interface économie
        // À implémenter selon l'interface
    }

    // ==================== PHASE 3: MODÉRATION ====================
    async loadModerationData(serverId) {
        try {
            const [logs, config, automod] = await Promise.all([
                fetch(`${this.baseURL}/api/moderation/logs/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/moderation/config/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/moderation/automod/${serverId}`).then(r => r.json())
            ]);
            
            this.updateModerationUI(logs, config, automod);
            
        } catch (error) {
            console.error('❌ Erreur modération:', error);
        }
    }

    updateModerationUI(logs, config, automod) {
        // Mettre à jour l'interface modération
        const moderationActions = document.getElementById('moderationActions');
        if (moderationActions && logs.length > 0) {
            moderationActions.innerHTML = '';
            logs.forEach(log => {
                const item = document.createElement('div');
                item.className = 'activity-item';
                item.innerHTML = `
                    <div class="activity-icon">
                        <i class="fas ${this.getModerationIcon(log.action)}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-text">${log.action}: ${log.target_user}</div>
                        <div class="activity-time">${this.formatTime(log.timestamp)}</div>
                    </div>
                `;
                moderationActions.appendChild(item);
            });
        }
    }

    // ==================== PHASE 4: MUSIQUE ====================
    async loadMusicData(serverId) {
        try {
            const [queue, status, config] = await Promise.all([
                fetch(`${this.baseURL}/api/music/queue/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/music/status/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/music/config/${serverId}`).then(r => r.json())
            ]);
            
            this.updateMusicUI(queue, status, config);
            
        } catch (error) {
            console.error('❌ Erreur musique:', error);
        }
    }

    updateMusicUI(queue, status, config) {
        // Mettre à jour l'interface musique
        const musicQueue = document.getElementById('musicQueue');
        if (musicQueue) {
            if (queue.length > 0) {
                musicQueue.innerHTML = '';
                queue.forEach(song => {
                    const item = document.createElement('div');
                    item.className = 'activity-item';
                    item.innerHTML = `
                        <div class="activity-icon">
                            <i class="fas fa-music"></i>
                        </div>
                        <div class="activity-content">
                            <div class="activity-text">${song.title}</div>
                            <div class="activity-time">${song.duration}</div>
                        </div>
                    `;
                    musicQueue.appendChild(item);
                });
            } else {
                musicQueue.innerHTML = '<div style="text-align: center; color: #888; padding: 20px;">File d\'attente vide</div>';
            }
        }
    }

    // ==================== PHASE 5: GAMING ====================
    async loadGamingData(serverId) {
        try {
            const [levels, rewards, minigames] = await Promise.all([
                fetch(`${this.baseURL}/api/gaming/levels/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/gaming/rewards/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/gaming/minigames/${serverId}`).then(r => r.json())
            ]);
            
            this.updateGamingUI(levels, rewards, minigames);
            
        } catch (error) {
            console.error('❌ Erreur gaming:', error);
        }
    }

    updateGamingUI(levels, rewards, minigames) {
        // Mettre à jour l'interface gaming
    }

    // ==================== PHASE 6: ANALYTICS ====================
    async loadAnalyticsData(serverId) {
        try {
            const [metrics, users, events] = await Promise.all([
                fetch(`${this.baseURL}/api/analytics/metrics/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/analytics/users/${serverId}`).then(r => r.json()),
                fetch(`${this.baseURL}/api/analytics/events/${serverId}`).then(r => r.json())
            ]);
            
            this.updateAnalyticsUI(metrics, users, events);
            
        } catch (error) {
            console.error('❌ Erreur analytics:', error);
        }
    }

    updateAnalyticsUI(metrics, users, events) {
        // Mettre à jour l'interface analytics
        const activeUsers = document.getElementById('active-users');
        if (activeUsers) {
            activeUsers.textContent = users.active_24h || 0;
        }
        
        const usersTrend = document.getElementById('users-trend');
        if (usersTrend) {
            const trend = users.trend > 0 ? 'arrow-up' : 'arrow-down';
            const color = users.trend > 0 ? '#00ff88' : '#ff4444';
            usersTrend.innerHTML = `<i class="fas fa-${trend}" style="color: ${color};"></i> ${Math.abs(users.trend)}% vs hier`;
        }
    }

    // ==================== CONFIGURATION SERVEUR ====================
    async loadServerConfig(serverId) {
        try {
            const config = await fetch(`${this.baseURL}/api/server/config/${serverId}`).then(r => r.json());
            this.updateServerConfigUI(config);
        } catch (error) {
            console.error('❌ Erreur config serveur:', error);
        }
    }

    updateServerConfigUI(config) {
        // Mettre à jour l'interface de configuration
    }

    // ==================== TEMPS RÉEL ====================
    startRealTimeUpdates() {
        // Mise à jour toutes les 30 secondes
        setInterval(() => {
            if (this.currentServer) {
                this.loadDashboardData();
                this.loadServerData(this.currentServer);
            }
        }, 30000);
    }

    async loadServerData(serverId) {
        await Promise.all([
            this.loadEconomyData(serverId),
            this.loadModerationData(serverId),
            this.loadMusicData(serverId),
            this.loadGamingData(serverId),
            this.loadAnalyticsData(serverId)
        ]);
    }

    // ==================== UTILITAIRES ====================
    getActivityIcon(type) {
        const icons = {
            'join': 'fa-user-plus',
            'leave': 'fa-user-minus',
            'command': 'fa-terminal',
            'music': 'fa-music',
            'moderation': 'fa-shield-alt',
            'economy': 'fa-coins',
            'gaming': 'fa-gamepad'
        };
        return icons[type] || 'fa-info-circle';
    }

    getModerationIcon(action) {
        const icons = {
            'ban': 'fa-ban',
            'kick': 'fa-user-times',
            'mute': 'fa-volume-mute',
            'warn': 'fa-exclamation-triangle'
        };
        return icons[action] || 'fa-shield-alt';
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

    setupEventListeners() {
        // Event listeners pour l'interface
        document.addEventListener('DOMContentLoaded', () => {
            console.log('✅ Arsenal WebPanel - Interface chargée');
        });
    }

    // ==================== ONGLETS DÉTAILLÉS ====================
    async showTab(tabName) {
        console.log(`🔄 Chargement onglet: ${tabName}`);
        
        // Mettre à jour l'interface
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeTab = document.querySelector(`[onclick="window.arsenalAPI.showTab('${tabName}')"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        // Afficher le loading
        const contentArea = document.getElementById('tab-content');
        if (contentArea) {
            contentArea.innerHTML = '<div class="loading-spinner">Chargement...</div>';
        }
        
        // Charger le contenu selon l'onglet
        try {
            let content = '';
            switch (tabName) {
                case 'bot':
                    content = await this.loadBotDetailed();
                    break;
                case 'serveurs':
                    content = await this.loadServersDetailed();
                    break;
                case 'utilisateurs':
                    content = await this.loadUsersDetailed();
                    break;
                case 'commandes':
                    content = await this.loadCommandsDetailed();
                    break;
                default:
                    content = '<div class="error">Onglet non trouvé</div>';
            }
            
            if (contentArea) {
                contentArea.innerHTML = content;
            }
            
            console.log(`✅ Onglet ${tabName} chargé`);
        } catch (error) {
            console.error(`❌ Erreur chargement onglet ${tabName}:`, error);
            if (contentArea) {
                contentArea.innerHTML = '<div class="error">Erreur de chargement</div>';
            }
        }
    }
    
    async loadBotDetailed() {
        const response = await fetch(`${this.baseURL}/api/bot/detailed`);
        const data = await response.json();
        
        return `
            <div class="detailed-content">
                <h3>📊 Informations détaillées du Bot</h3>
                
                <div class="info-grid">
                    <div class="info-card">
                        <h4>🤖 Bot Arsenal V4</h4>
                        <p><strong>Version:</strong> ${data.bot_info.version}</p>
                        <p><strong>Uptime:</strong> ${data.bot_info.uptime}</p>
                        <p><strong>Serveurs:</strong> ${data.bot_info.guild_count}</p>
                        <p><strong>Utilisateurs:</strong> ${data.bot_info.user_count}</p>
                    </div>
                    
                    <div class="info-card">
                        <h4>⚡ Performance</h4>
                        <p><strong>Latence:</strong> ${data.performance.latency}</p>
                        <p><strong>RAM:</strong> ${data.performance.memory_usage}</p>
                        <p><strong>CPU:</strong> ${data.performance.cpu_usage}</p>
                        <p><strong>Statut:</strong> <span class="status-${data.performance.status}">${data.performance.status}</span></p>
                    </div>
                    
                    <div class="info-card">
                        <h4>📈 Statistiques</h4>
                        <p><strong>Commandes exécutées:</strong> ${data.statistics.commands_executed}</p>
                        <p><strong>Messages traités:</strong> ${data.statistics.messages_processed}</p>
                        <p><strong>Erreurs:</strong> ${data.statistics.errors}</p>
                        <p><strong>Succès:</strong> ${data.statistics.success_rate}%</p>
                    </div>
                    
                    <div class="info-card">
                        <h4>🔧 Santé du système</h4>
                        <p><strong>Base de données:</strong> <span class="status-${data.health.database}">${data.health.database}</span></p>
                        <p><strong>Discord API:</strong> <span class="status-${data.health.discord}">${data.health.discord}</span></p>
                        <p><strong>WebPanel:</strong> <span class="status-${data.health.webpanel}">${data.health.webpanel}</span></p>
                    </div>
                </div>
            </div>
        `;
    }
    
    async loadServersDetailed() {
        const response = await fetch(`${this.baseURL}/api/servers/detailed`);
        const data = await response.json();
        
        let serversHTML = '';
        data.servers.forEach(server => {
            serversHTML += `
                <div class="server-card">
                    <div class="server-header">
                        <div class="server-icon">${server.icon ? `<img src="${server.icon}" alt="${server.name}">` : server.name.charAt(0)}</div>
                        <div class="server-info">
                            <h4>${server.name}</h4>
                            <p>Propriétaire: ${server.owner}</p>
                        </div>
                        ${server.premium ? '<div class="premium-badge">💎</div>' : ''}
                    </div>
                    <div class="server-stats">
                        <div class="stat-item">
                            <span class="stat-label">Membres total:</span>
                            <span class="stat-value">${server.members.total}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Membres actifs:</span>
                            <span class="stat-value">${server.members.online}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Bots:</span>
                            <span class="stat-value">${server.members.bots}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Canaux texte:</span>
                            <span class="stat-value">${server.channels.text}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Canaux vocaux:</span>
                            <span class="stat-value">${server.channels.voice}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Messages aujourd'hui:</span>
                            <span class="stat-value">${server.activity.messages_today}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        return `
            <div class="detailed-content">
                <h3>🏰 Serveurs détaillés (${data.total_servers})</h3>
                <div class="summary-stats">
                    <div class="summary-item">
                        <strong>Total membres:</strong> ${data.total_members}
                    </div>
                    <div class="summary-item">
                        <strong>Membres en ligne:</strong> ${data.total_online}
                    </div>
                </div>
                <div class="servers-grid">
                    ${serversHTML}
                </div>
            </div>
        `;
    }
    
    async loadUsersDetailed() {
        const response = await fetch(`${this.baseURL}/api/users/detailed`);
        const data = await response.json();
        
        let usersHTML = '';
        data.users.forEach(user => {
            usersHTML += `
                <div class="user-card">
                    <div class="user-header">
                        <div class="user-avatar">${user.avatar ? `<img src="${user.avatar}" alt="${user.username}">` : user.username.charAt(0)}</div>
                        <div class="user-info">
                            <h4>${user.global_name || user.username}</h4>
                            <p class="user-role">${user.role}</p>
                            <p class="user-status status-${user.status}">${user.status}</p>
                        </div>
                        ${user.premium ? '<div class="premium-badge">💎</div>' : ''}
                        ${user.bot ? '<div class="bot-badge">🤖</div>' : ''}
                    </div>
                    <div class="user-stats">
                        <div class="stat-item">
                            <span class="stat-label">Commandes utilisées:</span>
                            <span class="stat-value">${user.stats.commands_used}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Messages envoyés:</span>
                            <span class="stat-value">${user.stats.messages_sent}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Avertissements:</span>
                            <span class="stat-value">${user.stats.warnings}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Dernière activité:</span>
                            <span class="stat-value">${user.last_seen}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        return `
            <div class="detailed-content">
                <h3>👥 Utilisateurs détaillés (${data.total_users})</h3>
                <div class="summary-stats">
                    <div class="summary-item">
                        <strong>En ligne:</strong> ${data.online_users}
                    </div>
                    <div class="summary-item">
                        <strong>Bots:</strong> ${data.bots}
                    </div>
                    <div class="summary-item">
                        <strong>Premium:</strong> ${data.premium_users}
                    </div>
                </div>
                <div class="users-grid">
                    ${usersHTML}
                </div>
            </div>
        `;
    }
    
    async loadCommandsDetailed() {
        const response = await fetch(`${this.baseURL}/api/commands/detailed`);
        const data = await response.json();
        
        let commandsHTML = '';
        data.commands.forEach(command => {
            commandsHTML += `
                <div class="command-card">
                    <div class="command-header">
                        <h4>${command.name}</h4>
                        <span class="command-category">${command.category}</span>
                        ${command.enabled ? '<span class="status-enabled">✅</span>' : '<span class="status-disabled">❌</span>'}
                    </div>
                    <p class="command-description">${command.description}</p>
                    <p class="command-usage"><strong>Usage:</strong> <code>${command.usage}</code></p>
                    <div class="command-stats">
                        <div class="stat-item">
                            <span class="stat-label">Utilisations totales:</span>
                            <span class="stat-value">${command.stats.total_uses}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Aujourd'hui:</span>
                            <span class="stat-value">${command.stats.uses_today}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Cette semaine:</span>
                            <span class="stat-value">${command.stats.uses_this_week}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Dernière utilisation:</span>
                            <span class="stat-value">${command.stats.last_used}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        return `
            <div class="detailed-content">
                <h3>⚡ Commandes détaillées (${data.total_commands})</h3>
                <div class="summary-stats">
                    <div class="summary-item">
                        <strong>Activées:</strong> ${data.enabled_commands}
                    </div>
                    <div class="summary-item">
                        <strong>Utilisations totales:</strong> ${data.global_stats.total_uses}
                    </div>
                    <div class="summary-item">
                        <strong>Plus populaire:</strong> ${data.global_stats.most_popular}
                    </div>
                </div>
                <div class="commands-grid">
                    ${commandsHTML}
                </div>
            </div>
        `;
    }
}

// Initialisation globale
window.arsenalAPI = new ArsenalAPI();

// Fonctions globales pour l'interface
async function refreshDashboard() {
    await window.arsenalAPI.loadDashboardData();
}

async function refreshServers() {
    await window.arsenalAPI.loadUserServers();
}

async function loadActivity() {
    await window.arsenalAPI.loadActivity();
}

function logout() {
    window.location.href = '/auth/logout';
}

function switchAccount() {
    window.location.href = '/auth/login';
}

console.log('🚀 Arsenal V4 WebPanel API - Chargé !');
