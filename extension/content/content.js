// content.js - Smart Product Detector (E-commerce Only)
console.log('[Tracker] Active on:', window.location.hostname);

// ---- E-commerce domain list ----
const ECOMMERCE_DOMAINS = [
  'amazon', 'amzn', 'ebay', 'etsy', 'walmart', 'target', 'bestbuy',
  'aliexpress', 'alibaba', 'shopify', 'etsy', 'zara', 'hm', 'nike',
  'adidas', 'shein', 'temu', 'wish', 'newegg', 'costco', 'barnesandnoble',
  'bookdepository', 'wayfair', 'homedepot', 'lowes', 'macys', 'kohl',
  'sephora', 'ultra', 'shop', 'store', 'buy', 'product'
];

// ---- State ----
let isTracking = true;
let processedProducts = new Set();
let detectionInterval = null;
let isInitialized = false;
let domainMatched = false;

// ---- Check if current domain is e-commerce ----
function isEcommerceDomain() {
  const hostname = window.location.hostname.toLowerCase().replace('www.', '');
  
  // Check if it's a known e-commerce domain
  for (const d of ECOMMERCE_DOMAINS) {
    if (hostname.includes(d)) return true;
  }
  
  // Check for shopping-related URL patterns
  const url = window.location.href.toLowerCase();
  const shoppingPaths = ['/product/', '/products/', '/item/', '/dp/', '/buy/', '/shop/', '/cart/', '/checkout/'];
  for (const path of shoppingPaths) {
    if (url.includes(path)) return true;
  }
  
  return false;
}

