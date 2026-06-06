// Background service worker - handles data persistence and core logic
console.log('[Purchase Tracker] Background service worker loaded');

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'trackPurchase') {
        handleTrackPurchase(request.products);
    }
});

async function handleTrackPurchase(products) {
    try {
        // Get current data
        const data = await chrome.storage.local.get(['purchases', 'categories', 'trends']);
        
        let purchases = data.purchases || [];
        let categories = data.categories || {};
        let trends = data.trends || {};

        // Process each product
        products.forEach(product => {
            const purchase = {
                title: product.title || 'Unknown Product',
                price: product.price,
                category: product.category || 'Uncategorized',
                domain: product.domain,
                url: product.url,
                date: product.date || new Date().toISOString()
            };

            purchases.push(purchase);

            // Update category count
            const category = purchase.category;
            categories[category] = (categories[category] || 0) + 1;

            // Track trends (domain-based)
            const domain = purchase.domain;
            trends[domain] = (trends[domain] || 0) + 1;

            // Send notification
            notifyPurchaseTracked(purchase);
        });

        // Save updated data
        await chrome.storage.local.set({
            purchases: purchases.slice(-10000), // Keep last 10000 purchases
            categories: categories,
            trends: trends,
            lastUpdated: new Date().toISOString()
        });

        console.log(`[Purchase Tracker] Tracked ${products.length} purchase(s)`);
    } catch (error) {
        console.error('[Purchase Tracker] Error tracking purchase:', error);
    }
}

function notifyPurchaseTracked(purchase) {
    // Create a desktop notification
    chrome.notifications.create({
        type: 'basic',
        iconUrl: chrome.runtime.getURL('icons/icon128.png'),
        title: 'Purchase Tracked! ',
        message: `${purchase.title} - $${purchase.price.toFixed(2)}`,
        priority: 1
    });
}

// Listen for tab updates to reset daily data if needed
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
        checkAndResetDailyData();
    }
});

async function checkAndResetDailyData() {
    const data = await chrome.storage.local.get(['lastDate']);
    const today = new Date().toDateString();

    if (data.lastDate !== today) {
        // Reset daily-specific data but keep historical data
        await chrome.storage.local.set({
            lastDate: today,
            categories: {}
        });
    }
}

// Initialize notifications permission
chrome.notifications.getPermissionLevel(level => {
    if (level !== 'granted') {
        // Could request permission here if needed
    }
});
