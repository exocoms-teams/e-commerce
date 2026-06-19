// options.js - Complete standalone version (no backend required)
let allData = null;
let charts = {};
const COLORS = ['#6c47ff','#a855f7','#06b6d4','#10b981','#f59e0b','#f87171','#34d399','#60a5fa','#e879f9','#fb923c'];

// ---- Init ----

document.addEventListener('DOMContentLoaded', () => {
  setupNav();
  setupControls();
  refresh();
  setInterval(refresh, 30000);
});

// ---- Get data from storage ----

async function getDataFromStorage() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['products', 'categories', 'domains', 'daily', 'lastUpdated'], (data) => {
      const store = {
        products: data.products || {},
        categories: data.categories || {},
        domains: data.domains || {},
        daily: data.daily || {},
        lastUpdated: data.lastUpdated || null,
      };
      
      // Enrich products with computed values
      const products = Object.values(store.products);
      const now = Date.now();
      const dayMs = 86400000;

      const enriched = products.map(p => {
        const prices = p.prices || [];
        const ratings = p.ratings || [];
        const reviews = p.reviews || [];
        const soldCounts = p.soldCounts || [];
        const viewLog = p.viewLog || [];

        const avgPrice = prices.length ? (prices.reduce((s, x) => s + x.value, 0) / prices.length).toFixed(2) : null;
        const latestPrice = prices.length ? prices[prices.length - 1].value : null;
        const avgRating = ratings.length ? (ratings.reduce((s, x) => s + x, 0) / ratings.length).toFixed(1) : null;
        const latestSold = soldCounts.length ? soldCounts[soldCounts.length - 1].value : null;
        const soldDelta = soldCounts.length >= 2 ? soldCounts[soldCounts.length - 1].value - soldCounts[0].value : null;

        let priceTrend = null;
        if (prices.length >= 2 && avgPrice) {
          const diff = latestPrice - parseFloat(avgPrice);
          priceTrend = Math.round((diff / parseFloat(avgPrice)) * 100);
        }

        const views7d = viewLog.filter(t => now - new Date(t).getTime() < 7 * dayMs).length;
        const views3d = viewLog.filter(t => now - new Date(t).getTime() < 3 * dayMs).length;
        const views3to6d = viewLog.filter(t => {
          const age = now - new Date(t).getTime();
          return age >= 3 * dayMs && age < 6 * dayMs;
        }).length;
        const isRising = views3d > 0 && views3d > views3to6d * 1.5;

        // Compute trend score
        const trendScore = computeTrendScore(p);

        return {
          ...p,
          avgPrice,
          latestPrice,
          avgRating,
          latestSold,
          soldDelta,
          priceTrend,
          views7d,
          isRising,
          trendScore,
          viewCount: p.viewCount || 0,
          purchaseCount: p.purchaseCount || 0,
        };
      });

      enriched.sort((a, b) => b.trendScore - a.trendScore);

      resolve({
        products: enriched,
        categories: store.categories,
        domains: store.domains,
        daily: store.daily,
        lastUpdated: store.lastUpdated,
        totalProducts: products.length,
        totalViews: products.reduce((s, p) => s + (p.viewCount || 0), 0),
        totalPurchases: products.reduce((s, p) => s + (p.purchaseCount || 0), 0),
      });
    });
  });
}

// ---- Trend Score (copied from background) ----

function computeTrendScore(product) {
  const now = Date.now();
  const dayMs = 86400000;

  const viewLog = product.viewLog || [];
  const views7d = viewLog.filter(t => now - new Date(t).getTime() < 7 * dayMs).length;
  const views30d = viewLog.filter(t => now - new Date(t).getTime() < 30 * dayMs).length;
  const velocityScore = views7d * 3 + views30d * 1;

  const views3d = viewLog.filter(t => now - new Date(t).getTime() < 3 * dayMs).length;
  const views3to6d = viewLog.filter(t => {
    const age = now - new Date(t).getTime();
    return age >= 3 * dayMs && age < 6 * dayMs;
  }).length;
  const risingMultiplier = views3d > 0 && views3d > views3to6d * 1.5 ? 1.5 : 1.0;

  const soldCounts = product.soldCounts || [];
  let soldScore = 0;
  if (soldCounts.length >= 2) {
    const delta = soldCounts[soldCounts.length - 1].value - soldCounts[0].value;
    soldScore = Math.max(0, delta) * 0.5;
  } else if (soldCounts.length === 1) {
    soldScore = soldCounts[0].value * 0.05;
  }

  const purchaseScore = (product.purchaseCount || 0) * 10;

  let priceSignal = 0;
  const prices = product.prices || [];
  if (prices.length >= 2) {
    const avgPrice = prices.reduce((s, p) => s + p.value, 0) / prices.length;
    const latestPrice = prices[prices.length - 1].value;
    if (latestPrice < avgPrice * 0.95) priceSignal = 8;
    if (latestPrice < avgPrice * 0.85) priceSignal = 15;
  }

  let ratingSignal = 0;
  const ratings = product.ratings || [];
  const reviews = product.reviews || [];
  if (ratings.length > 0) {
    const avgRating = ratings.reduce((s, r) => s + r, 0) / ratings.length;
    const latestReviewCount = reviews.length > 0 ? reviews[reviews.length - 1] : 1;
    ratingSignal = avgRating * Math.log(1 + latestReviewCount) * 0.3;
  }

  const rawScore = velocityScore + soldScore + purchaseScore + priceSignal + ratingSignal;
  return Math.round(rawScore * risingMultiplier);
}

