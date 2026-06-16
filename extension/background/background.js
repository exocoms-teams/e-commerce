// background.js - Complete and fixed
console.log('[Tracker] Background service worker started');

// ---- State ----
let isTracking = true;
const productCache = new Map();

// ---- Initialize ----
chrome.storage.local.get(['trackingEnabled'], (data) => {
  isTracking = data.trackingEnabled !== false;
  console.log('[Tracker] Initial tracking state:', isTracking ? 'Active' : 'Paused');
});

// ---- Message Handler ----

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[Tracker] Message received:', request.action);
  
  if (request.action === 'productDetected') {
    handleProductDetected(request.product, request.isPurchase, request.source);
    sendResponse({ success: true });
    return true;
  }
  
  if (request.action === 'getData') {
    getData().then(sendResponse);
    return true;
  }
  
  if (request.action === 'clearData') {
    chrome.storage.local.clear(() => {
      sendResponse({ success: true });
    });
    return true;
  }
  
  if (request.action === 'addManualProduct') {
    handleProductDetected(request.product, true, request.product.domain || 'manual');
    sendResponse({ success: true });
    return true;
  }
  
  if (request.action === 'toggleTracking') {
    isTracking = !isTracking;
    chrome.storage.local.set({ trackingEnabled: isTracking }, () => {
      console.log('[Tracker] Tracking:', isTracking ? 'Active' : 'Paused');
      sendResponse({ tracking: isTracking });
    });
    return true;
  }
  
  if (request.action === 'getTrackingStatus') {
    sendResponse({ tracking: isTracking });
    return true;
  }
  
  if (request.action === 'trackingStatus') {
    // Content script notifying status change
    console.log('[Tracker] Content script status:', request.status);
    sendResponse({ success: true });
    return true;
  }
  
  if (request.action === 'forceDetect') {
    // Force detection on current tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'forceDetect' });
      }
    });
    sendResponse({ success: true });
    return true;
  }
});

// ---- Core Logic ----

async function handleProductDetected(product, isPurchase, source) {
  if (!product || !product.title) return;
  if (!isTracking) {
    console.log('[Tracker] Tracking paused, ignoring product');
    return;
  }
  
  // Check cache to avoid duplicates
  const cacheKey = `${source}::${product.title.substring(0, 50)}`;
  const now = Date.now();
  if (productCache.has(cacheKey)) {
    const lastSeen = productCache.get(cacheKey);
    if (now - lastSeen < 30000) {
      return; // Skip if seen in last 30 seconds
    }
  }
  productCache.set(cacheKey, now);
  
  // Clean cache periodically
  if (productCache.size > 200) {
    const oldEntries = [...productCache.entries()].filter(([_, time]) => now - time > 60000);
    for (const [key] of oldEntries) {
      productCache.delete(key);
    }
  }

  // Reject low-quality titles
  const domainRoot = source.replace('www.', '').split('.')[0].toLowerCase();
  if (product.title.toLowerCase().includes(domainRoot) && product.title.length < 30) {
    return;
  }

  try {
    const store = await getStore();
    const key = makeKey(product.title, product.domain || source);
    const nowIso = new Date().toISOString();

    if (!store.products[key]) {
      store.products[key] = {
        id: key,
        title: product.title.substring(0, 200),
        domain: product.domain || source,
        category: product.category || 'General',
        image: product.image || null,
        url: product.url || '',
        firstSeen: nowIso,
        lastSeen: nowIso,
        viewCount: 0,
        purchaseCount: 0,
        prices: [],
        ratings: [],
        reviews: [],
        soldCounts: [],
        viewLog: [],
      };
    }

    const entry = store.products[key];
    entry.viewCount += 1;
    entry.lastSeen = nowIso;

    entry.viewLog = entry.viewLog || [];
    entry.viewLog.push(nowIso);
    if (entry.viewLog.length > 60) {
      entry.viewLog = entry.viewLog.slice(-60);
    }

    if (isPurchase) {
      entry.purchaseCount += 1;
    }

    if (product.price && parseFloat(product.price) > 0) {
      entry.prices.push({ value: parseFloat(product.price), date: nowIso });
      if (entry.prices.length > 50) {
        entry.prices = entry.prices.slice(-50);
      }
    }

    const parsedRating = parseRating(product.rating);
    if (parsedRating !== null) {
      entry.ratings.push(parsedRating);
      if (entry.ratings.length > 20) {
        entry.ratings = entry.ratings.slice(-20);
      }
    }

    if (product.reviews) {
      const parsedReviews = parseInt(String(product.reviews).replace(/[^0-9]/g, '')) || null;
      if (parsedReviews !== null) {
        entry.reviews.push(parsedReviews);
        if (entry.reviews.length > 20) {
          entry.reviews = entry.reviews.slice(-20);
        }
      }
    }

    if (product.soldCount) {
      const raw = String(product.soldCount);
      const isFloor = raw.includes('+');
      const value = parseInt(raw.replace(/[^0-9]/g, '')) || null;
      if (value !== null) {
        entry.soldCounts.push({ value, isFloor, date: nowIso });
        if (entry.soldCounts.length > 20) {
          entry.soldCounts = entry.soldCounts.slice(-20);
        }
      }
    }

    const cat = product.category || 'General';
    store.categories[cat] = (store.categories[cat] || 0) + 1;
    store.domains[source] = (store.domains[source] || 0) + 1;

    const today = new Date().toISOString().split('T')[0];
    if (!store.daily[today]) {
      store.daily[today] = { views: 0, purchases: 0 };
    }
    store.daily[today].views += 1;
    if (isPurchase) {
      store.daily[today].purchases += 1;
    }

    store.lastUpdated = nowIso;
    await saveStore(store);

    // Notify if purchase
    if (isPurchase) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'Purchase Detected!',
        message: `${product.title.substring(0, 60)} tracked as a purchase.`,
        priority: 1,
      });
    }
  } catch (error) {
    console.error('[Tracker] Error handling product:', error);
  }
}

