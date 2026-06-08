// Popup logic
document.addEventListener('DOMContentLoaded', async () => {
  await loadData();
  setupListeners();
});

async function loadData() {
  const data = await sendMessage({ action: 'getData' });
  if (!data) return;

  document.getElementById('statProducts').textContent = data.totalProducts || 0;
  document.getElementById('statViews').textContent = fmt(data.totalViews || 0);
  document.getElementById('statPurchases').textContent = fmt(data.totalPurchases || 0);

  renderTrending(data.topProducts || []);
}

function renderTrending(products) {
  const list = document.getElementById('trendingList');
  if (!products.length) {
    list.innerHTML = '<p class="empty">Browse shopping sites to collect data.</p>';
    return;
  }

  list.innerHTML = products.slice(0, 8).map((p, i) => {
    const rankClass = i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : '';
    const fire = p.purchaseCount > 0 ? '🔥' : p.viewCount > 5 ? '📈' : '';
    const price = p.latestPrice ? `$${parseFloat(p.latestPrice).toFixed(2)}` : '';
    const meta = [p.domain, price, p.category].filter(Boolean).join(' · ');
    return `
      <div class="trending-item">
        <span class="rank ${rankClass}">#${i + 1}</span>
        <div class="item-info">
          <div class="item-title" title="${esc(p.title)}">${esc(p.title)}</div>
          <div class="item-meta">${esc(meta)}</div>
        </div>
        <span class="item-score">${fire} ${Math.round(p.trendScore)}</span>
      </div>
    `;
  }).join('');
}

function setupListeners() {
  document.getElementById('optionsBtn').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });

  document.getElementById('openDashboard').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
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

function sendMessage(msg) {
  return new Promise(resolve => {
    chrome.runtime.sendMessage(msg, response => {
      if (chrome.runtime.lastError) resolve(null);
      else resolve(response);
    });
  });
}

function fmt(n) {
  return n >= 1000 ? (n / 1000).toFixed(1) + 'k' : String(n);
}

function esc(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