// ---- Navigation ----

function setupNav() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const pageId = 'page-' + btn.dataset.page;
      const page = document.getElementById(pageId);
      if (page) page.classList.add('active');
      const title = document.getElementById('pageTitle');
      if (title) title.textContent = btn.textContent;
      renderCurrentPage();
    });
  });
}

function renderCurrentPage() {
  const active = document.querySelector('.page.active');
  if (!active || !allData) return;
  const id = active.id;
  if (id === 'page-trending') renderTrending();
  if (id === 'page-rising') renderRising();
  if (id === 'page-categories') renderCategories();
  if (id === 'page-domains') renderDomains();
  if (id === 'page-activity') renderActivity();
}

// ---- Refresh ----

async function refresh() {
  try {
    const data = await getDataFromStorage();
    allData = data;
    updateSidebar();
    renderCurrentPage();
    populateCategoryFilter();
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    if (dot) dot.className = 'status-dot online';
    if (text) text.textContent = 'Local storage';
  } catch (e) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    if (dot) dot.className = 'status-dot offline';
    if (text) text.textContent = 'Error loading data';
    console.error('Error loading data:', e);
  }
}

function updateSidebar() {
  setText('sTotal', allData?.totalProducts || 0);
  setText('sViews', allData?.totalViews || 0);
  setText('sPurchases', allData?.totalPurchases || 0);
  if (allData?.lastUpdated) {
    setText('sUpdated', new Date(allData.lastUpdated).toLocaleString());
  }
}

function populateCategoryFilter() {
  const sel = document.getElementById('categoryFilter');
  if (!sel) return;
  const currentVal = sel.value;
  sel.innerHTML = '<option value="">All Categories</option>';
  if (allData?.categories) {
    Object.keys(allData.categories).forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      sel.appendChild(opt);
    });
  }
  sel.value = currentVal;
}

// ---- Filter products ----

function filterProducts(products) {
  const searchInput = document.getElementById('searchInput');
  const categoryFilter = document.getElementById('categoryFilter');
  
  const search = searchInput?.value.toLowerCase() || '';
  const cat = categoryFilter?.value || '';
  
  return products.filter(p =>
    (!search || p.title.toLowerCase().includes(search) || p.domain.includes(search)) &&
    (!cat || p.category === cat)
  );
}

// ---- Trending Page ----