// ---- Domain-specific extractors ----
const extractors = {
  // Amazon
  amazon: function() {
    const products = [];
    const items = document.querySelectorAll('[data-asin]:not([data-asin=""])');
    
    for (const el of items) {
      const asin = el.getAttribute('data-asin');
      if (!asin || asin.length < 5) continue;
      
      const titleEl = el.querySelector('h2 a, .a-link-normal .a-text-normal, .s-title-instructions-style a, [data-cy="title"]');
      const title = titleEl ? titleEl.textContent.trim() : null;
      
      if (!title || title.length < 5) continue;
      
      const priceEl = el.querySelector('.a-price .a-offscreen, .a-price-whole, .s-price, [data-a-size="xl"] .a-price');
      let price = null;
      if (priceEl) {
        const priceText = priceEl.textContent.replace(/[^0-9.]/g, '');
        if (priceText) price = parseFloat(priceText);
      }
      
      const img = el.querySelector('img.s-image, img[data-image-latency]');
      const image = img ? (img.src || img.getAttribute('data-src')) : null;
      
      const urlEl = el.querySelector('a.a-link-normal, a.s-no-outline');
      const url = urlEl ? urlEl.href : '';
      
      const ratingEl = el.querySelector('.a-icon-alt, .a-row .a-icon-star');
      let rating = null;
      if (ratingEl) {
        const match = ratingEl.textContent.match(/[\d.]+/);
        if (match) rating = parseFloat(match[0]);
      }
      
      const reviewEl = el.querySelector('.a-size-base, .a-size-small .a-text-normal');
      let reviews = null;
      if (reviewEl) {
        const match = reviewEl.textContent.replace(/,/g, '').match(/\d+/);
        if (match) reviews = parseInt(match[0]);
      }
      
      products.push({
        title: title.substring(0, 200),
        price: price,
        image: image,
        url: url || window.location.href,
        domain: 'amazon.com',
        category: 'General',
        rating: rating,
        reviews: reviews,
        timestamp: new Date().toISOString()
      });
    }
    
    return products;
  },
  
  // eBay
  ebay: function() {
    const products = [];
    const items = document.querySelectorAll('.s-item, .srp-results .s-item, .lv-item');
    
    for (const el of items) {
      const titleEl = el.querySelector('.s-item__title, .lvtitle, .vip');
      const title = titleEl ? titleEl.textContent.trim() : null;
      if (!title || title.length < 5 || title.includes('Shop by')) continue;
      
      const priceEl = el.querySelector('.s-item__price, .lvprice, .vi-price, .notranslate');
      let price = null;
      if (priceEl) {
        const priceText = priceEl.textContent.replace(/[^0-9.]/g, '');
        if (priceText) price = parseFloat(priceText);
      }
      
      const img = el.querySelector('img, .s-item__image-img');
      const image = img ? (img.src || img.getAttribute('data-src')) : null;
      
      const urlEl = el.querySelector('a.s-item__link, a.lvtitle, a.vip');
      const url = urlEl ? urlEl.href : '';
      
      const soldEl = el.querySelector('.s-item__hotness, .s-item__purchaseOptions, .lvformat');
      let soldCount = null;
      if (soldEl) {
        const match = soldEl.textContent.match(/(\d+)\s*sold/i);
        if (match) soldCount = parseInt(match[1]);
      }
      
      products.push({
        title: title.substring(0, 200),
        price: price,
        image: image,
        url: url || window.location.href,
        domain: 'ebay.com',
        category: 'General',
        soldCount: soldCount,
        timestamp: new Date().toISOString()
      });
    }
    
    return products;
  },
  
  // Etsy
  etsy: function() {
    const products = [];
    const items = document.querySelectorAll('.listing-card, .wt-grid__item-xs-6, .wt-grid__item-xs-4, .listing-preview');
    
    for (const el of items) {
      const titleEl = el.querySelector('.listing-card__title, .wt-text-caption, .text-body-small');
      const title = titleEl ? titleEl.textContent.trim() : null;
      if (!title || title.length < 5) continue;
      
      const priceEl = el.querySelector('.wt-text-price, .currency-value, .price');
      let price = null;
      if (priceEl) {
        const priceText = priceEl.textContent.replace(/[^0-9.]/g, '');
        if (priceText) price = parseFloat(priceText);
      }
      
      const img = el.querySelector('img, .listing-card-image img');
      const image = img ? (img.src || img.getAttribute('data-src')) : null;
      
      const urlEl = el.querySelector('a.listing-link, a.wt-display-block');
      const url = urlEl ? urlEl.href : '';
      
      const ratingEl = el.querySelector('.star-rating, .wt-text-star-rating');
      let rating = null;
      if (ratingEl) {
        const match = ratingEl.textContent.match(/[\d.]+/);
        if (match) rating = parseFloat(match[0]);
      }
      
      products.push({
        title: title.substring(0, 200),
        price: price,
        image: image,
        url: url || window.location.href,
        domain: 'etsy.com',
        category: 'General',
        rating: rating,
        timestamp: new Date().toISOString()
      });
    }
    
    return products;
  },
  
  // Walmart
  walmart: function() {
    const products = [];
    const items = document.querySelectorAll('[data-testid="list-view"], .search-result, .product-card');
    
    for (const el of items) {
      const titleEl = el.querySelector('[data-testid="product-title"], .product-title, .w_font');
      const title = titleEl ? titleEl.textContent.trim() : null;
      if (!title || title.length < 5) continue;
      
      const priceEl = el.querySelector('[data-testid="price"], .price-now, .price-display');
      let price = null;
      if (priceEl) {
        const priceText = priceEl.textContent.replace(/[^0-9.]/g, '');
        if (priceText) price = parseFloat(priceText);
      }
      
      const img = el.querySelector('img, .product-image');
      const image = img ? (img.src || img.getAttribute('data-src')) : null;
      
      const urlEl = el.querySelector('a[data-testid="product-title-link"], a.product-link');
      const url = urlEl ? urlEl.href : '';
      
      const ratingEl = el.querySelector('.rating-stars, .product-rating');
      let rating = null;
      if (ratingEl) {
        const match = ratingEl.textContent.match(/[\d.]+/);
        if (match) rating = parseFloat(match[0]);
      }
      
      products.push({
        title: title.substring(0, 200),
        price: price,
        image: image,
        url: url || window.location.href,
        domain: 'walmart.com',
        category: 'General',
        rating: rating,
        timestamp: new Date().toISOString()
      });
    }
    
    return products;
  },
  
  // Target
  target: function() {
    const products = [];
    const items = document.querySelectorAll('[data-testid="product-card"], .product-card, .h-display-flex');
    
    for (const el of items) {
      const titleEl = el.querySelector('[data-testid="product-title"], .product-title, .h-text');
      const title = titleEl ? titleEl.textContent.trim() : null;
      if (!title || title.length < 5) continue;
      
      const priceEl = el.querySelector('[data-testid="price"], .price, .h-text-price');
      let price = null;
      if (priceEl) {
        const priceText = priceEl.textContent.replace(/[^0-9.]/g, '');
        if (priceText) price = parseFloat(priceText);
      }
      
      const img = el.querySelector('img, .product-image');
      const image = img ? (img.src || img.getAttribute('data-src')) : null;
      
      const urlEl = el.querySelector('a[data-testid="product-link"], a.product-link');
      const url = urlEl ? urlEl.href : '';
      
      products.push({
        title: title.substring(0, 200),
        price: price,
        image: image,
        url: url || window.location.href,
        domain: 'target.com',
        category: 'General',
        timestamp: new Date().toISOString()
      });
    }
    
    return products;
  },
  
  // General fallback extractor
  general: function() {
    const products = [];
    const selectors = [
      '[data-product]', '[data-product-id]', '[data-sku]', '[data-item-id]',
      '.product-item', '.product-card', '.product-tile', '.listing-item',
      '.item-card', '.search-result', '.product'
    ];
    
    let elements = [];
    for (const selector of selectors) {
      try {
        const found = document.querySelectorAll(selector);
        if (found.length > 0) {
          elements = [...elements, ...found];
        }
      } catch (e) {}
    }
    
    elements = [...new Set(elements)];
    
    // Filter out navigation elements
    for (const el of elements) {
      // Skip if it's clearly not a product
      if (el.closest('nav, header, footer, .nav, .menu, .sidebar, .footer')) continue;
      
      const title = el.getAttribute('data-title') || 
                    el.getAttribute('aria-label') ||
                    el.querySelector('h1, h2, h3, h4, .title, .name')?.textContent?.trim() ||
                    el.textContent?.trim();
      
      if (!title || title.length < 5 || title.length > 200) continue;
      
      // Skip if title looks like navigation text
      if (/^(home|menu|account|cart|checkout|login|register|search|filter|sort|page|next|prev)/i.test(title)) continue;
      
      const priceEl = el.querySelector('[class*="price"], [class*="cost"], [itemprop="price"]');
      let price = null;
      if (priceEl) {
        const priceText = priceEl.textContent.replace(/[^0-9.]/g, '');
        if (priceText) price = parseFloat(priceText);
      }
      
      const img = el.querySelector('img:not(.icon):not(.logo)');
      const image = img ? (img.src || img.getAttribute('data-src')) : null;
      
      const urlEl = el.querySelector('a[href*="/product/"], a[href*="/p/"], a[href*="/item/"]');
      const url = urlEl ? urlEl.href : '';
      
      products.push({
        title: title.substring(0, 200),
        price: price,
        image: image,
        url: url || window.location.href,
        domain: window.location.hostname.replace('www.', ''),
        category: 'General',
        timestamp: new Date().toISOString()
      });
    }
    
    return products;
  }
};

