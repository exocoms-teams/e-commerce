
let allData = null;
let charts = {};

const COLORS = [
  '#6c47ff','#a855f7','#06b6d4','#10b981','#f59e0b',
  '#f87171','#34d399','#60a5fa','#e879f9','#fb923c'
];

// ---- Init ----

document.addEventListener('DOMContentLoaded', async () => {
  setupNav();
  await refresh();
  setupControls();
});

async function refresh() {
  allData = await sendMessage({ action: 'getData' });
  if (!allData) return;
  updateSidebar();
  renderCurrentPage();
}

// ---- Navigation ----

function setupNav() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const pageId = 'page-' + btn.dataset.page;
      document.getElementById(pageId).classList.add('active');
      document.getElementById('pageTitle').textContent = btn.textContent;
      renderCurrentPage();
    });
  });
}

function renderCurrentPage() {
  const active = document.querySelector('.page.active');
  if (!active || !allData) return;
  const id = active.id;
  if (id === 'page-trending') renderTrending();
  if (id === 'page-categories') renderCategories();
  if (id === 'page-domains') renderDomains();
  if (id === 'page-activity') renderActivity();
}

// ---- Sidebar ----

function updateSidebar() {
  setText('sTotal', allData.totalProducts || 0);
  setText('sViews', allData.totalViews || 0);
  setText('sPurchases', allData.totalPurchases || 0);
  const updated = allData.lastUpdated ? new Date(allData.lastUpdated).toLocaleTimeString() : '--';
  setText('sUpdated', updated);
}

// ---- Trending Page ----