function renderTrending() {
  const products = filterProducts(allData?.products || []);
  const maxScore = products.length ? Math.max(...products.map(p => p.trendScore || 0)) : 1;

  const byViews = [...products].sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0))[0];
  const byPurchases = [...products].sort((a, b) => (b.purchaseCount || 0) - (a.purchaseCount || 0))[0];
  const cats = allData?.categories || {};
  const topCat = Object.entries(cats).sort((a, b) => b[1] - a[1])[0];
  const rising = products.filter(p => p.isRising);

  setText('kpiMostViewed', byViews ? truncate(byViews.title, 24) : '-');
  setText('kpiMostPurchased', byPurchases && byPurchases.purchaseCount > 0 ? truncate(byPurchases.title, 24) : '-');
  setText('kpiTopCat', topCat ? topCat[0] : '-');
  setText('kpiRising', rising.length > 0 ? `${rising.length} rising` : '-');

  const body = document.getElementById('trendingBody');
  if (!body) return;
  
  if (!products.length) {
    body.innerHTML = '<tr><td colspan="9" class="empty-row">No products tracked yet. Browse shopping sites.</td></tr>';
    return;
  }

  body.innerHTML = products.slice(0, 100).map((p, i) => {
    const rClass = i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : '';
    const price = p.latestPrice ? `$${parseFloat(p.latestPrice).toFixed(2)}` : '-';
    const priceTrend = renderPriceTrend(p.priceTrend);
    const soldHtml = renderSoldDelta(p.soldDelta, p.latestSold);
    const risingBadge = p.isRising ? '<span class="rising-badge">Rising</span>' : '';
    const pct = maxScore > 0 ? Math.round(((p.trendScore || 0) / maxScore) * 100) : 0;

    return `
      <tr>
        <td><span class="rank-badge ${rClass}">${i + 1}</span></td>
        <td>
          <div class="product-cell">
            <span class="name" title="${escapeHtml(p.title)}">${escapeHtml(truncate(p.title, 50))} ${risingBadge}</span>
            <span class="domain">${escapeHtml(p.domain)}</span>
          </div>
        </td>
        <td><span class="cat-pill">${escapeHtml(p.category || 'General')}</span></td>
        <td>${escapeHtml(p.domain)}</td>
        <td>${price} ${priceTrend}</td>
        <td>${p.viewCount || 0} <span style="color:var(--text-muted);font-size:11px;">(${p.views7d || 0} week)</span></td>
        <td>${p.purchaseCount > 0 ? `<strong style="color:var(--success)">${p.purchaseCount}</strong>` : '0'}</td>
        <td>${soldHtml}</td>
        <td>
          <div class="score-bar-wrap">
            <div class="score-bar"><div class="fill" style="width:${pct}%"></div></div>
            <span class="score-val">${Math.round(p.trendScore || 0)}</span>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// ---- Rising Page ----

function renderRising() {
  const products = allData?.products?.filter(p => p.isRising && p.views7d >= 2) || [];
  const body = document.getElementById('risingBody');
  if (!body) return;

  if (!products.length) {
    body.innerHTML = '<tr><td colspan="6" class="empty-row">No breakout products detected yet.</td></tr>';
    return;
  }

  body.innerHTML = products.slice(0, 20).map((p, i) => {
    const price = p.latestPrice ? `$${parseFloat(p.latestPrice).toFixed(2)}` : '-';
    const priceTrend = renderPriceTrend(p.priceTrend);
    const soldHtml = renderSoldDelta(p.soldDelta, p.latestSold);

    return `
      <tr>
        <td><span class="rank-badge">${i + 1}</span></td>
        <td>
          <div class="product-cell">
            <span class="name" title="${escapeHtml(p.title)}">${escapeHtml(truncate(p.title, 50))}</span>
            <span class="domain">${escapeHtml(p.domain)}</span>
          </div>
        </td>
        <td><span class="cat-pill">${escapeHtml(p.category || 'General')}</span></td>
        <td>${price} ${priceTrend}</td>
        <td><strong style="color:var(--success)">${p.views7d || 0}</strong></td>
        <td>${soldHtml}</td>
      </tr>
    `;
  }).join('');
}

// ---- Categories Page ----

function renderCategories() {
  const cats = allData?.categories || {};
  const entries = Object.entries(cats).sort((a, b) => b[1] - a[1]);
  const labels = entries.map(e => e[0]);
  const values = entries.map(e => e[1]);

  destroyChart('catPie');
  destroyChart('catBar');

  const pieChart = document.getElementById('catPieChart');
  const barChart = document.getElementById('catBarChart');

  if (entries.length && pieChart && barChart) {
    const c = getChartColors();
    charts.catPie = new Chart(pieChart, {
      type: 'doughnut',
      data: { 
        labels: labels.slice(0, 10), 
        datasets: [{ 
          data: values.slice(0, 10), 
          backgroundColor: COLORS, 
          borderColor: c.border, 
          borderWidth: 2 
        }] 
      },
      options: { 
        responsive: true, 
        plugins: { 
          legend: { 
            position: 'right', 
            labels: { 
              color: c.label, 
              font: { size: 11 } 
            } 
          } 
        } 
      }
    });

    charts.catBar = new Chart(barChart, {
      type: 'bar',
      data: { 
        labels: labels.slice(0, 10), 
        datasets: [{ 
          label: 'Views', 
          data: values.slice(0, 10), 
          backgroundColor: COLORS.map(c => c + 'cc'), 
          borderColor: COLORS, 
          borderWidth: 1, 
          borderRadius: 6 
        }] 
      },
      options: { 
        responsive: true, 
        indexAxis: 'y', 
        plugins: { legend: { display: false } }, 
        scales: { 
          x: { ticks: { color: c.text }, grid: { color: c.grid } },
          y: { ticks: { color: c.label }, grid: { display: false } }
        }
      }
    });
  }

  const products = allData?.products || [];
  const catRising = {};
  products.forEach(p => { 
    if (p.isRising) { 
      const c = p.category || 'General'; 
      catRising[c] = (catRising[c] || 0) + 1; 
    } 
  });

  const catList = document.getElementById('catList');
  if (catList) {
    catList.innerHTML = entries.map(([name, count]) => {
      const risingCount = catRising[name] || 0;
      const badge = risingCount > 0 ? `<span class="rising-badge">${risingCount} rising</span>` : '';
      return `<div class="cat-tag">${escapeHtml(name)} <span>${count}</span> ${badge}</div>`;
    }).join('');
  }
}

// ---- Domains Page ----

function renderDomains() {
  const domains = allData?.domains || {};
  const entries = Object.entries(domains).sort((a, b) => b[1] - a[1]);
  const max = entries.length ? entries[0][1] : 1;

  destroyChart('domain');

  const domainChart = document.getElementById('domainChart');
  if (entries.length && domainChart) {
    const c = getChartColors();
    charts.domain = new Chart(domainChart, {
      type: 'bar',
      data: {
        labels: entries.slice(0, 12).map(e => e[0]),
        datasets: [{ 
          label: 'Products', 
          data: entries.slice(0, 12).map(e => e[1]), 
          backgroundColor: COLORS.map(c => c + 'bb'), 
          borderColor: COLORS, 
          borderWidth: 1, 
          borderRadius: 6 
        }]
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        plugins: { legend: { display: false } }, 
        scales: { 
          x: { ticks: { color: c.label }, grid: { color: c.grid } },
          y: { ticks: { color: c.text }, grid: { color: c.grid }, beginAtZero: true }
        }
      }
    });
  }

  const domainList = document.getElementById('domainList');
  if (domainList) {
    domainList.innerHTML = entries.map(([domain, count]) => `
      <div class="domain-card">
        <div class="domain-name">${escapeHtml(domain)}</div>
        <div class="domain-count">${count} product${count !== 1 ? 's' : ''}</div>
        <div class="domain-bar"><div class="domain-fill" style="width:${Math.round((count / max) * 100)}%"></div></div>
      </div>
    `).join('');
  }
}

// ---- Activity Page ----

function renderActivity() {
  const daily = allData?.daily || {};
  const days = getLast14Days();
  const viewData = days.map(d => (daily[d] || {}).views || 0);
  const purchaseData = days.map(d => (daily[d] || {}).purchases || 0);
  const labels = days.map(d => d.slice(5));

  destroyChart('activity');

  const activityChart = document.getElementById('activityChart');
  if (activityChart) {
    const c = getChartColors();
    charts.activity = new Chart(activityChart, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { 
            label: 'Views', 
            data: viewData, 
            borderColor: c.primary, 
            backgroundColor: c.primary + '15', 
            borderWidth: 2, 
            fill: true, 
            tension: 0.4, 
            pointRadius: 3, 
            pointBackgroundColor: c.primary 
          },
          { 
            label: 'Purchases', 
            data: purchaseData, 
            borderColor: c.success, 
            backgroundColor: c.success + '15', 
            borderWidth: 2, 
            fill: true, 
            tension: 0.4, 
            pointRadius: 3, 
            pointBackgroundColor: c.success 
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: c.label } } },
        scales: {
          x: { ticks: { color: c.text }, grid: { color: c.grid } },
          y: { ticks: { color: c.text }, grid: { color: c.grid }, beginAtZero: true }
        }
      }
    });
  }

  const totalViews = allData?.totalViews || 0;
  const totalPurchases = allData?.totalPurchases || 0;
  const purchasePct = totalViews > 0 ? Math.round((totalPurchases / totalViews) * 100) : 0;

  const funnelWrap = document.getElementById('funnelWrap');
  if (funnelWrap) {
    funnelWrap.innerHTML = `
      <div class="funnel-row">
        <span class="funnel-label">Product Views</span>
        <div class="funnel-bar-bg"><div class="funnel-bar-fill views-fill" style="width:100%">${totalViews}</div></div>
        <span class="funnel-num">${totalViews}</span>
      </div>
      <div class="funnel-row">
        <span class="funnel-label">Purchases</span>
        <div class="funnel-bar-bg"><div class="funnel-bar-fill purchases-fill" style="width:${Math.max(purchasePct, totalPurchases > 0 ? 5 : 0)}%">${totalPurchases}</div></div>
        <span class="funnel-num">${totalPurchases}</span>
      </div>
      <div class="funnel-note" style="margin-top:8px;font-size:13px;color:var(--text-muted);">Conversion signal rate: <strong style="color:var(--success)">${purchasePct}%</strong></div>
    `;
  }
}

// ---- Controls ----

function setupControls() {
  const refreshBtn = document.getElementById('refreshBtn');
  if (refreshBtn) refreshBtn.addEventListener('click', refresh);

  const searchInput = document.getElementById('searchInput');
  if (searchInput) searchInput.addEventListener('input', renderTrending);

  const categoryFilter = document.getElementById('categoryFilter');
  if (categoryFilter) categoryFilter.addEventListener('change', renderTrending);

  // Export CSV
  const exportBtn = document.getElementById('exportBtn');
  if (exportBtn) exportBtn.addEventListener('click', exportCSV);

  // Export JSON
  const exportJsonBtn = document.getElementById('exportJsonBtn');
  if (exportJsonBtn) exportJsonBtn.addEventListener('click', exportJSON);

  // Import JSON
  const importJsonBtn = document.getElementById('importJsonBtn');
  if (importJsonBtn) {
    importJsonBtn.addEventListener('click', () => {
      const fileInput = document.getElementById('fileInput');
      if (fileInput) fileInput.click();
    });
  }

  const fileInput = document.getElementById('fileInput');
  if (fileInput) fileInput.addEventListener('change', importJSON);

  // Clear data
  const clearAllBtn = document.getElementById('clearAllBtn');
  if (clearAllBtn) clearAllBtn.addEventListener('click', clearData);
}

// ---- Export / Import ----

function exportCSV() {
  const products = allData?.products || [];
  let csv = 'Rank,Title,Category,Domain,Price,Views,Purchases,TrendScore,Rising\n';
  products.forEach((p, i) => {
    csv += `${i+1},"${escapeCsv(p.title)}","${p.category}","${p.domain}","${p.latestPrice || ''}",${p.viewCount || 0},${p.purchaseCount || 0},${Math.round(p.trendScore || 0)},${p.isRising ? 'Yes' : 'No'}\n`;
  });
  downloadFile(csv, `tracker-${date()}.csv`, 'text/csv');
}

function exportJSON() {
  chrome.storage.local.get(null, (data) => {
    const json = JSON.stringify(data, null, 2);
    downloadFile(json, `tracker-${date()}.json`, 'application/json');
  });
}

function importJSON(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const data = JSON.parse(e.target.result);
      chrome.storage.local.set(data, () => {
        alert('Data imported successfully! Refreshing...');
        location.reload();
      });
    } catch (err) {
      alert('Invalid JSON: ' + err.message);
    }
  };
  reader.readAsText(file);
  // Reset file input
  event.target.value = '';
}

function clearData() {
  if (!confirm('Delete ALL data? This cannot be undone.')) return;
  chrome.storage.local.clear(() => {
    alert('All data cleared.');
    location.reload();
  });
}

// ---- Helpers ----

function renderPriceTrend(priceTrend) {
  if (priceTrend === null || priceTrend === undefined) return '';
  if (priceTrend <= -5) return `<span class="price-down">-${Math.abs(priceTrend)}%</span>`;
  if (priceTrend >= 5) return `<span class="price-up">+${priceTrend}%</span>`;
  return '';
}

function renderSoldDelta(soldDelta, latestSold) {
  if (soldDelta !== null && soldDelta > 0) return `<span class="sold-delta">+${soldDelta}</span>`;
  if (latestSold !== null) return `${latestSold}`;
  return '-';
}

function destroyChart(key) {
  if (charts[key]) { 
    charts[key].destroy(); 
    delete charts[key]; 
  }
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function truncate(str, n) {
  return str && str.length > n ? str.substring(0, n) + '...' : (str || '');
}

function escapeHtml(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function escapeCsv(str) {
  return String(str || '').replace(/"/g, '""');
}

function date() {
  return new Date().toISOString().split('T')[0];
}

function getLast14Days() {
  return Array.from({ length: 14 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (13 - i));
    return d.toISOString().split('T')[0];
  });
}

function getChartColors() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark' ||
                 window.matchMedia('(prefers-color-scheme: dark)').matches;
  return {
    grid: isDark ? '#2a2a2a' : '#e5e5e5',
    text: isDark ? '#a3a3a3' : '#737373',
    label: isDark ? '#f5f5f5' : '#171717',
    primary: isDark ? '#a78bfa' : '#6c47ff',
    success: isDark ? '#34d399' : '#22c55e',
    border: isDark ? '#1a1a1a' : '#fff',
  };
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; 
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

console.log('[Options] Dashboard loaded successfully');