console.log('[Tracker] Background service worker started');

// ---- Message handler ----

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'productDetected') {
    handleProductDetected(request.product, request.isPurchase, request.source);
  }
  if (request.action === 'getData') {
    getData().then(sendResponse);
    return true;
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

  // Reject low-quality generic titles that match the domain (og:title fallback junk)
  if (product.title.toLowerCase().includes(source.replace('www.', '').split('.')[0].toLowerCase()) &&
      product.title.length < 30) return;

  const store = await getStore();
  const key = makeKey(product.title, product.domain);
  const now = new Date().toISOString();

  if (!store.products[key]) {
    store.products[key] = {
      id: key,
      title: product.title,
      domain: product.domain,
      category: product.category,
      image: product.image,
      url: product.url,
      firstSeen: now,
      lastSeen: now,
      viewCount: 0,
      purchaseCount: 0,
      prices: [],
      ratings: [],
      reviews: [],
      soldCounts: [],
      // Timestamped view log for velocity calculation (kept to last 60 entries)
      viewLog: [],
    };
  }

  const entry = store.products[key];

  entry.viewCount += 1;
  entry.lastSeen = now;

  // Store timestamped view for velocity tracking
  entry.viewLog = entry.viewLog || [];
  entry.viewLog.push(now);
  if (entry.viewLog.length > 60) entry.viewLog = entry.viewLog.slice(-60);

  if (isPurchase) {
    entry.purchaseCount += 1;
  }

  if (product.price && product.price > 0) {
    entry.prices.push({ value: product.price, date: now });
    if (entry.prices.length > 50) entry.prices = entry.prices.slice(-50);
  }

  // Robust rating parser — handles "4.5 out of 5 stars"
  const parsedRating = parseRating(product.rating);
  if (parsedRating !== null) entry.ratings.push(parsedRating);

  const parsedReviews = parseInt(String(product.reviews || '').replace(/[^0-9]/g, '')) || null;
  if (parsedReviews !== null) entry.reviews.push(parsedReviews);

  // Store sold count with floor flag for values like "1000+"
  if (product.soldCount) {
    const raw = String(product.soldCount);
    const isFloor = raw.includes('+');
    const value = parseInt(raw.replace(/[^0-9]/g, '')) || null;
    if (value !== null) {
      entry.soldCounts.push({ value, isFloor, date: now });
    }
  }

  ['ratings', 'reviews'].forEach(k => {
    if (entry[k].length > 20) entry[k] = entry[k].slice(-20);
  });
  if (entry.soldCounts.length > 20) entry.soldCounts = entry.soldCounts.slice(-20);

  const cat = product.category || 'General';
  store.categories[cat] = (store.categories[cat] || 0) + 1;
  store.domains[source] = (store.domains[source] || 0) + 1;

  const today = new Date().toISOString().split('T')[0];
  if (!store.daily[today]) store.daily[today] = { views: 0, purchases: 0 };
  store.daily[today].views += 1;
  if (isPurchase) store.daily[today].purchases += 1;

  store.lastUpdated = now;
  await saveStore(store);

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

// ---- Trend Scoring ----

function computeTrendScore(product) {
  const now = Date.now();
  const dayMs = 86400000;

  // Time-decayed view velocity: weight recent views more heavily
  const viewLog = product.viewLog || [];
  const views7d = viewLog.filter(t => now - new Date(t).getTime() < 7 * dayMs).length;
  const views30d = viewLog.filter(t => now - new Date(t).getTime() < 30 * dayMs).length;
  const velocityScore = views7d * 3 + views30d * 1;

  // Rising multiplier: compare last 3 days to previous 3 days
  const views3d = viewLog.filter(t => now - new Date(t).getTime() < 3 * dayMs).length;
  const views3to6d = viewLog.filter(t => {
    const age = now - new Date(t).getTime();
    return age >= 3 * dayMs && age < 6 * dayMs;
  }).length;
  const risingMultiplier = views3d > 0 && views3d > views3to6d * 1.5 ? 1.5 : 1.0;

  // Sold count delta (growth) instead of raw latest value
  const soldCounts = product.soldCounts || [];
  let soldScore = 0;
  if (soldCounts.length >= 2) {
    const delta = soldCounts[soldCounts.length - 1].value - soldCounts[0].value;
    soldScore = Math.max(0, delta) * 0.5;
  } else if (soldCounts.length === 1) {
    soldScore = soldCounts[0].value * 0.05; // small base credit for first reading
  }

  // Purchase signal
  const purchaseScore = product.purchaseCount * 10;

  // Price drop bonus
  let priceSignal = 0;
  const prices = product.prices || [];
  if (prices.length >= 2) {
    const avgPrice = prices.reduce((s, p) => s + p.value, 0) / prices.length;
    const latestPrice = prices[prices.length - 1].value;
    if (latestPrice < avgPrice * 0.95) priceSignal = 8; // 5%+ drop
    if (latestPrice < avgPrice * 0.85) priceSignal = 15; // 15%+ drop
  }

  // Rating quality signal — Bayesian-style: rating * log(1 + review_count)
  let ratingSignal = 0;
  const ratings = product.ratings || [];
  const reviews = product.reviews || [];
  if (ratings.length > 0) {
    const avgRating = ratings.reduce((s, r) => s + r, 0) / ratings.length;
    const latestReviewCount = reviews.length > 0 ? reviews[reviews.length - 1] : 1;
    ratingSignal = avgRating * Math.log(1 + latestReviewCount) * 0.3;
  }

  return Math.round(
    (velocityScore + soldScore + purchaseScore + priceSignal + ratingSignal) * risingMultiplier
  );
}

// ---- Data output ----

async function getData() {
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

    const avgPrice = prices.length
      ? (prices.reduce((s, x) => s + x.value, 0) / prices.length).toFixed(2)
      : null;
    const latestPrice = prices.length ? prices[prices.length - 1].value : null;
    const avgRating = ratings.length
      ? (ratings.reduce((s, x) => s + x, 0) / ratings.length).toFixed(1)
      : null;
    const latestSold = soldCounts.length ? soldCounts[soldCounts.length - 1].value : null;

    // Sold delta for display
    const soldDelta = soldCounts.length >= 2
      ? soldCounts[soldCounts.length - 1].value - soldCounts[0].value
      : null;

    // Price trend
    let priceTrend = null;
    if (prices.length >= 2 && avgPrice) {
      const diff = latestPrice - parseFloat(avgPrice);
      priceTrend = Math.round((diff / parseFloat(avgPrice)) * 100);
    }

    // Velocity for display
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

  // Rising products: significant velocity increase in last 3 days
  const rising = scored
    .filter(p => p.isRising && p.views7d >= 2)
    .slice(0, 10);

  return {
    products: scored,
    topProducts: scored.slice(0, 20),
    risingProducts: rising,
    categories: store.categories,
    domains: store.domains,
    daily: store.daily,
    lastUpdated: store.lastUpdated,
    totalProducts: products.length,
    totalViews: products.reduce((s, p) => s + p.viewCount, 0),
    totalPurchases: products.reduce((s, p) => s + p.purchaseCount, 0),
  };
}

// ---- Helpers ----

function parseRating(raw) {
  if (!raw) return null;
  const match = String(raw).match(/[\d.]+/);
  if (!match) return null;
  const val = parseFloat(match[0]);
  // Normalize 0-5 scale; reject implausible values
  if (val > 0 && val <= 5) return val;
  if (val > 5 && val <= 10) return val / 2; // some sites use 10-point scale
  return null;
}

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

function makeKey(title, domain) {
  return btoa(encodeURIComponent(`${domain}::${title.toLowerCase().trim().substring(0, 80)}`))
    .replace(/[^a-zA-Z0-9]/g, '')
    .substring(0, 32);
}