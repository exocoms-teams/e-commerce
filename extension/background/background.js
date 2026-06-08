// ============================================================
// MINEA TRACKER - Background Service Worker
// Central data store and aggregation engine
// ============================================================

console.log('[Minea Tracker] Background service worker started');

// ---- Message handler ----

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'productDetected') {
    handleProductDetected(request.product, request.isPurchase, request.source);
  }
  if (request.action === 'getData') {
    getData().then(sendResponse);
    return true; // async response
  }
  if (request.action === 'clearData') {
    chrome.storage.local.clear(() => sendResponse({ success: true }));
    return true;
  }
  if (request.action === 'addManualProduct') {
    handleProductDetected(request.product, true, request.product.domain || 'manual');
    sendResponse({ success: true });
  }
});

// ---- Core logic ----

async function handleProductDetected(product, isPurchase, source) {
  if (!product || !product.title) return;

  const store = await getStore();

  // Create a stable product key
  const key = makeKey(product.title, product.domain);

  if (!store.products[key]) {
    store.products[key] = {
      id: key,
      title: product.title,
      domain: product.domain,
      category: product.category,
      image: product.image,
      url: product.url,
      firstSeen: product.timestamp,
      lastSeen: product.timestamp,
      viewCount: 0,
      purchaseCount: 0,
      prices: [],
      ratings: [],
      reviews: [],
      soldCounts: [],
    };
  }

  const entry = store.products[key];

  // Update view count always
  entry.viewCount += 1;
  entry.lastSeen = product.timestamp;

  // Update purchase count on confirmed purchase
  if (isPurchase) {
    entry.purchaseCount += 1;
  }

  // Track price history
  if (product.price && product.price > 0) {
    entry.prices.push({ value: product.price, date: product.timestamp });
    if (entry.prices.length > 50) entry.prices = entry.prices.slice(-50);
  }

  // Track ratings / reviews
  if (product.rating) entry.ratings.push(product.rating);
  if (product.reviews) entry.reviews.push(product.reviews);
  if (product.soldCount) entry.soldCounts.push(product.soldCount);

  // Keep arrays slim
  ['ratings', 'reviews', 'soldCounts'].forEach(k => {
    if (entry[k].length > 20) entry[k] = entry[k].slice(-20);
  });

  // Update category stats
  const cat = product.category || 'General';
  store.categories[cat] = (store.categories[cat] || 0) + 1;

  // Update domain stats
  store.domains[source] = (store.domains[source] || 0) + 1;

  // Update daily activity
  const today = new Date().toISOString().split('T')[0];
  if (!store.daily[today]) store.daily[today] = { views: 0, purchases: 0 };
  store.daily[today].views += 1;
  if (isPurchase) store.daily[today].purchases += 1;

  store.lastUpdated = new Date().toISOString();

  await saveStore(store);

  // Notify popup if open
  if (isPurchase) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Purchase Detected!',
      message: `${product.title.substring(0, 60)} tracked as a purchase.`,
      priority: 1,
    });
  }
}

// ---- Storage helpers ----

async function getStore() {
  return new Promise(resolve => {
    chrome.storage.local.get(['products', 'categories', 'domains', 'daily', 'lastUpdated'], data => {
      resolve({
        products: data.products || {},
        categories: data.categories || {},
        domains: data.domains || {},
        daily: data.daily || {},
        lastUpdated: data.lastUpdated || null,
      });
    });
  });
}

async function saveStore(store) {
  return new Promise(resolve => {
    chrome.storage.local.set(store, resolve);
  });
}

async function getData() {
  const store = await getStore();

  // Compute trending products
  const products = Object.values(store.products);

  // Trending score = views * 1 + purchases * 10 + latest soldCount * 0.1
  const scored = products.map(p => ({
    ...p,
    avgPrice: p.prices.length ? (p.prices.reduce((s, x) => s + x.value, 0) / p.prices.length).toFixed(2) : null,
    latestPrice: p.prices.length ? p.prices[p.prices.length - 1].value : null,
    avgRating: p.ratings.length ? (p.ratings.reduce((s, x) => s + parseFloat(x), 0) / p.ratings.length).toFixed(1) : null,
    latestSold: p.soldCounts.length ? p.soldCounts[p.soldCounts.length - 1] : null,
    trendScore: p.viewCount * 1 + p.purchaseCount * 10 + (p.soldCounts[p.soldCounts.length - 1] || 0) * 0.1,
  }));

  scored.sort((a, b) => b.trendScore - a.trendScore);

  return {
    products: scored,
    topProducts: scored.slice(0, 20),
    categories: store.categories,
    domains: store.domains,
    daily: store.daily,
    lastUpdated: store.lastUpdated,
    totalProducts: products.length,
    totalViews: products.reduce((s, p) => s + p.viewCount, 0),
    totalPurchases: products.reduce((s, p) => s + p.purchaseCount, 0),
  };
}

function makeKey(title, domain) {
  return btoa(encodeURIComponent(`${domain}::${title.toLowerCase().trim().substring(0, 80)}`))
    .replace(/[^a-zA-Z0-9]/g, '')
    .substring(0, 32);
}