// ---- Trend Scoring ----

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

  const purchaseScore = product.purchaseCount * 10;

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

// ---- Data Operations ----

async function getData() {
  try {
    const store = await getStore();
    const products = Object.values(store.products);
    const now = Date.now();
    const dayMs = 86400000;

    const scored = products.map(p => {
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
        trendScore: computeTrendScore(p),
      };
    });

    scored.sort((a, b) => b.trendScore - a.trendScore);

    const rising = scored.filter(p => p.isRising && p.views7d >= 2).slice(0, 20);

    return {
      products: scored,
      topProducts: scored.slice(0, 20),
      risingProducts: rising,
      categories: store.categories || {},
      domains: store.domains || {},
      daily: store.daily || {},
      lastUpdated: store.lastUpdated || null,
      totalProducts: products.length,
      totalViews: products.reduce((s, p) => s + p.viewCount, 0),
      totalPurchases: products.reduce((s, p) => s + p.purchaseCount, 0),
    };
  } catch (error) {
    console.error('[Tracker] Error getting data:', error);
    return {
      products: [],
      topProducts: [],
      risingProducts: [],
      categories: {},
      domains: {},
      daily: {},
      lastUpdated: null,
      totalProducts: 0,
      totalViews: 0,
      totalPurchases: 0,
    };
  }
}

// ---- Storage Helpers ----

function getStore() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['products', 'categories', 'domains', 'daily', 'lastUpdated'], (data) => {
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

function saveStore(store) {
  return new Promise((resolve) => {
    chrome.storage.local.set(store, resolve);
  });
}

function makeKey(title, domain) {
  const raw = `${domain}::${title.toLowerCase().trim().substring(0, 80)}`;
  let hash = 0;
  for (let i = 0; i < raw.length; i++) {
    const char = raw.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(36).substring(0, 20);
}

function parseRating(raw) {
  if (!raw) return null;
  const match = String(raw).match(/[\d.]+/);
  if (!match) return null;
  const val = parseFloat(match[0]);
  if (val > 0 && val <= 5) return val;
  if (val > 5 && val <= 10) return val / 2;
  return null;
}

console.log('[Tracker] Background service worker ready');