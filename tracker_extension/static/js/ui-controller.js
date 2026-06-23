/* ============================================
   UI CONTROLLER
   Handles all UI interactions and updates
   ============================================ */

class UIController {
    constructor() {
        this.currentPage = 'dashboard';
        this.init();
    }

    init() {
        this.setupPageNavigation();
        this.setupSidebar();
        this.setupSearch();
        this.setupDarkMode();
        this.setupSettings();
    }

    /**
     * Setup page navigation
     */
    setupPageNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const pages = document.querySelectorAll('.page');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                this.switchPage(page);
            });
        });
    }

    /**
     * Switch page
     */
    switchPage(pageId) {
        // Remove active class from all pages and links
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

        // Add active class to selected page and link
        const page = document.getElementById(`${pageId}-page`);
        const link = document.querySelector(`[data-page="${pageId}"]`);

        if (page) {
            page.classList.add('active');
            this.currentPage = pageId;
        }
        if (link) {
            link.classList.add('active');
        }

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            history: 'Purchase History',
            analytics: 'Analytics',
            trends: 'Trends',
            settings: 'Settings',
            about: 'About'
        };
        document.getElementById('pageTitle').textContent = titles[pageId] || 'Dashboard';

        // Refresh page-specific content
        this.refreshPageContent(pageId);
    }

    /**
     * Refresh page-specific content
     */
    refreshPageContent(pageId) {
        switch (pageId) {
            case 'dashboard':
                this.updateDashboard();
                break;
            case 'history':
                this.updateHistory();
                break;
            case 'analytics':
                this.updateAnalytics();
                break;
            case 'trends':
                this.updateTrends();
                break;
            case 'about':
                this.updateAbout();
                break;
        }
    }

    /**
     * Setup sidebar
     */
    setupSidebar() {
        const toggle = document.querySelector('.sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');

        if (toggle) {
            toggle.addEventListener('click', () => {
                sidebar.classList.toggle('active');
            });
        }
    }

    /**
     * Setup search
     */
    setupSearch() {
        const searchInput = document.getElementById('globalSearch');
        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });
    }

    /**
     * Perform global search
     */
    performSearch(query) {
        if (!query.trim()) {
            this.switchPage('dashboard');
            return;
        }

        const results = dataManager.purchases.filter(p =>
            p.title.toLowerCase().includes(query.toLowerCase()) ||
            p.category.toLowerCase().includes(query.toLowerCase()) ||
            p.domain.toLowerCase().includes(query.toLowerCase())
        );

        // Switch to history page and highlight results
        this.switchPage('history');
        this.displaySearchResults(results);
    }

    /**
     * Display search results
     */
    displaySearchResults(results) {
        const historyList = document.getElementById('historyList');
        
        if (results.length === 0) {
            historyList.innerHTML = '<p class="empty-message">No purchases found matching your search</p>';
            return;
        }

        const tableHtml = `
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Domain</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${results.map((purchase, idx) => `
                        <tr>
                            <td>${purchase.title}</td>
                            <td>${purchase.category || 'Uncategorized'}</td>
                            <td>$${purchase.price.toFixed(2)}</td>
                            <td>${purchase.domain}</td>
                            <td>${new Date(purchase.date).toLocaleDateString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        historyList.innerHTML = tableHtml;
    }

    /**
     * Setup dark mode
     */
    setupDarkMode() {
        const darkModeToggle = document.getElementById('darkMode');
        const savedDarkMode = localStorage.getItem('darkMode') === 'true';

        if (savedDarkMode) {
            document.body.classList.add('dark-mode');
            if (darkModeToggle) darkModeToggle.checked = true;
        }

        if (darkModeToggle) {
            darkModeToggle.addEventListener('change', (e) => {
                document.body.classList.toggle('dark-mode');
                localStorage.setItem('darkMode', e.target.checked);
            });
        }
    }

    /**
     * Setup settings
     */
    setupSettings() {
        const refreshBtn = document.getElementById('refreshBtn');
        const exportBtn = document.getElementById('exportBtn');
        const importBtn = document.getElementById('importBtn');
        const exportDataBtn = document.getElementById('exportDataBtn');
        const importDataBtn = document.getElementById('importDataBtn');
        const clearDataBtn = document.getElementById('clearDataBtn');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshPageContent(this.currentPage);
                showNotification('Data refreshed!', 'success');
            });
        }

        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }

        if (importBtn) {
            importBtn.addEventListener('click', () => {
                document.getElementById('fileInput').click();
            });
        }

        if (exportDataBtn) {
            exportDataBtn.addEventListener('click', () => this.exportData());
        }

        if (importDataBtn) {
            importDataBtn.addEventListener('click', () => {
                document.getElementById('fileInput').click();
            });
        }

        if (clearDataBtn) {
            clearDataBtn.addEventListener('click', () => {
                if (confirm('Are you sure? This will delete all data permanently!')) {
                    dataManager.clearAll();
                    this.updateDashboard();
                    showNotification('All data cleared!', 'success');
                }
            });
        }

        // File input handler
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.importData(e));
        }
    }

    /**
     * Export data
     */
    exportData() {
        const data = dataManager.exportJSON();
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `purchase-tracker-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        showNotification('Data exported successfully!', 'success');
    }

    /**
     * Import data
     */
    importData(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (dataManager.importJSON(data)) {
                    this.updateDashboard();
                    showNotification('Data imported successfully!', 'success');
                }
            } catch (error) {
                showNotification('Error importing data: ' + error.message, 'error');
            }
        };
        reader.readAsText(file);
    }

    /**
     * Update dashboard
     */
    updateDashboard() {
        const stats = dataManager.getStats();
        const dailySpending = dataManager.getDailySpending(7);
        const topCategories = dataManager.getTopCategories(5);
        const recentPurchases = dataManager.getRecentPurchases(5);

        // Update stats
        document.getElementById('dashTotalPurchases').textContent = stats.total;
        document.getElementById('dashTotalAmount').textContent = `$${stats.amount.toFixed(2)}`;
        document.getElementById('dashAvgPrice').textContent = `$${stats.average.toFixed(2)}`;
        document.getElementById('dashCategoryCount').textContent = stats.categories;

        // Update changes (mock calculation)
        document.getElementById('dashPurchasesChange').textContent = `↗ +${Math.floor(Math.random() * 10)}%`;
        document.getElementById('dashAmountChange').textContent = `↗ +$${(Math.random() * 50).toFixed(2)}`;
        document.getElementById('dashAvgChange').textContent = `${Math.random() > 0.5 ? '↑' : '↓'} ${Math.floor(Math.random() * 5)}%`;
        document.getElementById('dashCategoryChange').textContent = `+${Math.floor(Math.random() * 2)} new`;

        // Update categories list
        this.updateCategoryList('topCategories', topCategories);

        // Update recent purchases
        this.updatePurchaseList('recentPurchases', recentPurchases);

        // Create chart
        const ctx = document.getElementById('spendingChart');
        if (ctx) {
            ChartManager.createSpendingChart(ctx, dailySpending);
        }
    }

    /**
     * Update history page
     */
    updateHistory() {
        const purchases = dataManager.getPurchases().sort((a, b) => new Date(b.date) - new Date(a.date));
        
        // Populate category filter
        const categoryFilter = document.getElementById('historyFilter');
        const categories = [...new Set(purchases.map(p => p.category || 'Uncategorized'))];
        
        categoryFilter.innerHTML = '<option value="">All Categories</option>' +
            categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');

        // Display history
        this.displayHistory(purchases);

        // Setup filters
        document.getElementById('historyFilter').addEventListener('change', () => this.applyHistoryFilters());
        document.getElementById('dateFilter').addEventListener('change', () => this.applyHistoryFilters());
        document.getElementById('clearFiltersBtn').addEventListener('click', () => {
            document.getElementById('historyFilter').value = '';
            document.getElementById('dateFilter').value = '';
            this.displayHistory(purchases);
        });
    }

    /**
     * Display history table
     */
    displayHistory(purchases) {
        const historyList = document.getElementById('historyList');
        
        if (purchases.length === 0) {
            historyList.innerHTML = '<p class="empty-message">No purchase history</p>';
            return;
        }

        const tableHtml = `
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Domain</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${purchases.map((purchase, idx) => `
                        <tr>
                            <td>${purchase.title}</td>
                            <td>${purchase.category || 'Uncategorized'}</td>
                            <td>$${purchase.price.toFixed(2)}</td>
                            <td>${purchase.domain}</td>
                            <td>${new Date(purchase.date).toLocaleDateString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        historyList.innerHTML = tableHtml;
    }

    /**
     * Apply history filters
     */
    applyHistoryFilters() {
        const category = document.getElementById('historyFilter').value;
        const date = document.getElementById('dateFilter').value;

        let filtered = dataManager.getPurchases();

        if (category) {
            filtered = filtered.filter(p => (p.category || 'Uncategorized') === category);
        }

        if (date) {
            const selectedDate = new Date(date);
            filtered = filtered.filter(p => {
                const purchaseDate = new Date(p.date);
                return purchaseDate.toDateString() === selectedDate.toDateString();
            });
        }

        this.displayHistory(filtered.sort((a, b) => new Date(b.date) - new Date(a.date)));
    }

    /**
     * Update analytics
     */
    updateAnalytics() {
        const topCategories = dataManager.getTopCategories(10);
        const distribution = dataManager.getPriceDistribution();
        const stats = dataManager.getStats();

        // Create charts
        const categoryCtx = document.getElementById('categoryChart');
        if (categoryCtx) {
            ChartManager.createCategoryChart(categoryCtx, topCategories);
        }

        const priceCtx = document.getElementById('priceChart');
        if (priceCtx) {
            ChartManager.createPriceChart(priceCtx, distribution);
        }

        // Display all categories
        this.displayAllCategories(topCategories);
    }

    /**
     * Display all categories
     */
    displayAllCategories(categories) {
        const container = document.getElementById('allCategories');
        
        if (categories.length === 0) {
            container.innerHTML = '<p class="empty-message">No categories yet</p>';
            return;
        }

        const html = categories.map(cat => {
            const total = dataManager.getPurchasesByCategory(cat.name)
                .reduce((sum, p) => sum + p.price, 0);
            return `
                <div class="category-row">
                    <div class="category-name-full">${cat.name}</div>
                    <div class="category-count-full">${cat.count} items</div>
                    <div class="category-amount">$${total.toFixed(2)}</div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    }

    /**
     * Update trends
     */
    updateTrends() {
        const topDomains = dataManager.getTopDomains();
        const dailySpending = dataManager.getDailySpending(30);

        // Display top domains
        this.displayTopDomains(topDomains);

        // Create trend chart
        const trendCtx = document.getElementById('trendChart');
        if (trendCtx) {
            ChartManager.createTrendChart(trendCtx, dailySpending);
        }

        // Create frequency chart
        const frequencyCtx = document.getElementById('frequencyChart');
        if (frequencyCtx) {
            ChartManager.createFrequencyChart(frequencyCtx, dailySpending);
        }
    }

    /**
     * Display top domains
     */
    displayTopDomains(domains) {
        const container = document.getElementById('topDomains');
        
        if (domains.length === 0) {
            container.innerHTML = '<p class="empty-message">No domain data yet</p>';
            return;
        }

        const html = domains.map(item => `
            <div class="domain-item">
                <span class="domain-name">${item.domain}</span>
                <span class="domain-count">${item.count}</span>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    /**
     * Update about page
     */
    updateAbout() {
        const stats = dataManager.getStats();
        document.getElementById('aboutTotalPurchases').textContent = stats.total;
        document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
        document.getElementById('dataSize').textContent = dataManager.getDataSize() + ' KB';
    }

    /**
     * Update category list
     */
    updateCategoryList(elementId, categories) {
        const container = document.getElementById(elementId);
        
        if (categories.length === 0) {
            container.innerHTML = '<p class="empty-message">No categories yet</p>';
            return;
        }

        const html = categories.map(cat => `
            <div class="category-item">
                <span class="category-name">${cat.name}</span>
                <span class="category-badge">${cat.count}</span>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    /**
     * Update purchase list
     */
    updatePurchaseList(elementId, purchases) {
        const container = document.getElementById(elementId);
        
        if (purchases.length === 0) {
            container.innerHTML = '<p class="empty-message">No purchases yet</p>';
            return;
        }

        const html = purchases.map(purchase => `
            <div class="purchase-item">
                <div class="purchase-info">
                    <div class="purchase-title">${purchase.title}</div>
                    <div class="purchase-meta">${purchase.domain} • ${new Date(purchase.date).toLocaleDateString()}</div>
                </div>
                <div class="purchase-price">$${purchase.price.toFixed(2)}</div>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// Create global UI controller
const uiController = new UIController();
