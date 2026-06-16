// popup.js - Complete with theme support
let allData = null;
let isTracking = true;

// ---- Theme ----

function getStoredTheme() {
  const saved = localStorage.getItem('tracker-theme');
  if (saved === 'light' || saved === 'dark') return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('tracker-theme', theme);
}

// Initialize theme
applyTheme(getStoredTheme());

// ---- Init ----

document.addEventListener('DOMContentLoaded', async () => {
  await loadData();
  setupListeners();
  updateTrackingStatus();
});

// ---- Data Loading ----

async function loadData() {
  const data = await sendMessage({ action: 'getData' });
  if (!data) return;

  allData = data;
  document.getElementById('statProducts').textContent = data.totalProducts || 0;
  document.getElementById('statViews').textContent = formatNumber(data.totalViews || 0);
  document.getElementById('statPurchases').textContent = formatNumber(data.totalPurchases || 0);

  renderTrending(data.topProducts || []);
}

function renderTrending(products) {
  const list = document.getElementById('trendingList');
  if (!products.length) {
    list.innerHTML = '<div class="empty-state">Browse shopping sites to collect data.</div>';
    return;
  }

  list.innerHTML = products.slice(0, 6).map((p, i) => {
    const rankClass = i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : '';
    const score = p.purchaseCount > 0 ? '🔥 ' : '';
    const price = p.latestPrice ? `$${parseFloat(p.latestPrice).toFixed(2)}` : '';
    const meta = [p.domain, price, p.category].filter(Boolean).join(' · ');

    return `
      <div class="trending-item">
        <span class="trending-rank ${rankClass}">#${i + 1}</span>
        <div class="trending-info">
          <div class="trending-title" title="${escapeHtml(p.title)}">${escapeHtml(p.title)}</div>
          <div class="trending-meta">${escapeHtml(meta)}</div>
        </div>
        <span class="trending-score">${score}${Math.round(p.trendScore)}</span>
      </div>
    `;
  }).join('');
}

// ---- Tracking Status ----

async function updateTrackingStatus() {
  const response = await sendMessage({ action: 'getTrackingStatus' });
  if (!response) return;
  
  isTracking = response.tracking !== false;
  const dot = document.getElementById('statusDot');
  const text = document.getElementById('statusText');
  const btn = document.getElementById('toggleBtn');
  
  if (isTracking) {
    dot.className = 'status-dot active';
    text.textContent = 'Tracking: Active';
    btn.textContent = 'Pause';
    btn.className = 'toggle-btn';
  } else {
    dot.className = 'status-dot paused';
    text.textContent = 'Tracking: Paused';
    btn.textContent = 'Resume';
    btn.className = 'toggle-btn paused';
  }
}

// ---- Listeners ----

function setupListeners() {
  document.getElementById('optionsBtn').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });

  document.getElementById('toggleBtn').addEventListener('click', async () => {
    await sendMessage({ action: 'toggleTracking' });
    updateTrackingStatus();
    setTimeout(loadData, 500);
  });

  document.getElementById('openDashboard').addEventListener('click', () => {
    chrome.tabs.create({ url: 'http://localhost:5000/dashboard/' });
  });

  document.getElementById('manualSave').addEventListener('click', () => {
    const title = document.getElementById('manualTitle').value.trim();
    const price = parseFloat(document.getElementById('manualPrice').value) || null;
    const category = document.getElementById('manualCategory').value.trim() || 'General';

    if (!title) {
      document.getElementById('manualTitle').focus();
      return;
    }

    sendMessage({
      action: 'addManualProduct',
      product: {
        title,
        price,
        category,
        domain: 'manual',
        url: '',
        timestamp: new Date().toISOString(),
      }
    });

    document.getElementById('manualTitle').value = '';
    document.getElementById('manualPrice').value = '';
    document.getElementById('manualCategory').value = '';

    setTimeout(loadData, 300);
  });
}

// ---- Helpers ----

function sendMessage(msg) {
  return new Promise(resolve => {
    chrome.runtime.sendMessage(msg, response => {
      if (chrome.runtime.lastError) resolve(null);
      else resolve(response);
    });
  });
}

function formatNumber(n) {
  return n >= 1000 ? (n / 1000).toFixed(1) + 'k' : String(n);
}

function escapeHtml(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}