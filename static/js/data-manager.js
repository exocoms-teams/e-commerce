/* ============================================
   DATA MANAGER
   Handles all data operations and storage
   ============================================ */

class DataManager {
    constructor() {
        this.purchases = [];
        this.categories = {};
        this.trends = {};
        this.lastSyncTime = null;
        this.syncInterval = 5000; // 5 seconds for demo
        this.init();
    }

    async init() {
        await this.loadData();
        this.startAutoSync();
    }

    /**
     * Load data from localStorage or Chrome extension
     */
    async loadData() {
        try {
            // Try to get data from localStorage first
            const stored = localStorage.getItem('purchaseTrackerData');
            if (stored) {
                const data = JSON.parse(stored);
                this.purchases = data.purchases || [];
                this.categories = data.categories || {};
                this.trends = data.trends || {};
                console.log('📦 Data loaded from localStorage');
                return;
            }

            // Try to get data from Chrome extension
            if (typeof chrome !== 'undefined' && chrome.storage) {
                chrome.storage.local.get(['purchases', 'categories', 'trends'], (data) => {
                    this.purchases = data.purchases || [];
                    this.categories = data.categories || {};
                    this.trends = data.trends || {};
                    this.lastSyncTime = new Date();
                    console.log('📦 Data synced from Chrome extension');
                    this.saveData();
                });
            }
        } catch (error) {
            console.error('❌ Error loading data:', error);
        }
    }

    /**
     * Save data to localStorage
     */
    saveData() {
        try {
            const data = {
                purchases: this.purchases,
                categories: this.categories,
                trends: this.trends,
                lastUpdated: new Date().toISOString()
            };
            localStorage.setItem('purchaseTrackerData', JSON.stringify(data));
            console.log('💾 Data saved to localStorage');
        } catch (error) {
            console.error('❌ Error saving data:', error);
        }
    }

    /**
     * Auto-sync with Chrome extension
     */
    startAutoSync() {
        setInterval(() => {
            this.loadData();
        }, this.syncInterval);
    }

    /**
     * Get all purchases
     */
    getPurchases() {
        return this.purchases;
    }

    /**
     * Get purchases by category
     */
    getPurchasesByCategory(category) {
        return this.purchases.filter(p => (p.category || 'Uncategorized') === category);
    }

    /**
     * Get purchases by date range
     */
    getPurchasesByDateRange(startDate, endDate) {
        return this.purchases.filter(p => {
            const date = new Date(p.date);
            return date >= startDate && date <= endDate;
        });
    }

    /**
     * Get purchases for last N days
     */
    getPurchasesLastDays(days) {
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        return this.getPurchasesByDateRange(startDate, new Date());
    }

    /**
     * Get statistics
     */
    getStats() {
        const total = this.purchases.length;
        const amount = this.purchases.reduce((sum, p) => sum + (p.price || 0), 0);
        const average = total > 0 ? amount / total : 0;
        const max = total > 0 ? Math.max(...this.purchases.map(p => p.price || 0)) : 0;
        const min = total > 0 ? Math.min(...this.purchases.map(p => p.price || 0)) : 0;

        return {
            total,
            amount,
            average,
            max,
            min,
            categories: Object.keys(this.categories).length,
            domains: Object.keys(this.trends).length
        };
    }

    /**
     * Get daily spending summary
     */
    getDailySpending(days = 7) {
        const data = {};
        const today = new Date();

        for (let i = 0; i < days; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

            const dayStart = new Date(date);
            dayStart.setHours(0, 0, 0, 0);
            const dayEnd = new Date(date);
            dayEnd.setHours(23, 59, 59, 999);

            const dayPurchases = this.getPurchasesByDateRange(dayStart, dayEnd);
            const amount = dayPurchases.reduce((sum, p) => sum + (p.price || 0), 0);

            data[dateStr] = {
                amount: parseFloat(amount.toFixed(2)),
                count: dayPurchases.length
            };
        }

        return data;
    }

