/* ============================================
   DASHBOARD FUNCTIONS
   Dashboard specific operations
   ============================================ */

class Dashboard {
    static initialize() {
        this.setupEventListeners();
        this.refreshAll();
        this.startAutoRefresh();
    }

    static setupEventListeners() {
        // Add purchase button (if exists)
        const addBtn = document.getElementById('addPurchaseBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showAddPurchaseModal());
        }
    }

    static refreshAll() {
        if (uiController.currentPage === 'dashboard') {
            uiController.updateDashboard();
        }
    }

    static startAutoRefresh() {
        setInterval(() => {
            if (uiController.currentPage === 'dashboard') {
                uiController.updateDashboard();
            }
        }, 30000); // Refresh every 30 seconds
    }

    static showAddPurchaseModal() {
        // Could be implemented to show a modal for adding purchases
        console.log('Add purchase modal');
    }
}

// Initialize dashboard
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        Dashboard.initialize();
    });
} else {
    Dashboard.initialize();
}
