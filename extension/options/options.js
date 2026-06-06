// Options page functionality
let allPurchases = [];

document.addEventListener('DOMContentLoaded', async () => {
    setupTabs();
    await loadData();
    setupEventListeners();
});

function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked tab
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

async function loadData() {
    const data = await chrome.storage.local.get(['purchases', 'categories', 'trends']);
    allPurchases = data.purchases || [];
    const categories = data.categories || {};
    const trends = data.trends || {};

    updateOverviewTab(categories);
    updateHistoryTab();
    updateTrendsTab(trends);
}

function updateOverviewTab(categories) {
    const totalPurchases = allPurchases.length;
    const totalAmount = allPurchases.reduce((sum, p) => sum + (p.price || 0), 0);
    const avgAmount = totalPurchases > 0 ? (totalAmount / totalPurchases) : 0;
    const maxAmount = totalPurchases > 0 ? Math.max(...allPurchases.map(p => p.price || 0)) : 0;

    document.getElementById('totalPurchases').textContent = totalPurchases;
    document.getElementById('totalAmount').textContent = `$${totalAmount.toFixed(2)}`;
    document.getElementById('avgAmount').textContent = `$${avgAmount.toFixed(2)}`;
    document.getElementById('maxAmount').textContent = `$${maxAmount.toFixed(2)}`;

    // Display top categories
    const sortedCategories = Object.entries(categories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    const categoriesHtml = sortedCategories.length > 0 ? sortedCategories.map(([name, count]) => `
        <div class="category-item">
            <span class="category-name">${name}</span>
            <span class="category-badge">${count}</span>
        </div>
    `).join('') : '<p class="empty-message">No categories yet</p>';

    document.getElementById('topCategories').innerHTML = categoriesHtml;
}

function updateHistoryTab() {
    const categoryFilter = document.getElementById('categoryFilter');
    const categories = new Set(allPurchases.map(p => p.category || 'Uncategorized'));

    // Populate category filter
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categoryFilter.appendChild(option);
    });

    displayHistory();
}

function displayHistory(searchTerm = '', filterCategory = '') {
    let filtered = allPurchases.slice().reverse(); // Most recent first

    if (searchTerm) {
        filtered = filtered.filter(p =>
            p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            p.domain.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }

    if (filterCategory) {
        filtered = filtered.filter(p => (p.category || 'Uncategorized') === filterCategory);
    }

    const historyHtml = filtered.length > 0 ? filtered.slice(0, 100).map((purchase, index) => `
        <div class="history-item">
            <div>
                <div class="history-title">${purchase.title}</div>
                <small class="history-date">${purchase.domain} • ${new Date(purchase.date).toLocaleDateString()}</small>
            </div>
            <span class="history-price">$${purchase.price.toFixed(2)}</span>
        </div>
    `).join('') : '<p class="empty-message">No purchases found</p>';

    document.getElementById('historyList').innerHTML = historyHtml;
}

function updateTrendsTab(trends) {
    const sortedDomains = Object.entries(trends)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    const domainsHtml = sortedDomains.length > 0 ? sortedDomains.map(([domain, count]) => `
        <div class="domain-item">
            <span>${domain}</span>
            <span class="category-badge">${count}</span>
        </div>
    `).join('') : '<p class="empty-message">No domain trends yet</p>';

    document.getElementById('domainsList').innerHTML = domainsHtml;
}

function setupEventListeners() {
    // Search functionality
    document.getElementById('searchInput').addEventListener('input', (e) => {
        const category = document.getElementById('categoryFilter').value;
        displayHistory(e.target.value, category);
    });

    // Category filter
    document.getElementById('categoryFilter').addEventListener('change', (e) => {
        const search = document.getElementById('searchInput').value;
        displayHistory(search, e.target.value);
    });

    // Export CSV
    document.getElementById('exportBtn').addEventListener('click', exportCSV);

    // Settings
    document.getElementById('notificationsToggle').addEventListener('change', (e) => {
        chrome.storage.local.set({ notificationsEnabled: e.target.checked });
    });

    document.getElementById('autoTrackToggle').addEventListener('change', (e) => {
        chrome.storage.local.set({ autoTrackEnabled: e.target.checked });
    });

    document.getElementById('refreshInterval').addEventListener('change', (e) => {
        chrome.storage.local.set({ refreshInterval: parseInt(e.target.value) });
    });

    document.getElementById('exportDataBtn').addEventListener('click', exportAllData);
    document.getElementById('importDataBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });

    document.getElementById('fileInput').addEventListener('change', importData);
    document.getElementById('clearAllBtn').addEventListener('click', clearAllData);
}

function exportCSV() {
    let csv = 'Title,Price,Category,Domain,Date\n';
    allPurchases.forEach(purchase => {
        csv += `"${purchase.title}","${purchase.price}","${purchase.category || 'Uncategorized'}","${purchase.domain}","${purchase.date}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `purchases_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

function exportAllData() {
    chrome.storage.local.get(null, (data) => {
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `purchase-tracker-backup_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
    });
}

function importData(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);
            chrome.storage.local.set(data, () => {
                alert('Data imported successfully!');
                location.reload();
            });
        } catch (error) {
            alert('Error importing data: ' + error.message);
        }
    };
    reader.readAsText(file);
}

async function clearAllData() {
    if (confirm('Are you sure you want to clear ALL data? This cannot be undone!')) {
        await chrome.storage.local.clear();
        alert('All data has been cleared.');
        location.reload();
    }
}
