// Popup functionality
document.addEventListener('DOMContentLoaded', async () => {
    await loadStats();
    setupEventListeners();
});

async function loadStats() {
    const data = await chrome.storage.local.get(['purchases', 'categories']);
    const purchases = data.purchases || [];
    const categories = data.categories || {};

    // Calculate stats
    const today = new Date().toDateString();
    const todaysPurchases = purchases.filter(p => new Date(p.date).toDateString() === today);

    const itemsCount = todaysPurchases.length;
    const totalSpent = todaysPurchases.reduce((sum, p) => sum + (parseFloat(p.price) || 0), 0);
    const avgPrice = itemsCount > 0 ? (totalSpent / itemsCount) : 0;

    // Update UI
    document.getElementById('itemsCount').textContent = itemsCount;
    document.getElementById('totalSpent').textContent = `$${totalSpent.toFixed(2)}`;
    document.getElementById('avgPrice').textContent = `$${avgPrice.toFixed(2)}`;
    document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();

    // Display categories
    displayCategories(categories);
}

function displayCategories(categories) {
    const list = document.getElementById('categoriesList');
    const categoryItems = Object.entries(categories);

    if (categoryItems.length === 0) {
        list.innerHTML = '<p class="empty-message">No categories tracked yet</p>';
        return;
    }

    list.innerHTML = categoryItems.map(([name, count]) => `
        <div class="category-item">
            <span class="category-name">${name}</span>
            <span class="category-count">${count}</span>
        </div>
    `).join('');
}

function setupEventListeners() {
    document.getElementById('settingsBtn').addEventListener('click', () => {
        chrome.runtime.openOptionsPage();
    });

    document.getElementById('viewHistoryBtn').addEventListener('click', () => {
        chrome.tabs.create({ url: chrome.runtime.getURL('options/options.html?tab=history') });
    });

    document.getElementById('clearDataBtn').addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
            await chrome.storage.local.clear();
            await loadStats();
        }
    });
}
