// ============================================================
// MINEA TRACKER - Content Script
// Detects products and purchase signals on e-commerce sites
// ============================================================

console.log('[Minea Tracker] Content script active on:', window.location.hostname);

// Site-specific scrapers for major platforms
const SITE_SCRAPERS = {
  'amazon.com': scrapeAmazon,
  'www.amazon.com': scrapeAmazon,
  'ebay.com': scrapeEbay,
  'www.ebay.com': scrapeEbay,
  'etsy.com': scrapeEtsy,
  'www.etsy.com': scrapeEtsy,
  'shopify.com': scrapeShopify,
  'aliexpress.com': scrapeAliExpress,
  'www.aliexpress.com': scrapeAliExpress,
  'walmart.com': scrapeWalmart,
  'www.walmart.com': scrapeWalmart,
};

// ---- Site-specific scrapers ----

function scrapeAmazon() {
  const titleEl = document.querySelector('#productTitle, #title');
  const priceEl = document.querySelector('.a-price .a-offscreen, #priceblock_ourprice, #priceblock_dealprice');
  const ratingEl = document.querySelector('#acrPopover');
  const reviewsEl = document.querySelector('#acrCustomerReviewText');
  const imageEl = document.querySelector('#landingImage, #imgBlkFront');
  const categoryEl = document.querySelector('#wayfinding-breadcrumbs_feature_div a:last-child');
  const bestsellerEl = document.querySelector('#SalesRank, .badge-text');

  return buildProduct({
    title: titleEl?.textContent?.trim(),
    price: priceEl?.textContent?.trim(),
    rating: ratingEl?.getAttribute('title')?.match(/[\d.]+/)?.[0],
    reviews: reviewsEl?.textContent?.trim(),
    image: imageEl?.src,
    category: categoryEl?.textContent?.trim(),
    badge: bestsellerEl?.textContent?.trim(),
  });
}

function scrapeEbay() {
  const titleEl = document.querySelector('#itemTitle, .x-item-title__mainTitle');
  const priceEl = document.querySelector('#prcIsum, .x-price-primary .ux-textspans');
  const soldEl = document.querySelector('.vi-qtyS-hot-red, [data-testid="x-quantity-sold"]');
  const imageEl = document.querySelector('#icImg, .ux-image-magnify__image--original');
  const categoryEl = document.querySelector('.breadcrumb a:last-child');

  return buildProduct({
    title: titleEl?.textContent?.replace('Details about', '').trim(),
    price: priceEl?.textContent?.trim(),
    soldCount: soldEl?.textContent?.trim(),
    image: imageEl?.src,
    category: categoryEl?.textContent?.trim(),
  });
}

function scrapeEtsy() {
  const titleEl = document.querySelector('h1[data-product-title], .wt-text-body-03');
  const priceEl = document.querySelector('.wt-text-title-03, [data-buy-box-region] .currency-value');
  const reviewsEl = document.querySelector('.wt-display-inline-flex .wt-text-body-01');
  const imageEl = document.querySelector('[data-index="0"] img, .wt-max-width-full');
  const categoryEl = document.querySelector('nav[aria-label="breadcrumb"] a:last-child');

  return buildProduct({
    title: titleEl?.textContent?.trim(),
    price: priceEl?.textContent?.trim(),
    reviews: reviewsEl?.textContent?.trim(),
    image: imageEl?.src,
    category: categoryEl?.textContent?.trim(),
  });
}

function scrapeShopify() {
  // Generic Shopify store scraper
  const titleEl = document.querySelector('.product__title h1, .product-single__title');
  const priceEl = document.querySelector('.product__price, .product-single__price');
  const imageEl = document.querySelector('.product__media img, .product-single__photo');

  return buildProduct({
    title: titleEl?.textContent?.trim(),
    price: priceEl?.textContent?.trim(),
    image: imageEl?.src,
  });
}

function scrapeAliExpress() {
  const titleEl = document.querySelector('.product-title-text, h1[data-pl="product-title"]');
  const priceEl = document.querySelector('.product-price-value, .uniform-banner-box-price');
  const ordersEl = document.querySelector('.product-reviewer-sold');
  const ratingEl = document.querySelector('.overview-rating-average');
  const imageEl = document.querySelector('.magnifier-image, .product-image img');

  return buildProduct({
    title: titleEl?.textContent?.trim(),
    price: priceEl?.textContent?.trim(),
    soldCount: ordersEl?.textContent?.trim(),
    rating: ratingEl?.textContent?.trim(),
    image: imageEl?.src,
  });
}

