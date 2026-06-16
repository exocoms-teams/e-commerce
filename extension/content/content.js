// content.js - Silent Universal Detector (Works Everywhere, No Console Spam)
console.log('[Tracker] Active on:', window.location.hostname);

// ---- State ----
let isTracking = true;
let processedProducts = new Set();
let detectionInterval = null;
let isInitialized = false;

// ---- Universal Detection ----

function detectProducts() {
  if (!isTracking) return [];
  
  const products = [];
  const found = new Set();
  
  // Look for common product indicators
  const productIndicators = [
    '[data-asin]', '[data-product]', '[data-product-id]', '[data-sku]', '[data-item-id]',
    '.product', '.product-item', '.product-card', '.product-tile', '.product-cell',
    '.item', '.listing', '.listing-card', '.s-item', '.search-result',
    '.grid-item', '.card-item', '[class*="product"]', '[class*="item"]', '[class*="listing"]'
  ];
  
  // Collect potential product elements
  let potentialProducts = [];
  for (const selector of productIndicators) {
    try {
      const elements = document.querySelectorAll(selector);
      if (elements.length > 0) {
        potentialProducts.push(...elements);
      }
    } catch (e) {}
  }
  
  potentialProducts = [...new Set(potentialProducts)];
  
  // Process each potential product
  potentialProducts.forEach((el) => {
    if (el.innerText.length < 10) return;
    
    const id = el.getAttribute('data-asin') || 
               el.getAttribute('data-product-id') ||
               el.getAttribute('data-sku') ||
               el.getAttribute('data-id') ||
               el.getAttribute('id') ||
               el.querySelector('a')?.href ||
               el.innerText.substring(0, 30);
    
    if (found.has(id) || processedProducts.has(id)) return;
    found.add(id);
    processedProducts.add(id);
    
    const product = extractProductUniversal(el);
    if (product && product.title && product.title.length > 2) {
      products.push(product);
    }
  });
  
  // If no products found, look for product links
  if (products.length === 0) {
    const linkPatterns = [
      'a[href*="/product/"]', 'a[href*="/products/"]',
      'a[href*="/p/"]', 'a[href*="/item/"]',
      'a[href*="/dp/"]', 'a[href*="/buy/"]', 'a[href*="/shop/"]'
    ];
    
    for (const pattern of linkPatterns) {
      try {
        const links = document.querySelectorAll(pattern);
        for (const link of links) {
          const title = link.textContent?.trim() || link.getAttribute('aria-label') || link.getAttribute('title');
          if (title && title.length > 5) {
            const id = link.href || title;
            if (!found.has(id) && !processedProducts.has(id)) {
              found.add(id);
              processedProducts.add(id);
              products.push({
                title: title.substring(0, 200),
                price: null,
                url: link.href || window.location.href,
                domain: window.location.hostname.replace('www.', ''),
                timestamp: new Date().toISOString(),
                category: 'General'
              });
            }
          }
        }
        if (products.length > 0) break;
      } catch (e) {}
    }
  }
  
  // Look for structured data (JSON-LD)
  if (products.length === 0) {
    try {
      const scripts = document.querySelectorAll('script[type="application/ld+json"]');
      for (const script of scripts) {
        try {
          const data = JSON.parse(script.textContent);
          const productData = findProductInJson(data);
          if (productData && productData.name) {
            const id = productData.name + (productData.sku || '');
            if (!found.has(id) && !processedProducts.has(id)) {
              found.add(id);
              processedProducts.add(id);
              products.push({
                title: productData.name.substring(0, 200),
                price: productData.price || null,
                description: productData.description || null,
                image: productData.image || null,
                url: window.location.href,
                domain: window.location.hostname.replace('www.', ''),
                timestamp: new Date().toISOString(),
                category: productData.category || 'General'
              });
            }
          }
        } catch (e) {}
      }
    } catch (e) {}
  }
  
  return products;
}

// ---- Helper: Find Product in JSON-LD ----

function findProductInJson(data) {
  if (data['@type'] === 'Product' || data['@type'] === 'product') {
    return data;
  }
  
  if (data['@graph'] && Array.isArray(data['@graph'])) {
    for (const item of data['@graph']) {
      if (item['@type'] === 'Product' || item['@type'] === 'product') {
        return item;
      }
    }
  }
  
  if (Array.isArray(data)) {
    for (const item of data) {
      const result = findProductInJson(item);
      if (result) return result;
    }
  }
  
  if (typeof data === 'object' && data !== null) {
    for (const key of Object.keys(data)) {
      if (typeof data[key] === 'object') {
        const result = findProductInJson(data[key]);
        if (result) return result;
      }
    }
  }
  
  return null;
}

// ---- Universal Product Extraction ----

