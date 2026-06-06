/* ============================================
   MAIN APP
   Application initialization and utilities
   ============================================ */

// Utility function for notifications
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // Could create a toast notification UI here
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Purchase Tracker Web Application Initializing...');

    // Wait for data to load
    await new Promise(resolve => setTimeout(resolve, 500));

    // Initialize UI
    console.log('✅ Application Ready');

    // Add some sample data if none exists
    if (dataManager.getPurchases().length === 0) {
        console.log('📝 Adding sample data for demonstration...');
        addSampleData();
    }

    // Show dashboard
    uiController.switchPage('dashboard');
});

/**
 * Add sample data for demonstration
 */
function addSampleData() {
    const samplePurchases = [
        { title: 'Laptop Computer', price: 1299.99, category: 'Electronics', domain: 'amazon.com' },
        { title: 'USB-C Cable', price: 15.99, category: 'Electronics', domain: 'amazon.com' },
        { title: 'Blue Jeans', price: 89.99, category: 'Clothing', domain: 'hm.com' },
        { title: 'Running Shoes', price: 129.99, category: 'Clothing', domain: 'nike.com' },
        { title: 'Coffee Maker', price: 89.99, category: 'Home', domain: 'amazon.com' },
        { title: 'Organic Coffee Beans', price: 14.99, category: 'Food', domain: 'wholefoods.com' },
        { title: 'Yoga Mat', price: 29.99, category: 'Sports', domain: 'ebay.com' },
        { title: 'Psychology Book', price: 22.99, category: 'Books', domain: 'bookdepository.com' },
        { title: 'Phone Case', price: 19.99, category: 'Electronics', domain: 'amazon.com' },
        { title: 'Kitchen Knife Set', price: 79.99, category: 'Home', domain: 'amazon.com' }
    ];

    samplePurchases.forEach((purchase, index) => {
        const date = new Date();
        date.setDate(date.getDate() - index);
        purchase.date = date.toISOString();
        dataManager.addPurchase(purchase);
    });

    console.log('✅ Sample data added');
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Format date
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

/**
 * Get favicon
 */
function getFavicon(domain) {
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Export functions globally
 */
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.getFavicon = getFavicon;
window.showNotification = showNotification;