function renderTrending() {
  const products = filterProducts(allData.products || []);

  // KPIs
  const byViews = [...products].sort((a, b) => b.viewCount - a.viewCount)[0];
  const byPurchases = [...products].sort((a, b) => b.purchaseCount - a.purchaseCount)[0];

  setText('kpiMostViewed', byViews ? truncate(byViews.title, 24) : '-');
  setText('kpiMostPurchased', byPurchases && byPurchases.purchaseCount > 0 ? truncate(byPurchases.title, 24) : '-');

  const cats = allData.categories || {};
  const topCat = Object.entries(cats).sort((a, b) => b[1] - a[1])[0];
  setText('kpiTopCat', topCat ? topCat[0] : '-');

  const domains = allData.domains || {};
  const topDomain = Object.entries(domains).sort((a, b) => b[1] - a[1])[0];
  setText('kpiTopStore', topDomain ? topDomain[0] : '-');

  // Table
  const maxScore = products.length ? products[0].trendScore : 1;
  const body = document.getElementById('trendingBody');

  if (!products.length) {
    body.innerHTML = '<tr><td colspan="8" class="empty-row">No products tracked yet. Browse shopping sites.</td></tr>';
    return;
  }

  body.innerHTML = products.slice(0, 100).map((p, i) => {
    const rClass = i === 0 ? 'r1' : i === 1 ? 'r2' : i === 2 ? 'r3' : '';
    const price = p.latestPrice ? `$${parseFloat(p.latestPrice).toFixed(2)}` : '-';
    const pct = maxScore > 0 ? Math.round((p.trendScore / maxScore) * 100) : 0;
    return `
      <tr>
        <td><span class="rank-badge ${rClass}">${i + 1}</span></td>
        <td>
          <div class="product-cell">
            <span class="product-name" title="${esc(p.title)}">${esc(truncate(p.title, 50))}</span>
            <span class="product-url">${esc(p.domain)}</span>
          </div>
        </td>
        <td><span class="cat-pill">${esc(p.category || 'General')}</span></td>
        <td>${esc(p.domain)}</td>
        <td>${price}</td>
        <td>${p.viewCount}</td>
        <td>${p.purchaseCount > 0 ? `<strong style="color:var(--success)">${p.purchaseCount}</strong>` : '0'}</td>
        <td>
          <div class="score-bar-wrap">
            <div class="score-bar"><div class="score-fill" style="width:${pct}%"></div></div>
            <span class="score-val">${Math.round(p.trendScore)}</span>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// ---- Categories Page ----

function renderCategories() {
  const cats = allData.categories || {};
  const entries = Object.entries(cats).sort((a, b) => b[1] - a[1]);
  const labels = entries.map(e => e[0]);
  const values = entries.map(e => e[1]);

  destroyChart('catPie');
  destroyChart('catBar');

  if (entries.length === 0) return;

  charts.catPie = new Chart(document.getElementById('catPieChart'), {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: COLORS, borderColor: '#13131a', borderWidth: 3 }]
    },
    options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'right', labels: { color: '#e4e4f0', font: { size: 11 } } } } }
  });

  charts.catBar = new Chart(document.getElementById('catBarChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'Product Views', data: values, backgroundColor: COLORS.map(c => c + 'cc'), borderColor: COLORS, borderWidth: 1, borderRadius: 6 }]
    },
    options: {
      responsive: true, indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: { x: { ticks: { color: '#6b7280' }, grid: { color: '#25253a' } }, y: { ticks: { color: '#e4e4f0' }, grid: { display: false } } }
    }
  });

  document.getElementById('catList').innerHTML = entries.map(([name, count], i) =>
    `<div class="cat-tag">${name} <span>${count}</span></div>`
  ).join('');
}

// ---- Domains Page ----

function renderDomains() {
  const domains = allData.domains || {};
  const entries = Object.entries(domains).sort((a, b) => b[1] - a[1]);
  const max = entries.length ? entries[0][1] : 1;

  destroyChart('domain');

  if (entries.length === 0) return;

  charts.domain = new Chart(document.getElementById('domainChart'), {
    type: 'bar',
    data: {
      labels: entries.slice(0, 12).map(e => e[0]),
      datasets: [{
        label: 'Products Detected',
        data: entries.slice(0, 12).map(e => e[1]),
        backgroundColor: COLORS.map(c => c + 'bb'),
        borderColor: COLORS,
        borderWidth: 1,
        borderRadius: 8,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#e4e4f0' }, grid: { color: '#25253a' } },
        y: { ticks: { color: '#6b7280' }, grid: { color: '#25253a' }, beginAtZero: true }
      }
    }
  });

  document.getElementById('domainList').innerHTML = entries.map(([domain, count], i) => `
    <div class="domain-card">
      <span class="domain-name">${domain}</span>
      <span class="domain-count">${count} product${count !== 1 ? 's' : ''} detected</span>
      <div class="domain-bar"><div class="domain-fill" style="width:${Math.round((count/max)*100)}%"></div></div>
    </div>
  `).join('');
}

// ---- Activity Page ----

function renderActivity() {
  const daily = allData.daily || {};
  const days = getLast14Days();

  const viewData = days.map(d => (daily[d] || {}).views || 0);
  const purchaseData = days.map(d => (daily[d] || {}).purchases || 0);
  const labels = days.map(d => d.slice(5)); // MM-DD

  destroyChart('activity');

  charts.activity = new Chart(document.getElementById('activityChart'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Views',
          data: viewData,
          borderColor: '#6c47ff',
          backgroundColor: 'rgba(108,71,255,0.08)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#6c47ff',
        },
        {
          label: 'Purchases',
          data: purchaseData,
          borderColor: '#34d399',
          backgroundColor: 'rgba(52,211,153,0.08)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#34d399',
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#e4e4f0' } } },
      scales: {
        x: { ticks: { color: '#6b7280' }, grid: { color: '#25253a' } },
        y: { ticks: { color: '#6b7280' }, grid: { color: '#25253a' }, beginAtZero: true }
      }
    }
  });

  // Funnel
  const totalViews = allData.totalViews || 0;
  const totalPurchases = allData.totalPurchases || 0;
  const viewPct = 100;
  const purchasePct = totalViews > 0 ? Math.round((totalPurchases / totalViews) * 100) : 0;

  document.getElementById('funnelWrap').innerHTML = `
    <div class="funnel-row">
      <span class="funnel-label">Product Views</span>
      <div class="funnel-bar-bg">
        <div class="funnel-bar-fill views-fill" style="width:${viewPct}%">${totalViews}</div>
      </div>
      <span class="funnel-num">${totalViews}</span>
    </div>
    <div class="funnel-row">
      <span class="funnel-label">Purchases</span>
      <div class="funnel-bar-bg">
        <div class="funnel-bar-fill purchases-fill" style="width:${Math.max(purchasePct, totalPurchases > 0 ? 5 : 0)}%">${totalPurchases}</div>
      </div>
      <span class="funnel-num">${totalPurchases}</span>
    </div>
    <p style="margin-top:8px;font-size:12px;color:var(--muted)">
      Conversion signal rate: <strong style="color:var(--success)">${purchasePct}%</strong>
    </p>
  `;
}

// ---- Controls ----

function setupControls() {
  document.getElementById('refreshBtn').addEventListener('click', refresh);

  document.getElementById('searchInput').addEventListener('input', () => renderTrending());
  document.getElementById('categoryFilter').addEventListener('change', () => renderTrending());

  // Populate category filter
  const sel = document.getElementById('categoryFilter');
  const cats = Object.keys(allData?.categories || {});
  cats.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    sel.appendChild(opt);
  });

  document.getElementById('exportBtn').addEventListener('click', exportCSV);
  document.getElementById('exportJsonBtn').addEventListener('click', exportJSON);
  document.getElementById('importJsonBtn').addEventListener('click', () => document.getElementById('fileInput').click());
  document.getElementById('fileInput').addEventListener('change', importJSON);
  document.getElementById('clearAllBtn').addEventListener('click', clearData);
}

function filterProducts(products) {
  const search = document.getElementById('searchInput')?.value.toLowerCase() || '';
  const cat = document.getElementById('categoryFilter')?.value || '';
  return products.filter(p =>
    (!search || p.title.toLowerCase().includes(search) || p.domain.includes(search)) &&
    (!cat || p.category === cat)
  );
}

// ---- Export / Import ----

function exportCSV() {
  const products = allData?.products || [];
  let csv = 'Rank,Title,Category,Domain,Price,Views,Purchases,TrendScore,FirstSeen,LastSeen\n';
  products.forEach((p, i) => {
    csv += `${i+1},"${esc2(p.title)}","${p.category}","${p.domain}","${p.latestPrice || ''}",${p.viewCount},${p.purchaseCount},${Math.round(p.trendScore)},"${p.firstSeen}","${p.lastSeen}"\n`;
  });
  downloadFile(csv, `tracker-${date()}.csv`, 'text/csv');
}

function exportJSON() {
  downloadFile(JSON.stringify(allData, null, 2), `tracker-${date()}.json`, 'application/json');
}

function importJSON(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const data = JSON.parse(e.target.result);
      chrome.storage.local.set(data, () => {
        alert('Data imported. Refreshing...');
        location.reload();
      });
    } catch (err) {
      alert('Invalid JSON file: ' + err.message);
    }
  };
  reader.readAsText(file);
}

function clearData() {
  if (!confirm('Delete ALL tracking data? This cannot be undone.')) return;
  sendMessage({ action: 'clearData' }).then(() => location.reload());
}

// ---- Helpers ----

function sendMessage(msg) {
  return new Promise(resolve => {
    chrome.runtime.sendMessage(msg, r => {
      if (chrome.runtime.lastError) resolve(null);
      else resolve(r);
    });
  });
}

function destroyChart(key) {
  if (charts[key]) { charts[key].destroy(); delete charts[key]; }
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function truncate(str, n) {
  return str && str.length > n ? str.substring(0, n) + '...' : (str || '');
}

function esc(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function esc2(str) { return String(str || '').replace(/"/g, '""'); }

function date() { return new Date().toISOString().split('T')[0]; }

function getLast14Days() {
  const days = [];
  for (let i = 13; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    days.push(d.toISOString().split('T')[0]);
  }
  return days;
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