    /**
     * Get top categories
     */
    getTopCategories(limit = 5) {
        return Object.entries(this.categories)
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([name, count]) => ({ name, count }));
    }

    /**
     * Get top domains
     */
    getTopDomains(limit = 10) {
        return Object.entries(this.trends)
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([domain, count]) => ({ domain, count }));
    }

    /**
     * Get recent purchases
     */
    getRecentPurchases(limit = 5) {
        return this.purchases
            .sort((a, b) => new Date(b.date) - new Date(a.date))
            .slice(0, limit);
    }

    /**
     * Add a purchase
     */
    addPurchase(purchase) {
        const newPurchase = {
            title: purchase.title || 'Unknown Product',
            price: parseFloat(purchase.price) || 0,
            category: purchase.category || 'Uncategorized',
            domain: purchase.domain || 'unknown',
            url: purchase.url || '',
            date: purchase.date || new Date().toISOString()
        };

        this.purchases.push(newPurchase);
        this.updateCategories(newPurchase.category);
        this.updateTrends(newPurchase.domain);
        this.saveData();

        return newPurchase;
    }

    /**
     * Delete a purchase
     */
    deletePurchase(index) {
        if (index >= 0 && index < this.purchases.length) {
            const purchase = this.purchases[index];
            this.purchases.splice(index, 1);

            // Recalculate categories
            this.recalculateCategories();
            this.recalculateTrends();
            this.saveData();

            return true;
        }
        return false;
    }

    /**
     * Update category count
     */
    updateCategories(category) {
        this.categories[category] = (this.categories[category] || 0) + 1;
    }

    /**
     * Update trends (domain count)
     */
    updateTrends(domain) {
        this.trends[domain] = (this.trends[domain] || 0) + 1;
    }

    /**
     * Recalculate categories
     */
    recalculateCategories() {
        this.categories = {};
        this.purchases.forEach(p => {
            const category = p.category || 'Uncategorized';
            this.categories[category] = (this.categories[category] || 0) + 1;
        });
    }

    /**
     * Recalculate trends
     */
    recalculateTrends() {
        this.trends = {};
        this.purchases.forEach(p => {
            const domain = p.domain || 'unknown';
            this.trends[domain] = (this.trends[domain] || 0) + 1;
        });
    }

    /**
     * Clear all data
     */
    clearAll() {
        this.purchases = [];
        this.categories = {};
        this.trends = {};
        localStorage.removeItem('purchaseTrackerData');
        console.log('🗑️ All data cleared');
    }

    /**
     * Export data as JSON
     */
    exportJSON() {
        return {
            purchases: this.purchases,
            categories: this.categories,
            trends: this.trends,
            exportedAt: new Date().toISOString()
        };
    }

    /**
     * Import data from JSON
     */
    importJSON(data) {
        try {
            this.purchases = data.purchases || [];
            this.categories = data.categories || {};
            this.trends = data.trends || {};
            this.saveData();
            console.log('✅ Data imported successfully');
            return true;
        } catch (error) {
            console.error('❌ Error importing data:', error);
            return false;
        }
    }

    /**
     * Export data as CSV
     */
    exportCSV() {
        let csv = 'Title,Price,Category,Domain,Date\n';
        this.purchases.forEach(p => {
            csv += `"${p.title}","${p.price}","${p.category || 'Uncategorized'}","${p.domain}","${p.date}"\n`;
        });
        return csv;
    }

    /**
     * Get data size in KB
     */
    getDataSize() {
        const data = JSON.stringify(this.exportJSON());
        return (new TextEncoder().encode(data).length / 1024).toFixed(2);
    }

    /**
     * Get price distribution
     */
    getPriceDistribution(ranges = [10, 25, 50, 100]) {
        const distribution = {};
        let lastRange = 0;

        ranges.forEach(range => {
            distribution[`$${lastRange}-$${range}`] = 0;
            lastRange = range;
        });
        distribution[`$${lastRange}+`] = 0;

        this.purchases.forEach(p => {
            for (let i = 0; i < ranges.length; i++) {
                if (p.price <= ranges[i]) {
                    const key = i === 0 ? `$0-$${ranges[0]}` : `$${ranges[i-1]}-$${ranges[i]}`;
                    distribution[key]++;
                    return;
                }
            }
            distribution[`$${lastRange}+`]++;
        });

        return distribution;
    }
}

// Create global data manager instance
const dataManager = new DataManager();