function scrapeWalmart() {
  const titleEl = document.querySelector('[itemprop="name"], .prod-ProductTitle');
  const priceEl = document.querySelector('[itemprop="price"], .price-characteristic');
  const reviewsEl = document.querySelector('.stars-reviews-count-node');
  const imageEl = document.querySelector('[data-testid="hero-image"] img');

  return buildProduct({
    title: titleEl?.textContent?.trim(),
    price: priceEl?.textContent?.trim(),
    reviews: reviewsEl?.textContent?.trim(),
    image: imageEl?.src,
  });
}

// Generic scraper as fallback
function scrapeGeneric() {
  // Structured data (JSON-LD)
  const jsonLd = document.querySelector('script[type="application/ld+json"]');
  if (jsonLd) {
    try {
      const data = JSON.parse(jsonLd.textContent);
      const product = Array.isArray(data) ? data.find(d => d['@type'] === 'Product') : data;
      if (product && product['@type'] === 'Product') {
        return buildProduct({
          title: product.name,
          price: product.offers?.price?.toString(),
          rating: product.aggregateRating?.ratingValue?.toString(),
          reviews: product.aggregateRating?.reviewCount?.toString(),
          image: Array.isArray(product.image) ? product.image[0] : product.image,
          category: product.category,
        });
      }
    } catch (e) {}
  }

  // Microdata / OpenGraph fallback
  const ogTitle = document.querySelector('meta[property="og:title"]')?.content;
  const ogPrice = document.querySelector('meta[property="product:price:amount"]')?.content;
  const ogImage = document.querySelector('meta[property="og:image"]')?.content;

  if (ogTitle) {
    return buildProduct({ title: ogTitle, price: ogPrice, image: ogImage });
  }

  return null;
}

// ---- Helpers ----

function buildProduct({ title, price, rating, reviews, soldCount, image, category, badge }) {
  if (!title) return null;

  const numericPrice = parseFloat(String(price || '').replace(/[^0-9.]/g, '')) || null;
  const numericRating = parseFloat(rating) || null;
  const numericReviews = parseInt(String(reviews || '').replace(/[^0-9]/g, '')) || null;
  const numericSold = parseInt(String(soldCount || '').replace(/[^0-9]/g, '')) || null;

  return {
    title: title.substring(0, 200),
    price: numericPrice,
    rating: numericRating,
    reviews: numericReviews,
    soldCount: numericSold,
    image: image || null,
    category: category || guessCategory(title),
    badge: badge || null,
    url: window.location.href,
    domain: window.location.hostname.replace('www.', ''),
    timestamp: new Date().toISOString(),
    pageTitle: document.title,
  };
}

function guessCategory(title) {
  const t = title.toLowerCase();
  if (/phone|laptop|tablet|cable|charger|headphone|speaker|camera/.test(t)) return 'Electronics';
  if (/shirt|dress|shoes|pants|jacket|clothing|fashion/.test(t)) return 'Clothing';
  if (/sofa|chair|table|bed|lamp|furniture|home decor/.test(t)) return 'Home & Furniture';
  if (/book|novel|guide|manual/.test(t)) return 'Books';
  if (/vitamin|supplement|health|beauty|skincare/.test(t)) return 'Health & Beauty';
  if (/toy|game|kids|children/.test(t)) return 'Toys & Games';
  if (/food|snack|drink|coffee|tea/.test(t)) return 'Food & Drink';
  if (/sport|fitness|gym|yoga|outdoor/.test(t)) return 'Sports';
  if (/pet|dog|cat|fish/.test(t)) return 'Pet Supplies';
  return 'General';
}

// ---- Purchase signal detection ----

function detectPurchaseSignal() {
  const url = window.location.href.toLowerCase();
  const body = document.body.innerText.toLowerCase();

  const purchaseKeywords = [
    'order confirmed', 'thank you for your order', 'order placed',
    'purchase confirmed', 'payment successful', 'order #', 'order number',
    'your order has been', 'successfully placed'
  ];

  return purchaseKeywords.some(kw => url.includes(kw.replace(/ /g, '-')) || body.includes(kw));
}

// ---- Main execution ----

function run() {
  const hostname = window.location.hostname;
  const scraper = SITE_SCRAPERS[hostname] || scrapeGeneric;
  const product = scraper();

  if (!product) return;

  const isPurchase = detectPurchaseSignal();

  chrome.runtime.sendMessage({
    action: 'productDetected',
    product,
    isPurchase,
    source: hostname,
  }, response => {
    if (chrome.runtime.lastError) {
      // Extension context may be invalidated; ignore silently
    }
  });
}

// Run on load and after dynamic content settles
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => setTimeout(run, 1500));
} else {
  setTimeout(run, 1500);
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getPageProduct') {
    const hostname = window.location.hostname;
    const scraper = SITE_SCRAPERS[hostname] || scrapeGeneric;
    sendResponse({ product: scraper() });
  }
});
