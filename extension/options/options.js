// options.js - Complete and fixed
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

  const mobileToggle = document.getElementById('mobileToggle');
  if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      if (sidebar) sidebar.classList.toggle('open');
    });
  }
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
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');

  try {
    const response = await fetch('http://localhost:5000/api/products?limit=200');
    if (!response.ok) throw new Error('API error');
    const data = await response.json();
    allData = data;

    if (statusDot) statusDot.className = 'status-dot online';
    if (statusText) statusText.textContent = 'Connected';

    updateSidebar();
    renderCurrentPage();

    const risingCount = allData.products?.filter(p => p.is_rising).length || 0;
    const badge = document.getElementById('risingBadge');
    if (badge) badge.textContent = risingCount;

    populateCategoryFilter();
  } catch (e) {
    if (statusDot) statusDot.className = 'status-dot offline';
    if (statusText) statusText.textContent = 'Backend offline — run: python app.py';
    const body = document.getElementById('trendingBody');
    if (body) {
      body.innerHTML = '<tr><td colspan="9" class="empty-row">⚠️ Backend not running. Start with: python app.py</td></tr>';
    }
  }
}

function updateSidebar() {
  setText('sTotal', allData?.total_products || 0);
  setText('sViews', allData?.total_views || 0);
  setText('sPurchases', allData?.total_purchases || 0);
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

// ---- Trending ----

function renderTrending() {
  const products = filterProducts(allData?.products || []);
  const maxScore = products.length ? products[0].trend_score : 1;

  const byViews = [...products].sort((a, b) => b.view_count - a.view_count)[0];
  const byPurchases = [...products].sort((a, b) => b.purchase_count - a.purchase_count)[0];
  const cats = allData?.categories || {};
  const topCat = Object.entries(cats).sort((a, b) => b[1] - a[1])[0];
  const rising = products.filter(p => p.is_rising);

  setText('kpiMostViewed', byViews ? truncate(byViews.title, 24) : '-');
  setText('kpiMostPurchased', byPurchases && byPurchases.purchase_count > 0 ? truncate(byPurchases.title, 24) : '-');
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
    const price = p.latest_price ? `$${parseFloat(p.latest_price).toFixed(2)}` : '-';
    const priceTrend = renderPriceTrend(p.price_trend);
    const soldHtml = renderSoldDelta(p.sold_delta, p.latest_sold);
    const risingBadge = p.is_rising ? '<span class="rising-badge">Rising</span>' : '';
    const pct = maxScore > 0 ? Math.round((p.trend_score / maxScore) * 100) : 0;

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
        <td>${p.view_count} <span style="color:var(--text-muted);font-size:11px;">(${p.views_7d || 0} week)</span></td>
        <td>${p.purchase_count > 0 ? `<strong style="color:var(--success)">${p.purchase_count}</strong>` : '0'}</td>
        <td>${soldHtml}</td>
        <td>
          <div class="score-bar-wrap">
            <div class="score-bar"><div class="fill" style="width:${pct}%"></div></div>
            <span class="score-val">${Math.round(p.trend_score)}</span>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// ---- Rising ----

function renderRising() {
  const products = allData?.products?.filter(p => p.is_rising && p.views_7d >= 2) || [];
  const body = document.getElementById('risingBody');
  if (!body) return;

  if (!products.length) {
    body.innerHTML = '<tr><td colspan="6" class="empty-row">No breakout products detected yet.</td></tr>';
    return;
  }

  body.innerHTML = products.slice(0, 20).map((p, i) => {
    const price = p.latest_price ? `$${parseFloat(p.latest_price).toFixed(2)}` : '-';
    const priceTrend = renderPriceTrend(p.price_trend);
    const soldHtml = renderSoldDelta(p.sold_delta, p.latest_sold);

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
        <td><strong style="color:var(--success)">${p.views_7d || 0}</strong></td>
        <td>${soldHtml}</td>
      </tr>
    `;
  }).join('');
}

// ---- Categories ----

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
    charts.catPie = new Chart(pieChart, {
      type: 'doughnut',
      data: { 
        labels: labels.slice(0, 10), 
        datasets: [{ 
          data: values.slice(0, 10), 
          backgroundColor: COLORS, 
          borderColor: '#161b22', 
          borderWidth: 2 
        }] 
      },
      options: { 
        responsive: true, 
        plugins: { 
          legend: { 
            position: 'right', 
            labels: { 
              color: getChartColors().label, 
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
          x: { ticks: { color: getChartColors().text }, grid: { color: getChartColors().grid } },
          y: { ticks: { color: getChartColors().label }, grid: { display: false } }
        }
      }
    });
  }

  const products = allData?.products || [];
  const catRising = {};
  products.forEach(p => { 
    if (p.is_rising) { 
      const c = p.category || 'General'; 
      catRising[c] = (catRising[c] || 0) + 1; 
    } 
  });

  const catList = document.getElementById('catList');
  if (catList) {
    catList.innerHTML = entries.map(([name, count]) => {
      const risingCount = catRising[name] || 0;
      const badge = risingCount > 0 ? `<span class="rising-badge">${risingCount} rising</span>` : '';
      return `<div class="tag">${escapeHtml(name)} <span class="count">${count}</span> ${badge}</div>`;
    }).join('');
  }
}

// ---- Domains ----

function renderDomains() {
  const domains = allData?.domains || {};
  const entries = Object.entries(domains).sort((a, b) => b[1] - a[1]);
  const max = entries.length ? entries[0][1] : 1;

  destroyChart('domain');

  const domainChart = document.getElementById('domainChart');
  if (entries.length && domainChart) {
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
          x: { ticks: { color: getChartColors().label }, grid: { color: getChartColors().grid } },
          y: { ticks: { color: getChartColors().text }, grid: { color: getChartColors().grid }, beginAtZero: true }
        }
      }
    });
  }

  const domainList = document.getElementById('domainList');
  if (domainList) {
    domainList.innerHTML = entries.map(([domain, count]) => `
      <div class="domain-card">
        <div class="name">${escapeHtml(domain)}</div>
        <div class="count">${count} product${count !== 1 ? 's' : ''}</div>
        <div class="bar"><div class="fill" style="width:${Math.round((count / max) * 100)}%"></div></div>
      </div>
    `).join('');
  }
}

// ---- Activity ----

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

  const totalViews = allData?.total_views || 0;
  const totalPurchases = allData?.total_purchases || 0;
  const purchasePct = totalViews > 0 ? Math.round((totalPurchases / totalViews) * 100) : 0;

  const funnelWrap = document.getElementById('funnelWrap');
  if (funnelWrap) {
    funnelWrap.innerHTML = `
      <div class="funnel-row">
        <span class="label">Product Views</span>
        <div class="bar-bg"><div class="bar-fill views" style="width:100%">${totalViews}</div></div>
        <span class="num">${totalViews}</span>
      </div>
      <div class="funnel-row">
        <span class="label">Purchases</span>
        <div class="bar-bg"><div class="bar-fill purchases" style="width:${Math.max(purchasePct, totalPurchases > 0 ? 5 : 0)}%">${totalPurchases}</div></div>
        <span class="num">${totalPurchases}</span>
      </div>
      <div class="funnel-note">Conversion signal rate: <strong style="color:var(--success)">${purchasePct}%</strong></div>
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

  const exportBtn = document.getElementById('exportBtn');
  if (exportBtn) exportBtn.addEventListener('click', exportCSV);

  const exportJsonBtn = document.getElementById('exportJsonBtn');
  if (exportJsonBtn) exportJsonBtn.addEventListener('click', exportJSON);

  const importJsonBtn = document.getElementById('importJsonBtn');
  if (importJsonBtn) {
    importJsonBtn.addEventListener('click', () => {
      const fileInput = document.getElementById('fileInput');
      if (fileInput) fileInput.click();
    });
  }

  const fileInput = document.getElementById('fileInput');
  if (fileInput) fileInput.addEventListener('change', importJSON);

  const clearAllBtn = document.getElementById('clearAllBtn');
  if (clearAllBtn) clearAllBtn.addEventListener('click', clearData);

  // Populate category filter
  if (allData?.categories) {
    populateCategoryFilter();
  }
}

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

// ---- Export / Import ----

function exportCSV() {
  const products = allData?.products || [];
  let csv = 'Rank,Title,Category,Domain,Price,Views,Purchases,TrendScore,Rising\n';
  products.forEach((p, i) => {
    csv += `${i+1},"${escapeCsv(p.title)}","${p.category}","${p.domain}","${p.latest_price || ''}",${p.view_count},${p.purchase_count},${Math.round(p.trend_score)},${p.is_rising ? 'Yes' : 'No'}\n`;
  });
  downloadFile(csv, `tracker-${date()}.csv`, 'text/csv');
}

function exportJSON() {
  fetch('http://localhost:5000/api/export')
    .then(r => r.json())
    .then(data => downloadFile(JSON.stringify(data, null, 2), `tracker-${date()}.json`, 'application/json'))
    .catch(() => alert('Backend not running. Start with: python app.py'));
}

function importJSON(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const data = JSON.parse(e.target.result);
      fetch('http://localhost:5000/api/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }).then(() => {
        alert('Data imported. Refreshing...');
        location.reload();
      }).catch(() => alert('Backend not running'));
    } catch (err) {
      alert('Invalid JSON: ' + err.message);
    }
  };
  reader.readAsText(file);
}

function clearData() {
  if (!confirm('Delete ALL data? This cannot be undone.')) return;
  fetch('http://localhost:5000/api/clear', { method: 'DELETE' })
    .then(() => location.reload())
    .catch(() => alert('Backend not running'));
}

function escapeCsv(str) {
  return String(str || '').replace(/"/g, '""');
}

function date() {
  return new Date().toISOString().split('T')[0];
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; 
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

console.log('[Options] Dashboard loaded successfully');