// ---- Get domain-specific extractor ----
function getExtractor() {
  const hostname = window.location.hostname.toLowerCase();
  
  if (hostname.includes('amazon') || hostname.includes('amzn')) return extractors.amazon;
  if (hostname.includes('ebay')) return extractors.ebay;
  if (hostname.includes('etsy')) return extractors.etsy;
  if (hostname.includes('walmart')) return extractors.walmart;
  if (hostname.includes('target')) return extractors.target;
  
  // Check URL patterns
  const url = window.location.href.toLowerCase();
  if (url.includes('/product/') || url.includes('/products/') || url.includes('/item/')) {
    return extractors.general;
  }
  
  return extractors.general;
}

// ---- Detect products ----
function detectProducts() {
  if (!isTracking || !domainMatched) return [];
  
  try {
    const extractor = getExtractor();
    const products = extractor();
    
    // Filter out duplicates and low-quality results
    const validProducts = [];
    const seen = new Set();
    
    for (const p of products) {
      if (!p || !p.title || p.title.length < 3) continue;
      
      const key = p.title.substring(0, 40).toLowerCase();
      if (seen.has(key) || processedProducts.has(key)) continue;
      
      seen.add(key);
      processedProducts.add(key);
      
      // Only include if it looks like a real product (has price or image or reasonable title)
      if (p.price !== null && p.price > 0) {
        validProducts.push(p);
      } else if (p.image && p.image.startsWith('http')) {
        validProducts.push(p);
      } else if (p.title.length > 10 && !p.title.includes(' ')) {
        validProducts.push(p);
      }
    }
    
    return validProducts.slice(0, 20); // Limit per scan
  } catch (e) {
    console.warn('[Tracker] Detection error:', e);
    return [];
  }
}

