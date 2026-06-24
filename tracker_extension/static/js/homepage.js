// homepage.js - Home page functionality
document.addEventListener('DOMContentLoaded', function() {
    function loadStats() {
        try {
            if (typeof chrome !== 'undefined' && chrome.storage) {
                chrome.storage.local.get(['products', 'categories', 'domains', 'daily'], function(data) {
                    var products = data.products || {};
                    var domains = data.domains || {};
                    var productList = Object.values(products);
                    var totalProducts = productList.length;
                    var totalViews = 0;
                    var totalPurchases = 0;
                    for (var i = 0; i < productList.length; i++) {
                        totalViews += productList[i].viewCount || 0;
                        totalPurchases += productList[i].purchaseCount || 0;
                    }
                    var totalDomains = Object.keys(domains).length;
                    updateStats(totalProducts, totalViews, totalPurchases, totalDomains);
                    renderRecentProducts(productList);
                });
                return;
            }
            var stored = localStorage.getItem('purchaseTrackerData');
            if (stored) {
                var data = JSON.parse(stored);
                var purchases = data.purchases || [];
                var domainSet = {};
                for (var i = 0; i < purchases.length; i++) {
                    if (purchases[i].domain) {
                        domainSet[purchases[i].domain] = true;
                    }
                }
                var domainCount = Object.keys(domainSet).length;
                updateStats(purchases.length, purchases.length, purchases.length, domainCount);
                renderRecentProducts(purchases);
                return;
            }
            updateStats(0, 0, 0, 0);
            document.getElementById('recentProducts').innerHTML = 
                '<div class="col-12">' +
                '<div class="text-center text-muted py-4">' +
                '<p>No products tracked yet. Install the extension and start browsing!</p>' +
                '</div></div>';
        } catch (e) {
            console.warn('Could not load stats:', e);
        }
    }
    
    function updateStats(products, views, purchases, domains) {
        var prodEl = document.getElementById('statProducts');
        var viewsEl = document.getElementById('statViews');
        var purchEl = document.getElementById('statPurchases');
        var domEl = document.getElementById('statDomains');
        if (prodEl) prodEl.textContent = formatNumber(products);
        if (viewsEl) viewsEl.textContent = formatNumber(views);
        if (purchEl) purchEl.textContent = formatNumber(purchases);
        if (domEl) domEl.textContent = formatNumber(domains);
    }
    
    function formatNumber(n) {
        if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
        if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
        return n;
    }
    
    function renderRecentProducts(products) {
        var container = document.getElementById('recentProducts');
        if (!products || products.length === 0) {
            container.innerHTML = 
                '<div class="col-12">' +
                '<div class="text-center text-muted py-4">' +
                '<p>No products tracked yet. Start browsing shopping sites!</p>' +
                '</div></div>';
            return;
        }
        var sorted = products.sort(function(a, b) {
            var dateA = new Date(a.lastSeen || a.tracking_date || a.date || 0);
            var dateB = new Date(b.lastSeen || b.tracking_date || b.date || 0);
            return dateB - dateA;
        }).slice(0, 6);
        var html = '';
        for (var i = 0; i < sorted.length; i++) {
            var p = sorted[i];
            var title = p.title || p.product_name || 'Unknown Product';
            var price = p.latestPrice || p.price || 0;
            var domain = p.domain || p.website || 'Unknown';
            var date = p.lastSeen || p.tracking_date || p.date || new Date().toISOString();
            html += 
                '<div class="col-md-4 col-sm-6">' +
                '<div class="card h-100 shadow-sm">' +
                '<div class="card-body">' +
                '<h6 class="card-title text-truncate" title="' + escapeHtml(title) + '">' + escapeHtml(title) + '</h6>' +
                '<div class="d-flex justify-content-between align-items-center mt-2">' +
                '<span class="badge bg-primary">' + escapeHtml(domain) + '</span>' +
                '<span class="fw-bold text-success">$' + parseFloat(price).toFixed(2) + '</span>' +
                '</div>' +
                '<small class="text-muted d-block mt-2">' + new Date(date).toLocaleDateString() + '</small>' +
                '</div></div></div>';
        }
        container.innerHTML = html;
    }
    
    function escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
    
    loadStats();
    setInterval(loadStats, 30000);
});