function extractProductUniversal(el) {
  try {
    // ---- Extract Title ----
    let title = null;
    const titleSelectors = [
      'h1', 'h2', 'h3', 'h4',
      '.product-title', '.product-name', '.item-title',
      '.product-name', '.item-name', '.title',
      '[class*="title"]', '[class*="name"]',
      '[itemprop="name"]', '[property="og:title"]',
      'meta[property="og:title"]'
    ];
    
    for (const selector of titleSelectors) {
      try {
        let el_title = null;
        if (selector.startsWith('meta')) {
          el_title = document.querySelector(selector);
          if (el_title) {
            title = el_title.getAttribute('content') || el_title.getAttribute('value');
          }
        } else {
          el_title = el.querySelector(selector);
          if (el_title) {
            title = el_title.textContent?.trim() || el_title.getAttribute('aria-label') || el_title.getAttribute('title');
          }
        }
        if (title && title.length > 3) break;
      } catch (e) {}
    }
    
    if (!title) {
      title = el.getAttribute('aria-label') || 
              el.getAttribute('data-title') ||
              el.getAttribute('title');
    }
    
    if (!title) {
      const heading = el.querySelector('h1, h2, h3, h4, h5, h6');
      if (heading) {
        title = heading.textContent?.trim() || '';
      }
    }
    
    if (!title) {
      const text = el.textContent?.trim() || '';
      if (text.length > 5 && text.length < 200) {
        title = text;
      }
    }
    
    if (!title || title.length < 3) return null;
    title = title.replace(/^New\s+/, '').replace(/^Details about\s+/, '').trim();
    
    // ---- Extract Price ----
    let price = null;
    const priceSelectors = [
      '.price', '.product-price', '.item-price',
      '[class*="price"]', '[class*="cost"]',
      '[itemprop="price"]', '.a-price .a-offscreen', '.s-item__price'
    ];
    
    for (const selector of priceSelectors) {
      try {
        const el_price = el.querySelector(selector);
        if (el_price) {
          const priceText = el_price.textContent?.trim() || el_price.getAttribute('content') || '';
          const match = priceText.match(/\$?([\d,]+\.?[\d]*)/);
          if (match) {
            price = parseFloat(match[1].replace(/,/g, ''));
            if (price > 0) break;
          }
        }
      } catch (e) {}
    }
    
    if (!price) {
      const metaPrice = document.querySelector('meta[property="product:price:amount"]');
      if (metaPrice) {
        const priceText = metaPrice.getAttribute('content') || '';
        const match = priceText.match(/\$?([\d,]+\.?[\d]*)/);
        if (match) {
          price = parseFloat(match[1].replace(/,/g, ''));
        }
      }
    }
    
    // ---- Extract Image ----
    let image = null;
    const imageSelectors = [
      'img:not([src*="icon"]):not([src*="logo"])',
      '.product-image img', '.product-img',
      '[itemprop="image"]', 'meta[property="og:image"]'
    ];
    
    for (const selector of imageSelectors) {
      try {
        if (selector.startsWith('meta')) {
          const meta = document.querySelector(selector);
          if (meta) {
            image = meta.getAttribute('content');
            if (image && image.startsWith('http')) break;
          }
        } else {
          const img = el.querySelector(selector);
          if (img) {
            image = img.src || img.getAttribute('data-src') || img.getAttribute('lazy-src');
            if (image && image.startsWith('http')) break;
          }
        }
      } catch (e) {}
    }
    
    // ---- Extract Link ----
    let url = '';
    const linkSelectors = [
      'a[href*="/product/"]', 'a[href*="/p/"]',
      'a[href*="/item/"]', 'a[href*="/dp/"]',
      'a:not([href*="#"]):not([href*="javascript"])'
    ];
    
    for (const selector of linkSelectors) {
      try {
        const link = el.querySelector(selector);
        if (link) {
          url = link.href || link.getAttribute('href');
          if (url && url.startsWith('http')) break;
        }
      } catch (e) {}
    }
    
    if (!url) {
      const link = el.querySelector('a');
      if (link) url = link.href || '';
    }
    
    // ---- Extract Category ----
    let category = 'General';
    const categorySelectors = [
      '.category', '.breadcrumb', '.breadcrumbs',
      '[class*="category"]', '[class*="breadcrumb"]'
    ];
    
    for (const selector of categorySelectors) {
      try {
        const el_cat = document.querySelector(selector);
        if (el_cat) {
          const links = el_cat.querySelectorAll('a');
          if (links.length > 0) {
            category = links[links.length - 1].textContent.trim() || category;
            break;
          }
          const items = el_cat.textContent.split(/[>/|]/).map(s => s.trim()).filter(Boolean);
          if (items.length > 0) {
            category = items[items.length - 1] || category;
            break;
          }
        }
      } catch (e) {}
    }
    
    const hostname = window.location.hostname.replace('www.', '');
    
    return {
      title: title.substring(0, 200),
      price: price || null,
      image: image || null,
      category: category || 'General',
      url: url || window.location.href,
      domain: hostname,
      timestamp: new Date().toISOString()
    };
  } catch (e) {
    return null;
  }
}

// ---- Send Product ----

function sendProduct(product) {
  if (!product || !product.title) return;
  
  chrome.runtime.sendMessage({
    action: 'productDetected',
    product: product,
    isPurchase: false,
    source: window.location.hostname
  }, () => {});
}

function processDetectedProducts() {
  if (!isTracking) return;
  const products = detectProducts();
  
  if (products.length > 0) {
    products.forEach((product, index) => {
      setTimeout(() => sendProduct(product), index * 200);
    });
  }
}

// ---- Controls ----

function startTracking() {
  if (isTracking) return;
  isTracking = true;
  if (detectionInterval) clearInterval(detectionInterval);
  detectionInterval = setInterval(processDetectedProducts, 5000);
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

function toggleTracking() {
  if (isTracking) {
    stopTracking();
  } else {
    startTracking();
  }
}

// ---- Init ----

function init() {
  if (isInitialized) return;
  isInitialized = true;
  
  chrome.storage.local.get(['trackingEnabled'], (data) => {
    isTracking = data.trackingEnabled !== false;
    if (isTracking) {
      startTracking();
    }
  });

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
    if (request.action === 'getPageProduct') {
      const products = detectProducts();
      sendResponse({ products: products });
      return true;
    }
  });
  
  setTimeout(processDetectedProducts, 1500);
  setTimeout(processDetectedProducts, 4000);
}

// ---- Start ----

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => setTimeout(init, 500));
} else {
  setTimeout(init, 500);
}