// ---- Send product to background ----
function sendProduct(product) {
  if (!product || !product.title) return;
  
  chrome.runtime.sendMessage({
    action: 'productDetected',
    product: product,
    isPurchase: false,
    source: window.location.hostname
  }, () => {});
}

// ---- Process detected products with debounce ----
let processingTimeout = null;

function processDetectedProducts() {
  if (!isTracking || !domainMatched) return;
  
  if (processingTimeout) {
    clearTimeout(processingTimeout);
  }
  
  processingTimeout = setTimeout(() => {
    const products = detectProducts();
    
    if (products.length > 0) {
      console.log(`[Tracker] Found ${products.length} products on page`);
      products.forEach((product, index) => {
        setTimeout(() => sendProduct(product), index * 300);
      });
    }
    
    processingTimeout = null;
  }, 500);
}

// ---- Controls ----
function startTracking() {
  if (isTracking) return;
  isTracking = true;
  if (detectionInterval) clearInterval(detectionInterval);
  detectionInterval = setInterval(processDetectedProducts, 8000);
  processDetectedProducts();
}

function stopTracking() {
  if (!isTracking) return;
  isTracking = false;
  if (detectionInterval) {
    clearInterval(detectionInterval);
    detectionInterval = null;
  }
}

// ---- Init ----
function init() {
  if (isInitialized) return;
  isInitialized = true;
  
  // Check if we're on an e-commerce site
  domainMatched = isEcommerceDomain();
  
  if (!domainMatched) {
    console.log('[Tracker] Not an e-commerce site. Tracking disabled.');
    return;
  }
  
  console.log('[Tracker] E-commerce domain detected. Starting tracker.');
  
  chrome.storage.local.get(['trackingEnabled'], (data) => {
    isTracking = data.trackingEnabled !== false;
    if (isTracking) {
      startTracking();
    }
  });

  // Listen for messages
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'toggleTracking') {
      toggleTracking();
      sendResponse({ tracking: isTracking });
      return true;
    }
    if (request.action === 'getTrackingStatus') {
      sendResponse({ tracking: isTracking });
      return true;
    }
    if (request.action === 'forceDetect') {
      processDetectedProducts();
      sendResponse({ success: true });
      return true;
    }
  });
  
  // Initial detection after page load
  setTimeout(processDetectedProducts, 2000);
  setTimeout(processDetectedProducts, 5000);
}

// ---- Start ----
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => setTimeout(init, 300));
} else {
  setTimeout(init, 300);
}